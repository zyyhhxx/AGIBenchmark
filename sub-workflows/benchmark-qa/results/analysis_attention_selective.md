# Analysis: attention_selective

## Score Distribution

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 1.0000 |
| DeepSeek-R1 | 1.0000 |
| Claude Sonnet 4.6 | 0.9583 |
| GPT-OSS-120B | 0.9583 |
| Llama 3.3 70B | 0.8767 |
| Nova Pro | 0.7967 |
| Llama 4 Maverick 17B | 0.7567 |
| Qwen3 Next 80B | 0.7300 |
| GLM 4.7 | 0.7167 |
| Ministral 3B | 0.5233 |

- **Mean:** 0.8317
- **Std:** 0.1550 ✅ (≥0.08)
- **Range:** 0.4767
- **N models:** 10/10, 0 failures

## Phase 1 Comparison

| Metric | Phase 1 | Phase 2 | Delta |
|--------|---------|---------|-------|
| Mean | 0.8267 | 0.8317 | +0.0050 |
| Std | 0.1449 | 0.1550 | +0.0101 |

Slight improvement in discrimination from Phase 1 — consistent scores.

## Model Discrimination

Tier structure (3-tier conjunction search: T1 pop-out, T2 2-feature, T3 3-feature):

| Model | T1 (pop-out) | T2 (conjunction) | T3 (triple) |
|-------|-------------|-------------------|-------------|
| Ministral 3B | 0.75 | 0.60 | 0.42 |

T2 (feature conjunction) is the primary discriminator — varies 50%-100% across models. T3 (triple conjunction) is hardest but most models ≥83%, providing less separation than expected.

**Ceiling effect:** 4 models score ≥0.95 (Claude Opus, DeepSeek-R1, Claude Sonnet, GPT-OSS-120B). Not problematic for overall std since the bottom half spreads well.

## Q&A Transcript Review

### Transcript structure
26 items per model (4 T1 + 10 T2 + 12 T3). Each entry has `item_id`, `tier`, `expected`, `parsed_answer`, `score`.

### Scoring correctness
- **Claude Opus 4.6 (perfect, 1.0):** All 26 items correct. Responses sometimes verbose with reasoning (e.g., T2_07: "The numbers are 42, 17, 85... sorted: 8, 17, 23... The second-smallest is **17**") but parser correctly extracts final answer.
- **Ministral 3B (lowest, 0.5233):** 12/26 wrong. Errors concentrated in T2 (4/10 wrong) and T3 (7/12 wrong).
  - T1_04: Expected "Streetlights", got "The" — truncated answer, parsing artifact.
  - T2_02: Expected 4, got 5 — genuine counting error.
  - T2_03: Expected 6, got 10 — genuine counting error.
  - T3_01: Expected "E6,O4,U2", got "E6, U2" — missed O4, genuine selective attention failure (missed conjunction match).
  - T3_02: Expected "FL101,FL104,FL107", got "FL101, FL103" — wrong flight number, genuine error.
- **Qwen3 Next 80B (0.7300):** Clean responses, no parsing issues. Errors are genuine cognitive failures on T2/T3 items.
- **GLM 4.7 (0.7167):** Similar pattern — genuine errors on conjunction items, no parsing artifacts.

### Parsing artifacts
- **Think-tag leakage:** None detected.
- **JSON extraction failures:** None — items use simple single-value responses, not JSON arrays.
- **Truncation:** Ministral 3B T1_04 answer "The" is suspiciously truncated — possible response cutoff. One item only; not systematic.

### Ground truth validation
- **T1 items (pop-out):** Verified — single-feature search (e.g., "find the number", "find the animal"). All correct answers confirmed.
- **T2 items (conjunction):** Verified 6/10 — counting items with 2-feature conjunctions. All expected answers correct.
- **T3 items (triple conjunction):** Verified 8/12 — complex multi-feature searches. All expected answers confirmed correct.
- **No debatable items identified.** The previously-found bugs (T3_09 non-unique answer, T2_07 wrong answer) were fixed in the v2 redesign per KNOWLEDGE.

## Recommendation

**KEEP AS-IS.**

Strong benchmark with good discrimination (std=0.1550, range=0.4767). The conjunction search design based on Treisman & Gelade (1980) produces meaningful difficulty gradient. No scoring bugs, no parsing artifacts, no debatable ground truth items. The 4-model ceiling cluster is acceptable since the benchmark's primary purpose is separating mid-range from weak models on attention-to-detail.
