# Discriminatory Power Analysis
**Models:** 10 | **Benchmarks:** 26
**Models tested:** Claude Opus 4.6, Claude Sonnet 4.6, DeepSeek-R1, GLM 4.7, GPT-OSS-120B, Llama 3.3 70B, Llama 4 Maverick 17B, Ministral 3B, Nova Pro, Qwen3 Next 80B

## Summary Table

| Benchmark | Mean | Std | Min | Max | Range | N Valid | Flag |
|-----------|------|-----|-----|-----|-------|---------|------|
| attention_divided | 0.714 | 0.193 | 0.414 | 0.927 | 0.514 | 4 |  |
| attention_instruction_update | 0.710 | 0.277 | 0.299 | 0.975 | 0.676 | 4 |  |
| attention_selective | 0.880 | 0.054 | 0.820 | 0.950 | 0.130 | 3 |  |
| attention_vigilance | 0.647 | 0.121 | 0.568 | 0.856 | 0.288 | 4 |  |
| exec_func_crt | 0.538 | 0.060 | 0.454 | 0.612 | 0.157 | 4 |  |
| exec_func_nback | 0.751 | 0.177 | 0.514 | 1.000 | 0.486 | 4 |  |
| exec_func_task_switch | 0.792 | 0.099 | 0.713 | 0.959 | 0.246 | 4 |  |
| exec_func_tol | 0.038 | 0.066 | 0.000 | 0.153 | 0.153 | 4 |  |
| exec_func_wcst | 0.467 | 0.007 | 0.461 | 0.479 | 0.018 | 4 | ⚠️ LOW VAR |
| learning_curriculum | 0.650 | 0.114 | 0.460 | 0.760 | 0.300 | 4 |  |
| learning_curves | 0.626 | 0.063 | 0.547 | 0.717 | 0.170 | 5 |  |
| learning_interference | 0.440 | 0.037 | 0.400 | 0.500 | 0.100 | 5 | ⚠️ LOW VAR |
| learning_transfer | 0.646 | 0.260 | 0.280 | 1.000 | 0.720 | 5 |  |
| metacog_calibration | 0.218 | 0.362 | 0.000 | 0.998 | 0.998 | 7 |  |
| metacog_canary | 0.795 | 0.290 | 0.000 | 1.000 | 1.000 | 10 |  |
| metacog_control | 0.563 | 0.176 | 0.200 | 0.748 | 0.548 | 9 |  |
| metacog_epistemic_humility | 0.773 | 0.215 | 0.200 | 0.920 | 0.720 | 9 |  |
| metacog_epistemic_revision | 0.815 | 0.097 | 0.720 | 0.960 | 0.240 | 7 |  |
| metacog_error_detection | 0.871 | 0.072 | 0.748 | 0.974 | 0.226 | 9 |  |
| metacog_fok | 0.577 | 0.064 | 0.415 | 0.645 | 0.230 | 9 |  |
| metacog_jol | 0.389 | 0.090 | 0.200 | 0.465 | 0.265 | 9 |  |
| metacog_learning_monitoring | 0.828 | 0.079 | 0.691 | 0.910 | 0.220 | 9 |  |
| social_cog_emotional_prosody | 0.794 | 0.063 | 0.686 | 0.838 | 0.153 | 4 |  |
| social_cog_false_belief | 0.967 | 0.029 | 0.930 | 1.000 | 0.070 | 3 | ⚠️ CEILING |
| social_cog_pragmatic | 0.857 | 0.036 | 0.824 | 0.912 | 0.088 | 4 | ⚠️ LOW VAR |
| social_cog_sarcasm | 0.760 | 0.177 | 0.464 | 0.924 | 0.460 | 4 |  |

## Flagged Benchmarks

### Ceiling Effect (all scores > 0.9)
- **social_cog_false_belief**: mean=0.967, std=0.029, scores=[1.0, 0.97, 0.93]

### Low Variance (std < 0.05)
- **exec_func_wcst**: mean=0.467, std=0.007, scores=[0.479, 0.461, 0.465, 0.465]
- **learning_interference**: mean=0.440, std=0.037, scores=[0.5, 0.4, 0.4, 0.45, 0.45]
- **social_cog_pragmatic**: mean=0.857, std=0.036, scores=[0.868, 0.912, 0.824, 0.824]


## Overall: 4/26 benchmarks flagged
