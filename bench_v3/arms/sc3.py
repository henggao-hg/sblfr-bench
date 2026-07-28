"""A5 sc3_vote / A6 sc3_agg: same prompt sampled 3x, then vote or aggregator.
Ported from bench_v2 arms.py."""
from __future__ import annotations
from bench_v3.arms.base import propose_all, select_vote, select_agg, attach_proposals
from bench_v3.prompts.base_actor import BASE_SYSTEM
from bench_v3.prompts.aggregator import AGG_SYSTEM

_LABELS = ["sample0", "sample1", "sample2"]


def policy_sc3_vote(model):
    def f(obs, retry=False):
        recs = propose_all(model, [BASE_SYSTEM] * 3, _LABELS, obs)
        chosen, meta = select_vote(recs)
        return attach_proposals(chosen, "sc3_vote", recs, meta)
    return f


def policy_sc3_agg(model, rng):
    def f(obs, retry=False):
        recs = propose_all(model, [BASE_SYSTEM] * 3, _LABELS, obs)
        chosen, meta = select_agg(model, obs, recs, rng, AGG_SYSTEM)
        return attach_proposals(chosen, "sc3_agg", recs, meta)
    return f
