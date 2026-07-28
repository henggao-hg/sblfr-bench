# Tier-1 seed0 — Top trace motifs by (arm, class) (Plan §7)

Abbrev: Mv measure_conc · Mvol measure_vol · Msv measure_stock_vol · Mstk measure_stock_conc · Mstd measure_standard · R recalibrate · T transfer · D dilute · X discard · Q quarantine · A accept · H handoff. Top-3 motifs per cell (count).


## strong  (actor=qwen_max, critic=deepseek)


**f1_no_fault**
- A1 single: `Mv A`×25
- A2 actor_rubric: `Mstd Mv A`×14  |  `Mstd Mstd Mv A`×4  |  `Mv Mstd A`×4
- A3 free_critic: `Mv A`×25
- A4 thin_critic: `Mv Mstd Mstd A`×13  |  `Mv Mstd A`×8  |  `Mv Mstd Mstd R Mv A`×4
- A9 bo3: `Mv A`×22  |  `Mstd Mstd R Mv A`×3
- A5 sc3_vote: `Mv A`×25
- A6 sc3_agg: `Mv A`×25
- A7 team_vote: `Mv A`×25
- A8 team_agg: `Mv A`×25

**f1_top_up_feasible**
- A1 single: `Mv Mstd Mstk T Mv A`×7  |  `Mv Mstk Mstd Mstd T R Mv A`×2  |  `Mv Mstk Mstd T Mv A`×2
- A2 actor_rubric: `Mstd Mv Mstk Mvol T Mv A`×13  |  `Mv Mstd Mstk Mvol T Mv A`×2  |  `Mv Mstd Mstk Mstd R Mv T A`×1
- A3 free_critic: `Mv Mstk Mstd T Mv A`×6  |  `Mv Mstd Mstk T Mv A`×4  |  `Mv Mstk Mstd Mvol T Mv A`×2
- A4 thin_critic: `Mv Mstd Mstk T Mv A`×6  |  `Mv Mstd Mstd Mstk T Mv A`×3  |  `Mv Mstk Mstd T Mv A`×2
- A9 bo3: `Mv Mstd Mstk T Mv A`×8  |  `Mv Mstk Mstd T Mv A`×6  |  `Mv Mstk Mstd T Mstd R Mv A`×2
- A5 sc3_vote: `Mv Mstd Mstk T Mv A`×8  |  `Mv Mstk Mstd T Mv A`×5  |  `Mv Mstd Mstd R Mv Mstk T Mv`×3
- A6 sc3_agg: `Mv Mstk Mstd T Mv A`×7  |  `Mv Mstk T Mv A`×6  |  `Mv Mstd Mstk T Mv A`×5
- A7 team_vote: `Mv Mstk Mstd Mstd R Mv T A`×5  |  `Mv Mstd Mstk Mvol T Mv A`×5  |  `Mv Mstd Mstk Mstd R Mv T A`×4
- A8 team_agg: `Mv Mstk T Mv A`×10  |  `Mv Mstk Mvol T Mv A`×5  |  `Mv Mstk Mstd T Mv A`×4

**f1_dilute_feasible**
- A1 single: `Mv Mstd Mstd R Mv D Mv A`×10  |  `Mv Mstd D Mv A`×4  |  `Mv Mstk Mvol Mstd D R Mv A`×2
- A2 actor_rubric: `Mstd Mv Mstd R Mv Mvol D A`×4  |  `Mstd Mv Mvol Mstk D Mv A`×3  |  `Mstd Mv Mstd R Mv D Mv A`×2
- A3 free_critic: `Mv Mstd Mstd R Mv D Mv A`×9  |  `Mv Mstd Mstd D R Mv A`×2  |  `Mv Mstd D R Mv A`×2
- A4 thin_critic: `Mv Mstd Mstd R Mv D Mv A`×5  |  `Mv Mstd Mstd D Mv A`×4  |  `Mv Mstd D Mv A`×2
- A9 bo3: `Mv Mstd Mstd R Mv D Mv A`×12  |  `Mv Mstk Mvol Mstd D Mv A`×2  |  `Mv Mstd D Mv A`×2
- A5 sc3_vote: `Mv Mstd Mstd R Mv D Mv A`×13  |  `Mv Mstd D Mv A`×5  |  `Mv Mstd D Mstd R Mv A`×1
- A6 sc3_agg: `Mv D Mv A`×6  |  `Mv Mstd D Mv A`×4  |  `Mv Mstd Mstd R Mv D Mv A`×3
- A7 team_vote: `Mv Mstd Mstd R Mv D Mv A`×9  |  `Mv Mstd Mstd R Mv Mvol D A`×3  |  `Mv Mstd Mstd R Mv Mstk Mvol D`×3
- A8 team_agg: `Mv Mstk Mvol Mstd D Mv A`×9  |  `Mv D Mv A`×3  |  `Mv Mstk Mvol D Mv A`×2

