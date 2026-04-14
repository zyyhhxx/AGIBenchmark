# Analysis: social_cog_emotional_prosody

## Score Distribution (Phase 2, 10 models)
| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 0.564 |
| Claude Sonnet 4.6 | 0.470 |
| Qwen3 Next 80B | 0.374 |
| Llama 4 Maverick 17B | 0.348 |
| DeepSeek-R1 | 0.331 |
| Ministral 3B | 0.311 |
| GPT-OSS-120B | 0.307 |
| GLM 4.7 | 0.299 |
| Nova Pro | 0.278 |
| Llama 3.3 70B | 0.268 |

**Stats:** mean=0.3549, std=0.0888, range=0.2958, min=0.268, max=0.564

### Discrimination: **PASS** (std=0.089 ≥ 0.08)
Borderline — only 0.009 above threshold. Discrimination comes primarily from Claude Opus (0.564) pulling away from the pack; bottom 7 models cluster in 0.27–0.35 range (spread=0.08 within cluster).

### Phase 1 → Phase 2 Comparison
- Phase 1: mean=0.808, std=0.049 (ceiling effect, too easy)
- Phase 2: mean=0.355, std=0.089 (multiplicative hard-tier scoring compressed scores dramatically)
- **Improvement:** std nearly doubled; ceiling resolved. Mean dropped 0.45 points — expected given hard-tier requires both before AND after emotions correct.

## Q&A Transcript Review (5 models)

### Claude Opus 4.6 (highest, 0.564)
- 43 trials, avg=0.326, min=0.0, max=1.0
- No parsing artifacts. Clean JSON responses.
- Correctly identifies emotional shifts in most trials; strong on nuanced trigger identification.

### Llama 3.3 70B (lowest, 0.268)
- 43 trials, avg=0.209
- Responses are clean JSON. No parsing issues.
- Genuine capability gap — misidentifies emotions frequently, especially subtle shifts.

### DeepSeek-R1 (mid, 0.331)
- 43 trials, avg=0.209
- Reasoning model doesn't help with emotional prosody — extended chain-of-thought produces overanalysis of cues.

### Ministral 3B (surprising — 0.311, above Llama 3.3/Nova/GLM)
- 43 trials, avg=0.163. **All 43 responses wrapped in backtick fences** (`\`\`\`json...`).
- 36/43 trials scored 0.0 — but the aggregate score (0.311) comes from tier weighting, not raw accuracy.
- **Backtick fence impact:** All responses have fences but scoring still works for some items → `_strip_fences()` fix IS deployed. The 0.0 scores are genuine failures, not parse artifacts.

### Nova Pro (low, 0.278)
- 43 trials, avg=0.279
- Clean JSON, no parsing issues. Genuine low performance on emotion identification.

### Parsing Summary
- **Think-tag leakage:** None across all 10 models ✅
- **JSON comments:** None detected ✅
- **Backtick fences (Ministral 3B):** Present in all 43 responses but `_strip_fences()` is deployed — not causing parse failures

## Scoring Verification (Step 6)

**Multiplicative scoring for hard tier: CONFIRMED DEPLOYED**
- Code line 1084: `perfect = before_s * after_s` — both before and after emotions must be correct
- Tier weights: easy=0.10, medium=0.30, hard=0.60 — confirmed in code lines 1127-1129
- This is the primary lever compressing scores downward (mean from 0.81→0.36)

## Ground Truth Validation
- 43 items across 3 tiers (easy, medium, hard)
- Emotion labels are descriptive (e.g., "confrontational and accusatory", "friendly and casual") — allows reasonable variation in model responses
- No debatable items identified from transcript review

## Recommendation: **KEEP AS-IS**
- std=0.089 passes threshold (borderline)
- Multiplicative scoring fix confirmed deployed and working
- No parsing artifacts distorting scores
- Genuine cognitive challenge — even best model (Opus) only scores 0.564
- **Advisory:** If model roster changes, monitor std — removing Opus could drop std below threshold since it's the sole high-scorer
