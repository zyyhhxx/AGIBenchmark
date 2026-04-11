# Per-Track Discriminatory Analysis — Non-Metacognition Benchmarks

Generated from Bedrock multi-model runs (10 models).

## Track: learning

| Benchmark | N_models | Mean | Std | Min | Max | Range |
|-----------|----------|------|-----|-----|-----|-------|
| learning_curves | 9 | 0.654 | 0.064 | 0.547 | 0.727 | 0.180 |
| learning_transfer | 10 | 0.785 | 0.241 | 0.280 | 1.000 | 0.720 |
| learning_interference | 10 | 0.547 | 0.258 | 0.120 | 1.000 | 0.880 |
| learning_curriculum | 10 | 0.638 | 0.106 | 0.460 | 0.760 | 0.300 |

## Track: attention

| Benchmark | N_models | Mean | Std | Min | Max | Range |
|-----------|----------|------|-----|-----|-----|-------|
| attention_selective | 10 | 0.888 | 0.052 | 0.775 | 0.950 | 0.175 |
| attention_vigilance | 10 | 0.758 | 0.167 | 0.568 | 1.000 | 0.432 |
| attention_divided | 10 | 0.836 | 0.158 | 0.414 | 0.938 | 0.524 |
| attention_instruction_update | 10 | 0.856 | 0.215 | 0.299 | 0.983 | 0.684 |

## Track: executive_functions

| Benchmark | N_models | Mean | Std | Min | Max | Range |
|-----------|----------|------|-----|-----|-----|-------|
| exec_func_wcst | 10 | 0.607 | 0.225 | 0.261 | 1.000 | 0.739 |
| exec_func_tol | 9 | 0.247 | 0.279 | 0.000 | 0.800 | 0.800 |
| exec_func_task_switch | 10 | 0.881 | 0.110 | 0.713 | 1.000 | 0.287 |
| exec_func_nback | 9 | 0.889 | 0.171 | 0.514 | 1.000 | 0.486 |
| exec_func_crt | 10 | 0.681 | 0.143 | 0.454 | 0.914 | 0.460 |

## Track: social_cognition

| Benchmark | N_models | Mean | Std | Min | Max | Range |
|-----------|----------|------|-----|-----|-----|-------|
| social_cog_false_belief | 10 | 0.710 | 0.169 | 0.377 | 1.000 | 0.623 |
| social_cog_pragmatic | 9 | 0.751 | 0.212 | 0.304 | 0.956 | 0.652 |
| social_cog_sarcasm | 10 | 0.839 | 0.133 | 0.464 | 0.945 | 0.481 |
| social_cog_emotional_prosody | 10 | 0.808 | 0.047 | 0.686 | 0.858 | 0.172 |

## Per-Model Summary (Non-Metacog Tracks)

| Model | N_benchmarks | Mean Score | Std |
|-------|-------------|------------|-----|
| Claude Opus 4.6 | 17 | 0.830 | 0.212 |
| DeepSeek-R1 | 17 | 0.765 | 0.233 |
| GPT-OSS-120B | 17 | 0.803 | 0.198 |
| Llama 3.3 70B | 17 | 0.701 | 0.223 |
| Qwen3 Next 80B | 13 | 0.827 | 0.130 |
| Nova Pro | 17 | 0.625 | 0.168 |
| Llama 4 Maverick 17B | 17 | 0.718 | 0.262 |
| Claude Sonnet 4.6 | 17 | 0.806 | 0.225 |
| GLM 4.7 | 17 | 0.732 | 0.247 |
| Ministral 3B | 17 | 0.519 | 0.191 |

## Top Discriminating Benchmarks (by std)

| Rank | Benchmark | Track | Std | Range | N |
|------|-----------|-------|-----|-------|---|
| 1 | exec_func_tol | executive_functions | 0.279 | 0.800 | 9 |
| 2 | learning_interference | learning | 0.258 | 0.880 | 10 |
| 3 | learning_transfer | learning | 0.241 | 0.720 | 10 |
| 4 | exec_func_wcst | executive_functions | 0.225 | 0.739 | 10 |
| 5 | attention_instruction_update | attention | 0.215 | 0.684 | 10 |
| 6 | social_cog_pragmatic | social_cognition | 0.212 | 0.652 | 9 |
| 7 | exec_func_nback | executive_functions | 0.171 | 0.486 | 9 |
| 8 | social_cog_false_belief | social_cognition | 0.169 | 0.623 | 10 |
| 9 | attention_vigilance | attention | 0.167 | 0.432 | 10 |
| 10 | attention_divided | attention | 0.158 | 0.524 | 10 |