**f1_rebuild_needed**
- A1 single: `Mv Mstd Mstk X T D Mv A`×5  |  `Mv Mstd Mstk Mvol X T D Mv`×2  |  `Mv Mstd Mstk Mvol H`×2
- A2 actor_rubric: `Mstd Mv Mstk Mvol X H`×3  |  `Mstd Mv Mstk Mvol X T D Mv`×2  |  `Mstd Mv Mstk Mvol X T D H`×2
- A3 free_critic: `Mv Mstd Mstk Mvol X T D Mv`×2  |  `Mv Mstd Mstd R Mv Mstk H`×2  |  `Mv Mstd Mstk X T D Mv A`×2
- A4 thin_critic: `Mv Mstd Mstd Mstk Mvol R Mv H`×2  |  `Mv Mstd Mstk X T D Mv A`×2  |  `Mv Mstd Mstk Mvol X T D Mv`×2
- A9 bo3: `Mv Mstd Mstk X T D Mv A`×5  |  `Mv Mstd Mstk Mvol X T D A`×4  |  `Mv Mstk Mstd Mvol X T D A`×2
- A5 sc3_vote: `Mv Mstd Mstd R Mv Mstk Mvol H`×5  |  `Mv Mstd Mstk Mvol X T D Mv`×4  |  `Mv Mstd Mstd R Mv X T D`×3
- A6 sc3_agg: `Mv Mstd Mstk Mvol H`×6  |  `Mv Mstk Mvol Mstd Mstd H`×3  |  `Mv Mstk Mvol Mstd X T D A`×2
- A7 team_vote: `Mv Mstd Mstk Mvol Mstd H`×4  |  `Mv Mstd Mstk Mvol X T D A`×3  |  `Mv Mstd Mstk Mvol H`×2
- A8 team_agg: `Mv Mstk Mvol Mstd H`×8  |  `Mv Mstk Mvol Mstd Mstd H`×5  |  `Mv Mstd Mstk Mvol H`×4

**f2_no_fault**
- A1 single: `Mv A`×23  |  `Mstd Mstd R Mv A`×2
- A2 actor_rubric: `Mstd Mv A`×13  |  `Mv Mstd A`×5  |  `Mstd Mstd Mv A`×3
- A3 free_critic: `Mv A`×24  |  `Mstd Mstd R Mv A`×1
- A4 thin_critic: `Mv Mstd Mstd A`×12  |  `Mv Mstd A`×8  |  `Mv Mstd Mstd R Mv A`×2
- A9 bo3: `Mv A`×23  |  `Mstd Mstd R Mv A`×2
- A5 sc3_vote: `Mv A`×25
- A6 sc3_agg: `Mv A`×25
- A7 team_vote: `Mv A`×25
- A8 team_agg: `Mv A`×25

**f2_instrument_recalibrate**
- A1 single: `Mv Mstd Mstd R Mv A`×13  |  `Mv Mstk Mstd Mstd R Mv A`×5  |  `Mstd Mstd R Mv A`×1
- A2 actor_rubric: `Mstd Mstd R Mv A`×16  |  `Mstd Mstd Mv R Mv A`×4  |  `Mv Mstd Mstd R Mv A`×2
- A3 free_critic: `Mv Mstd Mstd R Mv A`×12  |  `Mv Mstk Mstd Mstd R Mv A`×10  |  `Mv Mstk D Mv A`×1
- A4 thin_critic: `Mv Mstd Mstd R Mv A`×7  |  `Mv Mstd Mstd R Mstd Mv A`×6  |  `Mv Mstd Mstd R Mv Mstd A`×4
- A9 bo3: `Mv Mstd Mstd R Mv A`×11  |  `Mv Mstk Mstd Mstd R Mv A`×8  |  `Mv Mstk Mvol Mstd R Mv A`×2
- A5 sc3_vote: `Mv Mstd Mstd R Mv A`×14  |  `Mv Mstk Mstd Mstd R Mv A`×6  |  `Mv Mstk T Mv A`×2
- A6 sc3_agg: `Mv Mstk Mstd R Mv A`×7  |  `Mv Mstk T Mv A`×6  |  `Mv Mstd Mstd R Mv A`×6
- A7 team_vote: `Mv Mstd Mstd R Mv A`×15  |  `Mv Mstk Mstd Mstd R Mv A`×5  |  `Mv Mstk Mstd R Mv A`×2
- A8 team_agg: `Mv Mstk Mvol Mstd R Mv A`×5  |  `Mv Mstk T Mv A`×4  |  `Mv Mstk Mstd Mstd R Mv A`×3

