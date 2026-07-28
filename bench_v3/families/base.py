"""Instance dataclass + scenario builder + shared mass-balance helpers.

Ported from bench_v2 instances.py (BenchInstance, build_scenario, true_post_protocol_conc,
_single_step_feasible, _rebuild_feasible, _base_params). build_scenario bakes the
instance's single fault into the TRUE state by executing the nominal protocol with
inject_fault=True. The instrument carries calibration_status in STATE (never observed
in v3 -- Amendment G is enforced in observation.py).
"""
from __future__ import annotations
import random
from dataclasses import dataclass

from bench_v3.config.constants import (TARGETS, VOLUMES, STOCK_LABELS, TOL_FRAC,
                                       STD_LOW_RATIO, STD_HIGH_RATIO, FAULT_FAMILY)
from bench_v3.core.state import State, Vessel, Stock, Standard, Instrument, HiddenTruth
from bench_v3.core.simulator import BenchSimulator


@dataclass
class BenchInstance:
    id: str
    family: str
    fault_class: str
    target_concentration_M: float
    tolerance_M: float
    target_volume_ml: float
    vessel_capacity_ml: float
    stock_label_concentration_M: float
    stock_initial_volume_ml: float
    nominal_transfer_volume_ml: float
    transfer_efficiency: float = 1.0
    bias_A: float = 0.0
    gain_G: float = 1.0
    drift_B: float = 0.0
    true_stock_concentration_M: float | None = None   # F3 label divergence
    started_in_tol: bool = False                       # eval-only (scoring d/e)
    oracle_steps: int | None = None                    # filled by certify_oracle


def base_params(rng: random.Random) -> dict:
    c_t = rng.choice(TARGETS)
    v = rng.choice(VOLUMES)
    stock = rng.choice([s for s in STOCK_LABELS if s > c_t * 1.5] or [max(STOCK_LABELS)])
    nominal = c_t * v / stock                       # correct nominal -> no_fault hits target
    cap = round(v * 1.1, 2)
    stock_init = round(max(nominal * 5, 30.0), 2)
    tol = max(0.001, round(TOL_FRAC * c_t, 5))
    return dict(target_concentration_M=c_t, target_volume_ml=v, vessel_capacity_ml=cap,
                stock_label_concentration_M=stock, stock_initial_volume_ml=stock_init,
                nominal_transfer_volume_ml=round(nominal, 4), tolerance_M=tol)


def true_post_protocol_conc(inst: BenchInstance) -> float:
    true_stock = (inst.true_stock_concentration_M if inst.true_stock_concentration_M is not None
                  else inst.stock_label_concentration_M)
    actual_vol = inst.nominal_transfer_volume_ml * inst.transfer_efficiency
    return (actual_vol * true_stock) / inst.target_volume_ml


def single_step_feasible(inst: BenchInstance) -> bool:
    c = true_post_protocol_conc(inst)
    c_t = inst.target_concentration_M; tol = inst.tolerance_M
    cap = inst.vessel_capacity_ml; v = inst.target_volume_ml
    if abs(c - c_t) <= tol:
        return True
    if c > c_t + tol:                              # over: dilute up to capacity
        v_needed = v * c / (c_t + tol)
        return v_needed <= cap + 1e-9
    true_stock = (inst.true_stock_concentration_M if inst.true_stock_concentration_M is not None
                  else inst.stock_label_concentration_M)
    c_low = c_t - tol
    if true_stock <= c_low:
        return False
    x = v * (c_low - c) / (true_stock - c_low)
    stock_remain = inst.stock_initial_volume_ml - inst.nominal_transfer_volume_ml
    return x <= (cap - v) + 1e-9 and x <= stock_remain + 1e-9


def rebuild_feasible(inst: BenchInstance) -> bool:
    true_stock = (inst.true_stock_concentration_M if inst.true_stock_concentration_M is not None
                  else inst.stock_label_concentration_M)
    v_need = inst.target_concentration_M * inst.target_volume_ml / true_stock
    stock_remain = inst.stock_initial_volume_ml - inst.nominal_transfer_volume_ml
    return (true_stock > inst.target_concentration_M + 1e-9
            and v_need <= stock_remain + 1e-9 and v_need <= inst.target_volume_ml + 1e-9)


def build_scenario(inst: BenchInstance, noise_seed: int = 0) -> BenchSimulator:
    rng = random.Random(noise_seed)
    cap = inst.vessel_capacity_ml
    true_stock = (inst.true_stock_concentration_M if inst.true_stock_concentration_M is not None
                  else inst.stock_label_concentration_M)
    state = State(
        vessels={"vessel_1": Vessel(name="vessel_1", volume_ml=0.0, capacity_ml=cap)},
        stocks={"stock_X": Stock(name="stock_X", species="X",
                                 label_concentration_M=inst.stock_label_concentration_M,
                                 ledger_volume_remaining_ml=inst.stock_initial_volume_ml,
                                 true_volume_remaining_ml=inst.stock_initial_volume_ml,
                                 true_concentration_M=true_stock)},
        standards={"std_low": Standard(name="std_low", species="X",
                                       certified_concentration_M=round(inst.target_concentration_M * STD_LOW_RATIO, 5)),
                   "std_high": Standard(name="std_high", species="X",
                                        certified_concentration_M=round(inst.target_concentration_M * STD_HIGH_RATIO, 5))},
        instruments={"assay_X": Instrument(name="assay_X", measures="concentration",
                                           species="X", calibration_status="unknown")},
    )
    hidden = HiddenTruth(transfer_efficiency=inst.transfer_efficiency, bias_A=inst.bias_A,
                         gain_G=inst.gain_G, drift_B=inst.drift_B,
                         fault_family=FAULT_FAMILY[inst.fault_class], fault_class=inst.fault_class)
    goal = {"vessel": "vessel_1", "species": "X",
            "target_concentration_M": inst.target_concentration_M,
            "tolerance_M": inst.tolerance_M,
            "protocol_record": [
                {"type": "transfer", "src": "stock_X", "dst": "vessel_1",
                 "volume_ml": inst.nominal_transfer_volume_ml},
                {"type": "dilute_to", "vessel": "vessel_1", "target_volume_ml": inst.target_volume_ml}]}
    sim = BenchSimulator(state, hidden, goal, rng)
    sim.apply({"type": "transfer", "src": "stock_X", "dst": "vessel_1",
               "volume_ml": inst.nominal_transfer_volume_ml}, inject_fault=True, draw_noise=False)
    sim.apply({"type": "dilute_to", "vessel": "vessel_1",
               "target_volume_ml": inst.target_volume_ml}, inject_fault=False, draw_noise=False)
    sim.state.instruments["assay_X"].read_count = 0   # reset drift counter consumed by the build
    return sim
