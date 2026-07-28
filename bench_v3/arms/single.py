"""A1 single, A2 actor_rubric (D1: swap rubric). Ported from bench_v2 arms.py."""
from __future__ import annotations
from bench_v3.arms.base import obs_user, ask
from bench_v3.prompts.base_actor import BASE_SYSTEM
from bench_v3.prompts.rubrics import L2


def policy_single(model):
    def f(obs, retry=False):
        return ask(model, BASE_SYSTEM, obs_user(obs), retry)
    return f


def policy_actor_rubric(model, rubric=L2):
    def f(obs, retry=False):
        return ask(model, BASE_SYSTEM + rubric, obs_user(obs), retry)
    return f
