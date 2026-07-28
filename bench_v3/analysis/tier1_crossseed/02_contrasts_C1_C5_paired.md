# Tier-1 cross-seed — C1–C5 paired contrasts (Plan §9)

Paired at the (seed, instance) level, pooled over all 3 seeds (so n_pairs = 3 x instances-in-both-arms). SUCCESS and CF tested SEPARATELY (never combined). McNemar = two-sided exact binomial on the discordant pairs (b = A-yes/B-no, c = A-no/B-yes). Δ = pooled A%−B%; CI = paired bootstrap 95% (2000 resamples, seed 0). sig = McNemar p<0.05.


## strong  (actor=qwen_max, critic=deepseek)


### SUCCESS
| contrast | A vs B | A SUCC% | B% | Δpp | boot95%CI | b(A>B) | c(B>A) | McNemar p | sig |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | A2 actor_rubric vs A1 single | 79.5 | 77.6 | +1.9 | [-1.1, +5.2] | 88 | 72 | 0.236 | no |
| C2 | A3 free_critic vs A1 single | 76.4 | 77.6 | -1.2 | [-4.0, +1.6] | 65 | 75 | 0.447 | no |
| C3a | A4 thin_critic vs A3 free_critic | 75.8 | 76.4 | -0.6 | [-3.4, +2.2] | 69 | 74 | 0.738 | no |
| C3b | A4 thin_critic vs A2 actor_rubric | 75.8 | 79.5 | -3.8 | [-6.5, -1.0] | 53 | 84 | 0.010 | yes |
| C4-sel-sc3 | A6 sc3_agg vs A5 sc3_vote | 81.6 | 79.5 | +2.1 | [-0.6, +4.6] | 68 | 51 | 0.142 | no |
| C4-sel-team | A8 team_agg vs A7 team_vote | 78.9 | 80.6 | -1.7 | [-4.0, +0.6] | 44 | 58 | 0.198 | no |
| C4-prop-vote | A7 team_vote vs A5 sc3_vote | 80.6 | 79.5 | +1.1 | [-1.7, +3.8] | 67 | 58 | 0.474 | no |
| C4-prop-agg | A8 team_agg vs A6 sc3_agg | 78.9 | 81.6 | -2.7 | [-4.6, -0.7] | 23 | 45 | 0.010 | yes |
| C5-vs-single | A9 bo3 vs A1 single | 88.5 | 77.6 | +10.9 | [+8.4, +13.5] | 108 | 18 | 7.9e-17 | yes |
| C5-vs-teamagg | A9 bo3 vs A8 team_agg | 88.5 | 78.9 | +9.6 | [+7.4, +11.9] | 90 | 11 | 1.4e-16 | yes |

### CRITICAL_FAIL
| contrast | A vs B | A CRIT% | B% | Δpp | boot95%CI | b(A>B) | c(B>A) | McNemar p | sig |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | A2 actor_rubric vs A1 single | 0.2 | 1.7 | -1.5 | [-2.4, -0.6] | 2 | 14 | 0.004 | yes |
| C2 | A3 free_critic vs A1 single | 1.5 | 1.7 | -0.2 | [-1.2, +0.6] | 6 | 8 | 0.791 | no |
| C3a | A4 thin_critic vs A3 free_critic | 0.2 | 1.5 | -1.2 | [-2.2, -0.4] | 2 | 12 | 0.013 | yes |
| C3b | A4 thin_critic vs A2 actor_rubric | 0.2 | 0.2 | +0.0 | [-0.5, +0.5] | 2 | 2 | 1.000 | no |
| C4-sel-sc3 | A6 sc3_agg vs A5 sc3_vote | 2.3 | 0.7 | +1.6 | [+0.8, +2.4] | 13 | 0 | 2.4e-04 | yes |
| C4-sel-team | A8 team_agg vs A7 team_vote | 3.2 | 0.2 | +2.9 | [+1.8, +4.1] | 25 | 1 | 8.0e-07 | yes |
| C4-prop-vote | A7 team_vote vs A5 sc3_vote | 0.2 | 0.7 | -0.5 | [-1.0, -0.1] | 0 | 4 | 0.125 | no |
| C4-prop-agg | A8 team_agg vs A6 sc3_agg | 3.2 | 2.3 | +0.8 | [-0.1, +1.8] | 12 | 5 | 0.143 | no |
| C5-vs-single | A9 bo3 vs A1 single | 0.7 | 1.7 | -1.0 | [-1.7, -0.4] | 1 | 9 | 0.021 | yes |
| C5-vs-teamagg | A9 bo3 vs A8 team_agg | 0.7 | 3.2 | -2.4 | [-3.6, -1.3] | 1 | 21 | 1.1e-05 | yes |


## weak  (actor=qwen32b, critic=qwen_max)


