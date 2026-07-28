"""arms gate: every arm constructs and drives an episode to a valid terminal with a FAKE
deterministic model (no API), and the eval-only audit records populate correctly
(proposals for sc3/team, critic verdict for free/thin) without leaking into action_log.
"""
import sys, json, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench_v3.arms.registry import build_arm
from bench_v3.arms.base import visible_rank
from bench_v3.arms.single import policy_single
from bench_v3.core.episode import run_episode
from bench_v3.tests._helpers import build_sim


class FakeModel:
    """Deterministic: actor measures then accepts; judge picks choice 1; critic approves."""
    def __init__(self, name="fake"):
        self.name = name; self.calls = self.pt = self.ct = 0
    def __call__(self, system, user):
        self.calls += 1; self.pt += 10; self.ct += 5
        if "selection judge" in system:
            return '{"choice": 1}'
        if "reviewer" in system:
            return '{"verdict": "approve"}'
        if '"measured_concentration_M"' in user:    # already measured -> accept
            return '{"type":"accept_batch","rationale":"done"}'
        return '{"type":"measure_concentration","vessel":"vessel_1","species":"X","rationale":"m"}'


def _clean(ep):
    blob = json.dumps(ep.action_log).lower()
    return all(b not in blob for b in ("rationale", "_critic", "_proposals", "calibration_status"))


def test_each_arm_terminates_and_audits():
    for arm in ["single", "actor_rubric", "free_critic", "thin_critic",
                "sc3_vote", "sc3_agg", "team_vote", "team_agg"]:
        actor, critic = FakeModel("actor"), FakeModel("critic")
        pol = build_arm(arm, actor, critic, random.Random(0))
        ep = run_episode(pol, build_sim(target=0.2))
        assert ep.terminal == "accept_batch", f"{arm}: terminal={ep.terminal}"
        assert _clean(ep), f"{arm}: action_log leaked an eval-only key"
        # audit records present where expected
        if arm in ("sc3_vote", "sc3_agg", "team_vote", "team_agg"):
            assert any(s.get("proposals") for s in ep.steps), f"{arm}: no proposals recorded"
            cand = next(s["proposals"]["candidates"] for s in ep.steps if s.get("proposals"))
            assert len(cand) == 3, f"{arm}: expected 3 candidates"
        if arm in ("free_critic", "thin_critic"):
            assert any(s.get("critic") for s in ep.steps), f"{arm}: no critic verdict recorded"
            cv = next(s["critic"] for s in ep.steps if s.get("critic"))
            assert cv["critic_verdict"] in ("approve", "revise", "empty", "parse_fail")
        print(f"  [ok] {arm:13s} terminal={ep.terminal} steps={ep.actions_used} clean_log={_clean(ep)}")
    print("[PASS] all 8 per-step arms construct, terminate, audit correctly, no action_log leak")


def test_bo3_visible_rank():
    actor = FakeModel("actor")
    eps = [run_episode(policy_single(actor), build_sim(target=0.2)) for _ in range(3)]
    best = max(eps, key=lambda e: visible_rank(e, 0.2))
    assert best.terminal == "accept_batch"
    print(f"[PASS] bo3 visible_rank picks an accept-terminal episode ({best.terminal})")


if __name__ == "__main__":
    test_each_arm_terminates_and_audits()
    test_bo3_visible_rank()
    print("\nALL ARM UNIT TESTS PASSED (fake deterministic model)")
