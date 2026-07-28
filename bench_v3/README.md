# bench_v3

Clean modular rebuild of the SBLFR-Chem recovery benchmark. Same logic as bench_v2
(which passed 42/42 conformance), re-homed into concept-bounded modules, with exactly
one behavioral change: **Amendment G — `calibration_status` is dropped from the
observation** (instrument health must be diagnosed by measuring a standard). The frozen
contract is in [`SPEC.md`](SPEC.md); upstream authority is `../Plan_Important/`.

Why the rebuild: in bench_v2 a small change (a logging field, a prompt word) could not
be localized — `env.py` and `arms.py` were monolithic. In v3 each concern is one file,
so any future change is attributable and the frozen decisions (DROP-F2, 4-tier scoring,
oracle certification, action-profile audit) live in clear modules.

## Module map
```
config/     constants.py (frozen scalars + registries), sweep configs
core/       actions, state, observation (LEAK SURFACE), simulator, verifier, episode, transcript
families/   f1_transfer, f2_instrument (DROP), f3_reagent, registry — sampling + membership
instances/  oracle, certify, generate, battery, library_v3.json
prompts/    base_actor, rubrics, personas, critic, aggregator, render (materials v1.4 verbatim)
arms/       single, actor_rubric, critic, sc3, team, bo3, registry
scoring/    outcomes, critical_fail, secondary, action_profile
runners/    run_sweep, run_arm, resume, dry_run
analysis/   summarize, paired_stats, plot_*, critic_audit, proposal_audit, render_transcripts
tests/      no-leak, recalibrate-gate, oracle-cert, scoring-predicates, action-profile
scripts/    freeze_library, run_battery, conformance_check
```
The two records that must NEVER mix: `core/observation.py` (what the agent sees —
whitelist) and `core/transcript.py` (eval-only: truth, critic, proposals, tokens, fault labels).

## Build order (each gate must pass before the next)
1. **skeleton** — dirs, SPEC.md, config/constants.py, README (this).  ← current
2. **core** — actions/state/observation/simulator/verifier/episode/transcript. Gate: scripted oracle runs one instance end-to-end.
3. **families + instances** — 11 classes, smoke, then freeze `library_v3.json`.
4. **scoring** — pass the v2 CF/SUCCESS/OVER/UNMANAGED predicate cases.
5. **oracle + battery** — oracle 0 fail, max steps ≤ 7, battery five-strategy disaster signatures.
6. **arms** — A1/A2 → critic → sc3/team/bo3, each unit-tested with a fake deterministic model.
7. **analysis + exports** — action profile / JSD / motifs (secondary); compact+detailed
   readable exports (JSONL + Markdown), VISIBLE / EVAL-ONLY separated.
8. **tests + scripts** — conformance + leak/gate/cert/scoring/profile tests.

## Verify (target, once built)
```
python -m bench_v3.scripts.conformance_check     # all pass
python -m bench_v3.scripts.run_battery           # five strategies trip the gate
python -m bench_v3.scripts.freeze_library        # 275 instances, 11 classes x25, 0 oracle fail, <=7
```

## Status (steps 1–8 built; all scriptable gates green)
- core / families / scoring / instances / prompts / arms / runners / analysis / scripts / tests all implemented.
- **Gates:** master conformance 22/22 PASS; `library_v3.json` = 275 (11 classes ×25, oracle 0-fail, steps ≤7);
  battery five strategies trip the gate (bit-identical to v2: 36/64, 36/64, 45/55, 0/0, 59/41);
  observation no-leak / Amendment G enforced (instrument view = {measures, species});
  prompts byte-identical to v2; full end-to-end dry_run (fake model, all arms) passes.
- **Reviews:** core + families/scoring/instances reviewed (subagent + codex) clean — codex caught one
  real leak (action_log could echo a policy-injected extra key) → fixed via strict redact whitelist.
  arms/runners/analysis review in progress.
- **Pending (needs LLM runs):** DROP-sanity gate — confirm no_fault needless-recalibration drops vs v2
  and instrument stays diagnosable-but-not-trivial; then S0/S1 on v3.
- bench_v2 stays intact as the reference / regression baseline (committed `24e1277`).

## Tests / verify
```
for t in test_observation_no_leak test_core_smoke test_families_membership test_scoring_predicates \
         test_oracle_cert test_arms test_prompts_verbatim test_action_profile; do python -m bench_v3.tests.$t; done
python -m bench_v3.scripts.conformance_check     # 22/22
python -m bench_v3.scripts.freeze_library        # 275, 11x25, steps<=7
python -m bench_v3.scripts.run_battery           # gate PASSED
python -m bench_v3.runners.dry_run               # end-to-end, no API
```
