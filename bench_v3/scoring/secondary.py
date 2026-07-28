"""Secondary metrics (NOT in the ladder): fault_cleared, needless_interventions, and
meter_reading_accurate (the calibration-accuracy check that certification enforces for
the instrument class, Amendment E2). Ported from bench_v2 scoring.py.
"""
from __future__ import annotations


def meter_reading_accurate(sim, eps=None) -> bool:
    """Amendment E2: is the calibrated meter's TERMINAL reading within eps of truth across
    the operating range (goal target + the two standards)? eps defaults to the goal
    tolerance. A correct 2-point recalibration passes; a 1-point-on-gain fails."""
    g = sim.goal; sp = g["species"]
    if eps is None:
        eps = g["tolerance_M"]
    pts = [g["target_concentration_M"]]
    pts += [s.certified_concentration_M for s in sim.state.standards.values() if s.species == sp]
    return max(abs(sim._instrument_reading(t, sp) - t) for t in pts) <= eps


def fault_cleared(ep, inst):
    """instrument: calibrated meter reads true within tolerance (not merely 'recalibrate
    was called'). Everything else: n.a. (None)."""
    fam = ep.sim.hidden.fault_family
    if fam == "instrument":
        return meter_reading_accurate(ep.sim)
    return None


def needless_interventions(ep, inst) -> int:
    """Count interventions on a no-fault object: recalibrate an honest meter / discard an
    in-tol batch / quarantine a label-accurate stock. Carries the over-intervention
    dimension; not in the ladder (Amendment D)."""
    fam = ep.sim.hidden.fault_family
    n = 0
    for e in ep.truth_log:
        t = e["type"]
        if t == "recalibrate" and fam != "instrument":
            n += 1
        elif t == "discard_vessel" and e["tib"]:
            n += 1
        elif t == "quarantine_stock" and e.get("stock_accurate"):
            n += 1
    return n
