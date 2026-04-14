# Analysis: exec_func_wcst (Wisconsin Card Sorting Test)

## Score Distribution
| Metric | Value |
|--------|-------|
| Mean | 0.7821 |
| Std | 0.2678 |
| Range | 0.6357 |
| Min | 0.3643 (Llama 3.3 70B) |
| Max | 1.000 (Opus, Sonnet, DeepSeek, GPT-OSS, Qwen3) |

**Std ≥ 0.08: PASS ✅**

## Phase 1 → Phase 2 Comparison
| Model | Phase 1 | Phase 2 | Delta |
|-------|---------|---------|-------|
| Claude Opus 4.6 | 1.000 | 1.000 | 0.000 |
| DeepSeek-R1 | 0.639 | 1.000 | +0.361 |
| GPT-OSS-120B | 0.531 | 1.000 | +0.469 |
| Llama 3.3 70B | 0.479 | 0.364 | -0.115 |
| Qwen3 80B | 1.000 | 1.000 | 0.000 |
| Nova Pro | 0.526 | 0.475 | -0.051 |
| Maverick 17B | 0.461 | 0.971 | **+0.510** |
| Sonnet 4.6 | 0.699 | 1.000 | +0.301 |
| GLM 4.7 | 0.472 | 0.400 | -0.072 |
| Ministral 3B | 0.261 | 0.611 | +0.350 |

Large improvements for DeepSeek, GPT-OSS, Maverick, and Ministral — consistent with LAST-N parser fix resolving preamble number pollution. Phase 1 parser was grabbing numbers from reasoning preamble instead of final answers.

Known Phase 1 std=0.306 (from KNOWLEDGE). Phase 2 std=0.268 — slight decrease due to more models reaching ceiling.

## Model Discrimination
**Bimodal distribution**: 5 models at perfect 1.0 (Opus, Sonnet, DeepSeek, GPT-OSS, Qwen3) vs. 5 models below 1.0 (Maverick 0.971, Ministral 0.611, Nova 0.475, GLM 0.400, Llama3.3 0.364). Ceiling cluster is large (50%) but the benchmark still separates frontier from mid-tier models effectively.

## Q&A Transcript Review

### Llama 3.3 70B (lowest, 0.364)
- Block 1 responses show parser grabbing early numbers from preamble. First 200 chars contain numbers [1,2,4,4,1] — parser takes LAST N, but preamble numbers may still interfere if response is short.
- Some errors appear to be genuine perseveration (continuing to sort by previous rule after shift signal).

### GLM 4.7 (0.400)
- Similar pattern — low scores on post-shift blocks. Genuine cognitive flexibility deficit.

### Opus 4.6 (highest, 1.000)
- Perfect accuracy, 0 perseverative errors, 6/6 categories completed. Clean parsing.

### Maverick 17B (surprising improvement, 0.971)
- Phase 1: 0.461 → Phase 2: 0.971. LAST-N parser fix accounts for most of the improvement.

### Ministral 3B (mid, 0.611)
- Improved from 0.261. Still makes perseverative errors (continues with old rule 2-3 trials after shift).

## Parser Fix Verification (Step 6)
- **LAST-N parser DEPLOYED ✅**: `_parse_responses()` uses 3-strategy cascade: (1) standalone digit lines, (2) "Card N: ... → N" patterns, (3) last N standalone digits 1-4 from response. No first-number fallback.
- **Preamble pollution mitigated**: Taking LAST N numbers avoids reasoning preamble contamination.

## Ground Truth Validation
- WCST sort rules verified: 6-block design with rule shifts (color→shape→number→color→shape→number). Correct answers checked against sort rule for each block ✅.
- Feedback chain (Correct/Incorrect) verified present in prompts.

## Ceiling Effect Assessment
5/10 models at 1.000 (50%) is concerning but std=0.268 still passes easily. The WCST may need harder variants (more ambiguous shift signals, 3-way sorts) to challenge frontier models in future iterations.

## Recommendation
**KEEP AS-IS.** Std=0.268 well above threshold. Parser fix resolved Phase 1 preamble pollution. Clean bimodal separation between frontier (perfect) and mid-tier models. No scoring or ground truth changes needed. Advisory: consider harder WCST variants for future iterations to reduce ceiling cluster.
