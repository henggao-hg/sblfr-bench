"""First real-LLM smoke of bench_v3 (also the DROP-sanity preview). All 9 arms on a few
hypothesis classes, one instance each, seed0. Critic pairing per rule: weak qwen32b ->
qwen_max critic; strong qwen_max -> deepseek critic.
usage: python -m bench_v3.runners.smoke_llm <weak|strong>
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v3.instances.generate import load_library
from bench_v3.runners.run_sweep import run_sweep, make_actor, make_critic

CLASSES = ["no_fault", "instrument_recalibrate", "rebuild_needed"]
ARMS = ["single", "actor_rubric", "free_critic", "thin_critic",
        "sc3_vote", "sc3_agg", "team_vote", "team_agg", "bo3"]

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "strong"
    lib = load_library()
    picks = []
    for fc in CLASSES:
        picks += [i for i in lib if i.fault_class == fc][:1]
    (ROOT / "bench_v3" / "results").mkdir(exist_ok=True)
    if which == "weak":
        actor, critic = make_actor("qwen32b"), make_critic("qwen_max")
        out = str(ROOT / "bench_v3" / "results" / "v3_smoke_weak.jsonl")
    else:
        actor, critic = make_actor("qwen_max"), make_critic("deepseek")
        out = str(ROOT / "bench_v3" / "results" / "v3_smoke_strong.jsonl")
    print(f"v3 smoke [{which}]: {ARMS} x {[i.id for i in picks]} x seed0 -> {out}", flush=True)
    import time; t0 = time.time()
    n, el = run_sweep(ARMS, actor, critic, [0], picks, out, verbose=True, do_interleave=True)
    print(f"v3 smoke [{which}] done: {n} ep, {round(el/60,1)} min", flush=True)
