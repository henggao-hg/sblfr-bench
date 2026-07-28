# Fable5 Seed0 Mechanism Notes

Date: 2026-07-01

Scope: notes from two Fable5 responses about Tier-1 seed0 results. This file records hypotheses, confirmed facts, interpretation cautions, and proposed next analyses. It does not change scoring or code.

## Context

Seed0 summary table discussed:

| Arm | Weak qwen32b | Strong qwen_max |
|---|---:|---:|
| single | 1/275 success, 26 CF | 212/275 success, 4 CF |
| actor_rubric | 56/275 success, 16 CF | 217/275 success, 0 CF |
| free_critic | 149/275 success, 29 CF | 208/275 success, 2 CF |
| thin_critic | 122/275 success, 16 CF | 203/275 success, 0 CF |
| sc3_vote | 1/275 success, 23 CF | 215/275 success, 2 CF |
| sc3_agg | 5/275 success, 19 CF | 222/275 success, 7 CF |
| team_vote | 0/275 success, 7 CF | 216/275 success, 1 CF |
| team_agg | 72/275 success, 32 CF | 212/275 success, 10 CF |
| bo3 | 1/275 success, 24 CF | 244/275 success, 1 CF |

## Findings From Fable5 Round 1

### 1. Weak free_critic is the largest gain and falsifies a simple "free critic has no effect" expectation

Fable5 points out that C2 was expected to behave like a negative control: free_critic approximately equal to single would support the simple version of hypothesis H. Seed0 weak does not do that:

- weak single: 1/275 success
- weak free_critic: 149/275 success

This is too large to treat as noise. It must be reported as a challenge to a naive version of H.

Interpretation offered by Fable5: weak free_critic is not information-free if the critic is a stronger model. It injects external model capability through the critique channel.

Confirmed code/data fact:

- weak actor = qwen32b
- weak free/thin critic = qwen_max
- strong actor = qwen_max
- strong free/thin critic = deepseek

Implication: weak free_critic is a "strong critic helps weak actor" condition, not a pure architecture-only condition.

### 2. Same-model quantity does not rescue the weak actor

Weak-side same-model or same-actor quantity arms stay near zero:

- single: 1/275
- sc3_vote: 1/275
- sc3_agg: 5/275
- bo3: 1/275

Fable5's read: extra calls alone do not help qwen32b. This supports the claim that weak-model gains are not explained by more sampling alone.

### 3. Strong bo3 is the strongest strong-side arm

Strong-side success:

- single: 212/275
- most step-level multi-agent arms: roughly 203-222/275
- bo3: 244/275

Fable5's read: for the strong actor, independent trajectory retries plus visible selection work better than committees or step-level wrappers. This suggests part of strong-model failure is trajectory-level variability.

Caution: bo3 uses about 3x compute and should be compared against compute-matched arms, not only against single.

### 4. Rubric mainly affects safety, especially for the strong actor

Strong-side CF:

- single: 4
- actor_rubric: 0
- thin_critic: 0
- bo3: 1

Fable5's read: for a strong model, the rubric has little success-rate effect but can reduce critical failures. This supports reporting success and CF on separate axes.

### 5. Weak thin_critic underperforms free_critic in raw success

Weak-side:

- free_critic: 149 success, 29 CF
- thin_critic: 122 success, 16 CF

Fable5 interprets this as a safety/success trade-off. The thin rubric pushes more verification and caution, reducing CF but increasing non-closure.

## Findings From Fable5 Round 2

### 1. team_agg 72/275 is a clean mechanism result, because the aggregator is the actor itself

Fable5 initially asked whether team_agg was contaminated by a stronger external aggregator. We checked the code:

- `sc3_agg` calls `select_agg(model, ...)`
- `team_agg` calls `select_agg(model, ...)`
- in both cases, `model` is the actor, not the critic
- the `critic` field in metrics is a runner-level field and should not be interpreted as actual usage for non-critic arms

Therefore weak team_agg does not use qwen_max. It uses qwen32b proposals and qwen32b selection.

Weak-side 2x2:

- single: 1/275
- sc3_agg: 5/275
- team_vote: 0/275
- team_agg: 72/275

Fable5's read: diversity plus discriminative selection is doing something that neither same-prompt aggregation nor majority voting achieves.

Caution: do not write "all gain comes from structure" too strongly. Persona prompts are also an intervention. Better wording: "large gain without an external critic model."

### 2. Free vs thin critic: thin buys safety and pays in unmanaged episodes

Verified seed0 weak outcome decomposition:

| Arm | SUCCESS | CF | HANDOFF/OVER | UNMANAGED |
|---|---:|---:|---:|---:|
| free_critic | 149 | 29 | 15 | 82 |
| thin_critic | 122 | 16 | 2 | 135 |

Mechanistic read:

