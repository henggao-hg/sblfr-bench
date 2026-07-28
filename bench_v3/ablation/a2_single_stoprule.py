"""Ablation A2: single_stoprule (second priority).

weak single wrapped by a deterministic rule: before each step, if the GOAL vessel has a
FRESH in-tolerance concentration reading, force accept_batch. "Fresh" = the most recent
committed measure_concentration on the goal vessel is in the tolerance band AND no
intervention that changes the goal vessel's concentration has been committed since that
reading. Interventions that invalidate the reading are ONLY those that actually alter the
goal vessel: transfer into/out of it, dilute_to it, discard it. recalibrate, standard /
stock / volume measurements, and quarantine do NOT invalidate a vessel reading.

Rationale (pre-registered in the spec): accepting on a STALE reading (e.g. measured
in-band, then transferred/diluted out of band, then accepted on the old number) measures
recklessness, not convergence, and would pollute the comparison against the critic's
convergence channel. The no-freshness version was explicitly considered and rejected.

Uses only observable fields (agent-visible action_log + goal) -- never truth. Empty log
and any step without a fresh in-band reading fall through to the frozen single policy.

Frozen pieces (policy_single) are imported, never modified.
Policy contract matches a frozen arm: policy(obs, retry=False) -> action dict or None.
"""
from __future__ import annotations

from bench_v3.arms.single import policy_single

ARM_NAME = "single_stoprule"


def _invalidates_vessel_reading(action: dict, vessel: str) -> bool:
    """True iff a committed action changes the GOAL vessel's concentration, making any
    prior reading of that vessel stale. Scoped to the goal vessel per the spec."""
    t = action.get("type")
    if t == "transfer":
        return action.get("dst") == vessel or action.get("src") == vessel
    if t == "dilute_to":
        return action.get("vessel") == vessel
    if t == "discard_vessel":
        return action.get("vessel") == vessel
    return False   # recalibrate / measure_* / quarantine_stock do not touch vessel conc


def policy_single_stoprule(model):
    base = policy_single(model)

    def f(obs, retry=False):
        g = obs.get("goal", {})
        vessel, species = g.get("vessel"), g.get("species")
        target, tol = g.get("target_concentration_M"), g.get("tolerance_M")
        # Walk the log in order; a matching measurement sets the fresh reading, a matching
        # intervention clears it. What survives to the end is the FRESH reading (if any).
        fresh_reading = None
        for e in obs.get("action_log", []):
            if not e.get("committed"):
                continue
            a = e.get("action") or {}
            if (a.get("type") == "measure_concentration"
                    and a.get("vessel") == vessel and a.get("species") == species):
                r = e.get("result") or {}
                if r.get("measured_concentration_M") is not None:
                    fresh_reading = r["measured_concentration_M"]
            elif _invalidates_vessel_reading(a, vessel):
                fresh_reading = None
        if (fresh_reading is not None and target is not None and tol is not None
                and abs(fresh_reading - target) <= tol):
            return {"type": "accept_batch"}
        return base(obs, retry=retry)
    return f
