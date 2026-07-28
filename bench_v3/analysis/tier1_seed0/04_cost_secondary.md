# Tier-1 seed0 — Cost & Secondary Safety Metrics (Plan §5–§6)


## strong  (actor=qwen_max, critic=deepseek)

### Cost per episode (§6)
| arm | actor_calls/ep | critic_calls/ep | total_calls/ep | actor_tok/ep | critic_tok/ep | total_tok/ep |
| --- | --- | --- | --- | --- | --- | --- |
| A1 single | 5.8 | 0 | 5.8 | 15161.7 | 0 | 15161.7 |
| A2 actor_rubric | 6.1 | 0 | 6.1 | 17232.7 | 0 | 17232.7 |
| A3 free_critic | 5.8 | 5.6 | 11.4 | 15354.3 | 7423.2 | 22777.5 |
| A4 thin_critic | 7.4 | 6.3 | 13.7 | 18589.0 | 12638.5 | 31227.5 |
| A9 bo3 | 17.3 | 0 | 17.3 | 45168.5 | 0 | 45168.5 |
| A5 sc3_vote | 17.1 | 0 | 17.1 | 44702.2 | 0 | 44702.2 |
| A6 sc3_agg | 20.5 | 0 | 20.5 | 45648.7 | 0 | 45648.7 |
| A7 team_vote | 17.4 | 0 | 17.4 | 48303.4 | 0 | 48303.4 |
| A8 team_agg | 19.5 | 0 | 19.5 | 44386.0 | 0 | 44386.0 |

### needless_interventions (§5): total / per-ep, by class
| arm | 1·no_fault | 1·top_up_feasible | 1·dilute_feasible | 1·rebuild_needed | 2·no_fault | 2·instrument_recalibrate | 2·chemistry_recoverable | 2·chemistry_rebuild | 3·no_fault | 3·rebalance_feasible | 3·rebalance_rebuild | all/ep |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 single | 0 | 13 | 18 | 9 | 2 | 0 | 14 | 6 | 0 | 10 | 11 | 0.3 |
| A2 actor_rubric | 1 | 8 | 14 | 3 | 1 | 0 | 8 | 5 | 2 | 8 | 2 | 0.19 |
| A3 free_critic | 0 | 11 | 20 | 9 | 1 | 0 | 13 | 7 | 1 | 5 | 4 | 0.26 |
| A4 thin_critic | 4 | 10 | 17 | 8 | 3 | 0 | 12 | 5 | 2 | 8 | 1 | 0.25 |
| A9 bo3 | 3 | 6 | 20 | 8 | 2 | 0 | 10 | 12 | 2 | 6 | 0 | 0.25 |
| A5 sc3_vote | 0 | 10 | 18 | 13 | 0 | 0 | 15 | 5 | 0 | 6 | 6 | 0.27 |
| A6 sc3_agg | 0 | 3 | 7 | 2 | 0 | 0 | 4 | 4 | 0 | 0 | 0 | 0.07 |
| A7 team_vote | 0 | 15 | 20 | 5 | 0 | 0 | 14 | 6 | 0 | 5 | 1 | 0.24 |
| A8 team_agg | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0.01 |

### CRITICAL_FAIL by cf_reason (§5)
| arm | CF total | a_accept_out_of_tol | c_quarantine_accurate | d_discard_in_tol | e_broke_good |
| --- | --- | --- | --- | --- | --- |
| A1 single | 4 | 0 | 1 | 0 | 3 |
| A2 actor_rubric | 0 | 0 | 0 | 0 | 0 |
| A3 free_critic | 2 | 0 | 0 | 0 | 2 |
| A4 thin_critic | 0 | 0 | 0 | 0 | 0 |
| A9 bo3 | 1 | 0 | 0 | 0 | 1 |
| A5 sc3_vote | 2 | 0 | 0 | 0 | 2 |
| A6 sc3_agg | 7 | 0 | 0 | 0 | 7 |
| A7 team_vote | 1 | 0 | 0 | 0 | 1 |
| A8 team_agg | 10 | 0 | 0 | 0 | 10 |

