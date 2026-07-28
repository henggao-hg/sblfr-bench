# Tier-1 cross-seed — Outcome per arm, by seed + mean (Plan §2/§9)

Each cell = SUCC% / CF% per seed, then across-seed mean and SD (SD shown once 3+ seeds). SD is the spread *across seeds* (a stability read); significance still comes from the paired McNemar tests (02_contrasts), not from this SD. % rounded.


## strong  (actor=qwen_max, critic=deepseek, seeds=[0, 1, 2])

| arm | SUCC%_s0 | SUCC%_s1 | SUCC%_s2 | SUCC%_mean | SUCC%_sd | CF%_s0 | CF%_s1 | CF%_s2 | CF%_mean | CF%_sd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 single | 77.1 | 76.4 | 79.3 | 77.6 | 1.2 | 1.5 | 2.2 | 1.5 | 1.7 | 0.3 |
| A2 actor_rubric | 78.9 | 80.4 | 79.3 | 79.5 | 0.6 | 0.0 | 0.4 | 0.4 | 0.3 | 0.2 |
| A3 free_critic | 75.6 | 75.6 | 77.8 | 76.3 | 1.0 | 0.7 | 1.5 | 2.2 | 1.5 | 0.6 |
| A4 thin_critic | 73.8 | 71.6 | 81.8 | 75.7 | 4.4 | 0.0 | 0.4 | 0.4 | 0.3 | 0.2 |
| A9 bo3 | 88.7 | 85.5 | 91.3 | 88.5 | 2.4 | 0.4 | 1.5 | 0.4 | 0.8 | 0.5 |
| A5 sc3_vote | 78.2 | 78.2 | 82.2 | 79.5 | 1.9 | 0.7 | 1.1 | 0.4 | 0.7 | 0.3 |
| A6 sc3_agg | 80.7 | 81.8 | 82.2 | 81.6 | 0.6 | 2.5 | 1.8 | 2.5 | 2.3 | 0.3 |
| A7 team_vote | 78.5 | 82.2 | 81.1 | 80.6 | 1.6 | 0.4 | 0.4 | 0.0 | 0.3 | 0.2 |
| A8 team_agg | 77.1 | 80.7 | 78.9 | 78.9 | 1.5 | 3.6 | 2.5 | 3.3 | 3.1 | 0.5 |

## weak  (actor=qwen32b, critic=qwen_max, seeds=[0, 1, 2])

| arm | SUCC%_s0 | SUCC%_s1 | SUCC%_s2 | SUCC%_mean | SUCC%_sd | CF%_s0 | CF%_s1 | CF%_s2 | CF%_mean | CF%_sd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 single | 0.4 | 0.7 | 0.4 | 0.5 | 0.1 | 9.5 | 13.5 | 11.6 | 11.5 | 1.6 |
| A2 actor_rubric | 20.4 | 22.2 | 18.5 | 20.4 | 1.5 | 5.8 | 6.2 | 5.8 | 5.9 | 0.2 |
| A3 free_critic | 54.2 | 53.5 | 52.4 | 53.4 | 0.7 | 10.5 | 9.8 | 8.4 | 9.6 | 0.9 |
| A4 thin_critic | 44.4 | 48.7 | 49.1 | 47.4 | 2.1 | 5.8 | 6.9 | 1.8 | 4.8 | 2.2 |
| A9 bo3 | 0.4 | 0.4 | 0.7 | 0.5 | 0.1 | 8.7 | 12.0 | 8.7 | 9.8 | 1.6 |
| A5 sc3_vote | 0.4 | 0.0 | 0.0 | 0.1 | 0.2 | 8.4 | 12.0 | 9.5 | 10.0 | 1.5 |
| A6 sc3_agg | 1.8 | 1.5 | 0.7 | 1.3 | 0.5 | 6.9 | 15.6 | 10.2 | 10.9 | 3.6 |
| A7 team_vote | 0.0 | 0.4 | 0.0 | 0.1 | 0.2 | 2.5 | 0.7 | 1.8 | 1.7 | 0.7 |
| A8 team_agg | 26.2 | 26.9 | 20.4 | 24.5 | 2.9 | 11.6 | 12.4 | 12.0 | 12.0 | 0.3 |
