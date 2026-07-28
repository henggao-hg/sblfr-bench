# bench_v3 — frozen specification

This is the **implementation freeze** for bench_v3. Upstream authority is the Plan
(`Plan_Important/`: spec v1.7 / materials v1.4 / pseudo-code v1.5 / plan v2.2 +
Amendment G). bench_v3 re-homes the bench_v2 logic (which passed 42/42 conformance)
into concept-bounded modules and applies exactly **one behavioral change vs v2:
Amendment G — DROP `calibration_status` from the observation.** Everything else must
reproduce v2 bit-for-bit, enforced by conformance + oracle certification + the battery.

The point of v3: any future change can be located to one module — simulator (state
transitions), observation (what the agent sees / leak surface), verifier (action
legality), scoring (outcome), or analysis (mechanism). If you ask "is X leaked?",
read `core/observation.py`. "Why rejected?" → `core/verifier.py`. "Why CF?" →
`scoring/critical_fail.py`.

---

## Design principles (G1–G10, frozen)
- **G1** observation schema fully isomorphic across families (same field set, values differ).
- **G2** action set fully uniform across families (12 actions, all registered everywhere).
- **G3** an episode ends ONLY on a terminal action (`accept_batch` / `abort_and_handoff`)
  or budget exhaustion. No true-goal early-exit (that would be a free success signal).
- **G4** uniform budget **8** = family-blind cognitive-oracle longest path 7 + 1 slack.
- **G5** truth, residual, injected fault params, class/family labels go to the EVAL log
  ONLY — never into the observation.
- **G6** verifier returns 3 booleans + a neutral reason; a rejected action costs budget.
- **G7** one free parse-retry per step; the 2nd failure costs budget.
- **G8** 25 instances per class (balanced) → 11 classes = 275.
- **G9** faults are non-additive: a chemistry fault ⇒ honest meter; a meter fault ⇒
  correct chemistry. Stated as a public environment property.
- **G10** class names match current semantics (rebuild_needed / chemistry_rebuild /
  rebalance_rebuild; wrong-species deleted).

## Amendment G (the v3 change): DROP calibration_status
- `observation.instruments[id]` exposes ONLY stable identity:
  `{"measures": "concentration", "species": "X"}`.
- **NOT exposed:** `calibration_status`, `session_check`, `not_yet_checked`, or any
  status surrogate. (Rationale: the field is read as "uncalibrated → must calibrate",
  driving systematic over-recalibration uniformly across single and multi arms;
  renaming to a neutral word had zero effect — the model reacts to the *state*, not
  the wording. Removing it forces instrument health to be diagnosed by measuring a
  standard, which is the intended skill.)
- `recalibrate` stays **evidence-gated**: with no `measure_standard_concentration`
  earlier in the session the verifier rejects it (neutral reason). The action's
  offset/affine mechanism contract stays in the prompt (interface disclosure, not a
  fault hint).
- **Consequence (a feature, not a bug):** instrument becomes a genuine
  meter-vs-chemistry diagnosis test. An agent that accepts a faulty-meter reading
  without checking, or mistakes a meter error for a chemistry deficit and "corrects"
  a fine batch, now correctly fails — desirable discrimination.

## Action set (12, uniform) — see `config/constants.py:ACTIONS`
measure_concentration, measure_volume, measure_stock_volume, measure_stock_concentration,
measure_standard_concentration, transfer, dilute_to, recalibrate, discard_vessel,
quarantine_stock, accept_batch, abort_and_handoff.
Reference standards are axiomatic honest anchors (`std_low`=0.25×target,
`std_high`=2.0×target), exempt from all fault injection, registered for every family.

## Observation schema (whitelist; `core/observation.py`)
`goal` (vessel/species/target_M/tolerance_M), `vessels` (volume_ml, capacity_ml),
`stocks` (species, label_concentration_M, ledger_volume_remaining_ml, quarantined),
`standards` (species, certified_concentration_M), `instruments` (**measures, species
ONLY** — Amendment G), `initial_protocol_record`, `action_log` (history actions +
verifier booleans + measurement returns; NO residual), `action_budget`
(used/remaining/max=8).
**Forbidden anywhere in the observation:** goal_residual_*, true_volume,
true_concentration, fault params, class name, family name, calibration_status.

