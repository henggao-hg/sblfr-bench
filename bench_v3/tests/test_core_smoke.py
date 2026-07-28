"""Core gate: a scripted oracle (no_fault path measure -> verify-standard -> accept)
runs one instance end-to-end through observation/simulator/verifier/episode, and the
agent never sees a status field at any step.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench_v3.core.episode import run_episode
from bench_v3.core.simulator import true_in_tol
from bench_v3.core.observation import assert_no_leak, visible_observation
from bench_v3.tests._helpers import build_sim


def _no_fault_oracle(obs, retry=False):
    # assert no leak in EVERY observation the policy receives
    assert_no_leak(obs)
    committed = [e["action"]["type"] for e in obs["action_log"]
                 if e.get("committed") and e.get("action")]
    if "measure_concentration" not in committed:
        return {"type": "measure_concentration", "vessel": "vessel_1", "species": "X"}
    if "measure_standard_concentration" not in committed:
        return {"type": "measure_standard_concentration", "standard": "std_high"}
    return {"type": "accept_batch"}


def test_no_fault_oracle_runs_end_to_end():
    sim = build_sim(target=0.2)            # honest meter, batch in tolerance
    ep = run_episode(_no_fault_oracle, sim)
    assert ep.terminal == "accept_batch", ep.terminal
    assert ep.actions_used == 3, ep.actions_used
    assert ep.committed_types == ["measure_concentration", "measure_standard_concentration", "accept_batch"]
    assert true_in_tol(ep.sim)
    # step transcript shape
    assert len(ep.steps) == 3 and all("critic" in s and "proposals" in s for s in ep.steps)
    print(f"[PASS] no_fault oracle: terminal={ep.terminal} steps={ep.actions_used} in_tol={true_in_tol(ep.sim)}")


def test_recalibrate_evidence_gate():
    # bare recalibrate (no standard measured) must be rejected and cost budget
    sim = build_sim()
    from bench_v3.core.verifier import verify
    ok, v = verify(sim, {"type": "recalibrate", "instrument": "assay_X"})
    assert not ok and v["resource_ok"] is False, v
    print(f"[PASS] recalibrate evidence-gate: bare recalibrate rejected -> {v['reason']}")


if __name__ == "__main__":
    test_no_fault_oracle_runs_end_to_end()
    test_recalibrate_evidence_gate()
    print("\nCORE SMOKE PASSED (oracle runs one instance; no-leak holds every step; recalibrate gated)")
