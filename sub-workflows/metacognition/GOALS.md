# GOALS.md — AGI Benchmark Hackathon (Final Submission)

## Active Goal
Submit **5 writeups** (one per track) to maximize prize chances. Deadline: **April 16, 2026** (11:59 PM UTC).

Priority order: Metacognition → Attention → Learning → Executive Functions → Social Cognition.

**SCOPE: ALL 5 TRACKS, NOT JUST METACOGNITION.**
The metacognition track is the quality bar — all other tracks must be brought up to the same standard:
- Fix all flagged benchmarks (low variance, ceiling effects) so every benchmark has std ≥ 0.10
- Run all benchmarks in every track against all 10 Bedrock models
- Draft a ≤1,500-word writeup per track following the required template
- Generate a cover image per track
- Produce a discriminatory analysis summary per track

Do NOT declare the workflow complete until all 5 tracks have: (1) all benchmarks passing std ≥ 0.08, (2) full 10-model results, (3) a polished writeup, and (4) a cover image.

## ⛔ Hard Rules
- **DO NOT upload notebooks to Kaggle using the CLI or API.** Let the human handle all Kaggle uploads manually via the web UI.
- **Each writeup must not exceed 1,500 words.** Follow the required template exactly.
- **All notebooks MUST be self-contained.** No `from data.*` imports — data must be inlined in the notebook. Kaggle has no access to local modules. Known broken: `metacog_canary.ipynb` has `from data.canary_items import ...` which must be replaced with inlined data.
- **No duplicate execution.** Each notebook must have exactly ONE `@kbench.task` definition and ONE `.run()` call. `if __name__ == "__main__"` guards do NOT work in Jupyter — `__name__` is always `"__main__"`. Known bugs (fix all):
  - `attention_divided.ipynb` — Cell 0 and Cell 2 are 100% identical duplicates. Delete Cell 2.
  - `attention_instruction_update.ipynb` — Same issue. Delete Cell 2.
  - `attention_vigilance.ipynb` — Double `.run()` (cell 2 + cell 3). Remove one.
  - `metacog_canary.ipynb` — Broken import + duplicate task + double `.run()`. Fix import to use inlined data, remove duplicate cells.
  - `metacog_epistemic_revision.ipynb` — Double `.run()` (cell 1 + cell 2). Delete cell 2.
  - `exec_func_crt.nbconvert.ipynb` — Exact duplicate of `exec_func_crt.ipynb`. Delete it.
- Note: Rules say "one (1) Submission per Team" for Hackathons — unclear if per-track or total. Ian will verify on Kaggle whether multiple writeups are allowed. Plan for 5, fall back to 1 (metacognition) if restricted.

## Submission Requirements (from competition rules, verified 2026-04-11)

Full rules saved in `repo/COMPETITION_RULES.md`.

A valid submission = **Kaggle Writeup** + **attached Kaggle Benchmark**

### Kaggle Writeup
- Created via **"New Writeup"** button (NOT a Discussion post)
- Must select a **Track** 
- ≤1,500 words — submissions over this limit may be penalized
- Must include a **cover image** (required to submit)
- Must click **"Submit"** button — drafts don't count
- Required template:
  ```
  ### Project Name
  ### Your Team
  ### Problem Statement
  ### Task & benchmark construction
  ### Dataset
  ### Technical details
  ### Results, insights, and conclusions
  ### Organizational affiliations
  ### References & citations
  ```

### Kaggle Benchmark (attached to writeup)
- Benchmark + tasks set to **private** (auto-publish after deadline)
- Attached via "Attachments" → "Add a link" → select benchmark

### Evaluation Criteria
| Criteria | Weight |
|----------|--------|
| Dataset quality & task construction | **50%** |
| Writeup quality | **20%** |
| Novelty, insights, discriminatory power | **30%** |

### Prizes
- 4 × $25,000 grand prizes (best across all tracks)
- 2 × $10,000 per track (14 unique winners total, no repeats)

## Track Status & Improvement Plan

### Track 1: Metacognition 🟢 (Priority 1 — READY)
**Status:** 9 benchmarks, 0 flagged, avg std 0.172, 7–10 models tested.
**Writeup:** `repo/WRITEUP_METACOGNITION.md` (1,154 words) ✅

**Improvements:**
- [ ] Re-run all 9 benchmarks against all 10 models for freshest numbers (Task 011)
- [ ] Polish writeup with any updated results

### Track 2: Attention 🟢 (Priority 2 — Good shape)
**Status:** 4 benchmarks, 0 flagged, avg std 0.161, but only 3-4 models tested.
| Benchmark | Mean | Std | Range | Models |
|-----------|------|-----|-------|--------|
| attention_divided | 0.714 | 0.193 | 0.514 | 4 |
| attention_instruction_update | 0.710 | 0.277 | 0.676 | 4 |
| attention_selective | 0.880 | 0.054 | 0.130 | 3 |
| attention_vigilance | 0.647 | 0.121 | 0.288 | 4 |

**Improvements:**
- [ ] Run all 4 benchmarks against all 10 models (more model coverage needed)
- [ ] attention_selective has low std (0.054) — monitor after more models, may need fixing
- [ ] Draft writeup: `repo/WRITEUP_ATTENTION.md`

