"""Ablation sweep driver (A1-A3). Mirrors runners/run_sweep.run_sweep -- same record
schema, same class-interleave, same resume + double-jsonl (metrics + transcript) -- but
dispatches through the three ablation arm files instead of the frozen arm registry, and
the arms are actor-only (no critic, no bo3). The frozen run_sweep is NOT imported for its
loop (it dispatches via the frozen build_arm); its side-effect-free helpers (interleave,
_done_keys, make_actor) ARE reused by import.

Output -> bench_v3/results/v3_ablation_<which>_seed<seed>.jsonl (+.transcript.jsonl),
distinct from the frozen v3_tier1_* files. Resumable.

usage: python -m bench_v3.ablation.run_ablation <weak|strong> <seed> [arm1,arm2,...]
       defaults: weak, seed 0, all three ablation arms.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v3.instances.generate import load_library
from bench_v3.families.base import build_scenario
from bench_v3.core.episode import run_episode
from bench_v3.scoring.outcomes import score
from bench_v3.scoring.secondary import fault_cleared, needless_interventions
from bench_v3.scoring.critical_fail import cf_reason
from bench_v3.runners.run_sweep import interleave, _done_keys, make_actor
from bench_v3.ablation.a1_rubric_reassert import policy_rubric_reassert, ARM_NAME as A1
from bench_v3.ablation.a2_single_stoprule import policy_single_stoprule, ARM_NAME as A2
from bench_v3.ablation.a3_single_personaB import policy_single_personaB, ARM_NAME as A3

ABLATION_ARMS = [A1, A2, A3]


def build_ablation_arm(name, actor):
    """arm-name -> per-step policy. Actor-only (no critic, no rng)."""
    table = {
        A1: lambda: policy_rubric_reassert(actor),
        A2: lambda: policy_single_stoprule(actor),
        A3: lambda: policy_single_personaB(actor),
    }
    return table[name]()


def run_ablation_sweep(arm_names, actor, seeds, instances, out_path,
                       verbose=True, do_interleave=True, resume=True):
    def tok_probe():
        return (actor.calls, actor.pt, actor.ct)
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
            for inst in instances:
                if (arm_name, seed, inst.id) in done:
                    skipped += 1
                    continue
                actor.reset()
                pol = build_ablation_arm(arm_name, actor)
                ep = run_episode(pol, build_scenario(inst, seed), tok_probe=tok_probe)
                outcome = score(ep, inst)
                rec = {"arm": arm_name, "actor": getattr(actor, "name", "?"),
                       "critic": None, "seed": seed,
                       "instance": inst.id, "family": inst.family, "class": inst.fault_class,
                       "outcome": outcome, "fault_cleared": fault_cleared(ep, inst),
                       "cf_reason": cf_reason(ep, inst), "needless": needless_interventions(ep, inst),
                       "committed_types": ep.committed_types, "actions_used": ep.actions_used,
                       "parse_fails": ep.parse_fails,
                       "actor_calls": actor.calls, "actor_pt": actor.pt, "actor_ct": actor.ct,
                       "critic_calls": 0, "critic_pt": 0, "critic_ct": 0}
                outf.write(json.dumps(rec) + "\n"); outf.flush()
                trec = {"arm": arm_name, "actor": getattr(actor, "name", "?"),
                        "critic": None, "seed": seed,
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


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "weak"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    arms = sys.argv[3].split(",") if len(sys.argv) > 3 else list(ABLATION_ARMS)
    bad = [a for a in arms if a not in ABLATION_ARMS]
    if bad:
        raise SystemExit(f"unknown ablation arm(s) {bad}; known = {ABLATION_ARMS}")
    actor_model = "qwen32b" if which == "weak" else "qwen_max"
    actor = make_actor(actor_model)      # temperature 1.0 factory (frozen convention)
    lib = load_library()
    (ROOT / "bench_v3" / "results").mkdir(exist_ok=True)
    out = str(ROOT / "bench_v3" / "results" / f"v3_ablation_{which}_seed{seed}.jsonl")
    print(f"v3 ABLATION [{which}] actor={actor_model}: {arms} x {len(lib)} x seed{seed} -> {out}", flush=True)
    t0 = time.time()
    n, el = run_ablation_sweep(arms, actor, [seed], lib, out, verbose=True, resume=True)
    print(f"v3 ABLATION [{which}] done: {n} new ep, {round(el/3600,1)} h", flush=True)
