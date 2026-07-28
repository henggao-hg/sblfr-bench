"""Critics (A3 free / A4 thin / A10 self+rubric) + the actor revise message.
Verbatim materials v1.4. thin = free + "judge against principles" + L2 + cite-number line.
"""
from bench_v3.prompts.rubrics import L2

FREE_CRITIC_SYSTEM = (
    "You are a reviewer. Below are the current observation and a proposed action with its rationale.\n"
    "Assess whether the proposed action is reasonable.\n"
    'Output exactly one JSON object, either {"verdict": "approve"} or {"verdict": "revise", '
    '"critique": "<one short sentence>"}. JSON only.'
)
THIN_CRITIC_SYSTEM = (
    FREE_CRITIC_SYSTEM + "\nJudge the proposal against the following operating principles." + L2
    + "\nIf you ask for a revision, cite the number of the violated principle in your critique."
)


def revise_msg(critique: str) -> str:
    return f"A reviewer assessed your proposed action: {critique}.\nPropose your final action now. JSON only."
