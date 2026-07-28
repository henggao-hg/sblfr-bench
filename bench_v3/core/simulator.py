"""Unified simulator: how the state changes.

ONE simulator for all three families (faults non-additive, G9). Ported from bench_v2
env.BenchSimulator -- behavior must match (Amendments A-F): noisy measurement
(true*(1+eps)), F1 transfer-efficiency hook, F2 instrument bias/gain reading transform,
measure_stock passes through the meter hook (Amendment A), evidence-based recalibrate
(Amendment D/E/F): >=2 distinct-concentration standards -> affine, 1 standard (or only
same-standard repeats, averaged -> one point) -> offset/bias only.

This file does NOT decide legality (verifier.py) or what the agent sees (observation.py).
"""
from __future__ import annotations
import random

from bench_v3.config.constants import SIGMA, TERMINAL_ACTIONS
from bench_v3.core.state import State, Instrument, HiddenTruth


class BenchSimulator:
    def __init__(self, state: State, hidden: HiddenTruth, goal: dict, rng: random.Random):
        self.state = state
        self.hidden = hidden
        self.goal = goal
        self.rng = rng
        # Amendment D/E1: std_name -> (certified_true, mean_observed, n_reads)
        self.measured_standards: dict = {}
        # None | ("bias", b) | ("affine", g, b); applied to every reading
        self.calibration = None

    # ---- fault hooks ----
    def _effective_transfer_volume(self, requested: float, *, inject_fault: bool) -> float:
        return requested * self.hidden.transfer_efficiency if inject_fault else requested

    def _conc_instrument(self, species: str):
        for ins in self.state.instruments.values():
            if ins.measures == "concentration" and (ins.species is None or ins.species == species):
                return ins
        return None

    def _bump_read_count(self, species: str) -> None:
        ins = self._conc_instrument(species)
        if ins is not None:
            ins.read_count += 1

    def _instrument_reading(self, true_value: float, species: str) -> float:
        ins = self._conc_instrument(species)
        raw = (self.hidden.gain_G * true_value + self.hidden.bias_A
               + self.hidden.drift_B * (ins.read_count if ins else 0))
        cal = self.calibration
        if cal is None:
            return raw
        if cal[0] == "bias":                 # one point: offset correction only
            return raw - cal[1]
        return (raw - cal[2]) / cal[1]       # two-point affine: observed = g*true + b -> invert

    def _sigma(self) -> float:
        return SIGMA * max(self.goal.get("target_concentration_M", 1e-3), 1e-3)

    # ---- apply ----
    def apply(self, action: dict, *, inject_fault: bool, draw_noise: bool) -> dict:
        t = action["type"]
        if t == "transfer":
            return self._transfer(action, inject_fault=inject_fault)
        if t == "dilute_to":
            return self._dilute_to(action)
        if t == "measure_concentration":
            return self._measure_concentration(action, draw_noise=draw_noise)
        if t == "measure_volume":
            v = self.state.vessels[action["vessel"]]
            return {"measured_volume_ml": round(v.volume_ml, 4)}
        if t == "measure_stock_volume":
            s = self.state.stocks[action["stock"]]
            return {"measured_stock_volume_ml": round(s.ledger_volume_remaining_ml, 4)}
        if t == "measure_stock_concentration":
            return self._measure_stock_concentration(action, draw_noise=draw_noise)
        if t == "measure_standard_concentration":
            return self._measure_standard(action, draw_noise=draw_noise)
        if t == "recalibrate":
            return self._recalibrate(action)
        if t == "discard_vessel":
            v = self.state.vessels[action["vessel"]]
            v.volume_ml = 0.0; v.species_mmol = {}
            return {"discarded": v.name}
        if t == "quarantine_stock":
            s = self.state.stocks[action["stock"]]
            s.quarantined = True
            return {"quarantined": s.name}
        if t in TERMINAL_ACTIONS:
            return {"acknowledged": t}
        raise ValueError(f"unhandled action {t!r}")

    def _transfer(self, action: dict, *, inject_fault: bool) -> dict:
        src = self.state.stocks[action["src"]]; dst = self.state.vessels[action["dst"]]
        requested = float(action["volume_ml"])
        actual_vol = self._effective_transfer_volume(requested, inject_fault=inject_fault)
        true_conc = src.get_true_concentration_M()        # F3: true (possibly mislabeled) conc
        sp = src.get_true_species()
        dst.species_mmol[sp] = dst.species_mmol.get(sp, 0.0) + actual_vol * true_conc
        dst.volume_ml += actual_vol
        src.ledger_volume_remaining_ml -= requested        # ledger records REQUESTED
        src.true_volume_remaining_ml -= actual_vol
        return {"transferred_to": dst.name}

    def _dilute_to(self, action: dict) -> dict:
        v = self.state.vessels[action["vessel"]]
        v.volume_ml = float(action["target_volume_ml"])
        return {"diluted_to": v.volume_ml}

    def _measure_concentration(self, action: dict, *, draw_noise: bool) -> dict:
        v = self.state.vessels[action["vessel"]]; sp = action["species"]
        if draw_noise:
            self._bump_read_count(sp)
        displayed = self._instrument_reading(v.concentration_M(sp), sp)
        if draw_noise:
            displayed = max(0.0, displayed + self.rng.gauss(0, self._sigma()))
        return {"measured_concentration_M": round(displayed, 5)}

    def _measure_stock_concentration(self, action: dict, *, draw_noise: bool) -> dict:
        s = self.state.stocks[action["stock"]]; sp = s.species   # species implicit (stock's)
        if draw_noise:
            self._bump_read_count(sp)
        displayed = self._instrument_reading(s.get_true_concentration_M(), sp)   # through meter hook (Amendment A)
        if draw_noise:
            displayed = max(0.0, displayed + self.rng.gauss(0, self._sigma()))
        return {"stock": s.name, "measured_concentration_M": round(displayed, 5)}

    def _measure_standard(self, action: dict, *, draw_noise: bool) -> dict:
        std = self.state.standards[action["standard"]]; sp = std.species
        if draw_noise:
            self._bump_read_count(sp)
        # standard is an axiomatic honest anchor; the meter transform still applies, so a
        # faulty meter mis-reads it by the same transform -> diagnosable.
        displayed = self._instrument_reading(std.certified_concentration_M, sp)
        if draw_noise:
            displayed = max(0.0, displayed + self.rng.gauss(0, self._sigma()))
            # Amendment D/E1: a "point" is a DISTINCT concentration; same-standard repeats
            # AVERAGE into one point (noise reduction, still bias-only). Keyed by std name.
            prev = self.measured_standards.get(std.name)
            if prev is None:
                self.measured_standards[std.name] = (std.certified_concentration_M, displayed, 1)
            else:
                _, mean, k = prev
                self.measured_standards[std.name] = (
                    std.certified_concentration_M, (mean * k + displayed) / (k + 1), k + 1)
        return {"standard": std.name, "certified_concentration_M": std.certified_concentration_M,
                "measured_concentration_M": round(displayed, 5)}

    def _recalibrate(self, action: dict) -> dict:
        # Amendment D/E1: >=2 DISTINCT-concentration standards -> affine (bias+gain);
        # a single standard (or only same-standard repeats) -> bias only, gain stays 1.
        ins = self.state.instruments[action["instrument"]]
        pts = [(t, o) for (t, o, _n) in self.measured_standards.values()]
        if len(pts) >= 2 and abs(pts[1][0] - pts[0][0]) > 1e-9:
            (t1, o1), (t2, o2) = pts[0], pts[1]
            g = (o2 - o1) / (t2 - t1); b = o1 - g * t1
            self.calibration = ("affine", g, b)
        elif pts:
            self.calibration = ("bias", pts[0][1] - pts[0][0])   # one point -> assume gain 1
        ins.calibration_status = "recalibrated"
        return {"recalibrated": ins.name}


def true_in_tol(sim) -> bool:
    g = sim.goal
    v = sim.state.vessels[g["vessel"]]
    return abs(v.concentration_M(g["species"]) - g["target_concentration_M"]) <= g["tolerance_M"]
