# cross_model_family

Cross model-family generalization probe (ablation-suite A5). Runs the existing
frozen benchmark (275 instances, existing arms, existing scoring) with a model
from a different family than Qwen and DeepSeek, to test whether the findings
generalize to a third-party model.

Self-contained: everything specific to this probe lives in this folder. It
reuses the frozen benchmark code read-only (run_sweep, load_library, arms,
scoring) and never modifies it. The new model is registered locally here, not
in the shared config.py. Results are written to bench_v3/results/.
