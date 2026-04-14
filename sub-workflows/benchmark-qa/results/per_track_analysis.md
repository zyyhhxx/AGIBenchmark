# Per-Track Discriminatory Analysis

Generated from 10 Bedrock models across 26 benchmarks (258/260 cells filled).

Missing: Qwen3 Next 80B × learning_curves, Qwen3 Next 80B × exec_func_nback (OOM-killed consistently).


## Attention

| Benchmark | Mean | Std | Min | Max | Range | N |
|-----------|------|-----|-----|-----|-------|---|
| attention_divided | 0.8356 | 0.1666 | 0.4139 | 0.9375 | 0.5236 | 10 |
| attention_instruction_update | 0.8560 | 0.2264 | 0.2992 | 0.9833 | 0.6841 | 10 |
| attention_selective | 0.8880 | 0.0544 | 0.7750 | 0.9500 | 0.1750 | 10 |
| attention_vigilance | 0.7581 | 0.1762 | 0.5677 | 1.0000 | 0.4323 | 10 |

**Track discriminatory power:** avg_range=0.4537, avg_std=0.1559
- Most discriminatory: **attention_instruction_update** (range=0.6841)
- Least discriminatory: **attention_selective** (range=0.1750)

## Learning

| Benchmark | Mean | Std | Min | Max | Range | N |
|-----------|------|-----|-----|-----|-------|---|
| learning_curriculum | 0.6380 | 0.1121 | 0.4600 | 0.7600 | 0.3000 | 10 |
| learning_curves | 0.6541 | 0.0682 | 0.5467 | 0.7267 | 0.1800 | 9 |
| learning_interference | 0.5474 | 0.2719 | 0.1200 | 1.0000 | 0.8800 | 10 |
| learning_transfer | 0.7850 | 0.2545 | 0.2800 | 1.0000 | 0.7200 | 10 |

**Track discriminatory power:** avg_range=0.5200, avg_std=0.1767
- Most discriminatory: **learning_interference** (range=0.8800)
- Least discriminatory: **learning_curves** (range=0.1800)

## Executive Functions

| Benchmark | Mean | Std | Min | Max | Range | N |
|-----------|------|-----|-----|-----|-------|---|
| exec_func_crt | 0.6814 | 0.1503 | 0.4542 | 0.9142 | 0.4600 | 10 |
| exec_func_nback | 0.8892 | 0.1816 | 0.5136 | 1.0000 | 0.4864 | 9 |
| exec_func_task_switch | 0.8811 | 0.1161 | 0.7125 | 1.0000 | 0.2875 | 10 |
| exec_func_tol | 0.2517 | 0.2797 | 0.0000 | 0.8000 | 0.8000 | 10 |
| exec_func_wcst | 0.6068 | 0.2372 | 0.2607 | 1.0000 | 0.7393 | 10 |

**Track discriminatory power:** avg_range=0.5546, avg_std=0.1930
- Most discriminatory: **exec_func_tol** (range=0.8000)
- Least discriminatory: **exec_func_task_switch** (range=0.2875)

## Social Cognition

| Benchmark | Mean | Std | Min | Max | Range | N |
|-----------|------|-----|-----|-----|-------|---|
| social_cog_emotional_prosody | 0.8082 | 0.0491 | 0.6856 | 0.8578 | 0.1722 | 10 |
| social_cog_false_belief | 0.7101 | 0.1776 | 0.3771 | 1.0000 | 0.6229 | 10 |
| social_cog_pragmatic | 0.7328 | 0.2199 | 0.3041 | 0.9560 | 0.6519 | 10 |
| social_cog_sarcasm | 0.8390 | 0.1407 | 0.4636 | 0.9450 | 0.4814 | 10 |

**Track discriminatory power:** avg_range=0.4821, avg_std=0.1468
- Most discriminatory: **social_cog_pragmatic** (range=0.6519)
- Least discriminatory: **social_cog_emotional_prosody** (range=0.1722)

## Metacognition

| Benchmark | Mean | Std | Min | Max | Range | N |
|-----------|------|-----|-----|-----|-------|---|
| metacog_calibration | 0.1651 | 0.3323 | 0.0000 | 0.9984 | 0.9984 | 10 |
| metacog_canary | 0.7951 | 0.3052 | 0.0000 | 1.0000 | 1.0000 | 10 |
| metacog_control | 0.5493 | 0.1810 | 0.2000 | 0.7479 | 0.5479 | 10 |
| metacog_epistemic_humility | 0.7881 | 0.2204 | 0.2000 | 0.9200 | 0.7200 | 10 |
| metacog_epistemic_revision | 0.8007 | 0.1018 | 0.6700 | 0.9600 | 0.2900 | 10 |
| metacog_error_detection | 0.8620 | 0.0769 | 0.7479 | 0.9735 | 0.2256 | 10 |
| metacog_fok | 0.5606 | 0.0827 | 0.4132 | 0.6452 | 0.2320 | 10 |
| metacog_jol | 0.3930 | 0.0905 | 0.2000 | 0.4647 | 0.2647 | 10 |
| metacog_learning_monitoring | 0.8344 | 0.0813 | 0.6906 | 0.9101 | 0.2195 | 10 |

**Track discriminatory power:** avg_range=0.4998, avg_std=0.1636
- Most discriminatory: **metacog_canary** (range=1.0000)
- Least discriminatory: **metacog_learning_monitoring** (range=0.2195)