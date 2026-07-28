"""Eval-only transcript structures.

EpisodeResult holds everything the evaluator keeps. NONE of this is ever fed back to
the agent (the agent sees only the sanitized observation in core/observation.py):

  action_log     AGENT-VISIBLE history (rationale/_critic/_proposals redacted) -- this
                 is the one field that also appears in the observation.
  steps          eval-side per-step transcript: full action (incl rationale), verifier
                 verdict, result, per-step truth (tib/tia/stock_accurate), per-step
                 token delta, and audit records (critic verdict / proposal pool).
  truth_log      per committed action: truth-in-tol before/after + stock label accuracy.
  committed_types ordered list of committed action types.
  sim            final simulator (carries HiddenTruth + true state) for scoring.

The split is deliberate: observation.py = what the agent sees; this = what the
evaluator records. They must never merge.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class EpisodeResult:
    terminal: str | None
    actions_used: int
    action_log: list
    committed_types: list
    sim: object
    calls: int = 0
    parse_fails: int = 0
    truth_log: list = field(default_factory=list)
    steps: list = field(default_factory=list)
