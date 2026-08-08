"""Tier-1 bo3_v2 runner (corrected selector).

New file. Does not modify any existing runner. Drives the parallel bo3_v2 sweep
(arms/bo3_v2/sweep.py) with the frozen config models, so the corrected bo3 can be
compared against the frozen v1 bo3 in v3_tier1_*.

  weak   = qwen32b   (local)
  strong = qwen3.7-max (API)
Critic pairing is irrelevant (bo3 has no critic).

Output: bench_v3/results/v3_bo3v2_tier1_<which>_seed<seed>.jsonl (+ .transcript),
kept separate from the frozen v3_tier1_* files. Resumable.

usage: python -m bench_v3.runners.run_bo3_v2 <weak|strong> [seed]
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v3.instances.generate import load_library
from bench_v3.runners.run_sweep import make_actor
from bench_v3.arms.bo3_v2.sweep import run_bo3v2_sweep

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "weak"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    actor = make_actor("qwen32b" if which == "weak" else "qwen_max")
    lib = load_library()
    (ROOT / "bench_v3" / "results").mkdir(exist_ok=True)
    out = str(ROOT / "bench_v3" / "results" / f"v3_bo3v2_tier1_{which}_seed{seed}.jsonl")
    print(f"bo3_v2 tier1 [{which}: {actor.name}] x {len(lib)} x seed{seed} -> {out}", flush=True)
    t0 = time.time()
    n, el = run_bo3v2_sweep(actor, [seed], lib, out, verbose=True, resume=True)
    print(f"bo3_v2 tier1 [{which}] done: {n} new ep, {round(el/3600,2)} h", flush=True)
