"""Behavioral action-distribution audit (Amendment G2) — MECHANISM, not an outcome
metric. Computation library; rendering/CLI lives in analysis/. Operates on metric rows
that carry `committed_types` (and `arm`/`class`). JSD is Jensen-Shannon (symmetric,
bounded, finite when an action is absent from one side); at small n it is noisy/biased
-> compare to the single self-split noise floor, only trust at adequate n.
"""
from __future__ import annotations
import math
import random
from collections import Counter

# 12 actions -> 6 groups (VERIFY_ANCHOR = the meter check against the axiom standard;
# measure_stock is a real-quantity probe -> MEASURE_BATCH).
GROUP = {
    "measure_concentration": "MEASURE_BATCH", "measure_volume": "MEASURE_BATCH",
    "measure_stock_volume": "MEASURE_BATCH", "measure_stock_concentration": "MEASURE_BATCH",
    "measure_standard_concentration": "VERIFY_ANCHOR",
    "recalibrate": "CALIBRATE",
    "transfer": "CORRECT_IN_PLACE", "dilute_to": "CORRECT_IN_PLACE",
    "discard_vessel": "REBUILD_OR_ISOLATE", "quarantine_stock": "REBUILD_OR_ISOLATE",
    "accept_batch": "TERMINAL", "abort_and_handoff": "TERMINAL",
}
GROUPS = ["MEASURE_BATCH", "VERIFY_ANCHOR", "CALIBRATE", "CORRECT_IN_PLACE",
          "REBUILD_OR_ISOLATE", "TERMINAL"]
ABBR = {"measure_concentration": "Mv", "measure_volume": "Mvol", "measure_stock_volume": "Msv",
        "measure_stock_concentration": "Mstk", "measure_standard_concentration": "Mstd",
        "recalibrate": "R", "transfer": "T", "dilute_to": "D", "discard_vessel": "X",
        "quarantine_stock": "Q", "accept_batch": "A", "abort_and_handoff": "H"}


def group_share(rows) -> dict:
    """step-weighted share of committed actions across the 6 groups."""
    c = Counter()
    for r in rows:
        for t in r.get("committed_types", []):
            c[GROUP.get(t, "?")] += 1
    n = sum(c.values()) or 1
    return {g: c.get(g, 0) / n for g in GROUPS}


def incidence(rows) -> dict:
    """% of episodes that did each key action at least once."""
    n = len(rows) or 1
    def frac(pred): return sum(1 for r in rows if pred(r.get("committed_types", []))) / n
    return {
        "std_check%": round(100 * frac(lambda ct: "measure_standard_concentration" in ct)),
        "recal%": round(100 * frac(lambda ct: "recalibrate" in ct)),
        "discard%": round(100 * frac(lambda ct: "discard_vessel" in ct)),
        "inplace%": round(100 * frac(lambda ct: ("transfer" in ct or "dilute_to" in ct))),
        "handoff%": round(100 * frac(lambda ct: "abort_and_handoff" in ct)),
        "accept%": round(100 * frac(lambda ct: "accept_batch" in ct)),
    }


def motif(row) -> str:
    return " ".join(ABBR.get(t, t[:2]) for t in row.get("committed_types", []))


def jsd(p: dict, q: dict) -> float:
    """Jensen-Shannon divergence (log2) over the 6 action groups; 0 = identical."""
    m = {g: (p.get(g, 0) + q.get(g, 0)) / 2 for g in GROUPS}
    def kl(a):
        return sum(a[g] * math.log2(a[g] / m[g]) for g in GROUPS if a.get(g, 0) > 0 and m[g] > 0)
    return round(0.5 * kl(p) + 0.5 * kl(q), 3)


def noise_floor(single_rows, trials=30, seed=0):
    """JSD between two random halves of the single arm's own episodes -> the sampling
    noise floor. JSD vs single is only meaningful ABOVE this. None if too few episodes."""
    if len(single_rows) < 6:
        return None
    rng = random.Random(seed); vals = []
    for _ in range(trials):
        rs = single_rows[:]; rng.shuffle(rs); h = len(rs) // 2
        vals.append(jsd(group_share(rs[:h]), group_share(rs[h:])))
    return round(sum(vals) / len(vals), 3)
