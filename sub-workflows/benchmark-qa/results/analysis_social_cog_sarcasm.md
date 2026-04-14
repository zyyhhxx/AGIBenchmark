# Analysis: social_cog_sarcasm

## Score Distribution (Phase 2, 10 models)
| Model | Score |
|-------|-------|
| Nova Pro | 0.999 |
| Llama 3.3 70B | 0.998 |
| GLM 4.7 | 0.997 |
| Qwen3 Next 80B | 0.994 |
| Claude Opus 4.6 | 0.981 |
| Claude Sonnet 4.6 | 0.980 |
| DeepSeek-R1 | 0.976 |
| GPT-OSS-120B | 0.969 |
| Llama 4 Maverick 17B | 0.969 |
| Ministral 3B | 0.909 |

**Stats:** mean=0.9772, std=0.0251, range=0.0891, min=0.909, max=0.999

### Discrimination: **FLAG — std=0.025 < 0.08** ⚠️
This benchmark is effectively saturated. All 10 models score ≥0.909. The only meaningful separation is between Ministral 3B (0.909) and the rest (0.969–0.999). Without Ministral 3B, std would drop to ~0.011.

### Phase 1 Comparison
- No Phase 1 scores recorded in KNOWLEDGE for sarcasm specifically, but KNOWLEDGE notes sarcasm was near-ceiling from the start.
- The current scores confirm: sarcasm detection is trivially easy for all models including 3B-class.

## Q&A Transcript Review (5 models)

### Nova Pro (highest, 0.999)
- 40 trials, 0 zeros, min=1.0, max=1.0 — **perfect score on all trials**
- Clean JSON responses. Correctly identifies sarcasm with high confidence in every item.

### Ministral 3B (lowest, 0.909)
- 40 trials, 11 zeros
- 36/40 responses wrapped in backtick fences. `_strip_fences()` deployed — fence stripping works.
- 11 failures may include some parse-related issues (backtick + complex JSON), but even correcting all 11 would only raise score to ~1.0
- Sarcasm score aggregation uses sincerity_rating proximity — Ministral's 11 failures could be genuine misidentifications or parse artifacts on borderline items

### Llama 3.3 70B (surprising — 0.998, near-perfect despite being a smaller model)
- 40 trials, 0 zeros, min=1.0, max=1.0 — perfect
- Sarcasm detection is not model-size dependent — even 70B models achieve ceiling

### DeepSeek-R1 (mid, 0.976)
- 40 trials, 2 zeros. 38/40 near-perfect. Two isolated failures.

### Claude Opus 4.6 (random, 0.981)
- 40 trials, 0 zeros, min=1.0, max=1.0 — perfect on raw trial scores; composite slightly below 1.0 due to sincerity rating granularity

### Parsing Summary
- **Think-tag leakage:** None ✅
- **JSON comments:** None detected ✅
- **Backtick fences (Ministral 3B):** 36/40 trials have fences; stripping is deployed; remaining failures may be partly parse-related but sarcasm is near-ceiling regardless

## Scoring Verification
- Scoring uses `sincerity_rating` proximity to ground truth (0 for sarcastic, 100 for sincere)
- 40 items total. No tier structure — flat difficulty.
- All models achieve near-perfect scores → benchmark lacks difficulty variation

## Ground Truth Validation
- Sarcasm items use clear contextual contradiction (e.g., waiting 45 min + "Well, that was quick service!")
- Items are unambiguous — the sarcastic interpretation is strongly supported by context in all cases
- **No debatable items** — sarcasm cues are heavy-handed by design, which is why models trivially solve them

## Recommendation: **REVISE — add harder sarcasm variants**
- **Current status:** std=0.025, BELOW 0.08 threshold
- **Problem:** All items use obvious context-utterance contradiction. Modern LLMs (even 3B) detect this pattern trivially.
- **Suggested revisions:**
  - Add **dry humor / deadpan** items where sarcasm has no contextual contradiction signal
  - Add **cultural sarcasm** requiring world knowledge (e.g., British understatement, Japanese tatemae)
  - Add **ambiguous sincerity** items where the literal reading is plausible (reverse traps)
  - Add **multi-turn sarcasm** where the sarcastic intent emerges over multiple exchanges
  - Increase to 3-tier difficulty (like pragmatic): obvious=0.10, contextual=0.35, subtle/ambiguous=0.55
- **Minimum action:** Without revision, this benchmark provides no discrimination signal and should be flagged in the track writeup as a known limitation
- **If no revision is planned:** Consider dropping from scored submission — a benchmark that can't discriminate adds noise, not signal
