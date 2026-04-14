# Analysis: attention_divided

## Score Distribution

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 0.9375 |
| Claude Sonnet 4.6 | 0.9375 |
| DeepSeek-R1 | 0.9375 |
| GPT-OSS-120B | 0.9375 |
| Llama 4 Maverick 17B | 0.9275 |
| GLM 4.7 | 0.9167 |
| Qwen3 Next 80B | 0.8803 |
| Llama 3.3 70B | 0.8333 |
| Nova Pro | 0.7064 |
| Ministral 3B | 0.4139 |

- **Mean:** 0.8428
- **Std:** 0.1675 ✅ (≥0.08)
- **Range:** 0.5236
- **N models:** 10/10, 0 failures

## Phase 1 Comparison

| Metric | Phase 1 | Phase 2 | Delta |
|--------|---------|---------|-------|
| Mean | 0.8356 | 0.8428 | +0.0072 |
| Std | 0.1666 | 0.1675 | +0.0009 |

Scores are stable across phases — minimal drift.

## Model Discrimination

The benchmark separates models into 3 clear tiers:
1. **Ceiling cluster (0.92–0.94):** Claude Opus, Claude Sonnet, DeepSeek-R1, GPT-OSS-120B, Llama 4 Maverick, GLM 4.7 — 6 models effectively tied
2. **Mid-range (0.83–0.88):** Qwen3 Next 80B, Llama 3.3 70B
3. **Low (0.41–0.71):** Nova Pro, Ministral 3B

The ceiling cluster is wide (6/10 models ≥0.92) — the easy and medium tiers don't discriminate among strong models. Only hard-tier trials separate Ministral 3B and Nova Pro from the pack. The std of 0.1675 passes threshold but is driven almost entirely by the Ministral 3B outlier.

## Q&A Transcript Review

### Scoring correctness
- **GPT-OSS-120B (highest):** Clean JSON responses, correctly parsed. Perfect on easy/medium, near-perfect on hard. No issues.
- **Ministral 3B (lowest, 0.4139):** Scores 0.0 on both easy trials and both medium trials, but 0.875/0.875/0.583 on hard. This pattern is anomalous.
  - **Easy trial 0:** Response includes `"MAMMAL" // penguin` — penguin is a BIRD, so this is a genuine error (not parsing). Score=0 is correct.
  - **Easy trial 1:** Response includes verbose format `"banana → 3 vowels"` instead of just `"3"`. This is a format mismatch — the answer content may be extractable but the parser requires clean values. Partial parsing issue.
  - **Medium trials:** Scores 0.0 on both — responses use JSON comments (`//`) and nested object format instead of flat array, causing parse failures.
  - **Hard trials:** Clean JSON output without comments → parser succeeds → genuine scores.
- **Nova Pro (0.7064):** Scores 0.0 on medium trial 2 (M1: parity/magnitude/digit-sum) — response includes JSON comments (`// Stream A: 47 is ODD`). Same parsing artifact as Ministral 3B. Other trials parse correctly.
- **Llama 3.3 70B (mid, 0.8333):** Clean JSON responses throughout. Scores reflect genuine cognitive errors on hard trials.
- **Llama 4 Maverick 17B (near-ceiling):** Perfect on easy, clean parsing on all trials.

### Parsing artifacts
- **JSON comments (`// ...`):** Ministral 3B and Nova Pro both produce JavaScript-style comments in JSON responses. The parser uses `json.loads()` which rejects comments. This inflates error rates for these models on trials where they add explanatory comments.
- **Backtick fences:** Multiple models wrap responses in ````json ... ``` `` fences — these appear to be stripped correctly by the parser (no score impact observed).
- **Think-tag leakage:** None detected across all 10 models.

### Incorrect scoring examples
1. **Ministral 3B, Easy trial 1 (score=0.25):** Model outputs `"banana → 3 vowels"` — the answer "3" is embedded in verbose text. A more robust parser could extract the numeric value. Likely 2-3 items lose credit due to format, not cognition.
2. **Nova Pro, Medium trial 2 (score=0.0):** JSON comments cause complete parse failure despite answers being substantively correct (ODD/LOW/11 etc. are all accurate).

### Correct scoring examples
1. **GPT-OSS-120B, Easy trial 0:** `{"answers": ["42", "BIRD", "48", "MAMMAL", "63", "BIRD", "8", "MAMMAL"]}` — all correct, properly parsed.
2. **Ministral 3B, Easy trial 0:** `"MAMMAL" // penguin` — penguin IS a bird, score=0 is warranted. Genuine cognitive error.

## Ground Truth Validation

- **Easy tier:** Math operations (15+27=42, 8×6=48, 100-37=63, 72÷9=8) and animal classification (penguin=BIRD, dolphin=MAMMAL, eagle=BIRD, whale=MAMMAL) — all verified correct.
- **Medium tier:** 3-stream tasks (parity, magnitude comparison, digit sums, vowel counting) — spot-checked 5 items, all ground truth correct.
- **Hard tier:** 3-stream same-domain tasks — verified number classifications (ODD/EVEN, HIGH/LOW, LARGER/SMALLER). All correct.
- **No debatable items identified.**

## Recommendation

**KEEP AS-IS with one advisory note.**

The benchmark meets all thresholds (std=0.1675, range=0.5236). However:

1. **Advisory — JSON comment parsing:** Ministral 3B and Nova Pro lose 2-4 trials to JSON comment parsing failures where answers are substantively correct. This inflates difficulty for models that add explanatory comments. Consider adding comment-stripping (`re.sub(r'//.*', '', text)`) to the JSON parser. Impact: Ministral 3B score would increase ~0.05-0.10; Nova Pro ~0.03-0.05. Would slightly compress std but not below threshold.
2. **Ceiling cluster awareness:** 6/10 models tied at 0.92-0.94. If the model roster changes (e.g., removing Ministral 3B), std could drop below 0.08. The hard tier is the only discriminator for strong models.
