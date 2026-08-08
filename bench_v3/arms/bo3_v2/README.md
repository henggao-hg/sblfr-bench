# bo3_v2

Corrected bo3 selector, run in parallel to the frozen v1 bo3. The frozen bo3
(`arms/base.py:visible_rank` plus the `runners/run_sweep.py` bo3 branch) is never
edited, so the v1 numbers stay attributable to the v1 bytes and both versions
remain auditable.

Difference from v1, the full selector spec (see `selector.py`):
1. The tie-break deviation uses only the last goal-vessel reading, not a stock or
   reference-standard reading.
2. A rollout with no vessel reading gets deviation infinity (no evidence it met
   the target, so it ranks last in a tie).
3. Exact ties are broken by the lowest rollout index (deterministic).

v2 also archives all three candidate rollouts in the transcript, so any future
re-selection needs no re-run.

Why it exists: the v1 tie-break did not distinguish the vessel reading from stock
or standard readings. See the SI audit note and the journal entry dated 2026-08-01
and the audit file `results/v3_crossmodel_strong_bo3_audit_seed0.jsonl`.

Outputs are prefixed `v3_bo3v2_`. Comparison against v1 lives in `analyze_bo3_v2.py`.
