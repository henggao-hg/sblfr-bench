"""PRIORITY test: observation no-leak + Amendment G.

The instrument public view must be EXACTLY {measures, species} -- never
calibration_status / session_check / any status surrogate -- even when the instrument
carries a status in STATE (e.g. after a recalibrate). And assert_no_leak must catch a
forbidden token if one is ever injected.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # sblfr-chem/ for `bench_v3` pkg

from bench_v3.core.observation import visible_observation, assert_no_leak, instrument_public_view
from bench_v3.config.constants import INSTRUMENT_PUBLIC_FIELDS
from bench_v3.tests._helpers import build_sim


def test_instrument_view_is_identity_only():
    # set a status in STATE deliberately -> it must NOT surface in the observation
    sim = build_sim(calibration_status="recalibrated")
    obs = visible_observation(sim, [], 0)
    iv = obs["instruments"]["assay_X"]
    assert iv == {"measures": "concentration", "species": "X"}, iv
    assert "calibration_status" not in iv and "session_check" not in iv
    assert set(iv) == set(INSTRUMENT_PUBLIC_FIELDS)
    print("[PASS] instrument view = {measures, species} only (status in state not exposed)")


def test_assert_no_leak_passes_on_clean_obs():
    for cs in ("unknown", "recalibrated"):
        obs = visible_observation(build_sim(calibration_status=cs), [], 0)
        assert_no_leak(obs)
    # serialized obs contains none of the forbidden tokens
    blob = json.dumps(visible_observation(build_sim(), [], 0)).lower()
    for bad in ("calibration_status", "session_check", "true_concentration", "fault_class"):
        assert bad not in blob
    print("[PASS] assert_no_leak passes on clean observation; no forbidden tokens in blob")


def test_assert_no_leak_catches_injected_leak():
    obs = visible_observation(build_sim(), [], 0)
    obs["instruments"]["assay_X"]["calibration_status"] = "unknown"   # inject a leak
    raised = False
    try:
        assert_no_leak(obs)
    except AssertionError:
        raised = True
    assert raised, "assert_no_leak FAILED to catch an injected calibration_status leak"
    print("[PASS] assert_no_leak catches an injected calibration_status leak (guard works)")


def test_redact_strips_extra_keys():
    from bench_v3.core.observation import redact_action
    a = {"type": "measure_volume", "vessel": "vessel_1",
         "calibration_status": "unknown", "rationale": "x", "junk": 1}
    assert redact_action(a) == {"type": "measure_volume", "vessel": "vessel_1"}, redact_action(a)
    assert redact_action({"type": "weird", "calibration_status": "x"}) == {"type": "weird"}
    print("[PASS] redact_action strict whitelist: extra keys (incl calibration_status) dropped")


def test_episode_action_log_never_leaks_injected_key():
    """BLOCKING#1 (codex): a policy that injects a forbidden extra key on its committed
    actions must NOT have it echo back via the agent-visible action_log."""
    from bench_v3.core.episode import run_episode
    import json
    def leaky(obs, retry=False):
        committed = [e["action"]["type"] for e in obs["action_log"]
                     if e.get("committed") and e.get("action")]
        if "measure_concentration" not in committed:
            return {"type": "measure_concentration", "vessel": "vessel_1", "species": "X",
                    "calibration_status": "LEAK", "rationale": "r"}
        return {"type": "accept_batch", "session_check": "LEAK"}
    ep = run_episode(leaky, build_sim())
    blob = json.dumps(ep.action_log).lower()
    for bad in ("leak", "calibration_status", "session_check", "rationale"):
        assert bad not in blob, f"action_log leaked '{bad}': {ep.action_log}"
    print("[PASS] episode action_log strips policy-injected forbidden keys (BLOCKING#1 fixed)")


if __name__ == "__main__":
    test_instrument_view_is_identity_only()
    test_assert_no_leak_passes_on_clean_obs()
    test_assert_no_leak_catches_injected_leak()
    test_redact_strips_extra_keys()
    test_episode_action_log_never_leaks_injected_key()
    print("\nALL OBSERVATION NO-LEAK / AMENDMENT G TESTS PASSED")
