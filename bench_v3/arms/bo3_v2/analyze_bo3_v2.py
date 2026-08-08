"""Compare bo3_v2 against the frozen v1 bo3.

tier1: v1 = arm 'bo3' rows in results/v3_tier1_<which>_seed<seed>.jsonl,
       v2 = results/v3_bo3v2_tier1_<which>_seed<seed>.jsonl.
cross-model strong seed0: v1 = arm 'bo3' in results/v3_crossmodel_strong_seed0.jsonl,
       v2 = the corrected_outcome column of the offline audit
       results/v3_crossmodel_strong_bo3_audit_seed0.jsonl (no re-run, per decision 4).

Decision line (pre-registered): SUCCESS should not differ materially from v1 and CF
should be flat or lower. This script prints the deltas so a deviation is visible.

usage: python -m bench_v3.arms.bo3_v2.analyze_bo3_v2
"""
import json
import collections
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[2] / "results"
TIERS = ["SUCCESS", "CRITICAL_FAIL", "OVER_CONSERVATIVE", "UNMANAGED"]


def dist(outcomes):
    c = collections.Counter(outcomes)
    return {k: c.get(k, 0) for k in TIERS}


def _rows(path, arm=None):
    out = []
    try:
        for l in open(path):
            r = json.loads(l)
            if arm is None or r.get("arm") == arm:
                out.append(r)
    except FileNotFoundError:
        return None
    return out


def line(tag, v1, v2):
    d1, d2 = dist(v1), dist(v2)
    print(f"\n[{tag}]  n_v1={len(v1)} n_v2={len(v2)}")
    for k in TIERS:
        print(f"  {k:18s} v1={d1[k]:3d}  v2={d2[k]:3d}  delta={d2[k]-d1[k]:+d}")
    flag = []
    if d2["CRITICAL_FAIL"] > d1["CRITICAL_FAIL"]:
        flag.append("CF UP (decision line: should be flat or down)")
    if abs(d2["SUCCESS"] - d1["SUCCESS"]) > max(5, int(0.03 * len(v1))):
        flag.append("SUCCESS moved materially")
    print("  >>> " + ("; ".join(flag) if flag else "within decision line"))


def main():
    # tier1
    for which in ["strong", "weak"]:
        for seed in [0, 1, 2]:
            v1 = _rows(RESULTS / f"v3_tier1_{which}_seed{seed}.jsonl", arm="bo3")
            v2 = _rows(RESULTS / f"v3_bo3v2_tier1_{which}_seed{seed}.jsonl")
            if v1 is None or v2 is None:
                print(f"[tier1 {which} seed{seed}] missing (v1={v1 is not None}, v2={v2 is not None})")
                continue
            line(f"tier1 {which} seed{seed}", [r["outcome"] for r in v1], [r["outcome"] for r in v2])
    # cross-model strong seed0 via offline audit
    v1 = _rows(RESULTS / "v3_crossmodel_strong_seed0.jsonl", arm="bo3")
    aud = _rows(RESULTS / "v3_crossmodel_strong_bo3_audit_seed0.jsonl")
    if v1 is not None and aud is not None:
        line("crossmodel strong seed0 (v2 = offline corrected audit)",
             [r["outcome"] for r in v1], [r["corrected_outcome"] for r in aud])
    else:
        print(f"[crossmodel strong seed0] missing (v1={v1 is not None}, audit={aud is not None})")


if __name__ == "__main__":
    main()