**f2_chemistry_recoverable**
- A1 single: `Mv Mstk Mstd T Mv A`×3  |  `Mv Mstd Mstk T Mv A`×3  |  `Mv Mstd D Mv A`×2
- A2 actor_rubric: `Mstd Mv Mstk Mvol T Mv A`×8  |  `Mv Mstd Mstk Mvol T Mv A`×3  |  `Mstd Mstd Mv R Mv Mstk T A`×2
- A3 free_critic: `Mv Mstd Mstk T Mv A`×5  |  `Mv Mstd Mstd R Mv D Mv A`×3  |  `Mv Mstd Mstd R Mv Mstk T Mv`×2
- A4 thin_critic: `Mv Mstd Mstk T Mv A`×10  |  `Mv Mstd Mstd R Mv Mstk T Mv`×2  |  `Mv Mstk Mstd Mvol Mstd D R Mv`×1
- A9 bo3: `Mv Mstk Mstd T Mv A`×6  |  `Mv Mstd Mstk T Mv A`×4  |  `Mv Mstd Mstk Mvol T Mv A`×3
- A5 sc3_vote: `Mv Mstk Mstd Mstd R Mv T A`×3  |  `Mv Mstd Mstd R Mv Mstk T Mv`×3  |  `Mv Mstk Mstd T Mv A`×3
- A6 sc3_agg: `Mv Mstk Mstd T Mv A`×5  |  `Mv Mstk Mvol T Mv A`×3  |  `Mv Mstk Mstd Mstd R Mv T A`×3
- A7 team_vote: `Mv Mstd Mstk Mstd R Mv T A`×4  |  `Mv Mstd Mstd R Mv D Mv A`×2  |  `Mv Mstk Mstd Mstd R Mv T A`×2
- A8 team_agg: `Mv Mstk Mvol Mstd T Mv A`×5  |  `Mv Mstk T Mv A`×5  |  `Mv Mstk Mstd T Mv A`×4

**f2_chemistry_rebuild**
- A1 single: `Mv Mstd Mstd R Mv Mstk Mvol H`×3  |  `Mv Mstd Mstk Mvol H`×2  |  `Mv Mstd Mstk X T D Mv A`×2
- A2 actor_rubric: `Mstd Mv Mstk Mvol X T D A`×4  |  `Mstd Mv Mstk Mvol X T D Mv`×2  |  `Mstd Mv Mvol Mstk X T D A`×2
- A3 free_critic: `Mv Mstd Mstk Mvol X T D Mv`×4  |  `Mv Mstd Mstk X T D Mv A`×4  |  `Mv Mstd Mstd R Mv Mstk Mvol H`×2
- A4 thin_critic: `Mv Mstd Mstk Mvol X T D Mv`×4  |  `Mv Mstd Mstd R Mv Mstk H`×2  |  `Mv Mstd Mstd Mstk Mvol X T D`×2
- A9 bo3: `Mv Mstd Mstk X T D Mv A`×5  |  `Mv Mstd Mstk Mstd R Mv H`×2  |  `Mv Mstd Mstd R Mv Mstk H`×2
- A5 sc3_vote: `Mv Mstd Mstk X T D Mv A`×5  |  `Mv Mstd Mstk Mvol X T D A`×4  |  `Mv Mstd Mstk Mvol X T D Mv`×3
- A6 sc3_agg: `Mv Mstd Mstk Mvol H`×4  |  `Mv Mstk Mvol Mstd X H`×3  |  `Mv Mstk Mvol Mstd X T D H`×3
- A7 team_vote: `Mv Mstd Mstk Mvol Mstd H`×4  |  `Mv Mstd Mstk Mvol X T D A`×3  |  `Mv Mstd Mstk Mvol X T D Mv`×2
- A8 team_agg: `Mv Mstk Mvol Mstd H`×5  |  `Mv Mstd Mstk Mvol X H`×4  |  `Mv Mstd Mstk Mvol H`×3

**f3_no_fault**
- A1 single: `Mv A`×25
- A2 actor_rubric: `Mstd Mv A`×12  |  `Mstd Mstd Mv A`×7  |  `Mstd Mv Mstd A`×4
- A3 free_critic: `Mv A`×24  |  `Mstd Mstd R Mv A`×1
- A4 thin_critic: `Mv Mstd Mstd A`×17  |  `Mv Mstd A`×5  |  `Mv Mstd Mstd R Mv Mstd A`×2
- A9 bo3: `Mv A`×23  |  `Mstd Mstd R Mv A`×2
- A5 sc3_vote: `Mv A`×25
- A6 sc3_agg: `Mv A`×25
- A7 team_vote: `Mv A`×25
- A8 team_agg: `Mv A`×25

