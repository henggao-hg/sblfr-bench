# Tier-1 Seed0 Mechanism Checks

Date: 2026-07-01

Scope: three follow-up checks requested after the Fable5 seed0 mechanism discussion.

No runner, arm, prompt, scoring, instance, or result file was modified. This is a read-only analysis over seed0 metrics/transcripts.

## 1. Model Role Labels

The raw metrics field `critic` is a runner-level pairing field. It is only an actual critic for `free_critic` and `thin_critic`.

### Weak group

Actor: `qwen32b`; runner-paired critic: `qwen_max`.

| Arm | Uses external critic? | Actual selector / wrapper |
|---|---:|---|
| single | no | none |
| actor_rubric | no | none; rubric is in actor prompt |
| free_critic | yes | qwen_max external critic |
| thin_critic | yes | qwen_max external critic with rubric |
| sc3_vote | no | vote over qwen32b samples |
| sc3_agg | no | qwen32b acts as aggregator |
| team_vote | no | vote over qwen32b persona proposals |
| team_agg | no | qwen32b acts as aggregator |
| bo3 | no | visible trajectory selector over qwen32b trajectories |

Key implication: weak `team_agg = 72/275` is not contaminated by qwen_max as aggregator. It is qwen32b proposing and qwen32b selecting.

### Strong group

Actor: `qwen_max`; runner-paired critic: `deepseek`.

| Arm | Uses external critic? | Actual selector / wrapper |
|---|---:|---|
| single | no | none |
| actor_rubric | no | none; rubric is in actor prompt |
| free_critic | yes | deepseek external critic |
| thin_critic | yes | deepseek external critic with rubric |
| sc3_vote | no | vote over qwen_max samples |
| sc3_agg | no | qwen_max acts as aggregator |
| team_vote | no | vote over qwen_max persona proposals |
| team_agg | no | qwen_max acts as aggregator |
| bo3 | no | visible trajectory selector over qwen_max trajectories |

Key implication: strong critic arms are not "qwen_max plus stronger critic." They are qwen_max plus deepseek as a different external critic.

## 2. Thin-Critic UNMANAGED Terminal State

Question: when `thin_critic` ends as `UNMANAGED`, was the final true batch already in tolerance, with the agent simply failing to close via `accept_batch`?

Method: for each `thin_critic` `UNMANAGED` transcript, inspect the final step's `tia` flag (true-in-tolerance after the action).

### Weak qwen32b + qwen_max thin critic

`thin_critic` UNMANAGED count: 135.

| Final true state | Count | Share |
|---|---:|---:|
| final `tia=True` | 31 | 23% |
| final `tia=False` | 101 | 75% |
| final `tia` unknown | 3 | 2% |

By class:

| Class | final in tolerance | final out of tolerance | unknown |
|---|---:|---:|---:|
| f1:dilute_feasible | 3 | 14 | 1 |
| f1:rebuild_needed | 6 | 18 | 0 |
| f1:top_up_feasible | 3 | 10 | 1 |
| f2:chemistry_rebuild | 6 | 17 | 0 |
| f2:chemistry_recoverable | 8 | 8 | 0 |
| f3:rebalance_feasible | 2 | 15 | 1 |
| f3:rebalance_rebuild | 3 | 19 | 0 |

Interpretation: for weak actor, thin critic's extra caution does not mostly produce "solved but forgot accept." Most UNMANAGED episodes are still genuinely out of tolerance. There is still a meaningful minority (31/135) where the batch appears solved at the final step but no terminal closeout occurred.

### Strong qwen_max + deepseek thin critic

`thin_critic` UNMANAGED count: 45.

| Final true state | Count | Share |
|---|---:|---:|
| final `tia=True` | 44 | 98% |
| final `tia=False` | 1 | 2% |
| final `tia` unknown | 0 | 0% |

By class:

| Class | final in tolerance | final out of tolerance |
|---|---:|---:|
| f1:dilute_feasible | 5 | 0 |
| f1:rebuild_needed | 10 | 1 |
| f1:top_up_feasible | 5 | 0 |
| f2:chemistry_rebuild | 10 | 0 |
| f2:chemistry_recoverable | 5 | 0 |
| f2:instrument_recalibrate | 1 | 0 |
| f3:rebalance_feasible | 3 | 0 |
| f3:rebalance_rebuild | 5 | 0 |