- free critic is permissive and helps the weak actor complete many feasible corrections.
- thin critic enforces evidence-gating principles, reducing CF.
- thin critic increases UNMANAGED, likely because extra verification/caution consumes budget and leaves no terminal closeout.

Class-level support:

- F2 instrument:
  - free: 5 SUCCESS / 20 CF
  - thin: 17 SUCCESS / 8 CF
- Simple feasible correction classes:
  - free tends to have higher raw success.
  - thin has more UNMANAGED.

Provisional phrasing: "Principles in the critic reduce unsafe actions, but under a fixed budget they can convert some recoverable episodes into unmanaged episodes."

### 3. Metrics field caution: `critic` is misleading for non-critic arms

The seed0 metrics rows include `critic=qwen_max` or `critic=deepseek` for all arms. This does not mean every arm used the critic.

Actual usage:

- Uses critic: `free_critic`, `thin_critic`
- Does not use critic: `single`, `actor_rubric`, `sc3_vote`, `sc3_agg`, `team_vote`, `team_agg`, `bo3`
- `sc3_agg` and `team_agg` use the actor model as selector.

Do not change running code during seed1. In analysis, add an explicit derived label such as `uses_critic` or `selector_model` so tables do not mislead readers.

### 4. Strong-side critic condition has an additional confound

Strong actor = qwen_max; external critic = deepseek. Therefore strong free/thin critic arms are not "strong actor plus stronger critic." They are strong actor plus a different model that may be weaker or less reliable as critic.

Interpretation caution:

- If strong free_critic does not improve over strong single, it may mean critic structure adds little.
- It may also mean deepseek is not strong enough or not reliable enough to improve qwen_max.

Suggested audit: inspect deepseek critic verdict quality, revise rate, and substantive critique content for strong-side critic arms.

## Current Seed0 Narrative Skeleton

Fable5 proposes the following seed0 mechanism read:

1. Weak actor: quantity alone fails.
   - single/sc3/bo3 near zero.
2. Weak actor: external capability helps.
   - free_critic is the largest raw-success gain.
3. Weak actor: principles shift success/safety trade-off.
   - thin_critic reduces CF but increases UNMANAGED.
4. Weak actor: diversity plus actor-side selection helps closure/recovery without external critic.
   - team_agg is much higher than team_vote and sc3_agg.
5. Strong actor: step-level committees are mostly flat.
   - most arms are near single.
6. Strong actor: full-trajectory best-of-3 is the main success-rate gain.
   - bo3 is highest but costs about 3x calls/tokens.
7. Strong actor: rubric appears more safety-relevant than success-relevant.
   - actor_rubric and thin_critic reduce CF to zero in seed0.

This should remain a seed0 mechanism read until seed1/seed2 confirm stability.

## Proposed Next Analyses

### A. Confirm seed1 stability before turning seed0 reads into claims

Once seed1 finishes:

- compare weak team_agg effect against seed0
- compare weak free/thin success and CF trade-off
- compare strong bo3 gain
- compare strong actor_rubric CF reduction

### B. Compute oracle@3 for sc3/team arms

Goal: determine whether good actions are present in the proposal pool but buried by the selector.

Especially relevant for:

- weak team_vote 0 vs team_agg 72
- weak sc3_agg 5 vs team_agg 72
- strong committees near single

Potential outputs:

- proposal_pool_has_success_candidate
- selected_candidate_rank
- oracle@3 success estimate

### C. Analyze thin_critic UNMANAGED terminal state

Question: among weak thin_critic's 135 UNMANAGED episodes, how many ended with true batch already in tolerance but no `accept_batch`?

This tests the "budget starvation / did not close" mechanism.

Suggested labels for analysis only:

- unmanaged_in_tolerance
- unmanaged_out_of_tolerance

Do not add new primary outcome categories unless explicitly decided.

### D. Add analysis-side model-role labels

Without changing raw results:

- `uses_critic`: yes/no
- `critic_model_actual`: only for free/thin critic
- `selector_model_actual`: actor for sc3_agg/team_agg; none for vote arms; visible selector for bo3

Purpose: prevent misreading the runner-level `critic` field.

### E. Audit strong-side deepseek critic quality

For strong free/thin critic arms:

- revise rate
- empty/parse-fail rate
- common critique reasons
- examples where critic changed a qwen_max action
- whether changed actions improved or worsened outcome

Purpose: rule out the simple explanation that "the critic did not help because it was not a good enough critic."

### F. Track success and CF separately in figures/slides

Fable5's interpretation reinforces the current figure design:

- success is not enough
- CF is a separate safety axis
- free critic can raise success while increasing CF
- thin critic can reduce CF while increasing UNMANAGED

## Terminology Note

`OVER_CONSERVATIVE` should likely be displayed as `HANDOFF` in plots/slides/paper. The raw label may remain unchanged during ongoing seed1 runs. `HANDOFF` is a neutral terminal behavior label; whether it is good or bad depends on the instance context.