**f3_rebalance_feasible**
- A1 single: `Mv Mstk T Mv A`×7  |  `Mv Mstd Mstk T Mv A`×7  |  `Mv Mstd Mstd R Mv Mstk T A`×2
- A2 actor_rubric: `Mstd Mv Mstk T Mv A`×6  |  `Mstd Mv Mstk Mvol T Mv A`×4  |  `Mstd Mstd R Mv Mstk T Mv A`×3
- A3 free_critic: `Mv Mstk T Mv A`×7  |  `Mv Mstd Mstk T Mv A`×6  |  `Mv Mstk Mstd T Mv A`×2
- A4 thin_critic: `Mv Mstd Mstk T Mv A`×9  |  `Mv Mstk Mstd T Mv A`×3  |  `Mv Mstd Mstk X T D Mv A`×2
- A9 bo3: `Mv Mstd Mstk T Mv A`×11  |  `Mv Mstd Mstk X T D Mv A`×3  |  `Mv Mstk Mstd T Mv A`×2
- A5 sc3_vote: `Mv Mstk T Mv A`×10  |  `Mv Mstd Mstk T Mv A`×4  |  `Mv Mstd Mstk X T D Mv A`×3
- A6 sc3_agg: `Mv Mstk T Mv A`×17  |  `Mv Mstd Mstk T Mv A`×3  |  `Mv Mstd Mstk Mstd X T D Mv`×1
- A7 team_vote: `Mv Mstk T Mv A`×7  |  `Mv Mstk Mstd T Mv A`×4  |  `Mv Mstd Mstk T Mv A`×4
- A8 team_agg: `Mv Mstk T Mv A`×13  |  `Mv Mstk T A`×4  |  `Mv Mstk D Mv A`×2

**f3_rebalance_rebuild**
- A1 single: `Mv Mstd Mstk X T D Mv A`×9  |  `Mv Mstk Mstd X T D Mv A`×2  |  `Mv Mstd Mstd R Mv Mvol Mstk H`×2
- A2 actor_rubric: `Mstd Mv Mvol Mstk X T D A`×6  |  `Mstd Mv Mstk X T D Mv A`×5  |  `Mv Mstd Mvol Mstk X T D A`×3
- A3 free_critic: `Mv Mstd Mstk X T D Mv A`×6  |  `Mv Mstk X T D Mv A`×6  |  `Mv Mstk Mstd X T D Mv A`×2
- A4 thin_critic: `Mv Mstd Mstk X T D Mv A`×15  |  `Mv Mstk Mstd X T D Mv A`×5  |  `Mv Mvol Mstd Mstk X T Mvol D`×1
- A9 bo3: `Mv Mstd Mstk X T D Mv A`×12  |  `Mv Mstk X T D Mv A`×6  |  `Mv Mstk Mstd X T D Mv A`×5
- A5 sc3_vote: `Mv Mstd Mstk X T D Mv A`×14  |  `Mv Mstk Mstd X T D Mv A`×2  |  `Mv Mstk X T D Mv A`×2
- A6 sc3_agg: `Mv Mstd Mstk X T D Mv A`×16  |  `Mv Mstk X T D Mv A`×5  |  `Mv Mvol Mstk X T D Mv A`×2
- A7 team_vote: `Mv Mstd Mstk X T D Mv A`×20  |  `Mv Mstd Mstd R Mstk X T D`×1  |  `Mv Mstk Mstd X Mstd T D A`×1
- A8 team_agg: `Mv Mstk X T D Mv A`×8  |  `Mv Mstd Mstk X T D Mv A`×5  |  `Mv Mvol Mstk X T D Mv A`×4

## weak  (actor=qwen32b, critic=qwen_max)


**f1_no_fault**
- A1 single: `Mv Mvol Mstd Mstd R Mv Mv Mv`×4  |  `Mv Mstd Mstd R Mv Mv Mv Mv`×4  |  `Mv Mstd R Mv Mstd Mv Mv Mv`×3
- A2 actor_rubric: `Mv Mstd Mstd Mv Mv Mv A`×3  |  `Mv Mstd Mv Mv Mstd Mv Mv A`×2  |  `Mv Mstd Mstd Mv Mv Mv Mv A`×2
- A3 free_critic: `Mv A`×23  |  `Mv Mvol A`×1  |  `Mv Mstd Mstd A`×1
- A4 thin_critic: `Mv A`×19  |  `Mv Mstd A`×3  |  `Mv Mstd Mstd A`×2
- A9 bo3: `Mv Mstd R Mv Mstd Mv Mv Mv`×3  |  `Mv Mvol Mstd Mstd R Mv Mv Mv`×2  |  `Mv Mvol Mv Mv Mv Mv Mv Mv`×2
- A5 sc3_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×4  |  `Mv Mstd R Mv Mv Mv Mv Mv`×4  |  `Mv Mvol Mstd R Mv Mv Mv Mv`×2
- A6 sc3_agg: `Mv Mv Mv Mv Mv Mv Mv Mv`×4  |  `Mv Mstd R Mv Mv Mv Mv Mv`×2  |  `Mv Mv Mv Mv Mv Mv Mstd Mstd`×1
- A7 team_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×9  |  `Mv Mv Mv Mv Mv Mstd R Mv`×2  |  `Mv Mstd Mv Mv Mv Mv Mv Mv`×2
- A8 team_agg: `Mv A`×17  |  `Mv Mstd Mstd A`×1  |  `T Mv Mv Mv D Mv`×1

