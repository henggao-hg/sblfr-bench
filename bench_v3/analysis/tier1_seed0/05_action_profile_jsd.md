# Tier-1 seed0 — Action Profile / JSD (Plan §7, MECHANISM ONLY)

Not a success metric. JSD vs single only meaningful ABOVE the single self-split noise floor.


## strong  (actor=qwen_max, critic=deepseek)  — single self-split noise floor JSD = 0.001

### group_share (step-weighted, 6 groups)
| arm | MEASURE_BATCH | VERIFY_ANCHOR | CALIBRATE | CORRECT_IN_PLACE | REBUILD_OR_ISOLATE | TERMINAL |
| --- | --- | --- | --- | --- | --- | --- |
| A1 single | 0.429 | 0.184 | 0.066 | 0.133 | 0.037 | 0.151 |
| A2 actor_rubric | 0.407 | 0.242 | 0.045 | 0.114 | 0.04 | 0.152 |
| A3 free_critic | 0.435 | 0.184 | 0.061 | 0.125 | 0.035 | 0.16 |
| A4 thin_critic | 0.387 | 0.273 | 0.055 | 0.119 | 0.034 | 0.132 |
| A9 bo3 | 0.433 | 0.173 | 0.059 | 0.127 | 0.034 | 0.174 |
| A5 sc3_vote | 0.433 | 0.177 | 0.06 | 0.138 | 0.04 | 0.152 |
| A6 sc3_agg | 0.479 | 0.131 | 0.026 | 0.136 | 0.038 | 0.192 |
| A7 team_vote | 0.442 | 0.193 | 0.057 | 0.118 | 0.032 | 0.159 |
| A8 team_agg | 0.517 | 0.107 | 0.013 | 0.128 | 0.03 | 0.205 |

### incidence (% episodes doing each action ≥once)
| arm | std_check% | recal% | discard% | inplace% | handoff% | accept% |
| --- | --- | --- | --- | --- | --- | --- |
| A1 single | 69 | 38 | 20 | 56 | 9 | 78 |
| A2 actor_rubric | 100 | 27 | 24 | 52 | 14 | 79 |
| A3 free_critic | 65 | 34 | 19 | 53 | 13 | 76 |
| A4 thin_critic | 100 | 35 | 21 | 55 | 10 | 74 |
| A9 bo3 | 71 | 34 | 20 | 54 | 11 | 89 |
| A5 sc3_vote | 67 | 34 | 23 | 57 | 8 | 79 |
| A6 sc3_agg | 52 | 13 | 19 | 53 | 15 | 83 |
| A7 team_vote | 70 | 33 | 19 | 51 | 13 | 79 |
| A8 team_agg | 45 | 6 | 15 | 51 | 20 | 80 |

### JSD vs single (overall)
| arm | JSD vs single | above floor? |
| --- | --- | --- |
| A2 actor_rubric | 0.005 | yes |
| A3 free_critic | 0.0 | no |
| A4 thin_critic | 0.008 | yes |
| A9 bo3 | 0.001 | no |
| A5 sc3_vote | 0.0 | no |
| A6 sc3_agg | 0.013 | yes |
| A7 team_vote | 0.001 | no |
| A8 team_agg | 0.028 | yes |

