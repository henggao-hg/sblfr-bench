"""action_profile gate: group shares normalize, JSD is 0 for identical distributions and
>0 for different ones, incidence + motif behave."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench_v3.scoring.action_profile import group_share, incidence, jsd, motif, noise_floor, GROUPS


def _rows(seqs):
    return [{"committed_types": s} for s in seqs]


def test_group_share_and_jsd():
    a = _rows([["measure_concentration", "accept_batch"]] * 4)
    b = _rows([["recalibrate", "abort_and_handoff"]] * 4)
    ga, gb = group_share(a), group_share(b)
    assert abs(sum(ga.values()) - 1.0) < 1e-9 and set(ga) == set(GROUPS)
    assert jsd(ga, ga) == 0.0, "JSD of identical must be 0"
    assert jsd(ga, gb) >= 0.4, f"JSD of near-disjoint distributions should be large, got {jsd(ga,gb)}"
    print(f"[PASS] group_share normalizes; JSD(identical)=0; JSD(disjoint)={jsd(ga,gb)}")


def test_incidence_and_motif():
    rows = _rows([["measure_concentration", "recalibrate", "accept_batch"],
                  ["measure_concentration", "abort_and_handoff"]])
    inc = incidence(rows)
    assert inc["recal%"] == 50 and inc["accept%"] == 50 and inc["handoff%"] == 50 and inc["std_check%"] == 0
    assert motif(rows[0]) == "Mv R A"
    print(f"[PASS] incidence {inc}; motif '{motif(rows[0])}'")


def test_noise_floor_small():
    assert noise_floor(_rows([["accept_batch"]] * 4)) is None   # <6 -> None
    print("[PASS] noise_floor returns None for too-few episodes")


if __name__ == "__main__":
    test_group_share_and_jsd()
    test_incidence_and_motif()
    test_noise_floor_small()
    print("\nACTION PROFILE PASSED")