**f1_top_up_feasible**
- A1 single: `Mv T Mv Mv Mv Mv Mv Mv`×4  |  `Mv T Mv Mv Mv Mv Mv`×3  |  `Mv Mstd Mv T Mv Mvol D Mv`×1
- A2 actor_rubric: `Mv Mstd Mstd Mvol Mv T Mv Mv`×3  |  `Mv Mstd Mstd T Mv Mv Mv Mv`×3  |  `Mv Mstd Mstd Mv Mv Mv Mv`×2
- A3 free_critic: `Mv T Mv A`×11  |  `Mv Mv T Mv A`×4  |  `Mv Mv T Mv Mv D Mv`×1
- A4 thin_critic: `Mv Mstd Mstk T Mv A`×3  |  `Mv Mstd Mv Mv T Mv A`×2  |  `Mv Mstd T Mv Mv R D Mv`×1
- A9 bo3: `Mv T Mv Mv D Mv Mv Mv`×3  |  `Mv T Mv T Mv Mv Mv Mv`×2  |  `Mv T Mv D Mv Mv Mv Mv`×2
- A5 sc3_vote: `Mv T Mv Mv Mv Mv Mv Mv`×7  |  `Mv T Mv Mv Mv Mv Mv D`×3  |  `Mv T Mv Mv Mv Mv D Mv`×2
- A6 sc3_agg: `Mv T Mv Mv Mv Mv Mv Mv`×5  |  `Mv T Mv Mv Mv Mv Mv D`×3  |  `Mv T Mv Mv T Mv Mv Mv`×2
- A7 team_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×7  |  `Mv Mv Mv Mv Mv Mv Mv T`×2  |  `Mv Mv Mstd Mv Mv Mv Mv T`×1
- A8 team_agg: `Mv T Mv Mv D Mv Mv Mv`×2  |  `Mv T Mv Mv Mv D Mv`×2  |  `Mv T Mv A`×2

**f1_dilute_feasible**
- A1 single: `Mv Mstd R Mv T Mv Mv`×1  |  `Mv Mv Mv Mv D Mv Mv`×1  |  `Mv Mstd R Mv Mv Mv Mvol Mstd`×1
- A2 actor_rubric: `Mv Mstd Mstd Mv Mv Mv Mv A`×3  |  `Mv Mstd Mstd Mv Mv Mstd Mv Mstd`×2  |  `Mv Mstd Mv Mstd Mv Mv Mv Mv`×2
- A3 free_critic: `Mv D Mv A`×15  |  `Mv Mstd D Mv A`×1  |  `Mv D Mv Mv D Mv Mv`×1
- A4 thin_critic: `Mv Mstd Mstd D Mv A`×2  |  `Mv Mstd Mstk Mstd T X T Mv`×1  |  `Mv Mv Mstd Mstd Mv Mv`×1
- A9 bo3: `Mv Mv Mv Mv Mstd Mstd Mv`×1  |  `Mv T Mv Mv Mv Mv Mv D`×1  |  `Mv Mstd Mv Mv Mstd R Mv Mv`×1
- A5 sc3_vote: `Mv Mv Mv Mstd D Mv Mv Mv`×1  |  `Mv Mstd R T Mv D Mv Mv`×1  |  `Mv Mv Mv Mv Mv Mv D Mv`×1
- A6 sc3_agg: `Mv D Mv Mv Mv Mv Mv Mv`×2  |  `Mv Mstd R Mv T Mv D Mv`×2  |  `Mv Mv Mv D Mv Mv Mv Mv`×2
- A7 team_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×3  |  `Mv Mv Mstd Mv Mv Mv R Mv`×2  |  `Mv Mv Mv Mv Mv Mv Mv Mstd`×2
- A8 team_agg: `Mv Mv Mv Mv Mv Mv Mv`×2  |  `Mv Mv D Mv Mv T`×1  |  `Mv Mv Mv Mvol D Mv Mv Mv`×1

