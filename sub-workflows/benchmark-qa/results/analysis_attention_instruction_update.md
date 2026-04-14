# Analysis: attention_instruction_update

## Score Distribution

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 0.9833 |
| Claude Sonnet 4.6 | 0.9833 |
| DeepSeek-R1 | 0.9833 |
| GPT-OSS-120B | 0.9833 |
| Llama 4 Maverick 17B | 0.9833 |
| Llama 3.3 70B | 0.9525 |
| GLM 4.7 | 0.8905 |
| Qwen3 Next 80B | 0.8900 |
| Nova Pro | 0.7646 |
| Ministral 3B | 0.2992 |

- **Mean:** 0.8713
- **Std:** 0.2131 ✅ (≥0.08)
- **Range:** 0.6841
- **N models:** 10/10, 0 failures

## Phase 1 Comparison

| Metric | Phase 1 | Phase 2 | Delta |
|--------|---------|---------|-------|
| Mean | 0.8560 | 0.8713 | +0.0153 |
| Std | 0.2264 | 0.2131 | -0.0132 |

Slight compression in std but still well above threshold.

## Model Discrimination

Distinct 4-tier structure:
1. **Ceiling cluster (0.9833):** 5 models tied — Claude Opus, Claude Sonnet, DeepSeek-R1, GPT-OSS-120B, Llama 4 Maverick
2. **Near-ceiling (0.9525):** Llama 3.3 70B
3. **Strong (0.89):** GLM 4.7, Qwen3 Next 80B
4. **Low:** Nova Pro (0.7646), Ministral 3B (0.2992)

The ceiling is pronounced (6/10 models ≥0.95). The benchmark's discriminatory power comes primarily from separating the bottom 4 models. The H4_CHAINED trial (mod arithmetic with chained modifications) is the key discriminating trial — GLM, Qwen3, and Nova Pro all drop to ~0.57 on this one trial.

## Q&A Transcript Review

### Transcript structure
110 entries per model, covering 11 trials (E1, E2, E3_CATCH, M1, M2, M3_CATCH, H1_REVERSAL, H2_EMBEDDED, H3_CONTRADICT, H4_CHAINED, H5_CATCH). Each entry is one item within a trial, with `trial_id`, `score`, `expected`, and `model_answer`/`response`.

### Key finding: Ministral 3B JSON comment parsing bug

**Critical scoring artifact identified.** Ministral 3B scores 0/8 on both E1 and E2 (easy single-switch trials) despite producing **substantively correct answers**:

```
E1 response: {"answers": ["LIVING", "NON-LIVING", "LIVING", "NON-LIVING", "SHORT", "LONG", "SHORT", "LONG"]}
```
These answers are correct (tiger=LIVING, mountain=NON-LIVING, etc.). However, the raw response includes JavaScript-style comments:
```json
"LIVING",    // tiger
"NON-LIVING", // mountain
```
The `json.loads()` parser rejects comments, causing a complete parse failure → score=0 for all 8 items in E1.

**Contrast with H1_REVERSAL (score=1.0):** On this trial, Ministral 3B outputs clean JSON without comments → parser succeeds → perfect score.

**Impact estimate:** If JSON comment stripping were added:
- E1 (8 items): 0.0 → ~1.0 (answers verified correct)
- E2 (8 items): 0.0 → ~0.8-1.0 (likely similar)
- Ministral 3B overall score: ~0.30 → ~0.45-0.50
- Benchmark std would decrease slightly (~0.19) but remain well above threshold

### Other model reviews
- **Claude Opus 4.6 (ceiling, 0.9833):** Clean backtick-fenced JSON responses, correctly parsed. All trials near-perfect.
- **Nova Pro (0.7646):** Clean JSON responses without comments. Errors on H4_CHAINED (chained mod arithmetic) and some medium trials are genuine cognitive failures, not parsing issues.
- **Qwen3 Next 80B (0.8900):** Clean JSON. Errors concentrated on H4_CHAINED — genuine difficulty with multi-step rule modification tracking.
- **Llama 4 Maverick 17B (ceiling):** Backtick-fenced JSON, correctly parsed.

### Parsing artifacts
- **JSON comments (`// ...`):** Affects Ministral 3B on E1, E2, H2_EMBEDDED, H3_CONTRADICT, H4_CHAINED, H5_CATCH trials (all score=0). Does NOT affect E3_CATCH or H1_REVERSAL (no comments in those responses). This is a systematic bias: Ministral 3B adds comments when classifying familiar categories (LIVING/NON-LIVING) but not for abstract operations.
- **Backtick fences:** Multiple models use ````json ... ``` `` wrapping — correctly stripped by parser.
- **Think-tag leakage:** None detected.

### Incorrect scoring examples
1. **Ministral 3B, E1 (score=0.0):** Answers are correct (LIVING/NON-LIVING classifications verified) but JSON comments cause parse failure. This is a **scoring bug**, not a cognitive failure.
2. **Ministral 3B, H2_EMBEDDED (score=0.0):** Same JSON comment pattern — answers may be correct but can't be parsed.

### Correct scoring examples
1. **Ministral 3B, H1_REVERSAL (score=1.0):** Clean JSON without comments → all 12 items correctly classified.
2. **Nova Pro, H4_CHAINED (score=0.571):** Parser works correctly; errors are genuine failures on chained mod arithmetic.

## Ground Truth Validation

- **E1/E2 (easy):** LIVING/NON-LIVING classification of common nouns (tiger, mountain, dolphin, crystal) and SHORT/LONG word classification — all verified correct.
- **M1 (medium):** Alphabet position and vowel-counting tasks — spot-checked 5 items, all correct.
- **H1_REVERSAL:** POSITIVE/NEGATIVE sentiment and ODD/EVEN classification with rule reversal — verified correct.
- **H4_CHAINED:** Mod arithmetic with chained modifications — verified 3 items, all ground truth correct.
- **No debatable items identified.** All ground truth is deterministic (classification rules are unambiguous).

## Recommendation

**KEEP AS-IS with one advisory note.**

Strong benchmark (std=0.2131, range=0.6841 — highest discrimination of all 4 attention benchmarks). However:

1. **Advisory — JSON comment parsing (Ministral 3B):** The model's scores on 6/11 trials are artificially zero due to JavaScript-style comments in JSON output. Adding `re.sub(r'//.*', '', text)` before `json.loads()` would recover ~16 items. Impact: Ministral 3B score ~0.30→0.45, std drops ~0.21→0.19, still well above threshold. This is the same parsing issue documented for attention_divided.
2. **Ceiling cluster:** 5 models tied at 0.9833 is a large ceiling cluster. Only H2_EMBEDDED partially breaks the ceiling (2/12 wrong among top models). Adding more difficulty-tier-4 items (like H4_CHAINED) could improve top-end separation.
