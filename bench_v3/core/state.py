"""bench_v3 state objects.

Reuses the proven core.py dataclasses (Vessel / Stock / Standard / Instrument / State
+ invariants / goal helpers) rather than re-deriving them, and adds HiddenTruth — the
eval-only injected fault (exactly one active per instance, G9). HiddenTruth is NEVER
observed; it lives on the simulator and goes only to the eval transcript.
"""
from __future__ import annotations
import sys
from dataclasses import dataclass
from pathlib import Path

# core.py lives at sblfr-chem/core.py (two levels up from bench_v3/core/state.py)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core import (  # noqa: E402
    State, Vessel, Stock, Standard, Instrument,
    check_invariants, goal_residual, goal_met,
)

__all__ = ["State", "Vessel", "Stock", "Standard", "Instrument",
           "check_invariants", "goal_residual", "goal_met", "HiddenTruth"]


@dataclass
class HiddenTruth:
    """Exactly one fault active per instance (G9); defaults = no fault. Eval-only."""
    transfer_efficiency: float = 1.0      # F1/F2-chem: delivered = requested * eff
    bias_A: float = 0.0                   # F2: reading = gain*true + bias + drift*reads
    gain_G: float = 1.0
    drift_B: float = 0.0                  # held out of the frozen library (Amendment C)
    fault_family: str = "none"            # eval-log only; never observed
    fault_class: str = "no_fault"         # eval-log only
