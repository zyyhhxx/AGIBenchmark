# GOALS.md — AGI Benchmark Hackathon (Final Submission)

## Active Goal
Submit a winning entry to the **Metacognition track**. Deadline: **April 16, 2026** (11:59 PM UTC).

## ⛔ Hard Rules
- **DO NOT upload notebooks to Kaggle using the CLI or API.** Let the human handle all Kaggle uploads manually via the web UI.
- **Writeup must not exceed 1,500 words.** Follow the required template exactly.

## Submission Requirements (from competition rules)

A valid submission = **Kaggle Writeup** + **attached Kaggle Benchmark**

### Kaggle Writeup
- Created via "New Writeup" button on the competition page
- Must select **Metacognition** as the track
- ≤1,500 words, must include cover image
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
- Benchmark + all tasks should be set to **private** (auto-publish after deadline)
- Attached via "Add a link" under "Attachments" → select benchmark
- URL format: `https://www.kaggle.com/benchmarks/<username>/<benchmark-name>`

### Evaluation Criteria
| Criteria | Weight | Description |
|----------|--------|-------------|
| Dataset quality & task construction | 50% | Verifiably correct answers, sufficient sample size, clean code, robust I/O verification |
| Writeup quality | 20% | Covers all 7 required sections clearly |
| Novelty, insights, discriminatory power | 30% | Meaningful signal, gradient of performance across models |

## Track: Metacognition
**Why this track:** 9 benchmarks (most of any track), 7–10 models tested per benchmark, zero flagged benchmarks, best discriminatory power (avg std=0.172), strongest novel insights.

### Our 9 Metacognition Benchmarks
| Benchmark | Mean | Std | Range | Models |
|-----------|------|-----|-------|--------|
| metacog_calibration | 0.218 | 0.362 | 0.998 | 7 |
| metacog_canary | 0.795 | 0.290 | 1.000 | 10 |
| metacog_control | 0.563 | 0.176 | 0.548 | 9 |
| metacog_epistemic_humility | 0.773 | 0.215 | 0.720 | 9 |
| metacog_epistemic_revision | 0.815 | 0.097 | 0.240 | 7 |
| metacog_error_detection | 0.871 | 0.072 | 0.226 | 9 |
| metacog_fok | 0.577 | 0.064 | 0.230 | 9 |
| metacog_jol | 0.389 | 0.090 | 0.265 | 9 |
| metacog_learning_monitoring | 0.828 | 0.079 | 0.220 | 9 |

### Key Insights for Writeup
- **Calibration failure is universal:** Most models score near 0 on confidence calibration — they can't accurately judge their own certainty
- **Three-tier pattern:** Opus-class > mid-tier > small models, but the gap varies dramatically by metacognitive faculty
- **Epistemic humility surprise:** Some smaller models outperform larger ones at admitting uncertainty
- **Canary benchmark:** Binary detection — clean discriminator between models that can vs can't self-monitor

## Remaining Tasks

### 1. Draft Writeup (≤1,500 words)
- Follow the required template exactly
- Save to `repo/WRITEUP_METACOGNITION.md`
- Ian will copy-paste into Kaggle's writeup editor

### 2. Ian's Manual Actions
- [ ] Create Writeup via "New Writeup" on competition page
- [ ] Select "Metacognition" track
- [ ] Paste writeup content
- [ ] Add cover image
- [ ] Attach benchmark via "Add a link" → select metacognition benchmark
- [ ] Click "Submit"

### 3. Optional: Submit additional tracks
- Can submit separate writeups for other tracks if time permits
- Priority order: Metacognition > Attention > Learning > Executive Functions > Social Cognition

## Context
- All 29 benchmarks implemented across 5 tracks
- 9 metacognition benchmarks tested against 7–10 models via Bedrock
- Benchmark collection and CB tasks created on Kaggle
- Results in `results/score_matrix.csv` and `results/discriminatory_analysis.md`

## Target Models (Amazon Bedrock)
| # | Model | Model ID |
|---|-------|----------|
| 1 | Claude Opus 4.6 | anthropic.claude-opus-4-6-v1 |
| 2 | DeepSeek-R1 | deepseek.r1-v1:0 |
| 3 | gpt-oss-120b | openai.gpt-oss-120b-1:0 |
| 4 | DeepSeek V3.2 | deepseek.v3.2 |
| 5 | Qwen3 Next 80B | qwen.qwen3-next-80b-a3b |
| 6 | Nova Pro | amazon.nova-pro-v1:0 |
| 7 | Llama 4 Maverick 17B | meta.llama4-maverick-17b-instruct-v1:0 |
| 8 | Claude Haiku 4.5 | anthropic.claude-haiku-4-5-20251001-v1:0 |
| 9 | GLM 4.7 | zai.glm-4.7 |
| 10 | Ministral 3B | mistral.ministral-3-3b-instruct |