### JSD vs single by class (discriminative classes) + behavior incidences
| arm | class | JSD vs single | discard% | handoff% | std_check% | recal% |
| --- | --- | --- | --- | --- | --- | --- |
| A2 actor_rubric | f2_instrument_recalibrate | 0.03 | 0 | 0 | 100 | 92 |
| A2 actor_rubric | f1_rebuild_needed | 0.007 | 84 | 64 | 100 | 12 |
| A2 actor_rubric | f2_chemistry_rebuild | 0.003 | 80 | 56 | 100 | 20 |
| A2 actor_rubric | f3_rebalance_rebuild | 0.014 | 92 | 24 | 100 | 8 |
| A3 free_critic | f2_instrument_recalibrate | 0.002 | 0 | 0 | 92 | 92 |
| A3 free_critic | f1_rebuild_needed | 0.002 | 56 | 60 | 100 | 36 |
| A3 free_critic | f2_chemistry_rebuild | 0.002 | 60 | 52 | 100 | 28 |
| A3 free_critic | f3_rebalance_rebuild | 0.007 | 92 | 20 | 72 | 16 |
| A4 thin_critic | f2_instrument_recalibrate | 0.01 | 0 | 0 | 100 | 100 |
| A4 thin_critic | f1_rebuild_needed | 0.003 | 60 | 48 | 100 | 32 |
| A4 thin_critic | f2_chemistry_rebuild | 0.002 | 60 | 52 | 100 | 20 |
| A4 thin_critic | f3_rebalance_rebuild | 0.019 | 100 | 0 | 100 | 4 |
| A9 bo3 | f2_instrument_recalibrate | 0.005 | 0 | 0 | 96 | 96 |
| A9 bo3 | f1_rebuild_needed | 0.003 | 60 | 44 | 100 | 32 |
| A9 bo3 | f2_chemistry_rebuild | 0.017 | 40 | 72 | 100 | 48 |
| A9 bo3 | f3_rebalance_rebuild | 0.036 | 100 | 0 | 72 | 0 |
| A5 sc3_vote | f2_instrument_recalibrate | 0.002 | 0 | 0 | 84 | 84 |
| A5 sc3_vote | f1_rebuild_needed | 0.005 | 56 | 48 | 100 | 52 |
| A5 sc3_vote | f2_chemistry_rebuild | 0.005 | 84 | 24 | 100 | 20 |
| A5 sc3_vote | f3_rebalance_rebuild | 0.004 | 92 | 12 | 92 | 24 |
| A6 sc3_agg | f2_instrument_recalibrate | 0.02 | 0 | 0 | 64 | 64 |
| A6 sc3_agg | f1_rebuild_needed | 0.018 | 44 | 76 | 96 | 8 |
| A6 sc3_agg | f2_chemistry_rebuild | 0.015 | 52 | 84 | 100 | 16 |
| A6 sc3_agg | f3_rebalance_rebuild | 0.036 | 100 | 0 | 72 | 0 |
| A7 team_vote | f2_instrument_recalibrate | 0.005 | 0 | 0 | 96 | 96 |
| A7 team_vote | f1_rebuild_needed | 0.016 | 40 | 72 | 100 | 20 |
| A7 team_vote | f2_chemistry_rebuild | 0.005 | 48 | 64 | 100 | 24 |
| A7 team_vote | f3_rebalance_rebuild | 0.019 | 100 | 0 | 100 | 4 |
| A8 team_agg | f2_instrument_recalibrate | 0.046 | 0 | 8 | 56 | 52 |
| A8 team_agg | f1_rebuild_needed | 0.076 | 24 | 96 | 100 | 0 |
| A8 team_agg | f2_chemistry_rebuild | 0.032 | 40 | 88 | 100 | 8 |
| A8 team_agg | f3_rebalance_rebuild | 0.047 | 92 | 8 | 44 | 0 |

## weak  (actor=qwen32b, critic=qwen_max)  — single self-split noise floor JSD = 0.001

### group_share (step-weighted, 6 groups)
| arm | MEASURE_BATCH | VERIFY_ANCHOR | CALIBRATE | CORRECT_IN_PLACE | REBUILD_OR_ISOLATE | TERMINAL |
| --- | --- | --- | --- | --- | --- | --- |
| A1 single | 0.692 | 0.107 | 0.055 | 0.143 | 0.002 | 0.0 |
| A2 actor_rubric | 0.617 | 0.283 | 0.006 | 0.033 | 0.029 | 0.032 |
| A3 free_critic | 0.558 | 0.05 | 0.008 | 0.225 | 0.012 | 0.147 |
| A4 thin_critic | 0.434 | 0.202 | 0.038 | 0.171 | 0.073 | 0.083 |
| A9 bo3 | 0.739 | 0.093 | 0.036 | 0.13 | 0.001 | 0.0 |
| A5 sc3_vote | 0.738 | 0.089 | 0.046 | 0.125 | 0.001 | 0.001 |
| A6 sc3_agg | 0.709 | 0.093 | 0.05 | 0.146 | 0.0 | 0.002 |
| A7 team_vote | 0.824 | 0.12 | 0.043 | 0.013 | 0.0 | 0.0 |
| A8 team_agg | 0.652 | 0.101 | 0.037 | 0.164 | 0.0 | 0.047 |

### incidence (% episodes doing each action ≥once)
| arm | std_check% | recal% | discard% | inplace% | handoff% | accept% |
| --- | --- | --- | --- | --- | --- | --- |
| A1 single | 55 | 40 | 2 | 66 | 0 | 0 |
| A2 actor_rubric | 100 | 4 | 22 | 22 | 1 | 23 |
| A3 free_critic | 16 | 4 | 5 | 69 | 7 | 61 |
| A4 thin_critic | 77 | 22 | 40 | 59 | 1 | 47 |
| A9 bo3 | 48 | 27 | 1 | 61 | 0 | 0 |
| A5 sc3_vote | 48 | 34 | 1 | 62 | 0 | 0 |
| A6 sc3_agg | 50 | 37 | 0 | 63 | 0 | 2 |
| A7 team_vote | 64 | 34 | 0 | 11 | 0 | 0 |
| A8 team_agg | 36 | 22 | 0 | 58 | 0 | 28 |