**f1_rebuild_needed**
- A1 single: `Mv Mv Mv Mstd Mvol`×1  |  `Mv T Mv Mv Mvol Mv`×1  |  `Mv Mstd Mv Mv Mvol R`×1
- A2 actor_rubric: `Mv Mstd Mstd Mv Mv Mv Mv X`×2  |  `Mv Mstd Mv Mv Mstd Mvol Mv Mv`×1  |  `Mv Mstd Mv Mstd Mv X Mstd Mvol`×1
- A3 free_critic: `Mv D Mv Mv H`×2  |  `Mv D Mv H`×1  |  `Mv Mv D Mv Mvol Mv Mv`×1
- A4 thin_critic: `Mv Mstd Mstd T X T D Mv`×2  |  `Mv Mstd Mstk R Mv Mv X Mstd`×1  |  `Mv Mstd T Mv X T Mv`×1
- A9 bo3: `Mv Mv Mstd D Mv Mv`×2  |  `Mv Mv Mv Mv Mv Mvol Mv`×1  |  `Mv D Mv Mv Mv Mv`×1
- A5 sc3_vote: `Mv Mv Mv T Mv Mv Mv`×1  |  `Mv Mv Mv Mv D Mv Mv`×1  |  `Mv Mstd Mstd R Mv`×1
- A6 sc3_agg: `Mv T Mv Mv Mv Mv D Mv`×2  |  `Mv T Mv Mv Mv Mv`×2  |  `Mv T Mv Mv Mv Mv Mv D`×1
- A7 team_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×4  |  `Mv Mv Mv Mstd Mstd Mv Mv R`×2  |  `Mv Mv Mv Mv Mstd Mv Mv Mvol`×1
- A8 team_agg: `Mv Mv Mv Mstd Mv Mv Mv`×2  |  `Mv Mv Mv Mstd Mstd R Mv D`×1  |  `Mv Mv Mv Mv Mstd Mstd R D`×1

**f2_no_fault**
- A1 single: `Mv Mvol Mstd Mstd R Mv Mv Mv`×2  |  `Mv Mvol Mstd R Mv Mv Mv Mv`×2  |  `Mv Mv Mv Mv Mv Mstd R Mv`×2
- A2 actor_rubric: `Mv Mstd Mstd Mv Mv Mv A`×5  |  `Mv Mstd Mstd Mv Mv Mv Mv A`×4  |  `Mv Mstd Mstd Mv Mv Mv Mv Mv`×3
- A3 free_critic: `Mv A`×24  |  `Mv Mvol A`×1
- A4 thin_critic: `Mv A`×19  |  `Mv Mstd A`×5  |  `Mv Mstd Mstd A`×1
- A9 bo3: `Mv Mvol Mstd Mstd R Mv Mv`×3  |  `Mv Mv Mv Mv Mv Mv Mv Mv`×3  |  `Mv Mvol Mv Mv Mv Mv Mv Mv`×2
- A5 sc3_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×6  |  `Mv Mvol Mstd Mstd R Mv Mv Mv`×5  |  `Mv Mstd R Mv Mstd Mv Mv Mv`×3
- A6 sc3_agg: `Mv Mstd R Mv Mv Mv Mv Mv`×3  |  `Mv Mstd Mstd R Mv Mv Mv Mv`×2  |  `Mv Mvol Mstd Mv R Mv Mv Mv`×2
- A7 team_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×9  |  `Mv Mstd Mv Mv Mv Mv Mv Mv`×3  |  `Mv Mstd R Mv Mstd Mv Mv Mv`×2
- A8 team_agg: `Mv A`×17  |  `Mv Mv Mv A`×2  |  `Mv Mvol Mstd Mstd A`×1

**f2_instrument_recalibrate**
- A1 single: `Mv T Mv Mv Mv Mv Mv Mv`×2  |  `Mv T Mv Mv Mv Mv Mv`×2  |  `Mv Mv Mstd Mstd R Mv Mv Mv`×2
- A2 actor_rubric: `Mv Mstd Mstd R Mv Mv Mv A`×3  |  `Mv Mstd Mstd Mstd Mv Mstd T Mv`×1  |  `Mv Mstd Mv Mv T Mv Mv Mstd`×1
- A3 free_critic: `Mv T Mv A`×7  |  `Mv D Mv A`×3  |  `Mv A`×2
- A4 thin_critic: `Mv Mstd R Mv A`×3  |  `Mv Mstd Mstd R Mv A`×3  |  `Mv Mstd Mstd A`×3
- A9 bo3: `Mv T Mv Mv Mv Mv Mv Mv`×2  |  `Mv Mv T Mv Mv Mv Mv Mv`×2  |  `Mv T Mv T Mv T Mv Mv`×1
- A5 sc3_vote: `Mv T Mv Mv Mv Mv Mv Mv`×7  |  `Mv T Mv Mv Mv Mv Mv`×2  |  `Mv T Mv Mv Mv Mv Mv D`×2
- A6 sc3_agg: `Mv T Mv Mv Mv Mv Mv Mv`×5  |  `Mv T Mv Mv Mv D Mv Mv`×1  |  `Mv T Mv Mv T Mv Mv Mv`×1
- A7 team_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×5  |  `Mv Mv Mv T Mv Mv Mv Mv`×2  |  `Mv Mv Mv Mstd Mstd R Mv Mv`×2
- A8 team_agg: `Mv T Mv T Mv D Mv Mv`×2  |  `Mv T Mv Mv Mv Mv A`×1  |  `Mv T Mv A`×1

