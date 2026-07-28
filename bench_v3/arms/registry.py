"""Arm registry: build_arm(name, actor, critic, rng) -> per-step policy. bo3 is handled
by the runner (3 single episodes + visible_rank), not here. Ported from bench_v2
run_sweep.build_arm.
"""
from __future__ import annotations
from bench_v3.arms import single, critic as critic_mod, sc3, team

ARMS = ["single", "actor_rubric", "free_critic", "thin_critic",
        "sc3_vote", "sc3_agg", "team_vote", "team_agg", "bo3"]


def build_arm(arm_name, actor, critic, rng):
    table = {
        "single": lambda: single.policy_single(actor),
        "actor_rubric": lambda: single.policy_actor_rubric(actor),
        "free_critic": lambda: critic_mod.policy_critic(actor, critic, False),
        "thin_critic": lambda: critic_mod.policy_critic(actor, critic, True),
        "sc3_vote": lambda: sc3.policy_sc3_vote(actor),
        "sc3_agg": lambda: sc3.policy_sc3_agg(actor, rng),
        "team_vote": lambda: team.policy_team_vote(actor),
        "team_agg": lambda: team.policy_team_agg(actor, rng),
    }
    return table[arm_name]()
