# Improvement Log: social_cog_sarcasm

## Summary

The sarcasm benchmark was redesigned from a flat 40-item benchmark to a 3-tier
85-item benchmark with weighted scoring. This resolved the std=0.025 ceiling effect.

## Problem

**Before redesign:** std=0.025, all 10 models scored ≥0.909. No meaningful discrimination.
Items used obvious context-utterance contradiction (e.g., waiting 45 min + "Well, that was quick!").
All frontier models trivially solved these items.

## Changes Made

### Task Code (`repo/benchmarks/social_cognition/task_sarcasm.py`)
- Already contained 3-tier structure from prior redesign iteration (code was ready, never re-run)
- Scoring: `score = 0.05 * tier1_composite + 0.15 * tier2_composite + 0.80 * tier3_binary_acc`
- Tier 1-2 composite = `0.50 * AUC + 0.30 * (1 - cal_error) + 0.20 * threshold_acc`
- Tier 3 uses binary accuracy only (AUC too forgiving for subtle items)

### Items (`repo/benchmarks/social_cognition/data/sarcasm_items.py`)
- **Total:** 85 items (was 40)
- **Tier 1** (difficulty=1): 40 items (20 sarcastic + 20 sincere) — obvious contradiction
- **Tier 2** (difficulty=2): 15 items (10 sarcastic + 5 sincere) — implicit/contextual contradiction
- **Tier 3** (difficulty=3): 30 items (17 sarcastic + 13 sincere) — subtle, deadpan, cultural, maximally ambiguous

### Notebook (`repo/notebooks/social_cog_sarcasm.ipynb`)
- Already synced with 3-tier code and 85-item data (pre-existing)
- Passes `jupyter nbconvert --to notebook` syntax validation ✅

## Before/After Scores

| Model | Before (v1, 40 items) | After (v2, 85 items) |
|-------|----------------------|----------------------|
| Claude Opus 4.6 | 0.981 | 0.9680 |
| Claude Sonnet 4.6 | 0.980 | 0.8874 |
| DeepSeek-R1 | 0.976 | 0.8360 |
| GPT-OSS-120B | 0.969 | 0.8075 |
| Llama 4 Maverick 17B | 0.969 | 0.9184 |
| Ministral 3B | 0.909 | 0.7162 |
| Nova Pro | 0.999 | 0.8623 |
| Llama 3.3 70B | 0.998 | 0.9454 |
| GLM 4.7 | 0.997 | 0.9186 |
| Qwen3 Next 80B | 0.994 | 0.6198 |

**Before:** mean=0.9772, std=0.0251, range=0.0891
**After:** mean=0.8480, std=0.1034, range=0.3482

## Verification

- std=0.1034 ≥ 0.08 threshold ✅ (was 0.025 — **4.1× improvement**)
- range=0.3482 (was 0.0891 — **3.9× improvement**)
- 10/10 models scored, 0 errors
- All item responses non-trivial (real sincerity ratings, not fallback=50)

## Tier Analysis

### Tier 1 (Obvious)
All frontier models score ≥0.95 on Tier 1 — as designed.
Ministral 3B Tier 1 acc=0.90 (4 errors on sarcastic items).

### Tier 2 (Contextual)
Most frontier models score ≥0.97. Ministral 3B drops to 0.87.

### Tier 3 (Subtle/Ambiguous)
Primary discriminator. Tier 3 accuracy by model:
- Claude Opus 4.6: 0.967 (1 error: N35 minimalist architecture item)
- Llama 3.3 70B: 0.933 (2 errors: S44, S45)
- GLM 4.7: 0.900 (3 errors: S39, S45, S46)
- Llama 4 Maverick 17B: 0.900 (3 errors: S39, S45, S46)
- Claude Sonnet 4.6: 0.867 (4 errors: S33, S40, S44, N36)
- Nova Pro: 0.833 (5 errors: S36, S39, S44, S45, S46)
- DeepSeek-R1: 0.800 (6 errors: S36, S39, S40, S44, S45, S46)
- GPT-OSS-120B: 0.733 (8 errors)
- Ministral 3B: 0.667 (10 errors)
- Qwen3 Next 80B: 0.533 (14 errors, including 7 false negatives on sincere N31-N37)

**Key Tier 3 failure items (hardest across models):**
- **S45** (IT professional's "Happy to help! That's what I'm here for." on 47th password reset): 7/10 models fail
- **S46** (chef's "Of course. I live for creative challenges" for impossible dietary restrictions): 6/10 models fail
- **S39** (couple arguing about dishes → "Thank you. I appreciate it." as power move): 5/10 models fail
- **S36** (crypto investor's "Oh, it's been a real learning experience."): 5/10 models fail

## Remaining Limitations

- Tier 3 still too easy for Claude Opus (0.967 acc); future iteration could add harder items
- Qwen3 shows sarcasm-bias: rates genuine sincere items as sarcastic (N31-N37 all=0 sincerity)
  — possible instruction-following artifact, not true sarcasm comprehension
- S45/S46 (professional obligatory positivity) are the hardest items even for frontier models

## Artifacts

- Code: `repo/benchmarks/social_cognition/task_sarcasm.py` (3-tier, verified)
- Data: `repo/benchmarks/social_cognition/data/sarcasm_items.py` (85 items)
- Notebook: `repo/notebooks/social_cog_sarcasm.ipynb` (synced, passes nbconvert)
- Transcripts: `repo/sub-workflows/benchmark-qa/results/qa_transcripts/social_cog_sarcasm_v2/` (10 model runs)
- This log: `repo/sub-workflows/benchmark-qa/results/improvement_log_social_cog_sarcasm.md`
