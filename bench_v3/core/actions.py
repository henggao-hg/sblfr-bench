"""Action schema + JSON extraction (pure: no state, no truth).

Defines validate_schema over the frozen 12-action set and extract_json_action (parse
the agent's reply into one action dict). Ported verbatim from bench_v2 (env.validate_schema
+ arms.extract_json_action) -- behavior must match.
"""
from __future__ import annotations
import json
import re

from bench_v3.config.constants import ACTIONS


def validate_schema(action) -> tuple[bool, str]:
    if not isinstance(action, dict) or "type" not in action:
        return False, "missing 'type'"
    t = action["type"]
    spec = ACTIONS.get(t)
    if spec is None:
        return False, f"unknown action type '{t}'"
    for f in spec["required"]:
        if f not in action:
            return False, f"missing field '{f}' for {t}"
    for f in spec["numeric"]:
        try:
            float(action[f])
        except (TypeError, ValueError):
            return False, f"field '{f}' must be numeric"
    return True, "ok"


def extract_json_action(text):
    """Parse one action dict from model text: last balanced {...} containing a 'type',
    else whole-text JSON. Returns the dict (may carry a 'rationale') or None."""
    if not text:
        return None
    cands = re.findall(r"\{[^{}]*\}", text.replace("\n", " "))
    for c in reversed(cands):
        try:
            d = json.loads(c)
        except Exception:
            continue
        if isinstance(d, dict) and "type" in d:
            return d
    try:
        d = json.loads(text)
        if isinstance(d, dict) and "type" in d:
            return d
    except Exception:
        pass
    return None