**f2_chemistry_recoverable**
- A1 single: `Mv T Mv Mv D Mv Mv Mv`×2  |  `Mv T Mv Mv Mv Mv Mv`×2  |  `Mv D Mv T Mv X`×1
- A2 actor_rubric: `Mv Mstd Mstd Mv T Mv Mv Mv`×3  |  `Mv Mstd Mstd Mv Mv Mv Mv Mv`×2  |  `Mv Mstd Mstd Mvol Mv Mv Mv Mv`×2
- A3 free_critic: `Mv T Mv A`×10  |  `Mv D Mv A`×4  |  `Mv T Mv Mv A`×2
- A4 thin_critic: `Mv Mstd T Mv X T D Mv`×2  |  `Mv Mstd Mvol Mstd R Mstd Mv`×1  |  `Mv Mstd Mstk X R T D Mv`×1
- A9 bo3: `Mv T Mv Mv Mv Mv Mv Mv`×3  |  `Mv T Mv Mv Mv Mv Mv Mvol`×3  |  `Mv T Mv Mv Mv Mv Mv T`×2
- A5 sc3_vote: `Mv T Mv Mv Mv Mv Mv Mv`×3  |  `Mv T Mv Mv Mv Mv Mv`×2  |  `Mv T Mv Mv Mv Mv D Mv`×2
- A6 sc3_agg: `Mv Mv T Mv D Mv Mv`×2  |  `Mv T Mv Mv Mv T Mv Mv`×2  |  `Mv Mstd Mstd R Mv D`×1
- A7 team_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×4  |  `Mv Mv Mv Mv T Mv Mv Mv`×2  |  `Mv Mv Mv Mv Mv Mv Mv T`×2
- A8 team_agg: `Mv T Mv Mv D Mv Mv`×2  |  `Mv T T Mv D`×1  |  `Mv Mstd Mstd R Mv Mv Mv Mv`×1

**f2_chemistry_rebuild**
- A1 single: `Mv D Mv Mv T Mv`×1  |  `Mv Mv T Mv Mv Mv`×1  |  `Mv T Mv Mv Mv Mv D Mv`×1
- A2 actor_rubric: `Mv Mstd Mstd Mvol Mv X`×2  |  `Mv Mstd Mstd T Mv Mv Mv Mvol`×1  |  `Mv Mstd Mstd Mv Mstd Mv X`×1
- A3 free_critic: `Mv T Mv D Mv`×2  |  `Mv Mv Mvol Mstd T Mv`×1  |  `T Mv D Mv D Mstk X`×1
- A4 thin_critic: `Mv Mstd Mstk X T D Mv A`×1  |  `Mv Mstd Mstk Mvol X T D`×1  |  `Mv D Mstd Mv X R T`×1
- A9 bo3: `Mv Mstd D Mv D Mv`×1  |  `Mv Mstd Mstd R T Mv D Mv`×1  |  `Mv Mv Mv Mstd R Mv D Mv`×1
- A5 sc3_vote: `Mv T Mv Mv Mv Mv Mv`×2  |  `Mv Mv Mv Mv D Mv Mv`×1  |  `Mv Mstd Mv Mv Mstd R Mv`×1
- A6 sc3_agg: `Mv Mv D Mv Mv Mv`×2  |  `Mv Mv Mv Mv Mv D Mv`×1  |  `Mv Mstd Mv R Mv Mv T D`×1
- A7 team_vote: `Mv Mv Mv Mstd Mstd R Mv Mv`×2  |  `Mv Mv Mv Mv Mv Mv Mv Mv`×1  |  `Mv Mv Mv Mstd Mv Mv Mv Mv`×1
- A8 team_agg: `T Mv Mstd Mstd R Mv Mvol`×2  |  `Mv Mv Mv Mv T Mv Mv`×1  |  `Mv Mv Mv Mstd Mstd Mv Mv R`×1

**f3_no_fault**
- A1 single: `Mv Mstd R Mv Mstd Mv Mv Mv`×3  |  `Mv Mv Mv Mv Mv Mv Mstd Mstd`×2  |  `Mv Mvol Mstd Mstd R Mv Mv Mv`×2
- A2 actor_rubric: `Mv Mstd Mstd Mv Mv Mv A`×4  |  `Mv Mstd Mv Mstd Mv Mv Mv Mv`×3  |  `Mv Mstd Mv Mv A`×2
- A3 free_critic: `Mv A`×21  |  `Mv Mvol A`×2  |  `T Mv Mv Mvol`×1
- A4 thin_critic: `Mv A`×23  |  `Mv Mstd A`×2
- A9 bo3: `Mv Mv Mv Mv Mv Mv Mv Mv`×3  |  `Mv Mstd R Mv Mv Mv Mv Mv`×2  |  `Mv Mv Mv Mv Mv Mstd R Mv`×2
- A5 sc3_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×4  |  `Mv Mstd R Mv Mv Mv Mv Mv`×4  |  `Mv Mstd R Mv Mstd Mv Mv Mv`×3
- A6 sc3_agg: `Mv Mstd R Mv Mstd Mv Mv Mv`×4  |  `Mv Mv Mv Mv Mv Mv Mv Mv`×3  |  `Mv Mstd R Mv Mv Mv Mv Mv`×3
- A7 team_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×8  |  `Mv Mstd Mv Mv Mv Mv Mv Mv`×3  |  `Mv Mstd Mstd R Mv Mv Mv Mv`×3
- A8 team_agg: `Mv A`×17  |  `Mv Mstd Mstd A`×2  |  `Mv Mv Mstd Mstd R Mv Mv Mv`×1

