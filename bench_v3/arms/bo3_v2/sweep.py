"""bo3_v2 sweep loop.

A COPY of the frozen runners/run_sweep.py bo3 branch, with two changes:
  - selection uses selector.select_bo3_v2 (the corrected tie-break)
  - all three candidate rollouts are archived in the transcript (full-candidate
    logging is the standing rule for bo3-class experiments from now on)
run_sweep.py is not imported for its loop and is never edited. The shared engine
(run_episode, build_scenario, scoring) is imported read-only, exactly as the
frozen bo3 path uses it.

Metrics record schema matches the frozen bo3 rec so v1 and v2 are directly
comparable. Resumable. Writes out.jsonl (metrics) + out.transcript.jsonl.
"""
from __future__ import annotations
import json
import time
from collections import OrderedDict

from bench_v3.families.base import build_scenario
from bench_v3.core.episode import run_episode
from bench_v3.scoring.outcomes import score
from bench_v3.scoring.secondary import fault_cleared, needless_interventions
from bench_v3.scoring.critical_fail import cf_reason
from bench_v3.arms.single import policy_single
from bench_v3.arms.bo3_v2.selector import visible_rank_v2, select_bo3_v2, last_vessel_reading

ARM_NAME = "bo3_v2"
N_ROLLOUTS = 3


def _interleave(instances):
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
    done = set()
    try:
        for l in open(out_path):
            r = json.loads(l)
            done.add((r["arm"], r["seed"], r["instance"]))
    except FileNotFoundError:
        pass
    return done


def _last_measurement(ep):
    """Last committed reading of any kind: (value, source_action_type)."""
    val, src = None, None
    for s in ep.steps:
        if s.get("committed") and (s.get("result") or {}).get("measured_concentration_M") is not None:
            val = s["result"]["measured_concentration_M"]
            src = (s.get("action") or {}).get("type")
    return val, src


def _candidate_record(ep, inst, idx, selected):
    """Full per-candidate archive: the selection fields PLUS the complete
    step-by-step trajectory, so any future selector can be re-applied with no rerun."""
    vr = visible_rank_v2(ep, inst.target_concentration_M)
    lm, lsrc = _last_measurement(ep)
    return {"idx": idx, "terminal": ep.terminal, "outcome": score(ep, inst),
            "cf_reason": cf_reason(ep, inst), "visible_rank_v2": [vr[0], vr[1]],
            "last_meas": lm, "last_meas_source": lsrc,
            "last_vessel_reading": last_vessel_reading(ep), "selected": selected,
            "actions_used": ep.actions_used, "committed_types": ep.committed_types,
            "steps": ep.steps}


def run_bo3v2_sweep(actor, seeds, instances, out_path, verbose=True,
                    do_interleave=True, resume=True):
    if do_interleave:
        instances = _interleave(instances)
    done = _done_keys(out_path) if resume else set()
    if done and verbose:
        print(f"  resume: skipping {len(done)} already-completed episodes", flush=True)
    outf = open(out_path, "a")
    tpath = out_path[:-6] + ".transcript.jsonl" if out_path.endswith(".jsonl") else out_path + ".transcript.jsonl"
    tf = open(tpath, "a")

    def tok_probe():
        return (actor.calls, actor.pt, actor.ct)

    n = 0
    t0 = time.time()
    for seed in seeds:
        for inst in instances:
            if (ARM_NAME, seed, inst.id) in done:
                continue
            actor.reset()
            # Same as the frozen bo3: 3 rollouts share the instance and noise seed,
            # only the model's temperature sampling differs. Selection is v2.
            eps = [run_episode(policy_single(actor), build_scenario(inst, seed), tok_probe=tok_probe)
                   for _ in range(N_ROLLOUTS)]
            sel = select_bo3_v2(eps, inst.target_concentration_M)
            ep = eps[sel]
            outcome = score(ep, inst)
            rec = {"arm": ARM_NAME, "actor": getattr(actor, "name", "?"), "critic": None,
                   "seed": seed, "instance": inst.id, "family": inst.family, "class": inst.fault_class,
                   "outcome": outcome, "fault_cleared": fault_cleared(ep, inst),
                   "cf_reason": cf_reason(ep, inst), "needless": needless_interventions(ep, inst),
                   "committed_types": ep.committed_types, "actions_used": ep.actions_used,
                   "parse_fails": ep.parse_fails,
                   "actor_calls": actor.calls, "actor_pt": actor.pt, "actor_ct": actor.ct,
                   "critic_calls": 0, "critic_pt": 0, "critic_ct": 0,
                   "selected_index": sel}
            outf.write(json.dumps(rec) + "\n"); outf.flush()
            trec = {"arm": ARM_NAME, "actor": getattr(actor, "name", "?"), "critic": None,
                    "seed": seed, "instance": inst.id, "family": inst.family, "class": inst.fault_class,
                    "outcome": outcome, "cf_reason": cf_reason(ep, inst),
                    "needless": needless_interventions(ep, inst), "terminal": ep.terminal,
                    "actions_used": ep.actions_used, "steps": ep.steps,
                    "selected_index": sel,
                    "candidates": [_candidate_record(eps[i], inst, i, i == sel)
                                   for i in range(N_ROLLOUTS)]}
            tf.write(json.dumps(trec) + "\n"); tf.flush()
            n += 1
            if verbose and n % 10 == 0:
                el = time.time() - t0
                print(f"  {n} ep, {round(el)}s, {round(el/n,1)}s/ep (last {inst.id}={outcome})", flush=True)
    outf.close(); tf.close()
    return n, time.time() - t0