### Track 3: Learning 🟡 (Priority 3 — One fix needed)
**Status:** 4 benchmarks, 1 flagged, avg std 0.119, 4-5 models tested.
| Benchmark | Mean | Std | Range | Models | Flag |
|-----------|------|-----|-------|--------|------|
| learning_curriculum | 0.650 | 0.114 | 0.300 | 4 | |
| learning_curves | 0.626 | 0.063 | 0.170 | 5 | |
| learning_interference | 0.440 | 0.037 | 0.100 | 5 | ⚠️ LOW VAR |
| learning_transfer | 0.646 | 0.260 | 0.720 | 5 | |

**Improvements:**
- [ ] Fix learning_interference (std=0.037, range=0.100 — needs harder/easier items for spread)
- [ ] Run all 4 benchmarks against all 10 models
- [ ] Draft writeup: `repo/WRITEUP_LEARNING.md`

### Track 4: Executive Functions 🟡 (Priority 4 — Two issues)
**Status:** 5 benchmarks, 1 flagged, avg std 0.082, 4 models tested.
| Benchmark | Mean | Std | Range | Models | Flag |
|-----------|------|-----|-------|--------|------|
| exec_func_crt | 0.538 | 0.060 | 0.157 | 4 | |
| exec_func_nback | 0.751 | 0.177 | 0.486 | 4 | |
| exec_func_task_switch | 0.792 | 0.099 | 0.246 | 4 | |
| exec_func_tol | 0.038 | 0.066 | 0.153 | 4 | near-floor |
| exec_func_wcst | 0.467 | 0.007 | 0.018 | 4 | ⚠️ LOW VAR |

**Improvements:**
- [ ] Fix exec_func_wcst (std=0.007, essentially zero discrimination)
- [ ] Investigate exec_func_tol near-floor (mean=0.038) — may be too hard for all models
- [ ] Run all 5 benchmarks against all 10 models
- [ ] Draft writeup: `repo/WRITEUP_EXECUTIVE_FUNCTIONS.md`

### Track 5: Social Cognition 🔴 (Priority 5 — Weakest)
**Status:** 4 benchmarks, 2 flagged, avg std 0.076, 3-4 models tested.
| Benchmark | Mean | Std | Range | Models | Flag |
|-----------|------|-----|-------|--------|------|
| social_cog_emotional_prosody | 0.794 | 0.063 | 0.153 | 4 | |
| social_cog_false_belief | 0.967 | 0.029 | 0.070 | 3 | ⚠️ CEILING |
| social_cog_pragmatic | 0.857 | 0.036 | 0.088 | 4 | ⚠️ LOW VAR |
| social_cog_sarcasm | 0.760 | 0.177 | 0.460 | 4 | |

**Improvements:**
- [ ] Fix social_cog_false_belief (ceiling at 0.967 — too easy, needs harder ToM scenarios)
- [ ] Fix social_cog_pragmatic (std=0.036 — needs more nuanced pragmatic inference items)
- [ ] Run all 4 benchmarks against all 10 models
- [ ] Draft writeup: `repo/WRITEUP_SOCIAL_COGNITION.md`

## Workflow

### Phase 1: Metacognition submission (now)
1. ✅ Writeup drafted
2. Ian submits on Kaggle + confirms whether multiple writeups allowed
3. Optional: re-run 10-model suite for updated numbers

### Phase 2: Fix flagged benchmarks (parallel with writeup drafting)
4. Fix learning_interference, exec_func_wcst, exec_func_tol, social_cog_false_belief, social_cog_pragmatic
5. Re-test fixes against 3 models (Opus, mid-tier, Ministral 3B)

### Phase 3: Run all tracks against all 10 models
6. Full Bedrock runs for attention, learning, exec functions, social cognition
7. Generate per-track discriminatory analysis

### Phase 4: Draft remaining writeups
8. Attention, Learning, Executive Functions, Social Cognition writeups (≤1,500 words each)

### Phase 5: Ian submits remaining tracks
9. Create writeup per track, attach benchmark, submit

## Context
- All 29 benchmarks implemented across 5 tracks
- Notebooks uploaded to Kaggle, made public
- CB tasks registered, benchmark collections created
- 17 models run on CB platform
- 10-model Bedrock cross-validation partially complete (metacog has most coverage)
- Results in `results/score_matrix.csv` and `results/discriminatory_analysis.md`

## Target Models (Amazon Bedrock)
| # | Model | Model ID |
|---|-------|----------|
| 1 | Claude Opus 4.6 | anthropic.claude-opus-4-6-v1 |
| 2 | Claude Sonnet 4.6 | anthropic.claude-sonnet-4-6-v1 |
| 3 | DeepSeek-R1 | deepseek.r1-v1:0 |
| 4 | GLM 4.7 | zai.glm-4.7 |
| 5 | GPT-OSS-120B | openai.gpt-oss-120b-1:0 |
| 6 | Llama 3.3 70B | meta.llama3-3-70b-instruct-v1:0 |
| 7 | Llama 4 Maverick 17B | meta.llama4-maverick-17b-instruct-v1:0 |
| 8 | Ministral 3B | mistral.ministral-3-3b-instruct |
| 9 | Nova Pro | amazon.nova-pro-v1:0 |
| 10 | Qwen3 Next 80B | qwen.qwen3-next-80b-a3b |

## Competition Timeline
- March 17, 2026 — Start
- **April 16, 2026** — Final Submission Deadline (11:59 PM UTC)
- April 17 – May 31, 2026 — Judging Period
- June 1, 2026 — Anticipated Results