### SUCCESS
| contrast | A vs B | A SUCC% | B% | Δpp | boot95%CI | b(A>B) | c(B>A) | McNemar p | sig |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | A2 actor_rubric vs A1 single | 20.4 | 0.5 | +19.9 | [+17.2, +22.7] | 164 | 0 | 8.6e-50 | yes |
| C2 | A3 free_critic vs A1 single | 53.3 | 0.5 | +52.8 | [+49.5, +56.2] | 436 | 0 | 1.1e-131 | yes |
| C3a | A4 thin_critic vs A3 free_critic | 47.4 | 53.3 | -5.9 | [-9.3, -2.3] | 87 | 136 | 0.001 | yes |
| C3b | A4 thin_critic vs A2 actor_rubric | 47.4 | 20.4 | +27.0 | [+23.8, +30.3] | 230 | 7 | 7.1e-59 | yes |
| C4-sel-sc3 | A6 sc3_agg vs A5 sc3_vote | 1.3 | 0.1 | +1.2 | [+0.5, +2.1] | 11 | 1 | 0.006 | yes |
| C4-sel-team | A8 team_agg vs A7 team_vote | 24.5 | 0.1 | +24.4 | [+21.6, +27.3] | 201 | 0 | 6.2e-61 | yes |
| C4-prop-vote | A7 team_vote vs A5 sc3_vote | 0.1 | 0.1 | +0.0 | [-0.4, +0.4] | 1 | 1 | 1.000 | no |
| C4-prop-agg | A8 team_agg vs A6 sc3_agg | 24.5 | 1.3 | +23.2 | [+20.2, +26.1] | 194 | 3 | 1.3e-53 | yes |
| C5-vs-single | A9 bo3 vs A1 single | 0.5 | 0.5 | +0.0 | [-0.7, +0.7] | 4 | 4 | 1.000 | no |
| C5-vs-teamagg | A9 bo3 vs A8 team_agg | 0.5 | 24.5 | -24.0 | [-27.0, -21.2] | 0 | 198 | 5.0e-60 | yes |

### CRITICAL_FAIL
| contrast | A vs B | A CRIT% | B% | Δpp | boot95%CI | b(A>B) | c(B>A) | McNemar p | sig |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | A2 actor_rubric vs A1 single | 5.9 | 11.5 | -5.6 | [-7.9, -3.2] | 30 | 76 | 9.1e-06 | yes |
| C2 | A3 free_critic vs A1 single | 9.6 | 11.5 | -1.9 | [-4.0, +0.1] | 29 | 45 | 0.081 | no |
| C3a | A4 thin_critic vs A3 free_critic | 4.8 | 9.6 | -4.7 | [-6.9, -2.4] | 27 | 66 | 6.5e-05 | yes |
| C3b | A4 thin_critic vs A2 actor_rubric | 4.8 | 5.9 | -1.1 | [-3.0, +0.8] | 31 | 40 | 0.342 | no |
| C4-sel-sc3 | A6 sc3_agg vs A5 sc3_vote | 10.9 | 9.9 | +1.0 | [-1.0, +2.7] | 34 | 26 | 0.366 | no |
| C4-sel-team | A8 team_agg vs A7 team_vote | 12.0 | 1.7 | +10.3 | [+8.2, +12.5] | 86 | 1 | 1.1e-24 | yes |
| C4-prop-vote | A7 team_vote vs A5 sc3_vote | 1.7 | 9.9 | -8.2 | [-10.2, -6.4] | 1 | 69 | 1.2e-19 | yes |
| C4-prop-agg | A8 team_agg vs A6 sc3_agg | 12.0 | 10.9 | +1.1 | [-1.1, +3.3] | 47 | 38 | 0.386 | no |
| C5-vs-single | A9 bo3 vs A1 single | 9.8 | 11.5 | -1.7 | [-3.8, +0.4] | 28 | 42 | 0.120 | no |
| C5-vs-teamagg | A9 bo3 vs A8 team_agg | 9.8 | 12.0 | -2.2 | [-4.2, +0.0] | 30 | 48 | 0.054 | no |


**Reading:** a contrast is a real cross-seed effect only if McNemar sig=yes AND the bootstrap CI excludes 0. Δ is the effect size (pp). Question map:

- C1: rubric-in-actor vs single
- C2: rubric-less external critic vs single
- C3a: rubric-in-critic vs rubric-less critic
- C3b: rubric-in-critic vs rubric-in-actor
- C4-sel-sc3: selector: aggregator vs vote (sampling proposer)
- C4-sel-team: selector: aggregator vs vote (persona proposer)
- C4-prop-vote: proposer: personas vs sampling (vote selector)
- C4-prop-agg: proposer: personas vs sampling (aggregator selector)
- C5-vs-single: bo3 (3x compute) vs single
- C5-vs-teamagg: bo3 vs team_agg (equal-ish compute)