### JSD vs single (overall)
| arm | JSD vs single | above floor? |
| --- | --- | --- |
| A2 actor_rubric | 0.098 | yes |
| A3 free_critic | 0.107 | yes |
| A4 thin_critic | 0.103 | yes |
| A9 bo3 | 0.003 | yes |
| A5 sc3_vote | 0.002 | yes |
| A6 sc3_agg | 0.002 | yes |
| A7 team_vote | 0.052 | yes |
| A8 team_agg | 0.025 | yes |

### JSD vs single by class (discriminative classes) + behavior incidences
| arm | class | JSD vs single | discard% | handoff% | std_check% | recal% |
| --- | --- | --- | --- | --- | --- | --- |
| A2 actor_rubric | f2_instrument_recalibrate | 0.158 | 20 | 0 | 100 | 24 |
| A2 actor_rubric | f1_rebuild_needed | 0.17 | 72 | 4 | 100 | 0 |
| A2 actor_rubric | f2_chemistry_rebuild | 0.13 | 56 | 4 | 100 | 4 |
| A2 actor_rubric | f3_rebalance_rebuild | 0.133 | 80 | 0 | 100 | 4 |
| A3 free_critic | f2_instrument_recalibrate | 0.117 | 4 | 16 | 8 | 4 |
| A3 free_critic | f1_rebuild_needed | 0.046 | 12 | 28 | 36 | 8 |
| A3 free_critic | f2_chemistry_rebuild | 0.045 | 12 | 12 | 36 | 0 |
| A3 free_critic | f3_rebalance_rebuild | 0.048 | 16 | 16 | 52 | 12 |
| A4 thin_critic | f2_instrument_recalibrate | 0.202 | 16 | 0 | 92 | 40 |
| A4 thin_critic | f1_rebuild_needed | 0.121 | 96 | 0 | 100 | 24 |
| A4 thin_critic | f2_chemistry_rebuild | 0.12 | 88 | 4 | 100 | 28 |
| A4 thin_critic | f3_rebalance_rebuild | 0.098 | 88 | 4 | 100 | 24 |
| A9 bo3 | f2_instrument_recalibrate | 0.001 | 0 | 0 | 36 | 32 |
| A9 bo3 | f1_rebuild_needed | 0.002 | 0 | 0 | 56 | 16 |
| A9 bo3 | f2_chemistry_rebuild | 0.004 | 0 | 0 | 68 | 12 |
| A9 bo3 | f3_rebalance_rebuild | 0.025 | 4 | 0 | 56 | 16 |
| A5 sc3_vote | f2_instrument_recalibrate | 0.004 | 0 | 0 | 20 | 20 |
| A5 sc3_vote | f1_rebuild_needed | 0.002 | 0 | 0 | 60 | 32 |
| A5 sc3_vote | f2_chemistry_rebuild | 0.006 | 0 | 4 | 52 | 20 |
| A5 sc3_vote | f3_rebalance_rebuild | 0.005 | 4 | 0 | 72 | 44 |
| A6 sc3_agg | f2_instrument_recalibrate | 0.003 | 0 | 0 | 28 | 28 |
| A6 sc3_agg | f1_rebuild_needed | 0.0 | 0 | 0 | 48 | 24 |
| A6 sc3_agg | f2_chemistry_rebuild | 0.002 | 0 | 0 | 48 | 32 |
| A6 sc3_agg | f3_rebalance_rebuild | 0.003 | 0 | 0 | 60 | 48 |
| A7 team_vote | f2_instrument_recalibrate | 0.043 | 0 | 0 | 40 | 28 |
| A7 team_vote | f1_rebuild_needed | 0.104 | 0 | 0 | 76 | 48 |
| A7 team_vote | f2_chemistry_rebuild | 0.105 | 0 | 0 | 88 | 44 |
| A7 team_vote | f3_rebalance_rebuild | 0.073 | 0 | 0 | 92 | 64 |
| A8 team_agg | f2_instrument_recalibrate | 0.013 | 0 | 0 | 48 | 36 |
| A8 team_agg | f1_rebuild_needed | 0.017 | 0 | 0 | 68 | 44 |
| A8 team_agg | f2_chemistry_rebuild | 0.012 | 0 | 0 | 52 | 40 |
| A8 team_agg | f3_rebalance_rebuild | 0.008 | 0 | 0 | 56 | 36 |
