"""Sweep driver. Writes TWO files per run (paired design): lean metrics jsonl +
full eval transcript jsonl. Class-interleaved so partial data is representative.
Ported from bench_v2 run_sweep.py. run_sweep takes MODEL OBJECTS (each with __call__,
.reset(), .name, .calls/.pt/.ct) so it can be driven by real TokModels OR a fake model
(runners/dry_run.py) without touching the API.
"""
from __future__ import annotations
import asyncio, json, sys, time
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v3.instances.generate import load_library
from bench_v3.families.base import build_scenario
from bench_v3.core.episode import run_episode
from bench_v3.scoring.outcomes import score
from bench_v3.scoring.secondary import fault_cleared, needless_interventions
from bench_v3.scoring.critical_fail import cf_reason
from bench_v3.arms.registry import build_arm
from bench_v3.arms.base import visible_rank
from bench_v3.arms.single import policy_single

_CLIENTS = None


class TokModel:
    """Callable (system,user)->text accumulating calls+tokens; reset per episode.
    Lazily builds api_clients (real models). Not used by dry_run."""
    def __init__(self, model_name, temperature=1.0, max_tokens=1500):
        global _CLIENTS
        from api_clients import make_clients
        if _CLIENTS is None:
            _CLIENTS = make_clients()
        self.name = model_name; self.temp = temperature; self.maxtok = max_tokens
        self.calls = self.pt = self.ct = 0

    def reset(self):
        self.calls = self.pt = self.ct = 0

    def __call__(self, system, user):
        from api_clients import chat
        r = asyncio.run(chat(_CLIENTS[self.name], self.name, system, user,
                             temperature=self.temp, max_tokens=self.maxtok))
        self.calls += 1; self.pt += r.prompt_tokens; self.ct += r.completion_tokens
        return r.text or ""


# Sampling-temperature convention (bench_v2): the ACTOR runs at temperature 1.0 -- this is
# what gives sc3/team their 3 distinct samples/step AND bo3 its 3 distinct rollouts on the
# (now) shared noise seed. At temperature 0 those arms degenerate to single. The critic/judge
# runs cooler (0.4). Use these factories so a launcher can't set the wrong temperature.
def make_actor(name):
    return TokModel(name, temperature=1.0)

def make_critic(name):
    return TokModel(name, temperature=0.4)


def interleave(instances):
    groups = OrderedDict()
    for inst in instances:
        groups.setdefault(inst.fault_class, []).append(inst)
    out, i = [], 0
    while True:
        added = False
        for g in groups.values():
            if i < len(g):
                out.append(g[i]); added = True
        if not added:
            break
        i += 1
    return out


def _done_keys(out_path):
    """Set of (arm, seed, instance) already in the metrics file -> resume support
    (re-launch skips completed episodes; critical for long/paid runs)."""
    done = set()
    try:
        for l in open(out_path):
            r = json.loads(l)
            done.add((r["arm"], r["seed"], r["instance"]))
    except FileNotFoundError:
        pass
    return done


def run_sweep(arm_names, actor, critic, seeds, instances, out_path,
              verbose=True, do_interleave=True, resume=True):
    import random
    def tok_probe():
        return (actor.calls + (critic.calls if critic else 0),
                actor.pt + (critic.pt if critic else 0),
                actor.ct + (critic.ct if critic else 0))
    if do_interleave:
        instances = interleave(instances)
    done = _done_keys(out_path) if resume else set()
    if done and verbose:
        print(f"  resume: skipping {len(done)} already-completed episodes", flush=True)
    outf = open(out_path, "a")
    tpath = out_path[:-6] + ".transcript.jsonl" if out_path.endswith(".jsonl") else out_path + ".transcript.jsonl"
    tf = open(tpath, "a")
    n = 0; skipped = 0; t0 = time.time()
    for arm_name in arm_names:
        for seed in seeds:
            rng = random.Random(1000 + seed)
            for inst in instances:
                if (arm_name, seed, inst.id) in done:
                    skipped += 1
                    continue
                actor.reset()
                if critic:
                    critic.reset()
                if arm_name == "bo3":
                    # All 3 rollouts share the SAME scenario/noise seed as every other arm
                    # for this (instance, seed); only the model's temperature sampling differs.
                    # (Diverges intentionally from bench_v2's seed*100+i, which gave bo3 three
                    # noise realizations -> a confound where bo3 could win by drawing favorable
                    # noise rather than by the extra model attempts. Noise-matched here so bo3 is
                    # a clean equal-compute control vs team. Requires actor temperature > 0.)
                    eps = [run_episode(policy_single(actor), build_scenario(inst, seed), tok_probe=tok_probe)
                           for _ in range(3)]
                    ep = max(eps, key=lambda e: visible_rank(e, inst.target_concentration_M))
                else:
                    pol = build_arm(arm_name, actor, critic, rng)
                    ep = run_episode(pol, build_scenario(inst, seed), tok_probe=tok_probe)
                outcome = score(ep, inst)
                rec = {"arm": arm_name, "actor": getattr(actor, "name", "?"),
                       "critic": (getattr(critic, "name", None) if critic else None), "seed": seed,
                       "instance": inst.id, "family": inst.family, "class": inst.fault_class,
                       "outcome": outcome, "fault_cleared": fault_cleared(ep, inst),
                       "cf_reason": cf_reason(ep, inst), "needless": needless_interventions(ep, inst),
                       "committed_types": ep.committed_types, "actions_used": ep.actions_used,
                       "parse_fails": ep.parse_fails,
                       "actor_calls": actor.calls, "actor_pt": actor.pt, "actor_ct": actor.ct,
                       "critic_calls": (critic.calls if critic else 0),
                       "critic_pt": (critic.pt if critic else 0), "critic_ct": (critic.ct if critic else 0)}
                outf.write(json.dumps(rec) + "\n"); outf.flush()
                trec = {"arm": arm_name, "actor": getattr(actor, "name", "?"),
                        "critic": (getattr(critic, "name", None) if critic else None), "seed": seed,
                        "instance": inst.id, "family": inst.family, "class": inst.fault_class,
                        "outcome": outcome, "cf_reason": cf_reason(ep, inst),
                        "needless": needless_interventions(ep, inst), "terminal": ep.terminal,
                        "actions_used": ep.actions_used, "steps": ep.steps}
                tf.write(json.dumps(trec) + "\n"); tf.flush()
                n += 1
                if verbose and n % 10 == 0:
                    el = time.time() - t0
                    print(f"  {n} ep, {round(el)}s, {round(el/n,1)}s/ep (last {arm_name}/{inst.id}={outcome})", flush=True)
    outf.close(); tf.close()
    return n, time.time() - t0
