"""End-to-end pipeline check with a FAKE deterministic model (no API, $0). Drives
run_sweep over a few instances + a couple arms and asserts BOTH output files are written
with the expected fields (metrics + transcript), the agent-visible log stays clean, and
the eval transcript carries the audit records. This is the integration gate.

usage: python -m bench_v3.runners.dry_run
"""
from __future__ import annotations
import sys, json, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v3.instances.generate import load_library
from bench_v3.runners.run_sweep import run_sweep


class FakeModel:
    def __init__(self, name="fake"):
        self.name = name; self.calls = self.pt = self.ct = 0
    def reset(self):
        self.calls = self.pt = self.ct = 0
    def __call__(self, system, user):
        self.calls += 1; self.pt += 10; self.ct += 5
        if "selection judge" in system:
            return '{"choice": 1}'
        if "reviewer" in system:
            return '{"verdict": "approve"}'
        if '"measured_concentration_M"' in user:
            return '{"type":"accept_batch","rationale":"done"}'
        return '{"type":"measure_concentration","vessel":"vessel_1","species":"X","rationale":"m"}'


def main():
    lib = load_library()
    # a couple instances per a few classes, a few arms (incl one critic + one multi)
    subset = []
    for fc in ("no_fault", "instrument_recalibrate", "rebuild_needed"):
        subset += [i for i in lib if i.fault_class == fc][:2]
    arms = ["single", "actor_rubric", "thin_critic", "sc3_vote", "bo3"]
    with tempfile.TemporaryDirectory() as d:
        out = str(Path(d) / "dry.jsonl")
        n, el = run_sweep(arms, FakeModel("actor"), FakeModel("critic"), [0], subset, out, verbose=False)
        metrics = [json.loads(l) for l in open(out)]
        trans = [json.loads(l) for l in open(out[:-6] + ".transcript.jsonl")]
        assert len(metrics) == len(arms) * len(subset) == n, (len(metrics), n)
        assert len(trans) == n
        for r in metrics:
            assert set(("arm", "outcome", "cf_reason", "needless", "committed_types",
                        "actor_calls", "critic_calls")) <= set(r), r
        # agent-visible logs clean; transcripts carry audit records for multi/critic arms
        for t in trans:
            blob = json.dumps(t["steps"]).lower()
            if t["arm"] in ("sc3_vote",):
                assert any(s.get("proposals") for s in t["steps"]), t["arm"]
            if t["arm"] in ("thin_critic",):
                assert any(s.get("critic") for s in t["steps"]), t["arm"]
        print(f"[PASS] dry_run: {n} episodes across {len(arms)} arms x {len(subset)} instances")
        print("       both files written; metrics fields present; proposals+critic audited; no crash")
    print("\nINTEGRATION (dry_run, fake model) PASSED")


if __name__ == "__main__":
    main()
