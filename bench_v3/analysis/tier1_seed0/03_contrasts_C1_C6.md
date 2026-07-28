# Tier-1 seed0 — C1–C6 Pre-registered Contrasts (Plan §4)

Paired: same instance/seed/model-group. seed0 = **descriptive only** (no CI / significance until multi-seed). All % rounded.


## strong  (actor=qwen_max, critic=deepseek)

### C1 — actor_rubric (A2) vs single (A1): does rubric-in-actor help?
| arm | SUCC% | CF% | OVER% | n |
| --- | --- | --- | --- | --- |
| A1 single | 77 | 1 | 9 | 275 |
| A2 actor_rubric | 79 | 0 | 14 | 275 |
Δ SUCC = +2 pp,  Δ CF = -1 pp.  (class-level: see 02_outcome_by_class.md)

### C2 — free_critic (A3) vs single (A1): value of a rubric-less external critic?
| arm | SUCC% | CF% | OVER% | calls/ep | tokens/ep | n |
| --- | --- | --- | --- | --- | --- | --- |
| A1 single | 77 | 1 | 9 | 5.8 | 15161.7 | 275 |
| A3 free_critic | 76 | 1 | 13 | 11.3 | 22777.5 | 275 |
Δ SUCC = -1 pp,  Δ CF = +0 pp.

### C3 — thin_critic (A4) vs free_critic (A3) and vs actor_rubric (A2): where does the rubric work best?
| arm | SUCC% | CF% | OVER% | fault_cleared(instr) | needless/ep | n |
| --- | --- | --- | --- | --- | --- | --- |
| A2 actor_rubric | 79 | 0 | 14 | 92% (23/25) | 0.19 | 275 |
| A3 free_critic | 76 | 1 | 13 | 92% (23/25) | 0.26 | 275 |
| A4 thin_critic | 74 | 0 | 10 | 96% (24/25) | 0.25 | 275 |

### C4 — 2×2 (proposer: sampling vs personas) × (selector: vote vs aggregator)
| arm | SUCC% | CF% | OVER% | rebuild SUCC% | rebuild CF% | rebuild OVER% | n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A5 sc3_vote | 78 | 1 | 8 | 44 | 0 | 28 | 275 |
| A6 sc3_agg | 81 | 3 | 15 | 44 | 0 | 53 | 275 |
| A7 team_vote | 79 | 0 | 13 | 40 | 0 | 45 | 275 |
| A8 team_agg | 77 | 4 | 19 | 36 | 0 | 64 | 275 |

SUCC% main effects — selector(agg−vote): sc3 +3, team -2; proposer(team−sc3): vote +1, agg -4.
(rebuild SUCC/CF/OVER = aggregate over f1_rebuild_needed, f2_chemistry_rebuild, f3_rebalance_rebuild)

### C5 — bo3 (A9, ~3× compute) vs single (A1) and vs 2×2
| arm | SUCC% | CF% | OVER% | calls/ep | tokens/ep | n |
| --- | --- | --- | --- | --- | --- | --- |
| A1 single | 77 | 1 | 9 | 5.8 | 15161.7 | 275 |
| A9 bo3 | 89 | 0 | 11 | 17.3 | 45168.5 | 275 |
| A5 sc3_vote | 78 | 1 | 8 | 17.1 | 44702.2 | 275 |
| A6 sc3_agg | 81 | 3 | 15 | 20.5 | 45648.7 | 275 |
| A7 team_vote | 79 | 0 | 13 | 17.4 | 48303.4 | 275 |
| A8 team_agg | 77 | 4 | 19 | 19.5 | 44386.0 | 275 |
(bo3 is a compute control, not a low-cost improvement.)

### C6 — safety-discriminative classes (per arm): CF%, OVER%, fault_cleared, needless
| arm | CF% | OVER% | fault_cleared(instr) | needless/ep | n |
| --- | --- | --- | --- | --- | --- |
| A1 single | 4 | 24 | 84% (21/25) | 0.26 | 100 |
| A2 actor_rubric | 0 | 36 | 92% (23/25) | 0.1 | 100 |
| A3 free_critic | 2 | 33 | 92% (23/25) | 0.2 | 100 |
| A4 thin_critic | 0 | 25 | 96% (24/25) | 0.14 | 100 |
| A9 bo3 | 1 | 29 | 96% (24/25) | 0.2 | 100 |
| A5 sc3_vote | 2 | 21 | 84% (21/25) | 0.24 | 100 |
| A6 sc3_agg | 7 | 40 | 64% (16/25) | 0.06 | 100 |
| A7 team_vote | 1 | 34 | 96% (24/25) | 0.12 | 100 |
| A8 team_agg | 10 | 49 | 52% (13/25) | 0.02 | 100 |
(classes = instrument_recalibrate + the three rebuild classes)


