"""Why an action can or cannot execute. Read this to answer "why was it rejected?".

Returns 3 booleans + a NEUTRAL reason that cites only account/visible quantities (G6/O4);
a rejected action costs budget (handled in episode.py). Reasons never reveal truth.
Recalibrate is evidence-gated (Amendment D): no reference-standard measurement this
session -> reject. Invariants are checked on a dry-run snapshot (no rng, no recording).
Ported from bench_v2 env.validate_resources + env.verify.
"""
from __future__ import annotations
import copy

from bench_v3.config.constants import MEASURE_ACTIONS
from bench_v3.core.actions import validate_schema
from bench_v3.core.state import State, check_invariants
from bench_v3.core.simulator import BenchSimulator


def validate_resources(state: State, action: dict) -> tuple[bool, str]:
    t = action["type"]
    if t == "transfer":
        src = state.stocks.get(action["src"]); dst = state.vessels.get(action["dst"])
        if src is None:
            return False, f"unknown stock '{action['src']}'"
        if dst is None:
            return False, f"unknown vessel '{action['dst']}'"
        if src.quarantined:
            return False, f"stock '{src.name}' is quarantined"
        vol = float(action["volume_ml"])
        if vol <= 0:
            return False, f"transfer volume must be positive (got {vol})"
        if vol > src.ledger_volume_remaining_ml + 1e-9:
            return False, (f"insufficient stock '{src.name}' per ledger: requested "
                           f"{vol} mL, ledger has {src.ledger_volume_remaining_ml} mL")
        if dst.volume_ml + vol > dst.capacity_ml + 1e-9:
            return False, (f"vessel '{dst.name}' capacity exceeded: requested +{vol} mL, "
                           f"headroom {dst.capacity_ml - dst.volume_ml:.2f} mL")
    elif t == "dilute_to":
        v = state.vessels.get(action["vessel"])
        if v is None:
            return False, f"unknown vessel '{action['vessel']}'"
        target = float(action["target_volume_ml"])
        if target > v.capacity_ml + 1e-9:
            return False, (f"vessel '{v.name}' capacity exceeded: target {target} mL "
                           f"> capacity {v.capacity_ml} mL")
        if target < v.volume_ml - 1e-9:
            return False, f"cannot dilute below current volume ({v.volume_ml} mL)"
    elif t in MEASURE_ACTIONS:
        if t == "measure_standard_concentration":
            if action["standard"] not in state.standards:
                return False, f"unknown standard '{action['standard']}'"
        elif t in ("measure_stock_volume", "measure_stock_concentration"):
            if action["stock"] not in state.stocks:
                return False, f"unknown stock '{action['stock']}'"
        else:
            if action["vessel"] not in state.vessels:
                return False, f"unknown vessel '{action['vessel']}'"
    elif t == "recalibrate":
        if action["instrument"] not in state.instruments:
            return False, f"unknown instrument '{action['instrument']}'"
    elif t == "discard_vessel":
        if action["vessel"] not in state.vessels:
            return False, f"unknown vessel '{action['vessel']}'"
    elif t == "quarantine_stock":
        if action["stock"] not in state.stocks:
            return False, f"unknown stock '{action['stock']}'"
    return True, "ok"


def verify(sim: BenchSimulator, action: dict) -> tuple[bool, dict]:
    ok1, r1 = validate_schema(action)
    if not ok1:
        return False, {"schema_ok": False, "resource_ok": None,
                       "invariants_ok": None, "reason": f"schema: {r1}"}
    ok2, r2 = validate_resources(sim.state, action)
    if not ok2:
        return False, {"schema_ok": True, "resource_ok": False,
                       "invariants_ok": None, "reason": f"resource: {r2}"}
    # Amendment D: recalibrate needs a reference measurement this session (physics, not rubric)
    if action["type"] == "recalibrate" and not sim.measured_standards:
        return False, {"schema_ok": True, "resource_ok": False, "invariants_ok": None,
                       "reason": "resource: calibration requires at least one reference measurement in this session"}
    # invariants on a dry-run snapshot (no rng, no recording)
    snap = copy.deepcopy(sim.state)
    tmp = BenchSimulator(snap, sim.hidden, sim.goal, sim.rng)
    tmp.measured_standards = dict(sim.measured_standards); tmp.calibration = sim.calibration
    try:
        tmp.apply(action, inject_fault=False, draw_noise=False)
    except Exception as exc:
        return False, {"schema_ok": True, "resource_ok": True,
                       "invariants_ok": False, "reason": f"runtime: {type(exc).__name__}"}
    inv_ok, inv_vio = check_invariants(snap)
    if not inv_ok:
        return False, {"schema_ok": True, "resource_ok": True,
                       "invariants_ok": False, "reason": "invariants: " + "; ".join(inv_vio)}
    return True, {"schema_ok": True, "resource_ok": True, "invariants_ok": True, "reason": "ok"}
