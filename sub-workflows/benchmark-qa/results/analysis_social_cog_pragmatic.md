# Analysis: social_cog_pragmatic

## Score Distribution (Phase 2, 10 models)
| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 0.811 |
| Claude Sonnet 4.6 | 0.717 |
| Qwen3 Next 80B | 0.483 |
| GPT-OSS-120B | 0.479 |
| Nova Pro | 0.473 |
| DeepSeek-R1 | 0.456 |
| GLM 4.7 | 0.427 |
| Llama 4 Maverick 17B | 0.372 |
| Ministral 3B | 0.332 |
| Llama 3.3 70B | 0.236 |

**Stats:** mean=0.4786, std=0.1622, range=0.5756, min=0.236, max=0.811

### Discrimination: **PASS** (std=0.162 ≥ 0.08)
Excellent discrimination — best of the 4 social cognition benchmarks. Range=0.576 provides strong model separation. Clear tiering: Claude models top, mid-pack cluster (0.37–0.48), Llama 3.3 floor.

### Phase 1 → Phase 2 Comparison
- Phase 1: mean=0.824, std≈0.061 (ceiling, too easy)
- Phase 2: mean=0.479, std=0.162 (3-tier redesign resolved ceiling)
- **Major improvement:** Std nearly tripled; mean dropped 0.35 points.

## Q&A Transcript Review (5 models)

### Claude Opus 4.6 (highest, 0.811)
- 45 trials, 7 zeros. Tier scores: direct=0.876, indirect=0.800, complex=0.800
- Clean JSON responses. Correctly identifies pragmatic intent in most items including complex multi-layer irony.

### Llama 3.3 70B (lowest, 0.236)
- 45 trials, 25 zeros (56% failure rate)
- Clean responses — failures are genuine. Model interprets utterances literally, missing pragmatic implicature.
- Massive gap vs false_belief (0.863) — pragmatic inference is categorically harder than explicit ToM for this model.

### Nova Pro (mid, 0.473)
- 45 trials, 18 zeros. Clean JSON, no parsing issues.

### DeepSeek-R1 (surprising — 0.456, below mid-pack)
- 45 trials, 20 zeros. Reasoning model doesn't help with pragmatic inference — extended deliberation leads to overthinking simple implicatures.

### GLM 4.7 (random, 0.427)
- 45 trials, 19 zeros. Clean JSON, no parsing issues.

### Parsing Summary
- **Think-tag leakage:** None ✅
- **JSON comments:** None detected ✅
- **Ministral 3B backtick fences:** 39/45 responses have fences. `_strip_fences()` deployed — fences are stripped before JSON parsing. Zero-scored items are genuine failures.

## Scoring Verification (Step 6)

**3-tier design with weights 0.15/0.35/0.50: CONFIRMED DEPLOYED**
- Code: `0.15 * direct + 0.35 * indirect + 0.50 * complex`
- Per-tier formula: `intended_accuracy - 0.1 * literal_trap_rate`
- Opus tier breakdown: direct=0.876, indirect=0.800, complex=0.800
- 45 items total: 25 direct, 10 indirect, 10 complex — confirmed in summary JSON

## Ground Truth Validation

### Pragmatic implicature tiers
- **Direct tier** (25 items): scalar implicature, indirect requests, irony, understatement, relevance — well-established pragmatic categories
- **Indirect tier** (10 items): domain implicature, politeness indirection, maxim violations — require contextual reasoning
- **Complex tier** (10 items): litotes, rhetorical reversal, multi-layer irony, presupposition traps — highest cognitive demand

### Item review
- Opus's 7 failures (on 45 items) are spread across tiers — no systematic ground truth issue
- Llama 3.3 70B's 25 failures concentrate on indirect/complex tiers — expected difficulty gradient
- **No debatable items identified** — pragmatic intent is clearly deterministic given the conversational context provided

## Recommendation: **KEEP AS-IS**
- std=0.162 well above threshold — strongest discriminator in social cognition track
- 3-tier design confirmed working as intended
- Range=0.576 provides excellent model separation
- Family-level inversions (Llama 3.3 scores 0.236 on pragmatic but 0.863 on false_belief) provide genuine insight into differential social cognition capabilities
