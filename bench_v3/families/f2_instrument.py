"""F2 Instrument/Calibration: no_fault / instrument_recalibrate (bias|gain) /
chemistry_recoverable / chemistry_rebuild. instrument fault keeps batch chemistry
correct (G9); drift held out of the frozen library (Amendment C). Ported from
bench_v2 instances.py. (Amendment G — dropping calibration_status — is enforced in
observation.py, not here.)
"""
from __future__ import annotations
from bench_v3.config.constants import SIGMA, K_DETECT
from bench_v3.families.base import true_post_protocol_conc, single_step_feasible, rebuild_feasible


def detectable(inst) -> bool:
    """F2 instrument fault must move the std_high (2x) reading by >= tol + k*sigma."""
    c_hi = inst.target_concentration_M * 2.0
    dev = abs((inst.gain_G * c_hi + inst.bias_A + inst.drift_B) - c_hi)
    sigma = SIGMA * inst.target_concentration_M
    return dev >= inst.tolerance_M + K_DETECT * sigma


def sample(fc, rng, kw):
    c_t = kw["target_concentration_M"]; tol = kw["tolerance_M"]
    if fc == "no_fault":
        pass
    elif fc == "instrument_recalibrate":
        kind = rng.choice(["bias", "gain"])           # Amendment C: drift NOT in frozen library
        if kind == "bias":
            mag = (tol + K_DETECT * SIGMA * c_t) * rng.uniform(1.3, 2.5)
            kw["bias_A"] = round(mag * rng.choice([1, -1]), 6)
        else:  # gain: deviation at std_high (2x) = (G-1)*2*c_t must clear tol + k*sigma
            need = (tol + K_DETECT * SIGMA * c_t) / (2 * c_t) * rng.uniform(1.3, 2.5)
            kw["gain_G"] = round(1 + need * rng.choice([1, -1]), 6)
    elif fc == "chemistry_recoverable":
        if rng.random() < 0.5:
            kw["transfer_efficiency"] = round(rng.uniform(0.55, 0.90), 4)   # under
        else:
            kw["transfer_efficiency"] = round(rng.uniform(1.04, 1.12), 4)   # over
    elif fc == "chemistry_rebuild":
        kw["transfer_efficiency"] = round(rng.uniform(1.25, 1.60), 4)


def membership(inst) -> bool:
    c = true_post_protocol_conc(inst); c_t = inst.target_concentration_M; tol = inst.tolerance_M
    in_tol = abs(c - c_t) <= tol
    fc = inst.fault_class
    if fc == "no_fault":
        return in_tol and inst.transfer_efficiency == 1.0 and inst.gain_G == 1.0 and inst.bias_A == 0.0
    if fc == "instrument_recalibrate":
        return in_tol and detectable(inst)                 # chemistry correct, meter off + detectable
    if fc == "chemistry_recoverable":
        return (not in_tol) and single_step_feasible(inst)
    if fc == "chemistry_rebuild":
        return (not in_tol) and (not single_step_feasible(inst)) and rebuild_feasible(inst)
    return False
