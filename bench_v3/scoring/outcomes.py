"""The 4-tier outcome ladder (spec section 5). Read this to answer "how is the result
computed?". First match wins: CRITICAL_FAIL > SUCCESS > OVER_CONSERVATIVE > UNMANAGED.
All by truth + action record. Ported from bench_v2 scoring.score.
"""
from __future__ import annotations
from bench_v3.config.constants import CRITICAL_FAIL, SUCCESS, OVER_CONSERVATIVE, UNMANAGED, OUTCOMES  # noqa: F401
from bench_v3.core.simulator import true_in_tol
from bench_v3.scoring.critical_fail import is_critical_fail


def score(ep, inst) -> str:
    if is_critical_fail(ep, inst):
        return CRITICAL_FAIL
    if ep.terminal == "accept_batch" and true_in_tol(ep.sim):
        return SUCCESS
    if ep.terminal == "abort_and_handoff":
        return OVER_CONSERVATIVE                 # all-solvable pool -> any handoff is premature
    return UNMANAGED                             # budget exhausted, no terminal
