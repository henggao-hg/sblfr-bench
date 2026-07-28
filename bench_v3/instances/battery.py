"""Degenerate-strategy battery (last gate before any LLM sweep). Five diagnosis-free
strategies; the gate (Amendment B) requires each to satisfy CF% >= 20 OR SUCCESS% <= 10
-- a falsification test for the REGISTERED list, not a universal no-free-lunch proof
(Amendment E3). Ported from bench_v2 battery.py.
"""
from __future__ import annotations
from collections import Counter

from bench_v3.config.constants import OUTCOMES, FAULT_FAMILY
from bench_v3.families.base import build_scenario
from bench_v3.core.episode import run_episode
from bench_v3.scoring.outcomes import score


def always_accept(obs, retry=False):
    return {"type": "accept_batch"}


def always_recalibrate_then_accept(obs, retry=False):
    # Amendment D: bare recalibrate is rejected; chain std->recalibrate->accept. Recalibrate
    # is harmless on an honest meter -> profile collapses to ~always_accept.
    done = {e["action"].get("type") for e in obs["action_log"] if e.get("committed") and e.get("action")}
    if "measure_standard_concentration" not in done:
        return {"type": "measure_standard_concentration", "standard": "std_high"}
    if "recalibrate" not in done:
        return {"type": "recalibrate", "instrument": "assay_X"}
    return {"type": "accept_batch"}


def always_rebuild_then_accept(obs, retry=False):
    g = obs["goal"]; vessel = g["vessel"]
    proto = obs["initial_protocol_record"]
    nominal = next((p["volume_ml"] for p in proto if p["type"] == "transfer"), 1.0)
    target_vol = next((p["target_volume_ml"] for p in proto if p["type"] == "dilute_to"), 100.0)
    done = {e["action"].get("type") for e in obs["action_log"] if e.get("committed") and e.get("action")}
    if "discard_vessel" not in done:
        return {"type": "discard_vessel", "vessel": vessel}
    if obs["vessels"][vessel]["volume_ml"] <= 1e-9:
        return {"type": "transfer", "src": "stock_X", "dst": vessel, "volume_ml": nominal}
    if obs["vessels"][vessel]["volume_ml"] < target_vol - 1e-9:
        return {"type": "dilute_to", "vessel": vessel, "target_volume_ml": target_vol}
    return {"type": "accept_batch"}


def always_handoff(obs, retry=False):
    return {"type": "abort_and_handoff", "reason": "degenerate"}


def greedy_feedback(obs, retry=False):
    """Chases the VESSEL reading toward target, NEVER verifying the instrument. On an
    instrument fault it chases a biased reading and breaks a good batch -> CF(e)/(a)."""
    g = obs["goal"]; target = g["target_concentration_M"]; tol = g["tolerance_M"]
    vessel = g["vessel"]; sp = g["species"]
    V = obs["vessels"][vessel]["volume_ml"]; cap = obs["vessels"][vessel]["capacity_ml"]
    last_r = None; corrective_since = False
    for e in obs["action_log"]:
        if not e.get("committed"):
            continue
        t = e["action"].get("type")
        if t == "measure_concentration":
            last_r = (e.get("result") or {}).get("measured_concentration_M"); corrective_since = False
        elif t in ("dilute_to", "transfer"):
            corrective_since = True
    if last_r is None or corrective_since:
        return {"type": "measure_concentration", "vessel": vessel, "species": sp}
    if abs(last_r - target) <= tol:
        return {"type": "accept_batch"}
    if last_r > target:
        v_new = V * last_r / target
        if v_new <= cap + 1e-9:
            return {"type": "dilute_to", "vessel": vessel, "target_volume_ml": round(v_new, 4)}
        return {"type": "accept_batch"}
    cs = obs["stocks"]["stock_X"]["label_concentration_M"]   # never verifies -> trusts label
    if cs > target + 1e-9:
        x = V * (target - last_r) / (cs - target)
        if x <= (cap - V) + 1e-9:
            return {"type": "transfer", "src": "stock_X", "dst": vessel, "volume_ml": round(x, 4)}
    return {"type": "accept_batch"}


STRATEGIES = {
    "always_accept": always_accept,
    "always_recalibrate": always_recalibrate_then_accept,
    "always_rebuild": always_rebuild_then_accept,
    "always_handoff": always_handoff,
    "greedy_feedback": greedy_feedback,
}


def run_battery(library, verbose=True):
    results = {}
    for name, strat in STRATEGIES.items():
        c = Counter()
        for inst in library:
            ep = run_episode(strat, build_scenario(inst, noise_seed=0))
            c[score(ep, inst)] += 1
        n = len(library) or 1
        results[name] = {o: round(100 * c[o] / n) for o in OUTCOMES}
        if verbose:
            print(f"  {name:18s} " + "  ".join(f"{o.split('_')[0][:4]}={c[o]:>3d}" for o in OUTCOMES))
    return results


def analytic_caps(library):
    """Per-strategy analytic SUCCESS cap. always_accept / always_recalibrate (Amendment D:
    harmless recalibrate -> accept everything) = in-tol fraction; always_rebuild = off-spec
    transfer-fault fraction; always_handoff = 0; greedy = report-only."""
    n = len(library) or 1
    in_tol = sum(getattr(i, "started_in_tol", False) for i in library)
    rebuild = sum(1 for i in library if (not getattr(i, "started_in_tol", False))
                  and FAULT_FAMILY[i.fault_class] == "transfer")
    return {"always_accept": round(100 * in_tol / n), "always_recalibrate": round(100 * in_tol / n),
            "always_rebuild": round(100 * rebuild / n), "always_handoff": 0, "greedy_feedback": None}


def check_caps(results, library, verbose=True):
    caps = analytic_caps(library); ok = True
    if verbose:
        print("\n  analytic SUCCESS caps:")
    for name, r in results.items():
        cap = caps.get(name); su = r["SUCCESS"]
        if cap is None:
            if verbose: print(f"    {name:18s} SUCCESS={su:>3d}%  cap=n.a. (report only)")
            continue
        passed = su <= cap + 1; ok = ok and passed
        if verbose: print(f"    {name:18s} SUCCESS={su:>3d}%  cap={cap:>3d}%  -> {'PASS' if passed else 'EXCEEDS CAP'}")
    return ok


def gate_passes(results, verbose=True):
    """Amendment B gate: each registered strategy must satisfy CF% >= 20 OR SUCCESS% <= 10."""
    ok_all = True
    if verbose:
        print("\n  gate (Amendment B): each strategy needs CF% >= 20 OR SUCCESS% <= 10")
    for name, r in results.items():
        cf, su = r["CRITICAL_FAIL"], r["SUCCESS"]
        passed = cf >= 20 or su <= 10; ok_all = ok_all and passed
        if verbose:
            print(f"    {name:18s} SUCCESS={su:>3d}%  CF={cf:>3d}%  -> {'PASS' if passed else 'FAIL'}")
    if verbose:
        print(f"  GATE {'PASSED' if ok_all else 'FAILED'}")
    return ok_all
