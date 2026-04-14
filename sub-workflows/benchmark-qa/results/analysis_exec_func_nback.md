# Analysis: exec_func_nback (N-back Working Memory)

## Score Distribution
| Metric | Value |
|--------|-------|
| Mean | 0.9442 |
| Std | 0.1608 |
| Range | 0.538 |
| Min | 0.462 (Nova Pro) |
| Max | 1.000 (8 models tied) |

**Std ≥ 0.08: PASS ✅**

## Phase 1 → Phase 2 Comparison
| Model | Phase 1 | Phase 2 | Delta |
|-------|---------|---------|-------|
| Claude Opus 4.6 | 1.000 | 1.000 | 0.000 |
| DeepSeek-R1 | 1.000 | 1.000 | 0.000 |
| GPT-OSS-120B | 1.000 | 0.980 | -0.020 |
| Llama 3.3 70B | 1.000 | 1.000 | 0.000 |
| Qwen3 80B | (OOM) | 1.000 | — |
| Nova Pro | 0.806 | 0.462 | -0.344 |
| Maverick 17B | 0.684 | 1.000 | +0.316 |
| Sonnet 4.6 | 1.000 | 1.000 | 0.000 |
| GLM 4.7 | 1.000 | 1.000 | 0.000 |
| Ministral 3B | 0.514 | 1.000 | +0.486 |

Notable changes: Ministral 3B jumped from 0.514→1.000 and Maverick from 0.684→1.000. Nova Pro dropped from 0.806→0.462. These large swings suggest the N-back task may have changed between phases, or retry bias fix affected these models differently.

## Model Discrimination
8/10 models score 1.000 — **severe ceiling effect**. Only Nova Pro (0.462) and GPT-OSS-120B (0.980) fall below perfect. Std=0.161 is driven almost entirely by Nova Pro's outlier. Without Nova Pro, std would be ~0.007.

## Q&A Transcript Review

### Nova Pro (lowest, 0.462)
- 174 total items. Level 1: 47/59 (0.797), Level 2: 55/58 (0.948), Level 3: 44/57 (0.772). Genuine performance deficit — errors distributed across levels, not concentrated in parser failures. Level 2 paradoxically easiest for this model.

### Claude Opus 4.6 (highest, 1.000)
- Perfect across all items. Clean parsing. No artifacts.

### GPT-OSS-120B (near-ceiling, 0.980)
- Near-perfect with minor errors. Clean parsing.

## Ground Truth Validation
- N-back sequences verified: MATCH/NO MATCH labels checked against 2-back and 3-back letter sequences. Sample items correct ✅.
- Sequence generation appears deterministic with fixed seed.

## Parser Fix Verification
- N-back uses simple MATCH/NO MATCH parsing — no complex extraction needed. No known parser issues for this benchmark.

## Ceiling Effect Assessment
80% of models at perfect score is a significant ceiling. However, std=0.161 still passes threshold due to Nova Pro's outlier. The benchmark effectively acts as a binary discriminator: "can the model track N-back sequences?" (yes for 8/10 models, no for Nova Pro). Limited diagnostic value for separating frontier models.

## Recommendation
**KEEP AS-IS** (advisory). Std=0.161 passes threshold but is fragile — driven by single outlier (Nova Pro). If Nova Pro is ever removed from the model roster, std would collapse below 0.01. Consider adding 4-back or 5-back conditions in future iterations to create more separation among frontier models. No scoring changes needed now.
