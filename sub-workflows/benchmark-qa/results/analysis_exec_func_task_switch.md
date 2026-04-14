# Analysis: exec_func_task_switch (Task Switching)

## Score Distribution
| Metric | Value |
|--------|-------|
| Mean | 0.8212 |
| Std | 0.1509 |
| Range | 0.470 |
| Min | 0.530 (Maverick 17B) |
| Max | 1.000 (Opus 4.6, DeepSeek-R1, GPT-OSS-120B) |

**Std ≥ 0.08: PASS ✅**

## Phase 1 → Phase 2 Comparison
| Model | Phase 1 | Phase 2 | Delta |
|-------|---------|---------|-------|
| Claude Opus 4.6 | 1.000 | 1.000 | 0.000 |
| DeepSeek-R1 | 1.000 | 1.000 | 0.000 |
| GPT-OSS-120B | 1.000 | 1.000 | 0.000 |
| Llama 3.3 70B | 0.723 | 0.705 | -0.018 |
| Qwen3 80B | 0.810 | 0.823 | +0.013 |
| Nova Pro | 0.713 | 0.700 | -0.013 |
| Maverick 17B | 0.959 | 0.530 | **-0.429** |
| Sonnet 4.6 | 0.901 | 0.751 | -0.150 |
| GLM 4.7 | 0.932 | 0.929 | -0.003 |
| Ministral 3B | 0.775 | 0.775 | 0.000 |

Phase stability is good for most models (delta <0.02). Notable regression: Maverick 17B dropped -0.429 — investigated below. Sonnet 4.6 dropped -0.150.

Known Phase 1 std=0.124 (from KNOWLEDGE). Phase 2 std=0.151 — improved discrimination.

## Model Discrimination
Good spread. Non-monotonic pattern confirmed: Ministral 3B (0.775) outscores Maverick 17B (0.530). Three models at ceiling (1.000). GLM 4.7 strong at 0.929. The task genuinely measures cognitive flexibility rather than raw model size.

## Q&A Transcript Review

### Maverick 17B (lowest, 0.530)
- 75 total items. 34 failures concentrated in slow_switch and rapid_switch blocks.
- **Root cause**: Maverick re-answers previous items' rules instead of tracking the current rule. In slow_switch block, responses contain reasoning about item #1 even when on item #3+. This is a genuine task-switching failure — the model perseverates on earlier rules.
- Not a parser bug. Parsed answers match what the model actually produced.

### Ministral 3B (surprising high, 0.775)
- First baseline item wrong (answered "odd" for "even"), but subsequent items mostly correct.
- Performs well on batch presentation — able to track rule switches. Surprising for a 3B model.

### Claude Opus 4.6 (highest, 1.000)
- Perfect. Clean parsing across all 75 items.

### Sonnet 4.6 (mid, 0.751)
- Errors concentrated in rapid-switch block. Consistent with switching cost increasing under rapid conditions.

### GLM 4.7 (random, 0.929)
- Near-perfect. Minor errors in rapid-switch block only.

## Ground Truth Validation
- Task switching rules verified: digit-sum parity (odd/even) and letter-position comparison checked. Sample ground truth labels correct ✅.
- Rule switching pattern (baseline → slow → rapid → random) validated.

## Parser Fix Verification
- Task switch uses simple odd/even/before/after parsing — no complex extraction needed. No known parser issues.

## Recommendation
**KEEP AS-IS.** Std=0.151 well above threshold. Maverick 17B's low score is genuine task-switching perseveration (not a parser bug). Non-monotonic size-performance relationship validates the benchmark as measuring cognitive flexibility specifically. No scoring or ground truth changes needed.
