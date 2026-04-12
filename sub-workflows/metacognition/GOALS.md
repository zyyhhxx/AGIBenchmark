# GOALS.md — AGI Benchmark Hackathon (Final Submission)

## Active Goal
Submit **5 writeups** (one per track) to maximize prize chances. Deadline: **April 16, 2026** (11:59 PM UTC).

**PRIORITY: Fix metacognition track first**, then bring all other tracks to the same quality.

Priority order: Metacognition → Attention → Learning → Executive Functions → Social Cognition.

**SCOPE: ALL 5 TRACKS, NOT JUST METACOGNITION.**
- Fix all benchmarks with std < 0.08 so every benchmark passes the threshold
- Run ALL benchmarks against ALL 10 Bedrock models (this works — most already have 10/10 scores)
- Draft a ≤1,500-word writeup per track following the required template
- Generate a cover image per track
- Produce a discriminatory analysis summary per track

Do NOT declare the workflow complete until all 5 tracks have: (1) all benchmarks passing std ≥ 0.08, (2) full 10-model results, (3) a polished writeup, and (4) a cover image.

## ⛔ Hard Rules
- **DO NOT upload notebooks to Kaggle using the CLI or API.** Let the human handle all Kaggle uploads manually via the web UI.
- **Each writeup must not exceed 1,500 words.** Follow the required template exactly.
- **All notebooks MUST be self-contained.** No `from data.*` imports — data must be inlined in the notebook. Kaggle has no access to local modules.
- **No duplicate execution.** Each notebook must have exactly ONE `@kbench.task` definition and ONE `.run()` call. `if __name__ == "__main__"` guards do NOT work in Jupyter — `__name__` is always `"__main__"`.
- **All notebook bugs (duplicate cells, broken imports, nbconvert duplicate) have been fixed.** If any new notebooks are created or modified, ensure they follow the same rules: one `@kbench.task`, one `.run()`, no `from data.*` imports, all data inlined.
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

## Metacognition Architecture Improvements (from 2026-04-12 review)

Architectural analysis identified redundancies, ceiling effects, and coverage gaps.
These should be addressed before final submission.

### Canary → Demote to Pass/Fail Gate
- Canary measures factuality detection, not true metacognition
- All frontier models score ~0.99 — no discrimination at the top
- **Action:** Demote to a pass/fail gate (>0.5 = pass). Not scored on the leaderboard.
- The fabrication-detection construct is subsumed by Calibration + Epistemic Humility

### Calibration → Run with v2 Questions
- New v2 question set (80 handcrafted across 5 difficulty tiers + 40 procedural) is pushed
- Targets ~60-70% overall accuracy for frontier models (old set was ~99%)
- **Action:** Run on Kaggle, verify scores produce meaningful spread
- Confidence prompt redesigned with clear semantics + 3 examples

### Error Detection → Redesign Harder
- Ceiling effect (0.69–0.99, top models near 1.0)
- **Action:** Add subtle errors (locally valid but globally inconsistent), clean chains with NO errors (tests false positive rate), multi-error chains (0/1/2/3 errors)
- Goal: push frontier std above 0.08

### Epistemic Revision → Redesign Harder
- Some ceiling (0.67–0.96)
- **Action:** Add ambiguous evidence (could be consistent or contradictory), conflicting sources with different reliability, cases where NOT revising is correct
- Tests genuine belief evaluation vs. reflexive compliance

### Learning Monitoring → Redesign or Merge into JOL
- Overlaps with JOL (both measure predicting own learning)
- Ceiling effect (0.69–0.91)
- **Action:** If time permits, redesign with adversarial learning material + interference tasks. Otherwise merge the online monitoring concept into an expanded JOL.

### NEW: Ease of Learning (EOL) — Add if Time Permits
- Biggest gap in Nelson & Narens monitoring timeline (pre-encoding monitoring)
- Present tasks of varying difficulty, have model predict difficulty BEFORE engaging, score prediction accuracy
- Completes the monitoring chain: EOL → JOL → FOK → Retrospective Calibration
- **Action:** Implement only if all other fixes are done and time remains

### Priority Order for Remaining Work
1. Run Calibration v2 on Kaggle — verify it works
2. Fix Error Detection ceiling (highest impact — currently below std threshold)
3. Fix Epistemic Revision ceiling
4. Demote Canary to gate in writeup
5. Learning Monitoring redesign (if time)
6. EOL benchmark (stretch goal)

## Current Status (as of 2026-04-12)

All 26 benchmarks have 10/10 model scores (except learning_curves 9/10, exec_func_nback 9/10).

### Metacognition — PRIORITY 1 (needs 1 fix)
| Benchmark | Mean | Std | Status |
|-----------|------|-----|--------|
| metacog_calibration | 0.165 | 0.332 | ✅ |
| metacog_canary | 0.795 | 0.305 | ✅ |
| metacog_control | 0.549 | 0.181 | ✅ |
| metacog_epistemic_humility | 0.788 | 0.220 | ✅ |
| metacog_epistemic_revision | 0.801 | 0.102 | ✅ |
| metacog_error_detection | 0.862 | 0.077 | ⚠️ below 0.08 — fix |
| metacog_fok | 0.561 | 0.083 | ✅ |
| metacog_jol | 0.393 | 0.091 | ✅ |
| metacog_learning_monitoring | 0.834 | 0.081 | ✅ |

Writeup: `repo/WRITEUP_METACOGNITION.md` (1,263 words) ✅
Cover image: `repo/assets/metacognition_cover.png` ✅

### Attention — check std after recent fixes
Writeup: `repo/WRITEUP_ATTENTION.md` — verify exists and quality

### Learning — check std after recent fixes
Writeup: `repo/WRITEUP_LEARNING.md` — verify exists and quality

### Executive Functions — check std after recent fixes
Writeup: `repo/WRITEUP_EXECUTIVE_FUNCTIONS.md` — verify exists and quality

### Social Cognition — check std after recent fixes
Writeup: `repo/WRITEUP_SOCIAL_COGNITION.md` — verify exists and quality

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
