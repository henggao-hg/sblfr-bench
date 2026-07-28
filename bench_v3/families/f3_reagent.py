"""F3 Reagent Quality: no_fault / rebalance_feasible / rebalance_rebuild.
Fault = stock true concentration != label (honest meter). Ported from bench_v2.
"""
from __future__ import annotations
from bench_v3.families.base import true_post_protocol_conc, single_step_feasible, rebuild_feasible


def sample(fc, rng, kw):
    label = kw["stock_label_concentration_M"]
    if fc == "no_fault":
        pass
    elif fc == "rebalance_feasible":
        m = rng.choice([rng.uniform(0.60, 0.88), rng.uniform(1.12, 1.40)])   # moderate divergence
        kw["true_stock_concentration_M"] = round(label * m, 5)
    elif fc == "rebalance_rebuild":
        m = rng.choice([rng.uniform(1.6, 2.4)])                              # true stock much HOTTER
        kw["true_stock_concentration_M"] = round(label * m, 5)


def membership(inst) -> bool:
    c = true_post_protocol_conc(inst); c_t = inst.target_concentration_M; tol = inst.tolerance_M
    in_tol = abs(c - c_t) <= tol
    fc = inst.fault_class
    if fc == "no_fault":
        return in_tol and inst.transfer_efficiency == 1.0 and inst.gain_G == 1.0 and inst.bias_A == 0.0
    if fc == "rebalance_feasible":
        return (not in_tol) and single_step_feasible(inst)
    if fc == "rebalance_rebuild":
        return (not in_tol) and (not single_step_feasible(inst)) and rebuild_feasible(inst)
    return False
