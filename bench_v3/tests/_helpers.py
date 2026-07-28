"""Tiny scenario builder for core tests (families/ not needed yet). Bakes the
post-protocol TRUE state directly so core (simulator/verifier/observation/episode)
can be exercised on one instance without the full generator."""
from __future__ import annotations
import random

from bench_v3.core.state import State, Vessel, Stock, Standard, Instrument, HiddenTruth
from bench_v3.core.simulator import BenchSimulator
from bench_v3.config.constants import STD_LOW_RATIO, STD_HIGH_RATIO, TOL_FRAC


def build_sim(target=0.2, vol=100.0, cap=None, stock_label=2.0, true_stock=None,
              bias=0.0, gain=1.0, true_conc=None, calibration_status="unknown",
              fault_class="no_fault", fault_family="none", seed=0):
    cap = cap if cap is not None else round(vol * 1.1, 2)
    tc = true_conc if true_conc is not None else target      # post-protocol true vessel conc
    ts = true_stock if true_stock is not None else stock_label
    state = State(
        vessels={"vessel_1": Vessel("vessel_1", vol, cap, {"X": tc * vol})},
        stocks={"stock_X": Stock("stock_X", "X", stock_label, 100.0, 100.0,
                                 true_concentration_M=ts)},
        standards={"std_low": Standard("std_low", "X", round(target * STD_LOW_RATIO, 5)),
                   "std_high": Standard("std_high", "X", round(target * STD_HIGH_RATIO, 5))},
        instruments={"assay_X": Instrument("assay_X", "concentration", "X", calibration_status, 0)},
    )
    hidden = HiddenTruth(bias_A=bias, gain_G=gain, fault_family=fault_family, fault_class=fault_class)
    goal = {"vessel": "vessel_1", "species": "X", "target_concentration_M": target,
            "tolerance_M": round(target * TOL_FRAC, 5), "protocol_record": [
                {"type": "transfer", "src": "stock_X", "dst": "vessel_1", "volume_ml": round(target * vol / stock_label, 4)},
                {"type": "dilute_to", "vessel": "vessel_1", "target_volume_ml": vol}]}
    return BenchSimulator(state, hidden, goal, random.Random(seed))