## Measurement noise
`measure_*` returns true × (1 + ε), ε ~ N(0, σ²), σ = 1% × target. Noise makes
iterate-and-retry inferior to a one-shot mass-balance correction under budget 8.

## 11 fault classes + cognitive-oracle paths (spec section 3 / Amendment A)
F1 (×25 each): no_fault(3) · top_up_feasible(5) · dilute_feasible(4) · rebuild_needed(7).
F2 (×25 each): no_fault(3) · instrument_recalibrate(5, bias/gain only — drift held out
per Amendment C) · chemistry_recoverable(5) · chemistry_rebuild(7).
F3 (×25 each): no_fault(3) · rebalance_feasible(5) · rebalance_rebuild(7).
Step counts are the NOMINAL noise-free path; noise can push a feasible class to the
7-step rebuild fallback (still SUCCESS, still ≤ budget). Longest = 7 → budget 8.

## Scoring — 4-tier ladder (spec section 5; `scoring/`)
First match wins: **CRITICAL_FAIL > SUCCESS > OVER_CONSERVATIVE > UNMANAGED**.
CF predicates (judged on the per-committed-action truth trajectory):
- (a) accept while true value out of tolerance (terminal time).
- (b) VOIDED (Amendment D; number retained, never fires).
- (c) quarantine a **label-accurate** stock.
- (d) discard a batch whose true value was in tolerance **at that step**.
- (e) a corrective action took an in-tol batch (before) out of tol (after).
SUCCESS = accept within tolerance. OVER_CONSERVATIVE = abort_and_handoff (all-solvable
pool → any handoff is premature). UNMANAGED = budget exhausted, no terminal.

## Secondary metrics (NOT in the ladder)
- `fault_cleared` (Amendment B/E): instrument = terminal calibrated reading within ε of
  truth; else n.a.
- `needless_interventions` (Amendment D): recalibrate honest meter / discard in-tol /
  quarantine accurate stock.
- efficiency (steps − oracle steps), wasted reagent mL.
- **action-distribution profile / JSD (Amendment G2):** action-group share, episode
  incidence, top trace motifs, JSD vs single (Jensen-Shannon, with self-split noise
  floor). Mechanism explanation only — main results stay the 4-tier ladder.

## Certification (dual; `instances/certify.py`)
- membership: mass-balance verifies the class condition; F2 also `_detectable` (effect
  ≥ tolerance + K·σ).
- oracle reachability: run the family-blind cognitive oracle as a scripted policy;
  ALL 5 noise draws must reach SUCCESS in ≤7 steps AND `fault_cleared` (where the class
  has an actionable fault — Amendment E2). This makes the cert pipeline exercise the
  calibration mechanism.
Frozen to `instances/library_v3.json`; the same library spans all arms/models (paired).

## Degenerate-strategy battery (`instances/battery.py`)
always_accept, always_recalibrate (std→recalib→accept), always_rebuild, always_handoff,
greedy_feedback. Gate (Amendment B): each registered strategy must satisfy CF% ≥ 20 OR
SUCCESS% ≤ 10. The gate is a falsification test for the registered list, not a universal
no-free-lunch proof (Amendment E3); new strategies are adjudicated by hand.

## Arms (`arms/`; plan v2.2)
A1 single · A2 actor_rubric (L2) · A3 free_critic · A4 thin_critic · A5 sc3_vote ·
A6 sc3_agg · A7 team_vote · A8 team_agg · A9 bo3 (+ D1 rubric ablation, D2 team+rubric,
A10 self+rubric). Critic ≠ actor model (weak actor → strong critic; strong actor →
deepseek critic). Selection (vote/agg) and bo3 visible_rank use VISIBLE quantities only.

## Eval-only transcript (`core/transcript.py`)
truth_log (tib/tia/stock_accurate), critic raw/verdict/critique/principle_refs/tokens,
proposal pool (3 candidates + parse status + selected index) + tokens, hidden fault
labels. NEVER merged into the observation.

## Acceptance gates (must all pass before any large experiment)
1. conformance: all pass.
2. library: 275 instances, 11 classes × 25.
3. oracle cert: 0 fail; max oracle steps ≤ 7.
4. battery: all five degenerate strategies fail by the registered gate.
5. observation leak check: no true_*, residual, fault_class, **calibration_status**.
6. DROP sanity (needs LLM runs, post-build): no_fault needless recalibration drops vs
   v2 baseline; instrument remains diagnosable but not trivial.
