"""A9 bo3 — whole-episode best-of-3 by VISIBLE rank (no hidden truth). bo3 is
episode-LEVEL (run single 3x at the runner, pick max by visible_rank), so the ranking
function lives here; the runner orchestrates the 3 episodes. Ported from bench_v2.
"""
from __future__ import annotations
from bench_v3.arms.base import visible_rank  # re-export: (ep, target) -> sortable key

__all__ = ["visible_rank"]