Interpretation: for strong actor, thin critic's UNMANAGED failures are almost entirely "batch solved but no accept before budget ended." This strongly supports the budget-starvation / over-verification mechanism for strong thin critic.

## 3. Strong-Side DeepSeek Critic Audit

Question: is the strong-side external critic condition really an informative critic, or is deepseek often silent/empty?

Scope: strong seed0, arms `free_critic` and `thin_critic`.

### free_critic

Episodes: 275. Critic reviews: 1535.

| Verdict | Count | Share |
|---|---:|---:|
| approve | 1332 | 87% |
| revise | 48 | 3% |
| empty | 151 | 10% |
| parse_fail | 4 | <1% |

Episodes with any revise: 44/275.

Outcome by revise status:

| Revise status | SUCCESS | CF | HANDOFF/OVER | UNMANAGED |
|---|---:|---:|---:|---:|
| no revise | 192 | 2 | 16 | 21 |
| with revise | 16 | 0 | 20 | 8 |

Sample revise critiques:

- `f2_chemistry_rebuild_00`: "Discarding vessel_1 would remove it from the workspace, making it impossible to achieve the goal..."
- `f2_chemistry_recoverable_01`: "Recalibration is not justified given the small deviations in standard measurements..."
- `f1_rebuild_needed_02`: "The assay appears calibrated based on standard measurements; the vessel concentration is above target, so recalibration is unnecessary..."

Interpretation: free deepseek critic mostly approves, with a low revise rate and a nontrivial empty rate. It is not exerting a strong supervisory force over qwen_max.

### thin_critic

Episodes: 275. Critic reviews: 1739.

| Verdict | Count | Share |
|---|---:|---:|
| approve | 850 | 49% |
| revise | 283 | 16% |
| empty | 591 | 34% |
| parse_fail | 15 | 1% |

Episodes with any revise: 190/275.

Outcome by revise status:

| Revise status | SUCCESS | CF | HANDOFF/OVER | UNMANAGED |
|---|---:|---:|---:|---:|
| no revise | 53 | 0 | 15 | 17 |
| with revise | 150 | 0 | 12 | 28 |

Principle references in revise critiques:

| Principle ref | Count |
|---|---:|
| 2 | 157 |
| 7 | 77 |
| 8 | 15 |
| 1 | 12 |
| 9 | 6 |
| 3 | 5 |
| 6 | 2 |

Sample revise critiques:

- `f1_no_fault_00`: "Must verify the instrument against a reference standard before a terminal action (principle 2)."
- `f1_no_fault_00`: "Recalibration is unnecessary because the vessel measurement ... is within tolerance ..., violating principle 7."
- `f1_dilute_feasible_00`: "Violates principle 2: before taking a corrective or diagnostic action like measuring volume, you must first verify the instrument..."
- `f1_dilute_feasible_00`: "Instrument assay_X is reading standards accurately and does not need recalibration (principle 7)."

Interpretation: thin deepseek critic is active when it returns content, and its revisions are dominated by rubric principles, especially instrument verification and avoiding unnecessary recalibration. However, it has a very high empty verdict rate (591/1739 = 34%), so strong-side critic results should be interpreted with this reliability caveat.

## Mechanism Takeaways From These Checks

1. Weak `team_agg` remains a clean no-external-critic mechanism: qwen32b can do better when it generates diverse proposals and then selects among them.

2. Weak `free_critic` and `thin_critic` are capability-injection conditions, because qwen_max is the critic.

3. Thin critic has different failure modes by actor strength:
   - weak: most UNMANAGED episodes are still out of tolerance, though some are solved-without-accept.
   - strong: almost all UNMANAGED episodes are solved-without-accept, consistent with over-verification consuming budget.

4. Strong-side critic arms have a critic-quality caveat:
   - deepseek free critic is mostly approve/silent.
   - deepseek thin critic is active but often empty.
   - Therefore "critic does not help strong qwen_max" should be phrased carefully: this tests qwen_max plus deepseek critic, not qwen_max plus a stronger critic.

## Recommended Follow-Up

After seed1 completes:

1. Recompute the same three checks for seed1.
2. Check whether weak `team_agg` stays above `sc3_agg` and `team_vote`.
3. Check whether strong thin-critic UNMANAGED remains mostly `final tia=True`.
4. Check whether deepseek critic empty rate remains high.
5. Compute oracle@3 for proposal-pool arms to separate "good proposal absent" from "good proposal present but not selected."