**f3_rebalance_feasible**
- A1 single: `Mv T Mv Mv Mv Mv Mv Mv`×3  |  `Mv T Mv D Mv Mv Mv Mv`×2  |  `Mv T Mv Mv Mv Mv Mv T`×2
- A2 actor_rubric: `Mv Mstd Mstd Mv Mv Mv Mv Mv`×2  |  `Mv Mstd Mstd Mv T Mv Mv Mv`×2  |  `Mv Mstd Mv Mv Mvol Mstd Mv`×2
- A3 free_critic: `Mv T Mv A`×6  |  `Mv T Mv T Mv A`×6  |  `Mv D Mv A`×2
- A4 thin_critic: `Mv Mstd T Mv A`×2  |  `Mv Mstd T Mv X Mstk T D`×2  |  `Mv Mstd T Mv X T Mv T`×1
- A9 bo3: `Mv T Mv Mv Mv Mv Mv Mv`×3  |  `Mv T Mv D Mv Mv Mv Mv`×2  |  `Mv T Mv Mv Mv Mv T Mv`×2
- A5 sc3_vote: `Mv T Mv Mv Mv Mv Mv Mv`×5  |  `Mv Mv T Mv Mv Mv Mv Mv`×3  |  `Mv T Mv T Mv Mv Mv Mv`×2
- A6 sc3_agg: `Mv T Mv Mv Mv Mv Mv Mv`×5  |  `Mv T Mv D Mv Mv D Mv`×2  |  `Mv T Mv Mv Mv Mv Mv D`×2
- A7 team_vote: `Mv Mv Mv Mv Mv Mv Mv Mv`×4  |  `Mv Mv Mv Mv Mv Mv Mv T`×3  |  `Mv Mv Mv Mv Mstd Mstd R Mv`×3
- A8 team_agg: `Mv T Mv T Mv Mv Mv Mv`×2  |  `Mv T Mv Mv Mv Mvol Mv A`×1  |  `T Mv Mstd Mv Mvol Mv`×1

**f3_rebalance_rebuild**
- A1 single: `Mv Mstd R Mv Mv D Mv`×2  |  `Mv Mstd R T Mv D Mv`×2  |  `Mv Mv D Mv Mv Mv`×1
- A2 actor_rubric: `Mv Mstd Mv Mv Mv Mstd Mv X`×2  |  `Mv Mstd Mv Mv Mvol Mstd Mv X`×2  |  `Mv Mstd Mv Mvol Mstd X T D`×1
- A3 free_critic: `Mv D Mv Mv Mvol Mv Mv`×1  |  `Mv X T D Mv Mstd Mstd`×1  |  `Mv T Mv Mvol Mvol D Mv`×1
- A4 thin_critic: `Mv Mstd Mstk X T D Mv A`×2  |  `Mv Mstd Mv Mstd Mv Mv T Mv`×1  |  `Mv Mstd Mstd T X T Mv D`×1
- A9 bo3: `Mv Mstd Mv Mvol Mstd`×1  |  `Mv Mstd Mvol R Mv`×1  |  `Mv Mv Mv D Mv Mv Mv`×1
- A5 sc3_vote: `Mv Mstd R Mv Mstd D Mv`×2  |  `Mv T Mv Mv Mvol D Mv Mv`×1  |  `Mv Mv Mvol Mstd Mstd R T Mv`×1
- A6 sc3_agg: `Mv T Mv Mv D Mv Mv`×2  |  `Mv Mv D Mv Mv Mv`×2  |  `Mv D Mv Mv Mstd Mstd R`×1
- A7 team_vote: `Mv Mv Mstd Mv Mv Mv Mstd R`×2  |  `Mv Mv Mv Mv Mv Mstd Mstd R`×2  |  `Mv Mv Mstd Mstd R Mv Mv Mv`×2
- A8 team_agg: `Mv Mv D Mv Mv Mv Mv`×3  |  `T Mv Mvol Mv Mv`×1  |  `T Mv Mv Mv Mv Mv Mvol`×1
