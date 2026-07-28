"""families gate: every one of the 11 classes can be sampled to a member, and the
scenario the simulator bakes agrees with the analytic membership math (the truth the
oracle/cert will rely on).
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench_v3.families.registry import sample_instance, certify_membership, all_class_specs
from bench_v3.families.base import build_scenario, true_post_protocol_conc
from bench_v3.core.simulator import true_in_tol


def _find_member(fam, fc, rng, tries=4000):
    for _ in range(tries):
        inst = sample_instance(fam, fc, rng)
        if certify_membership(inst):
            return inst
    return None


def test_every_class_fills_and_is_consistent():
    rng = random.Random(7)
    for fam, fc in all_class_specs():
        inst = _find_member(fam, fc, rng)
        assert inst is not None, f"could not sample a member for {fam}/{fc}"
        sim = build_scenario(inst, noise_seed=0)
        # analytic post-protocol conc must equal the simulator's baked true conc
        baked = sim.state.vessels["vessel_1"].concentration_M("X")
        analytic = true_post_protocol_conc(inst)
        assert abs(baked - analytic) < 1e-6, f"{fam}/{fc}: baked {baked} != analytic {analytic}"
        # class-condition sanity on the baked truth
        nf = (fc == "no_fault")
        if nf:
            assert true_in_tol(sim), f"{fam}/no_fault baked out of tol"
        if fc in ("rebuild_needed", "chemistry_rebuild", "rebalance_rebuild"):
            assert not true_in_tol(sim), f"{fam}/{fc} baked in tol (should be off-spec)"
        print(f"  [ok] {fam}/{fc:24s} baked_conc={baked:.5f} target={inst.target_concentration_M} in_tol={true_in_tol(sim)}")
    print("\nALL 11 CLASSES FILL + simulator truth matches analytic membership")


if __name__ == "__main__":
    test_every_class_fills_and_is_consistent()
