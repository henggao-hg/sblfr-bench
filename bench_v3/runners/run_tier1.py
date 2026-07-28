"""Tier-1 sweep: 9 arms x 275 x seed0. Cheap/headline arms first (single, actor_rubric,
free/thin critic, bo3) so C1/C2/C3 land early; the four expensive 2x2 arms last (so an
early kill saves the most). RESUMABLE (re-launch skips completed episodes). Critic pairing
per rule: weak qwen32b -> qwen_max critic; strong qwen_max -> deepseek critic.
usage: python -m bench_v3.runners.run_tier1 <weak|strong>
"""
import sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v3.instances.generate import load_library
from bench_v3.runners.run_sweep import run_sweep, make_actor, make_critic

ARMS = ["single", "actor_rubric", "free_critic", "thin_critic", "bo3",
        "sc3_vote", "sc3_agg", "team_vote", "team_agg"]   # 2x2 hogs last

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "weak"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0     # extra seeds for CI; default 0 (back-compat)
    lib = load_library()
    (ROOT / "bench_v3" / "results").mkdir(exist_ok=True)
    if which == "weak":
        actor, critic = make_actor("qwen32b"), make_critic("qwen_max")
    else:
        actor, critic = make_actor("qwen_max"), make_critic("deepseek")
    out = str(ROOT / "bench_v3" / "results" / f"v3_tier1_{which}_seed{seed}.jsonl")
    print(f"v3 Tier-1 [{which}]: {ARMS} x {len(lib)} x seed{seed} -> {out}", flush=True)
    t0 = time.time()
    n, el = run_sweep(ARMS, actor, critic, [seed], lib, out, verbose=True, resume=True)
    print(f"v3 Tier-1 [{which}] done: {n} new ep, {round(el/3600,1)} h", flush=True)