## weak  (actor=qwen32b, critic=qwen_max)

### C1 — actor_rubric (A2) vs single (A1): does rubric-in-actor help?
| arm | SUCC% | CF% | OVER% | n |
| --- | --- | --- | --- | --- |
| A1 single | 0 | 9 | 0 | 275 |
| A2 actor_rubric | 20 | 6 | 1 | 275 |
Δ SUCC = +20 pp,  Δ CF = -3 pp.  (class-level: see 02_outcome_by_class.md)

### C2 — free_critic (A3) vs single (A1): value of a rubric-less external critic?
| arm | SUCC% | CF% | OVER% | calls/ep | tokens/ep | n |
| --- | --- | --- | --- | --- | --- | --- |
| A1 single | 0 | 9 | 0 | 8.0 | 8377.6 | 275 |
| A3 free_critic | 54 | 11 | 5 | 13.6 | 16092.8 | 275 |
Δ SUCC = +54 pp,  Δ CF = +2 pp.

### C3 — thin_critic (A4) vs free_critic (A3) and vs actor_rubric (A2): where does the rubric work best?
| arm | SUCC% | CF% | OVER% | fault_cleared(instr) | needless/ep | n |
| --- | --- | --- | --- | --- | --- | --- |
| A2 actor_rubric | 20 | 6 | 1 | 24% (6/25) | 0.04 | 275 |
| A3 free_critic | 54 | 11 | 5 | 4% (1/25) | 0.03 | 275 |
| A4 thin_critic | 44 | 6 | 1 | 28% (7/25) | 0.2 | 275 |

### C4 — 2×2 (proposer: sampling vs personas) × (selector: vote vs aggregator)
| arm | SUCC% | CF% | OVER% | rebuild SUCC% | rebuild CF% | rebuild OVER% | n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A5 sc3_vote | 0 | 8 | 0 | 0 | 0 | 1 | 275 |
| A6 sc3_agg | 2 | 7 | 0 | 0 | 0 | 0 | 275 |
| A7 team_vote | 0 | 3 | 0 | 0 | 0 | 0 | 275 |
| A8 team_agg | 26 | 12 | 0 | 0 | 0 | 0 | 275 |

SUCC% main effects — selector(agg−vote): sc3 +2, team +26; proposer(team−sc3): vote +0, agg +24.
(rebuild SUCC/CF/OVER = aggregate over f1_rebuild_needed, f2_chemistry_rebuild, f3_rebalance_rebuild)

### C5 — bo3 (A9, ~3× compute) vs single (A1) and vs 2×2
| arm | SUCC% | CF% | OVER% | calls/ep | tokens/ep | n |
| --- | --- | --- | --- | --- | --- | --- |
| A1 single | 0 | 9 | 0 | 8.0 | 8377.6 | 275 |
| A9 bo3 | 0 | 9 | 0 | 24.0 | 25243.3 | 275 |
| A5 sc3_vote | 0 | 8 | 0 | 24.0 | 25153.5 | 275 |
| A6 sc3_agg | 2 | 7 | 0 | 31.7 | 31265.2 | 275 |
| A7 team_vote | 0 | 3 | 0 | 24 | 26282.0 | 275 |
| A8 team_agg | 26 | 12 | 0 | 26.6 | 26756.0 | 275 |
(bo3 is a compute control, not a low-cost improvement.)

### C6 — safety-discriminative classes (per arm): CF%, OVER%, fault_cleared, needless
| arm | CF% | OVER% | fault_cleared(instr) | needless/ep | n |
| --- | --- | --- | --- | --- | --- |
| A1 single | 19 | 0 | 20% (5/25) | 0.26 | 100 |
| A2 actor_rubric | 9 | 2 | 24% (6/25) | 0.07 | 100 |
| A3 free_critic | 21 | 14 | 4% (1/25) | 0.05 | 100 |
| A4 thin_critic | 8 | 2 | 28% (7/25) | 0.22 | 100 |
| A9 bo3 | 20 | 0 | 20% (5/25) | 0.11 | 100 |
| A5 sc3_vote | 18 | 1 | 16% (4/25) | 0.24 | 100 |
| A6 sc3_agg | 15 | 0 | 20% (5/25) | 0.26 | 100 |
| A7 team_vote | 7 | 0 | 20% (5/25) | 0.39 | 100 |
| A8 team_agg | 19 | 0 | 32% (8/25) | 0.3 | 100 |
(classes = instrument_recalibrate + the three rebuild classes)

