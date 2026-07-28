"""Guard against retype error: every bench_v3 prompt constant must be byte-identical to
the frozen bench_v2 prompts (materials v1.4)."""
import sys, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# load bench_v2/prompts.py standalone (bench_v2 is not a package)
_spec = importlib.util.spec_from_file_location("v2prompts", str(ROOT / "bench_v2" / "prompts.py"))
v2 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(v2)

from bench_v3.prompts import base_actor, rubrics, personas, aggregator, critic, render


def test_prompts_byte_identical_to_v2():
    pairs = [
        ("BASE_SYSTEM", base_actor.BASE_SYSTEM, v2.BASE_SYSTEM),
        ("ALLOWED_ACTIONS_BLOCK", base_actor.ALLOWED_ACTIONS_BLOCK, v2.ALLOWED_ACTIONS_BLOCK),
        ("FORMAT_RETRY_MSG", base_actor.FORMAT_RETRY_MSG, v2.FORMAT_RETRY_MSG),
        ("L2", rubrics.L2, v2.L2), ("L1", rubrics.L1, v2.L1), ("L3", rubrics.L3, v2.L3),
        ("GENERIC", rubrics.GENERIC, v2.GENERIC),
        ("PERSONA_A", personas.PERSONA_A, v2.PERSONA_A),
        ("PERSONA_B", personas.PERSONA_B, v2.PERSONA_B),
        ("PERSONA_C", personas.PERSONA_C, v2.PERSONA_C),
        ("AGG_SYSTEM", aggregator.AGG_SYSTEM, v2.AGG_SYSTEM),
        ("FREE_CRITIC_SYSTEM", critic.FREE_CRITIC_SYSTEM, v2.FREE_CRITIC_SYSTEM),
        ("THIN_CRITIC_SYSTEM", critic.THIN_CRITIC_SYSTEM, v2.THIN_CRITIC_SYSTEM),
    ]
    for name, a, b in pairs:
        assert a == b, f"{name} differs from bench_v2"
    assert critic.revise_msg("XYZ") == v2.revise_msg("XYZ")
    assert render.base_user("OBS") == v2.base_user("OBS")
    print(f"[PASS] all {len(pairs)} prompt constants + revise_msg + base_user byte-identical to bench_v2")


if __name__ == "__main__":
    test_prompts_byte_identical_to_v2()
    print("\nPROMPTS VERBATIM PASSED")
