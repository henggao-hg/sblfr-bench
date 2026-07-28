"""The family-blind cognitive oracle (L2 procedure). ONE scripted policy that does not
know the fault class; it diagnoses from its own measurements read back from
obs['action_log']. It is the budget-setting reference AND the certify_oracle reachability
checker. Ported from bench_v2 oracle.cognitive_oracle (with the 2-point instrument fix):
on a detected instrument fault it measures BOTH standards (gain needs two points), then
corrects the stored vessel reading analytically. Does NOT read any status field
(Amendment G has no effect on the oracle).
"""
from __future__ import annotations


def obs_target_vol(proto):
    return next((p["target_volume_ml"] for p in proto if p["type"] == "dilute_to"), 100.0)


def _last_measures(obs):
    vessel_C = None; vessel_after_recal = False
    std_hi = None; std_lo = None; recal = False
    for e in obs["action_log"]:
        if not e.get("committed"):
            continue
        a = e["action"]; r = e.get("result") or {}; t = a.get("type")
        if t == "recalibrate":
            recal = True
        elif t == "measure_concentration":
            vessel_C = r.get("measured_concentration_M"); vessel_after_recal = recal
        elif t == "measure_standard_concentration":
            if a.get("standard") == "std_high":
                std_hi = (r.get("measured_concentration_M"), r.get("certified_concentration_M"))
            elif a.get("standard") == "std_low":
                std_lo = (r.get("measured_concentration_M"), r.get("certified_concentration_M"))
    return vessel_C, vessel_after_recal, std_hi, std_lo, recal


def _stock_conc(obs):
    val = None; after_recal = False; recal = False
    for e in obs["action_log"]:
        if not e.get("committed"):
            continue
        a = e["action"]; r = e.get("result") or {}
        if a.get("type") == "recalibrate":
            recal = True
        elif a.get("type") == "measure_stock_concentration":
            val = r.get("measured_concentration_M"); after_recal = recal
    return val, after_recal


def cognitive_oracle(obs, retry=False):
    g = obs["goal"]; target = g["target_concentration_M"]; tol = g["tolerance_M"]
    vessel = g["vessel"]; sp = g["species"]
    cap = obs["vessels"][vessel]["capacity_ml"]
    Vtgt = obs_target_vol(obs["initial_protocol_record"])
    vessel_C, v_after_recal, std_hi, std_lo, recal = _last_measures(obs)
    stock_C, stock_after_recal = _stock_conc(obs)
    instr_thresh = tol

    # 1. measure vessel
    if vessel_C is None:
        return {"type": "measure_concentration", "vessel": vessel, "species": sp}
    # 2. verify the instrument against the high standard
    if std_hi is None:
        return {"type": "measure_standard_concentration", "standard": "std_high"}
    meas_hi, cert_hi = std_hi
    instrument_off = abs(meas_hi - cert_hi) > instr_thresh
    # 3. instrument off -> need a SECOND standard (gain needs two points), then recalibrate;
    #    after recalibration correct the stored vessel reading analytically (no extra step).
    if instrument_off:
        if std_lo is None:
            return {"type": "measure_standard_concentration", "standard": "std_low"}
        if not recal:
            return {"type": "recalibrate", "instrument": "assay_X"}
    if instrument_off and recal:
        meas_lo, cert_lo = std_lo
        gslope = (meas_hi - meas_lo) / (cert_hi - cert_lo)
        b = meas_lo - gslope * cert_lo
        r_v = (vessel_C - b) / gslope if abs(gslope) > 1e-12 else vessel_C
    else:
        r_v = vessel_C
    if abs(r_v - target) <= tol:
        return {"type": "accept_batch"}

    # corrective phase. r_v was measured at the protocol volume Vtgt; all feasibility
    # math uses Vtgt, never the live (post-correction) volume.
    corr = [e["action"]["type"] for e in obs["action_log"]
            if e.get("committed") and e["action"].get("type") in ("transfer", "dilute_to", "discard_vessel")]
    has_discard = "discard_vessel" in corr
    need_stock = (stock_C is None) or (recal and not stock_after_recal)
    over = r_v > target + tol
    v_dilute = Vtgt * r_v / target
    dilute_ok = over and (v_dilute <= cap + 1e-9)

    # single-step path (no rebuild)
    if not has_discard:
        if dilute_ok:
            if "dilute_to" not in corr:
                return {"type": "dilute_to", "vessel": vessel, "target_volume_ml": round(v_dilute, 4)}
            return {"type": "accept_batch"}
        if not over:
            if need_stock:
                return {"type": "measure_stock_concentration", "stock": "stock_X"}
            if stock_C > target + 1e-9:
                x = Vtgt * (target - r_v) / (stock_C - target)
                if x <= (cap - Vtgt) + 1e-9:
                    if "transfer" not in corr:
                        return {"type": "transfer", "src": "stock_X", "dst": vessel, "volume_ml": round(x, 4)}
                    return {"type": "accept_batch"}
    # rebuild path: measure_stock -> discard -> transfer(w) -> dilute(Vtgt) -> accept
    if need_stock:
        return {"type": "measure_stock_concentration", "stock": "stock_X"}
    if "discard_vessel" not in corr:
        return {"type": "discard_vessel", "vessel": vessel}
    if "transfer" not in corr:
        w = target * Vtgt / stock_C
        return {"type": "transfer", "src": "stock_X", "dst": vessel, "volume_ml": round(w, 4)}
    if "dilute_to" not in corr:
        return {"type": "dilute_to", "vessel": vessel, "target_volume_ml": round(Vtgt, 4)}
    return {"type": "accept_batch"}
