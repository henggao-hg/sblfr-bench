# Tier-1 seed0 — Case Audit Index (Plan §8)

Curated candidate episodes for manual audit (max 3 per finding). Action sequence shown as motif; interpretation is left to the manual write-up (Plan §10: anecdotes only explain patterns already in the aggregate).


## strong team_agg OVER_CONSERVATIVE (aggregator biased to handoff?)
| model | arm | instance | outcome | cf_reason | motif | transcript |
| --- | --- | --- | --- | --- | --- | --- |
| strong | A8 team_agg | f1_rebuild_needed_00 | OVER_CONSERVATIVE | — | `Mv Mstd Mstk H` | v3_tier1_strong_seed0.transcript.jsonl:L2204 |
| strong | A8 team_agg | f2_chemistry_rebuild_00 | OVER_CONSERVATIVE | — | `Mv Mstk Mvol Mstd H` | v3_tier1_strong_seed0.transcript.jsonl:L2207 |
| strong | A8 team_agg | f1_rebuild_needed_01 | OVER_CONSERVATIVE | — | `Mv Mstd Mstk Mvol H` | v3_tier1_strong_seed0.transcript.jsonl:L2213 |

## weak CRITICAL_FAIL e_broke_good (corrective broke a good batch?)
| model | arm | instance | outcome | cf_reason | motif | transcript |
| --- | --- | --- | --- | --- | --- | --- |
| weak | A1 single | f2_instrument_recalibrate_00 | CRITICAL_FAIL | e_broke_good | `Mv T Mv Mv Mv Mv Mv Mv` | v3_tier1_weak_seed0.transcript.jsonl:L5 |
| weak | A1 single | f2_instrument_recalibrate_01 | CRITICAL_FAIL | e_broke_good | `Mv T Mv T Mv T Mv Mv` | v3_tier1_weak_seed0.transcript.jsonl:L14 |
| weak | A1 single | f2_instrument_recalibrate_02 | CRITICAL_FAIL | e_broke_good | `Mv T Mv Mv Mv D Mv` | v3_tier1_weak_seed0.transcript.jsonl:L23 |

## weak thin_critic — typical SUCCESS and non-SUCCESS
| model | arm | instance | outcome | cf_reason | motif | transcript |
| --- | --- | --- | --- | --- | --- | --- |
| weak | A4 thin_critic | f1_no_fault_00 | SUCCESS | — | `Mv Mstd R Mv A` | v3_tier1_weak_seed0.transcript.jsonl:L826 |
| weak | A4 thin_critic | f2_instrument_recalibrate_00 | SUCCESS | — | `Mv Mstd R Mv A` | v3_tier1_weak_seed0.transcript.jsonl:L830 |
| weak | A4 thin_critic | f1_top_up_feasible_00 | UNMANAGED | — | `Mv Mstd T Mv Mv R D Mv` | v3_tier1_weak_seed0.transcript.jsonl:L827 |

## bo3 typical SUCCESS (one of 3 runs went right?)
| model | arm | instance | outcome | cf_reason | motif | transcript |
| --- | --- | --- | --- | --- | --- | --- |
| strong | A9 bo3 | f1_no_fault_00 | SUCCESS | — | `Mv A` | v3_tier1_strong_seed0.transcript.jsonl:L1101 |
| strong | A9 bo3 | f1_top_up_feasible_00 | SUCCESS | — | `Mv Mstd Mstk T Mv A` | v3_tier1_strong_seed0.transcript.jsonl:L1102 |
| strong | A9 bo3 | f1_dilute_feasible_00 | SUCCESS | — | `Mv Mstd Mstd R Mv D Mv A` | v3_tier1_strong_seed0.transcript.jsonl:L1103 |
