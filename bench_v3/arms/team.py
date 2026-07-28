"""A7 team_vote / A8 team_agg: 3 personas (style only), then vote or aggregator.
D2 = team_agg with_rubric=True. Ported from bench_v2 arms.py."""
from __future__ import annotations
from bench_v3.arms.base import propose_all, select_vote, select_agg, attach_proposals
from bench_v3.prompts.base_actor import BASE_SYSTEM
from bench_v3.prompts.aggregator import AGG_SYSTEM
from bench_v3.prompts.personas import PERSONA_A, PERSONA_B, PERSONA_C
from bench_v3.prompts.rubrics import L2

_LABELS = ["persona_A", "persona_B", "persona_C"]


def _systems(with_rubric):
    rub = L2 if with_rubric else ""
    return [BASE_SYSTEM + p + rub for p in (PERSONA_A, PERSONA_B, PERSONA_C)]


def policy_team_vote(model, with_rubric=False):
    systems = _systems(with_rubric)
    def f(obs, retry=False):
        recs = propose_all(model, systems, _LABELS, obs)
        chosen, meta = select_vote(recs)
        return attach_proposals(chosen, "team_vote", recs, meta)
    return f


def policy_team_agg(model, rng, with_rubric=False):
    systems = _systems(with_rubric)
    def f(obs, retry=False):
        recs = propose_all(model, systems, _LABELS, obs)
        chosen, meta = select_agg(model, obs, recs, rng, AGG_SYSTEM)
        return attach_proposals(chosen, "team_agg", recs, meta)
    return f
