# Analysis: social_cog_false_belief

## Score Distribution (Phase 2, 10 models)
| Model | Score |
|-------|-------|
| Llama 3.3 70B | 0.863 |
| Qwen3 Next 80B | 0.863 |
| Claude Sonnet 4.6 | 0.852 |
| Llama 4 Maverick 17B | 0.754 |
| DeepSeek-R1 | 0.708 |
| Nova Pro | 0.646 |
| GLM 4.7 | 0.625 |
| GPT-OSS-120B | 0.613 |
| Claude Opus 4.6 | 0.583 |
| Ministral 3B | 0.563 |

**Stats:** mean=0.7069, std=0.1128, range=0.3000, min=0.563, max=0.863

### Discrimination: **PASS** (std=0.113 ≥ 0.08)
Good spread. Interesting rank inversion: Claude Opus 4.6 (0.583) ranks 9th/10, below even Ministral 3B on some tiers. Llama 3.3 70B ties for top — suggests ToM capability isn't strictly correlated with model size.

### Phase 1 → Phase 2 Comparison
- Phase 1: mean=0.964 (ceiling — all models >0.85)
- Phase 2: mean=0.707, std=0.113 (v5 redesign with 5-tier difficulty resolved ceiling)
- **Major improvement:** Std went from near-zero to 0.113; mean dropped 0.26 points.

## Q&A Transcript Review (5 models)

### Llama 3.3 70B (highest tied, 0.863)
- 34 trials, 5 failures (indices 8, 10, 25, 27, 31)
- Clean text responses (no JSON required for false_belief). No parsing issues.
- Failures concentrated in higher-order items as expected.

### Ministral 3B (lowest, 0.563)
- 34 trials, 14 failures
- No backtick fences (false_belief uses free-text responses, not JSON)
- Failures spread across all tiers — genuine ToM limitation.

### Claude Opus 4.6 (surprising — 0.583, 9th of 10)
- 34 trials, 8 failures at indices [9, 14, 15, 16, 18, 19, 21, 23]
- All failures are on 4th-order items — Opus answers "what X actually thinks" instead of "what Y thinks X thinks"
- This is the **perspective confusion trap** documented in KNOWLEDGE (FB52/FB56 pattern)
- Opus's chain-of-thought reasoning leads it to collapse nested belief chains into the actual state of affairs
- **Not a scoring bug** — genuine 4th-order ToM failure for this model

### DeepSeek-R1 (mid, 0.708)
- 34 trials, 5 failures
- Reasoning model performs mid-tier — extended reasoning helps on some nested beliefs but confabulates on others

### Llama 4 Maverick 17B (random, 0.754)
- 34 trials, 7 failures. Clean responses, no parsing issues.

### Parsing Summary
- **Think-tag leakage:** None ✅
- **JSON comments:** N/A (free-text responses) ✅
- **Backtick fences:** None (false_belief doesn't use JSON format) ✅

## Scoring Verification (Step 6)

**Tier weights — DISCREPANCY with task description:**
- Task step 6 says: 0.05/0.05/0.10/0.60/0.20
- **Deployed code uses: 0.00/0.00/0.05/0.70/0.25**
- T1 and T2 are zeroed out entirely; T4 gets 70% (not 60%); T5 gets 25% (not 20%)
- This is a MORE aggressive weighting toward higher-order items than the task specified
- **Impact:** Makes the benchmark harder and more discriminating — consistent with the observed results
- The deployed weights are the v5 final iteration documented in KNOWLEDGE

## Ground Truth Validation

### 4th-order perspective traps
- Items at indices 9, 14-16, 18-19, 21, 23 are the primary discriminators
- Opus fails 8/34 items — all in the 4th-order tier
- The correct answers require tracking 4 nested belief states (e.g., "What does A think B thinks C thinks D put the object?")
- Reviewed Opus's responses: it correctly traces 3 levels but collapses to ground truth at the 4th level — a genuine cognitive limitation, not ambiguous ground truth

### FB52/FB56 specific items
- Trial IDs not present in transcript format (indexed by position, not named IDs)
- However, the perspective confusion pattern matches KNOWLEDGE documentation of FB52/FB56
- Items at indices ~9 and ~14-23 correspond to T4/T5 scenarios with the documented trap structure

### No debatable items found
- All correct answers are deterministic given the scenario text
- No ambiguous belief chains where multiple answers could be defensible

## Recommendation: **KEEP AS-IS**
- std=0.113 comfortably above threshold
- v5 redesign resolved the Phase 1 ceiling effect
- 4th-order perspective traps are genuine cognitive discriminators
- Deployed tier weights (0/0/0.05/0.70/0.25) differ from task spec but are the intended v5 weights
- **Note:** Opus ranking 9th is a real finding, not a bug — 4th-order ToM is a genuine weakness for this model despite its overall frontier capabilities
