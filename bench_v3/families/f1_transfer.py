"""F1 Transfer/Dilution: no_fault / top_up_feasible / dilute_feasible / rebuild_needed.
Fault = transfer-efficiency multiplier (honest meter). Ported from bench_v2 instances.py.
"""
from __future__ import annotations
from bench_v3.families.base import true_post_protocol_conc, single_step_feasible, rebuild_feasible


def sample(fc, rng, kw):
    if fc == "no_fault":
        pass
    elif fc == "top_up_feasible":
        kw["transfer_efficiency"] = round(rng.uniform(0.55, 0.90), 4)   # under-delivered
    elif fc == "dilute_feasible":
        kw["transfer_efficiency"] = round(rng.uniform(1.04, 1.12), 4)   # mild over
    elif fc == "rebuild_needed":
        kw["transfer_efficiency"] = round(rng.uniform(1.25, 1.60), 4)   # large over -> no single-step fix


def membership(inst) -> bool:
    c = true_post_protocol_conc(inst); c_t = inst.target_concentration_M; tol = inst.tolerance_M
    in_tol = abs(c - c_t) <= tol
    fc = inst.fault_class
    if fc == "no_fault":
        return in_tol and inst.transfer_efficiency == 1.0 and inst.gain_G == 1.0 and inst.bias_A == 0.0
    if fc == "top_up_feasible":
        return c < c_t - tol and single_step_feasible(inst)
    if fc == "dilute_feasible":
        return c > c_t + tol and single_step_feasible(inst)
    if fc == "rebuild_needed":
        return (not in_tol) and (not single_step_feasible(inst)) and rebuild_feasible(inst)
    return False
