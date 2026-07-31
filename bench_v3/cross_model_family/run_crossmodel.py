"""Cross model-family probe runner (ablation A5).

Runs the frozen 275-instance benchmark with a third-party model family:
  weak   = Llama 3.1 8B  (Meta, local Ollama)  actor
  strong = gpt-5.6-luna  (OpenAI)              actor
Critic for the critic-using arms is Qwen3.7-Max (config `qwen_max`), reused
read-only. The critic is only built when an arm actually needs it, so a
single/actor_rubric run touches just the two actor models.

Reuses run_sweep / load_library / arms / scoring unchanged. Writes the standard
paired metrics + transcript jsonl into bench_v3/results/.

usage:
  SBLFR_API_KEYS_PATH=path/to/API-keys.txt \
    python -m bench_v3.cross_model_family.run_crossmodel <weak|strong> [seed] [arm1,arm2,...]
default arms = single only.
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v3.instances.generate import load_library
from bench_v3.runners.run_sweep import run_sweep, make_critic
from bench_v3.cross_model_family.models import make_actor

ALL_ARMS = ["single", "actor_rubric", "free_critic", "thin_critic",
            "sc3_vote", "sc3_agg", "team_vote", "team_agg", "bo3"]
_CRITIC_ARMS = {"free_critic", "thin_critic"}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "weak"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    arms = sys.argv[3].split(",") if len(sys.argv) > 3 else ["single"]

    lib = load_library()
    (ROOT / "bench_v3" / "results").mkdir(exist_ok=True)
    actor = make_actor(which)
    # Both weak and strong pair with Qwen3.7-Max as critic; build it only if needed.
    critic = make_critic("qwen_max") if (set(arms) & _CRITIC_ARMS) else None

    out = str(ROOT / "bench_v3" / "results" / f"v3_crossmodel_{which}_seed{seed}.jsonl")
    print(f"cross-model [{which}: {actor.name}] arms={arms} x {len(lib)} x seed{seed} -> {out}",
          flush=True)
    t0 = time.time()
    n, el = run_sweep(arms, actor, critic, [seed], lib, out, verbose=True, resume=True)
    print(f"cross-model [{which}] done: {n} new ep, {round(el/3600, 2)} h", flush=True)
