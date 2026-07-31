"""Cross model-family ablation runner.

Drives the frozen ablation arms (single_stoprule, single_personaB, rubric_reassert)
with the local cross-family actor (Llama 3.1 8B weak / gpt-5.6-luna strong) instead
of the config models. Reuses run_ablation_sweep unchanged (it already takes an actor
object), so no ablation or frozen code is modified.

Output -> bench_v3/results/v3_crossmodel_ablation_<which>_seed<seed>.jsonl, distinct
from the frozen ablation and the crossmodel main-arm files. Resumable.

usage:
  SBLFR_API_KEYS_PATH=path/to/API-keys.txt \
    python -m bench_v3.cross_model_family.run_ablation_cm <weak|strong> [seed] [arm1,arm2,...]
default arms = all three ablation arms.
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v3.instances.generate import load_library
from bench_v3.ablation.run_ablation import run_ablation_sweep, ABLATION_ARMS
from bench_v3.cross_model_family.models import make_actor

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "weak"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    arms = sys.argv[3].split(",") if len(sys.argv) > 3 else list(ABLATION_ARMS)
    bad = [a for a in arms if a not in ABLATION_ARMS]
    if bad:
        raise SystemExit(f"unknown ablation arm(s) {bad}; known = {ABLATION_ARMS}")

    actor = make_actor(which)
    lib = load_library()
    (ROOT / "bench_v3" / "results").mkdir(exist_ok=True)
    out = str(ROOT / "bench_v3" / "results" / f"v3_crossmodel_ablation_{which}_seed{seed}.jsonl")
    print(f"cross-model ABLATION [{which}: {actor.name}]: {arms} x {len(lib)} x seed{seed} -> {out}",
          flush=True)
    t0 = time.time()
    n, el = run_ablation_sweep(arms, actor, [seed], lib, out, verbose=True, resume=True)
    print(f"cross-model ABLATION [{which}] done: {n} new ep, {round(el/3600, 2)} h", flush=True)
