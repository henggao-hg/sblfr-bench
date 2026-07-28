"""Ablation A1: rubric_reassert (highest priority, main-line adjudication experiment).

Like actor_rubric (L2 in the system prompt) but ALSO re-states the 9 principles in full
at the very end of every per-step user message. The only difference from actor_rubric is
the extra rubric appended to the user turn. Tests whether the decay of rubric adherence
is a positional-freshness effect (restating each turn should recover it) or needs
reactive feedback on the draft (a static restate would not).

Frozen pieces (BASE_SYSTEM, L2, ask, obs_user) are imported, never modified.
Policy contract matches a frozen arm: policy(obs, retry=False) -> action dict or None.
"""
from __future__ import annotations

from bench_v3.arms.base import obs_user, ask
from bench_v3.prompts.base_actor import BASE_SYSTEM
from bench_v3.prompts.rubrics import L2

ARM_NAME = "rubric_reassert"


def policy_rubric_reassert(model, rubric=L2):
    def f(obs, retry=False):
        user = obs_user(obs) + rubric          # re-state the principles at the message tail
        return ask(model, BASE_SYSTEM + rubric, user, retry)
    return f