## weak  (actor=qwen32b, critic=qwen_max)

### Cost per episode (§6)
| arm | actor_calls/ep | critic_calls/ep | total_calls/ep | actor_tok/ep | critic_tok/ep | total_tok/ep |
| --- | --- | --- | --- | --- | --- | --- |
| A1 single | 8.0 | 0 | 8.0 | 8377.6 | 0 | 8377.6 |
| A2 actor_rubric | 7.8 | 0 | 7.8 | 9813.8 | 0 | 9813.8 |
| A3 free_critic | 8.4 | 5.3 | 13.7 | 8594.5 | 7498.3 | 16092.8 |
| A4 thin_critic | 10.3 | 6.1 | 16.4 | 10832.1 | 13050.5 | 23882.6 |
| A9 bo3 | 24.0 | 0 | 24.0 | 25243.3 | 0 | 25243.3 |
| A5 sc3_vote | 24.0 | 0 | 24.0 | 25153.5 | 0 | 25153.5 |
| A6 sc3_agg | 31.7 | 0 | 31.7 | 31265.2 | 0 | 31265.2 |
| A7 team_vote | 24 | 0 | 24 | 26282.0 | 0 | 26282.0 |
| A8 team_agg | 26.6 | 0 | 26.6 | 26756.0 | 0 | 26756.0 |

### needless_interventions (§5): total / per-ep, by class
| arm | 1·no_fault | 1·top_up_feasible | 1·dilute_feasible | 1·rebuild_needed | 2·no_fault | 2·instrument_recalibrate | 2·chemistry_recoverable | 2·chemistry_rebuild | 3·no_fault | 3·rebalance_feasible | 3·rebalance_rebuild | all/ep |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 single | 23 | 1 | 14 | 6 | 18 | 0 | 4 | 5 | 20 | 3 | 15 | 0.4 |
| A2 actor_rubric | 0 | 1 | 2 | 0 | 0 | 5 | 0 | 1 | 1 | 0 | 1 | 0.04 |
| A3 free_critic | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 3 | 0.03 |
| A4 thin_critic | 1 | 5 | 6 | 6 | 0 | 3 | 12 | 7 | 0 | 9 | 6 | 0.2 |
| A9 bo3 | 17 | 1 | 7 | 4 | 12 | 0 | 4 | 3 | 14 | 0 | 4 | 0.24 |
| A5 sc3_vote | 16 | 0 | 10 | 8 | 16 | 0 | 4 | 5 | 17 | 3 | 11 | 0.33 |
| A6 sc3_agg | 16 | 0 | 11 | 6 | 20 | 0 | 3 | 8 | 17 | 2 | 12 | 0.35 |
| A7 team_vote | 7 | 4 | 8 | 12 | 8 | 0 | 4 | 11 | 11 | 6 | 16 | 0.32 |
| A8 team_agg | 1 | 1 | 8 | 11 | 2 | 0 | 5 | 10 | 3 | 2 | 9 | 0.19 |

### CRITICAL_FAIL by cf_reason (§5)
| arm | CF total | a_accept_out_of_tol | c_quarantine_accurate | d_discard_in_tol | e_broke_good |
| --- | --- | --- | --- | --- | --- |
| A1 single | 26 | 0 | 0 | 4 | 22 |
| A2 actor_rubric | 16 | 8 | 0 | 5 | 3 |
| A3 free_critic | 29 | 6 | 0 | 0 | 23 |
| A4 thin_critic | 16 | 6 | 0 | 5 | 5 |
| A9 bo3 | 24 | 0 | 0 | 1 | 23 |
| A5 sc3_vote | 23 | 0 | 0 | 2 | 21 |
| A6 sc3_agg | 19 | 0 | 0 | 0 | 19 |
| A7 team_vote | 7 | 0 | 0 | 0 | 7 |
| A8 team_agg | 32 | 4 | 0 | 0 | 28 |
