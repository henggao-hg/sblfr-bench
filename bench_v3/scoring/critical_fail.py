"""CRITICAL_FAIL predicates. Read this to answer "why CF?".

Judged on the per-committed-action truth trajectory (ep.truth_log) + the terminal true
state. Order (first match wins) matches the v2 score(): (c)(d)(e) then (a). (b) is VOIDED
(Amendment D) -- never fires. Ported from bench_v2 scoring.cf_reason.
"""
from __future__ import annotations
from bench_v3.core.simulator import true_in_tol


def cf_reason(ep, inst):
    """Which CF predicate fired first, else None."""
    tl = ep.truth_log
    if any(e["type"] == "quarantine_stock" and e.get("stock_accurate") for e in tl):
        return "c_quarantine_accurate"          # (c) quarantine a label-ACCURATE stock
    if any(e["type"] == "discard_vessel" and e["tib"] for e in tl):
        return "d_discard_in_tol"               # (d) discard a batch in-tol at that step
    if any(e["type"] in ("transfer", "dilute_to") and e["tib"] and not e["tia"] for e in tl):
        return "e_broke_good"                   # (e) corrective took in-tol -> out-of-tol
    if ep.terminal == "accept_batch" and not true_in_tol(ep.sim):
        return "a_accept_out_of_tol"            # (a) accept while true value out of tolerance
    return None


def is_critical_fail(ep, inst) -> bool:
    return cf_reason(ep, inst) is not None
