"""Ablation A3: single_personaB (third priority).

weak single with persona B (decisive-fixer style, zero task knowledge) appended to the
system prompt; no team, no judge. Tests whether persona B alone unlocks terminal
proposals (single almost never terminates), raising SUCCESS but also a_accept CF.

Frozen pieces (BASE_SYSTEM, PERSONA_B, ask, obs_user) are imported, never modified.
Policy contract matches a frozen arm: policy(obs, retry=False) -> action dict or None.
"""
from __future__ import annotations

from bench_v3.arms.base import obs_user, ask
from bench_v3.prompts.base_actor import BASE_SYSTEM
from bench_v3.prompts.personas import PERSONA_B

ARM_NAME = "single_personaB"


def policy_single_personaB(model):
    def f(obs, retry=False):
        return ask(model, BASE_SYSTEM + PERSONA_B, obs_user(obs), retry)
    return f
