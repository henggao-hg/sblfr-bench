# Tier-1 cross-seed — Data Health (Plan §1, seeds [0, 1, 2])

| group | seed | actor | critic | rows | arms(275) | dup_keys | parse_fails | runtime_errors | max_act | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| strong | 0 | qwen_max | deepseek | 2475 | 9/9 | 0 | 0 | 0(grp) | 8 | OK |
| strong | 1 | qwen_max | deepseek | 2475 | 9/9 | 0 | 3 | 0(grp) | 8 | OK |
| strong | 2 | qwen_max | deepseek | 2475 | 9/9 | 0 | 0 | 0(grp) | 8 | OK |
| weak | 0 | qwen32b | qwen_max | 2475 | 9/9 | 0 | 0 | 0(grp) | 8 | OK |
| weak | 1 | qwen32b | qwen_max | 2475 | 9/9 | 0 | 0 | 0(grp) | 8 | OK |
| weak | 2 | qwen32b | qwen_max | 2475 | 9/9 | 0 | 0 | 0(grp) | 8 | OK |

runtime_errors counted per group across all seed logs.
