# Tier-1 seed0 — 9-arm Outcome Tables (Plan §2)

Outcomes are the 4-tier ladder only. % rounded.

## strong  (actor=qwen_max, critic=deepseek)

| arm | SUCC% | CF% | OVER% | UNMA% | n | parse_fails | calls/ep | tokens/ep |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 single | 77 | 1 | 9 | 13 | 275 | 0 | 5.8 | 15161.7 |
| A2 actor_rubric | 79 | 0 | 14 | 7 | 275 | 0 | 6.1 | 17232.7 |
| A3 free_critic | 76 | 1 | 13 | 11 | 275 | 0 | 11.3 | 22777.5 |
| A4 thin_critic | 74 | 0 | 10 | 16 | 275 | 0 | 13.7 | 31227.4 |
| A9 bo3 | 89 | 0 | 11 | 0 | 275 | 0 | 17.3 | 45168.5 |
| A5 sc3_vote | 78 | 1 | 8 | 13 | 275 | 0 | 17.1 | 44702.2 |
| A6 sc3_agg | 81 | 3 | 15 | 2 | 275 | 0 | 20.5 | 45648.7 |
| A7 team_vote | 79 | 0 | 13 | 8 | 275 | 0 | 17.4 | 48303.4 |
| A8 team_agg | 77 | 4 | 19 | 0 | 275 | 0 | 19.5 | 44386.0 |

## weak  (actor=qwen32b, critic=qwen_max)

| arm | SUCC% | CF% | OVER% | UNMA% | n | parse_fails | calls/ep | tokens/ep |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 single | 0 | 9 | 0 | 90 | 275 | 0 | 8.0 | 8377.6 |
| A2 actor_rubric | 20 | 6 | 1 | 73 | 275 | 0 | 7.8 | 9813.8 |
| A3 free_critic | 54 | 11 | 5 | 30 | 275 | 0 | 13.6 | 16092.8 |
| A4 thin_critic | 44 | 6 | 1 | 49 | 275 | 0 | 16.4 | 23882.6 |
| A9 bo3 | 0 | 9 | 0 | 91 | 275 | 0 | 24.0 | 25243.3 |
| A5 sc3_vote | 0 | 8 | 0 | 91 | 275 | 0 | 24.0 | 25153.5 |
| A6 sc3_agg | 2 | 7 | 0 | 91 | 275 | 0 | 31.7 | 31265.2 |
| A7 team_vote | 0 | 3 | 0 | 97 | 275 | 0 | 24 | 26282.0 |
| A8 team_agg | 26 | 12 | 0 | 62 | 275 | 0 | 26.6 | 26756.0 |

