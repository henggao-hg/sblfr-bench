# Tier-1 seed0 — Data Health (Plan §1)

seed0 only. weak_seed1/strong_seed1 excluded by design.

| group | actor | critic | seed | metrics_rows | transcript_rows | arms_complete(275) | dup_keys | key_match | parse_fails | runtime_errors | max_actions_used | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| strong | qwen_max | deepseek | 0 | 2475 | 2475 | 9/9 | 0 | 0 mismatch | 0 | 0 (logs_tier1_strong.out) | 8 | OK |
| weak | qwen32b | qwen_max | 0 | 2475 | 2475 | 9/9 | 0 | 0 mismatch | 0 | 0 (logs_tier1_weak.out) | 8 | OK |

- key_match = transcript vs metrics agreement on (arm,seed,instance)->(outcome,actions_used). Key-level (order-insensitive); duplicate keys are caught separately by dup_keys.
- runtime_errors = count of lines matching Traceback/RuntimeError/ERROR/Exception in the seed0 run log(s); 'no log found' if the log file is absent.
