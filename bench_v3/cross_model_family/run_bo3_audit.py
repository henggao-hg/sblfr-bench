"""Luna bo3 audit rerun (robustness probe, NOT a correction).

Reruns the cross-model strong bo3 arm (Llama-family excluded, this is gpt-5.6-luna)
on seed0 with FULL per-candidate logging, to probe the selector tie-break ambiguity
in visible_rank (it keys on the last visible measured_concentration_M without
distinguishing goal vessel from stock or reference standard).

The selector rule is UNCHANGED: selected_index uses the same visible_rank as the
frozen runner. For the audit we additionally record what a corrected selector (same
tier, tie-break by the last VESSEL reading only) would pick, so a reader can see
whether the ambiguity ever changes the selection or the outcome.

This writes a NEW file and touches no frozen code and no existing results. Resumable
(re-launch skips instances already logged).

usage:
  SBLFR_API_KEYS_PATH=path/to/API-keys.txt \
    python -m bench_v3.cross_model_family.run_bo3_audit
output: bench_v3/results/v3_crossmodel_strong_bo3_audit_seed0.jsonl
"""
import sys
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v3.instances.generate import load_library
from bench_v3.families.base import build_scenario
from bench_v3.core.episode import run_episode
from bench_v3.scoring.outcomes import score
from bench_v3.scoring.critical_fail import cf_reason
from bench_v3.arms.base import visible_rank
from bench_v3.arms.single import policy_single
from bench_v3.cross_model_family.models import make_actor

SEED = 0
N_ROLLOUTS = 3


def _last_measurement(ep):
    """Last committed step that produced a concentration reading: (value, source_type)."""
    val, src = None, None
    for s in ep.steps:
        if s.get("committed") and (s.get("result") or {}).get("measured_concentration_M") is not None:
            val = s["result"]["measured_concentration_M"]
            src = s["action"]["type"]
    return val, src


def _last_vessel_dev(ep, target):
    """Deviation from target using the last VESSEL reading only (the corrected tie-break)."""
    val = None
    for s in ep.steps:
        if (s.get("committed") and s["action"].get("type") == "measure_concentration"
                and (s.get("result") or {}).get("measured_concentration_M") is not None):
            val = s["result"]["measured_concentration_M"]
    return abs(val - target) if val is not None else 1e9


if __name__ == "__main__":
    lib = load_library()
    actor = make_actor("strong")   # gpt-5.6-luna
    out = str(ROOT / "bench_v3" / "results" / f"v3_crossmodel_strong_bo3_audit_seed{SEED}.jsonl")

    done = set()
    try:
        for line in open(out):
            done.add(json.loads(line)["instance"])
    except FileNotFoundError:
        pass
    if done:
        print(f"  resume: skipping {len(done)} already-logged instances", flush=True)

    outf = open(out, "a")
    t0 = time.time()
    n = 0
    for inst in lib:
        if inst.id in done:
            continue
        target = inst.target_concentration_M
        cands = []
        for i in range(N_ROLLOUTS):
            actor.reset()
            ep = run_episode(policy_single(actor), build_scenario(inst, SEED))
            tier, negdev = visible_rank(ep, target)
            lm, lsrc = _last_measurement(ep)
            cands.append({
                "idx": i,
                "terminal": ep.terminal,
                "outcome": score(ep, inst),
                "cf_reason": cf_reason(ep, inst),
                "visible_rank": [tier, negdev],
                "last_meas": lm,
                "last_meas_source": lsrc,
                "corrected_dev": _last_vessel_dev(ep, target),
            })
        # selected_index: the frozen rule (unchanged) = argmax visible_rank
        sel = max(range(N_ROLLOUTS), key=lambda i: tuple(cands[i]["visible_rank"]))
        # corrected selector: same tier, tie-break by last-vessel deviation
        corr = max(range(N_ROLLOUTS),
                   key=lambda i: (cands[i]["visible_rank"][0], -cands[i]["corrected_dev"]))
        rec = {
            "instance": inst.id, "family": inst.family, "class": inst.fault_class,
            "target": target, "candidates": cands,
            "selected_index": sel, "selected_outcome": cands[sel]["outcome"],
            "corrected_index": corr, "corrected_outcome": cands[corr]["outcome"],
            "selection_differs": sel != corr,
            "outcome_differs": cands[sel]["outcome"] != cands[corr]["outcome"],
        }
        outf.write(json.dumps(rec) + "\n")
        outf.flush()
        n += 1
        if n % 10 == 0:
            el = time.time() - t0
            print(f"  {n} inst, {round(el)}s ({round(el/n,1)}s/inst)", flush=True)
    outf.close()
    print(f"bo3 audit done: {n} new instances, {round((time.time()-t0)/3600,2)}h -> {out}", flush=True)
