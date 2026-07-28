"""User-prompt construction. base_user(obs_json) builds the per-step user message
(observation + allowed actions). Verbatim materials v1.4.
"""
from bench_v3.prompts.base_actor import ALLOWED_ACTIONS_BLOCK


def base_user(obs_json: str) -> str:
    return (f"Current observation (JSON):\n{obs_json}\n\n{ALLOWED_ACTIONS_BLOCK}\n\n"
            "Propose the single best next action now. JSON only.")
