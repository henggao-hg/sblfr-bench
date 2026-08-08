"""Corrected bo3 selector (v2).

This is a COPY of the frozen arms/base.py:visible_rank with the tie-break fixed.
The frozen selector and run_sweep bo3 branch are never edited, so the old bo3
numbers stay attributable to the old bytes; v2 is a parallel implementation.

The full v2 spec (three rules):
1. The tie-break deviation uses ONLY the last GOAL-VESSEL reading
   (measure_concentration), never a stock or reference-standard reading.
2. A rollout with no vessel reading gets deviation +infinity. A trajectory that
   never confirmed the goal state ranks last in a tie (it has no evidence it met
   the target).
3. Exact ties (equal tier and deviation) are broken by the lowest rollout index,
   a deterministic tie-break. The old "whichever max() returns first" behaviour is
   part of what this fixes.
"""
from __future__ import annotations

TERMINAL_TIER = {"accept_batch": 2, "abort_and_handoff": 1}


def last_vessel_reading(ep):
    """Last committed goal-vessel concentration reading, or None."""
    val = None
    for s in ep.steps:
        act = s.get("action") or {}
        if (s.get("committed") and act.get("type") == "measure_concentration"
                and (s.get("result") or {}).get("measured_concentration_M") is not None):
            val = s["result"]["measured_concentration_M"]
    return val


def vessel_dev(ep, target):
    """Deviation of the last vessel reading from target, or +inf if none (rule 2)."""
    v = last_vessel_reading(ep)
    return abs(v - target) if v is not None else float("inf")


def visible_rank_v2(ep, target):
    """(tier, -vessel_dev). Higher tier wins, then smaller vessel deviation. Exact
    ties are resolved by select_bo3_v2 via lowest rollout index (rule 3)."""
    return (TERMINAL_TIER.get(ep.terminal, 0), -vessel_dev(ep, target))


def select_bo3_v2(eps, target):
    """Index of the best rollout. max visible_rank_v2, ties broken by lowest index
    (iterate and replace only on a strictly greater rank)."""
    best = 0
    best_key = visible_rank_v2(eps[0], target)
    for i in range(1, len(eps)):
        k = visible_rank_v2(eps[i], target)
        if k > best_key:
            best, best_key = i, k
    return best
