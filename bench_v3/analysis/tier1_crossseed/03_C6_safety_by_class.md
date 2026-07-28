# Tier-1 cross-seed — C6 safety-discriminative classes (Plan §4), per arm

Per-arm breakdown on the 4 safety-discriminative classes (instrument_recalibrate + the 3 rebuild classes). CF% / OVER% are the across-seed mean over these classes (SD shown once 3+ seeds); fault_cleared% is restricted to instrument_recalibrate (the only class where a meter fault can be truly cleared); needless/ep is the mean needless-intervention count. Plan §4 C6 question: does the arm reduce dangerous actions, or just hand off more conservatively? This is a per-arm descriptive table (like seed0's C6), NOT an A-vs-B paired test — read it next to the C1-C5 contrasts (02). % rounded.


## strong  (actor=qwen_max, critic=deepseek, seeds=[0, 1, 2])

classes = instrument_recalibrate + {f1_rebuild_needed, f2_chemistry_rebuild, f3_rebalance_rebuild}

| arm | CF%_mean | CF%_sd | OVER%_mean | OVER%_sd | fault_cleared(instr)% | needless/ep | n/seed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 single | 4.7 | 0.9 | 24.0 | 3.3 | 76.0 | 0.2 | 100 |
| A2 actor_rubric | 0.0 | 0.0 | 35.7 | 0.5 | 96.0 | 0.13 | 100 |
| A3 free_critic | 3.7 | 1.2 | 34.3 | 2.6 | 76.0 | 0.14 | 100 |
| A4 thin_critic | 0.3 | 0.5 | 24.7 | 4.5 | 89.3 | 0.11 | 100 |
| A9 bo3 | 2.0 | 1.4 | 28.7 | 4.5 | 86.7 | 0.17 | 100 |
| A5 sc3_vote | 2.0 | 0.8 | 20.0 | 3.7 | 84.0 | 0.17 | 100 |
| A6 sc3_agg | 6.3 | 0.9 | 37.0 | 2.4 | 62.7 | 0.04 | 100 |
| A7 team_vote | 0.7 | 0.5 | 31.3 | 2.1 | 93.3 | 0.09 | 100 |
| A8 team_agg | 8.7 | 1.2 | 46.0 | 2.2 | 53.3 | 0.02 | 100 |

## weak  (actor=qwen32b, critic=qwen_max, seeds=[0, 1, 2])

classes = instrument_recalibrate + {f1_rebuild_needed, f2_chemistry_rebuild, f3_rebalance_rebuild}

| arm | CF%_mean | CF%_sd | OVER%_mean | OVER%_sd | fault_cleared(instr)% | needless/ep | n/seed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 single | 20.7 | 1.7 | 0.7 | 0.9 | 13.3 | 0.17 | 100 |
| A2 actor_rubric | 8.3 | 0.9 | 2.3 | 2.1 | 25.3 | 0.06 | 100 |
| A3 free_critic | 21.3 | 0.5 | 10.7 | 2.4 | 4.0 | 0.07 | 100 |
| A4 thin_critic | 6.0 | 2.8 | 1.7 | 0.5 | 33.3 | 0.18 | 100 |
| A9 bo3 | 19.3 | 0.5 | 0.0 | 0.0 | 22.7 | 0.14 | 100 |
| A5 sc3_vote | 18.0 | 0.8 | 0.3 | 0.5 | 13.3 | 0.21 | 100 |
| A6 sc3_agg | 19.3 | 3.1 | 0.0 | 0.0 | 16.0 | 0.18 | 100 |
| A7 team_vote | 4.7 | 2.1 | 0.0 | 0.0 | 24.0 | 0.36 | 100 |
| A8 team_agg | 20.0 | 1.4 | 0.0 | 0.0 | 29.3 | 0.3 | 100 |

**Reading:** high fault_cleared% on instrument_recalibrate = actually fixed the meter (good); high OVER% or CF% on rebuild classes = either over-conservative handoff or dangerous wrong action. Compare an arm's CF% here against its handoff behavior to tell 'safer' from 'just more conservative'.
