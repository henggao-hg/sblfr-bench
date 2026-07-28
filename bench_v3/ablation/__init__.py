"""Ablation suite (harness-layer-only ablations, per the ablation-suite spec v1.0).

bench_v3 frozen code is imported, NEVER modified: environment / verifier / scoring /
instance library / prompts are all reused as-is; each ablation changes only the prompt or
a deterministic wrapper around the actor, lands under a NEW arm name, and writes the
standard metrics + transcript double-jsonl. Decision lines are pre-registered in the spec
and must not move after running.

Arms (one file each; all weak by default, seed0):
  a1_rubric_reassert.py  -- rubric_reassert : actor_rubric + restate the 9 principles each user turn
  a2_single_stoprule.py  -- single_stoprule : single wrapped by a deterministic in-tolerance -> accept rule
  a3_single_personaB.py  -- single_personaB: single with persona B's decisive-style line in the system prompt

Driver: run_ablation.py.
"""
