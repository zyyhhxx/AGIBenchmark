# Analysis: attention_vigilance

## Score Distribution

| Model | Score |
|-------|-------|
| DeepSeek-R1 | 1.0000 |
| GPT-OSS-120B | 1.0000 |
| Claude Sonnet 4.6 | 0.8647 |
| Claude Opus 4.6 | 0.8559 |
| Llama 4 Maverick 17B | 0.8559 |
| Qwen3 Next 80B | 0.7073 |
| Nova Pro | 0.6329 |
| Ministral 3B | 0.5856 |
| Llama 3.3 70B | 0.5653 |
| GLM 4.7 | 0.5599 |

- **Mean:** 0.7628
- **Std:** 0.1738 ✅ (≥0.08)
- **Range:** 0.4401
- **N models:** 10/10, 0 failures

## Phase 1 Comparison

| Metric | Phase 1 | Phase 2 | Delta |
|--------|---------|---------|-------|
| Mean | 0.7581 | 0.7628 | +0.0047 |
| Std | 0.1762 | 0.1738 | -0.0025 |

Virtually identical across phases — highly stable benchmark.

## Model Discrimination

Three distinct performance tiers:
1. **Perfect (1.0):** DeepSeek-R1, GPT-OSS-120B — both achieve perfect N-back accuracy
2. **Strong (0.86):** Claude Opus, Claude Sonnet, Llama 4 Maverick — consistent ~85% accuracy
3. **Weak (0.56–0.71):** Qwen3, Nova Pro, Ministral 3B, Llama 3.3 70B, GLM 4.7

The 4-back condition is the primary discriminator — hit rate drops from ~0.75 (top models) to ~0.23 (bottom models).

## Q&A Transcript Review

### Transcript structure
14 entries per model (segments of N-back task: mix of 3-back and 4-back). Each entry contains `prompt` (sequence + instructions), `response` (JSON array of YES/NO), and aggregate scoring in summary files. Individual `correct_answer`, `parsed_answer`, `score` fields are null — scoring happens at the aggregate level by comparing response arrays against computed ground truth.

### Scoring correctness — Manual ground truth verification

**q_001 (3-back):** Sequence [H, V, R, B, H, R, B, B, L, B], respond at positions 3-9:
- pos3=B vs pos0=H → NO ✓
- pos4=H vs pos1=V → NO ✓
- pos5=R vs pos2=R → YES ✓
- pos6=B vs pos3=B → YES ✓
- pos7=B vs pos4=H → NO ✓
- pos8=L vs pos5=R → NO ✓
- pos9=B vs pos6=B → YES ✓

**Ground truth: [NO, NO, YES, YES, NO, NO, YES]**

| Model | Response | Correct |
|-------|----------|---------|
| DeepSeek-R1 | [NO, NO, YES, YES, NO, NO, YES] | 7/7 ✅ |
| GPT-OSS-120B | [NO, NO, YES, YES, NO, NO, YES] | 7/7 ✅ |
| Llama 3.3 70B | [NO, NO, NO, NO, YES, NO, NO] | 3/7 ❌ |
| GLM 4.7 | [NO, YES, NO, NO, YES, NO, NO] | 2/7 ❌ |

Ground truth confirmed correct. Llama 3.3 70B and GLM 4.7 genuinely fail at 3-back tracking.

### Suspicious findings

- **Llama 3.3 70B runtime: 4.1s** for 14 segments is extremely fast (vs. DeepSeek-R1 at 42.3s, Claude Opus at 71.7s). With 413 output tokens total across 14 calls, this averages <0.3s per segment. The model is likely pattern-matching or defaulting to "NO" arrays without actually computing N-back matches. This is not a scoring bug — the model genuinely performs poorly because it's not investing computation.
- **GLM 4.7 backtick fences:** Responses wrapped in ````json ... ``` `` — parser handles this correctly (score=0.5599 reflects genuine errors, not parse failures).
- **Ministral 3B backtick fences + comments:** Some responses include inline comments (`// [10] P vs [7] B`). Parser appears to handle this correctly for vigilance since it extracts YES/NO arrays, but worth monitoring.

### Parsing artifacts
- **Think-tag leakage:** None detected.
- **JSON extraction failures:** None — all models produce parseable YES/NO arrays (backtick fences stripped correctly).
- **Claude Opus reasoning preamble:** "I need to check each marked position against the letter 3 positions earlier..." — reasoning precedes the JSON array. Parser correctly extracts the array from the end of response.

## Ground Truth Validation

Manually verified 3 segments (q_001, q_002 partial, q_003 partial) against N-back rules:
- All computed ground truth values are correct.
- N-back sequences use confusable letter pairs (B/D/P, M/N/L) as documented in KNOWLEDGE — this is intentional difficulty, not ambiguity.
- **No debatable items.** N-back has deterministic ground truth (exact letter matching).

## Recommendation

**KEEP AS-IS.**

Excellent benchmark (std=0.1738, range=0.4401). Clear three-tier separation with good spread. Two models at ceiling (1.0) is acceptable — the 4-back condition would need 5-back or 6-back to separate them further, which risks becoming too difficult for weaker models. Ground truth is deterministic and verified. The Llama 3.3 70B speed anomaly (4.1s) is interesting behavioral data, not a bug — it suggests the model invests minimal computation on this task, leading to low accuracy.
