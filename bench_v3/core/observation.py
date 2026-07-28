"""What the agent sees. THE leak surface — read this file to answer "is X leaked?".

Strict whitelist (G1/G5). Amendment G: the instrument public view exposes ONLY stable
identity {measures, species} -- NO calibration_status / session_check / any status
surrogate. Instrument health must be inferred via measure_standard_concentration.

Two helpers other modules MUST route through:
  redact_action(a)      strip eval-only keys (rationale / _critic / _proposals) before
                        an action enters the agent-visible action_log.
  visible_observation() build the whitelisted observation dict.

assert_no_leak(obs) is the guard used by tests/conformance: it fails if any forbidden
field or substring appears anywhere in the observation.
"""
from __future__ import annotations
import json

from bench_v3.config.constants import MAX_ACTIONS, INSTRUMENT_PUBLIC_FIELDS, ACTIONS

# keys that are eval-only and must never reach the agent via action_log
EVAL_ONLY_KEYS = ("rationale", "_critic", "_proposals")

# anything matching these (case-insensitive substrings) must NOT appear in an observation
FORBIDDEN_SUBSTRINGS = (
    "calibration_status", "session_check", "not_yet_checked",
    "true_concentration", "true_volume", "true_species", "residual",
    "fault_class", "fault_family", "transfer_efficiency", "bias_a", "gain_g", "drift_b",
    "_critic", "_proposals", "rationale",
)


def redact_action(action: dict) -> dict:
    """Strict inclusion-whitelist before an action enters the agent-visible action_log:
    keep ONLY 'type' + that action's schema fields. This drops rationale/_critic/_proposals
    AND any stray/extra key (a policy could emit e.g. 'calibration_status') -- a
    whitelist-by-exclusion would let such a key echo back into the next observation
    (caught by codex review). The full action is still used for sim/verify/transcript;
    only the agent-visible copy is restricted."""
    t = action.get("type")
    spec = ACTIONS.get(t)
    if spec is None:                       # schema-rejected unknown type: show only the type
        return {"type": t}
    keep = {"type"} | set(spec["required"]) | set(spec["numeric"])
    return {k: v for k, v in action.items() if k in keep}


def instrument_public_view(ins) -> dict:
    """Amendment G: stable identity only -- {measures, species}. No status field."""
    return {f: getattr(ins, f) for f in INSTRUMENT_PUBLIC_FIELDS}


def visible_observation(sim, action_log: list, actions_used: int) -> dict:
    st = sim.state
    return {
        "goal": {
            "vessel": sim.goal["vessel"], "species": sim.goal["species"],
            "target_concentration_M": sim.goal["target_concentration_M"],
            "tolerance_M": sim.goal["tolerance_M"],
        },
        "vessels": {n: {"volume_ml": round(v.volume_ml, 3), "capacity_ml": v.capacity_ml}
                    for n, v in st.vessels.items()},
        "stocks": {n: {"species": s.species, "label_concentration_M": s.label_concentration_M,
                       "ledger_volume_remaining_ml": round(s.ledger_volume_remaining_ml, 3),
                       "quarantined": s.quarantined}
                   for n, s in st.stocks.items()},
        "standards": {n: {"species": std.species,
                          "certified_concentration_M": std.certified_concentration_M}
                      for n, std in st.standards.items()},
        "instruments": {n: instrument_public_view(ins) for n, ins in st.instruments.items()},
        "initial_protocol_record": sim.goal.get("protocol_record", []),
        "action_log": action_log,
        "action_budget": {"actions_used": actions_used,
                          "actions_remaining": MAX_ACTIONS - actions_used,
                          "max_actions": MAX_ACTIONS},
    }


def assert_no_leak(obs: dict) -> None:
    """Raise AssertionError if the observation carries any forbidden field/substring.
    Structural check on instruments + a substring sweep over the serialized obs."""
    for n, iv in obs.get("instruments", {}).items():
        extra = set(iv) - set(INSTRUMENT_PUBLIC_FIELDS)
        assert not extra, f"instrument '{n}' leaks fields {extra} (Amendment G: only {INSTRUMENT_PUBLIC_FIELDS})"
    blob = json.dumps(obs, ensure_ascii=False).lower()
    for bad in FORBIDDEN_SUBSTRINGS:
        assert bad not in blob, f"observation leaks forbidden token '{bad}'"
