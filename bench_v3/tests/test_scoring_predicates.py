"""scoring gate: the v2 predicate cases. CF (a)(c)(d)(e) fire; (b) is voided
(recalibrate-honest-then-accept is SUCCESS); SUCCESS/OVER/UNMANAGED; needless counts.
Uses fake episodes with a real-evaluating true_in_tol (target=1.0, tol=0.1).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench_v3.config.constants import CRITICAL_FAIL, SUCCESS, OVER_CONSERVATIVE, UNMANAGED
from bench_v3.scoring.outcomes import score
from bench_v3.scoring.critical_fail import cf_reason
from bench_v3.scoring.secondary import needless_interventions


class _FV:
    def __init__(s, c): s.c = c
    def concentration_M(s, sp): return s.c
class _FState:
    def __init__(s, c): s.vessels = {"v": _FV(c)}; s.standards = {}
class _FHidden:
    def __init__(s, ff): s.fault_family = ff
class _FSim:
    def __init__(s, conc, ff): s.goal = {"vessel": "v", "species": "X",
        "target_concentration_M": 1.0, "tolerance_M": 0.1}; s.state = _FState(conc); s.hidden = _FHidden(ff)
class _FEp:
    def __init__(s, term, tl, conc, ff="none"):
        s.terminal = term; s.truth_log = tl; s.sim = _FSim(conc, ff)
        s.committed_types = [e["type"] for e in tl]


def q(t, tib=None, tia=None, acc=None): return {"type": t, "tib": tib, "tia": tia, "stock_accurate": acc}
IN, OUT = 1.0, 2.0   # vessel conc: in / out of tolerance (target 1.0 +- 0.1)


def test_ladder_and_cf_predicates():
    # (a) accept out-of-tol
    ep = _FEp("accept_batch", [q("accept_batch")], OUT)
    assert score(ep, None) == CRITICAL_FAIL and cf_reason(ep, None) == "a_accept_out_of_tol"
    # (c) quarantine label-accurate -> CF ; mislabeled -> not CF
    ep = _FEp("accept_batch", [q("quarantine_stock", acc=True)], IN)
    assert score(ep, None) == CRITICAL_FAIL and cf_reason(ep, None) == "c_quarantine_accurate"
    ep = _FEp("accept_batch", [q("quarantine_stock", acc=False)], IN)
    assert score(ep, None) == SUCCESS
    # (d) discard in-tol-at-step
    ep = _FEp("abort_and_handoff", [q("discard_vessel", tib=True, tia=False)], OUT)
    assert score(ep, None) == CRITICAL_FAIL and cf_reason(ep, None) == "d_discard_in_tol"
    # (e) corrective broke good
    ep = _FEp(None, [q("transfer", tib=True, tia=False)], OUT)
    assert score(ep, None) == CRITICAL_FAIL and cf_reason(ep, None) == "e_broke_good"
    # (b) VOIDED: recalibrate honest meter then accept -> SUCCESS
    ep = _FEp("accept_batch", [q("recalibrate", tib=True, tia=True), q("accept_batch", tib=True, tia=True)], IN)
    assert score(ep, None) == SUCCESS and cf_reason(ep, None) is None
    # plain SUCCESS / OVER / UNMANAGED
    assert score(_FEp("accept_batch", [], IN), None) == SUCCESS
    assert score(_FEp("abort_and_handoff", [], OUT), None) == OVER_CONSERVATIVE
    assert score(_FEp(None, [], OUT), None) == UNMANAGED
    print("[PASS] 4-tier ladder + CF predicates (a/c/d/e) + (b) voided + SUCCESS/OVER/UNMANAGED")


def test_needless():
    # recalibrate on an honest (non-instrument) meter counts; on instrument it does not
    ep = _FEp("accept_batch", [q("recalibrate", tib=True, tia=True), q("accept_batch")], IN, ff="none")
    assert needless_interventions(ep, None) == 1
    ep = _FEp("accept_batch", [q("recalibrate", tib=True, tia=True)], IN, ff="instrument")
    assert needless_interventions(ep, None) == 0
    # discard in-tol + quarantine accurate also count
    ep = _FEp(None, [q("discard_vessel", tib=True), q("quarantine_stock", acc=True)], OUT, ff="none")
    assert needless_interventions(ep, None) == 2
    print("[PASS] needless_interventions: honest-meter recalibrate / discard in-tol / quarantine accurate")


if __name__ == "__main__":
    test_ladder_and_cf_predicates()
    test_needless()
    print("\nSCORING PREDICATES PASSED")
