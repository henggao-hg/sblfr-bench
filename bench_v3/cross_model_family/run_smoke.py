"""Cross model-family smoke: single arm, a few classes, one instance each.

Validates the local model layer end-to-end through the real benchmark prompts,
for one actor at a time (weak = Llama 3.1 8B, strong = gpt-5.6-luna). single
uses no critic, so this exercises exactly the two new actor models.

usage:
  SBLFR_API_KEYS_PATH=path/to/API-keys.txt \
    python -m bench_v3.cross_model_family.run_smoke <weak|strong>
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v3.instances.generate import load_library
from bench_v3.runners.run_sweep import run_sweep
from bench_v3.cross_model_family.models import make_actor

CLASSES = ["no_fault", "instrument_recalibrate", "rebuild_needed"]

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "strong"
    lib = load_library()
    picks = []
    for fc in CLASSES:
        picks += [i for i in lib if i.fault_class == fc][:1]
    (ROOT / "bench_v3" / "results").mkdir(exist_ok=True)
    actor = make_actor(which)
    out = str(ROOT / "bench_v3" / "results" / f"v3_crossmodel_smoke_{which}.jsonl")
    print(f"cross-model smoke [{which}: {actor.name}]: single x {[i.id for i in picks]} -> {out}",
          flush=True)
    t0 = time.time()
    n, el = run_sweep(["single"], actor, None, [0], picks, out,
                      verbose=True, do_interleave=True, resume=False)
    print(f"cross-model smoke [{which}] done: {n} ep, {round(el/60, 1)} min", flush=True)
