# GOALS.md — AGI Benchmark Hackathon (Final Submission)

## Active Goal
Submit a winning entry to the **Metacognition track**. Deadline: **April 16, 2026** (11:59 PM UTC).

## ⛔ Hard Rules
- **DO NOT upload notebooks to Kaggle using the CLI or API.** Let the human handle all Kaggle uploads manually via the web UI.
- **Writeup must not exceed 1,500 words.** Follow the required template exactly.

## Submission Requirements (from competition rules, verified 2026-04-11)

A valid submission = **Kaggle Writeup** + **attached Kaggle Benchmark**

### Kaggle Writeup
- Created via **"New Writeup"** button on the competition page (NOT a Discussion post)
- Must select **Metacognition** as the track
- ≤1,500 words — submissions over this limit may be penalized
- Must include a **cover image** (required to submit)
- Must click **"Submit"** button — un-submitted or draft writeups will NOT be considered
- Optional attachments: Media Gallery, Public Notebook
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
- Attached via **"Attachments" → "Add a link"** → select benchmark from panel
- URL format: `https://www.kaggle.com/benchmarks/<username>/<benchmark-name>`
- All tasks must be authored by you
- Note: If you attach a private resource to a public writeup, it auto-publishes after deadline

### Evaluation Criteria
| Criteria | Weight | Description |
|----------|--------|-------------|
| Dataset quality & task construction | **50%** | Verifiably correct answers (no ambiguity), sufficient sample size, clean readable code, robust input prompt and output verification |
| Writeup quality | **20%** | Covers all 7 required sections clearly |
| Novelty, insights, discriminatory power | **30%** | Meaningful signal, gradient of performance across models. Benchmark where everyone scores 0% is as useless as one where everyone scores 100% |

### Minimum Requirements
- Target one primary domain (to keep the signal sharp)
- Clearly state which capability is being isolated
- Explain what new insight the benchmark reveals about model behavior within that domain

### Prizes
- 4 × $25,000 grand prizes (best across all tracks)
- 2 × $10,000 track prizes per track (10 track prizes total, 14 unique winners)
- No repeat winners between grand and track prizes

## Current Status (as of 2026-04-11)

### ✅ Completed
- All 29 benchmarks implemented across 5 tracks
- All notebooks uploaded to Kaggle and made **public**
- Ghost/duplicate notebooks deleted
- CB tasks registered on Kaggle Benchmarks platform
- Benchmark collection created
- 17 models run on CB platform
- 10-model Bedrock cross-validation complete (results in `results/score_matrix.csv`)
- Discriminatory analysis complete (results in `results/discriminatory_analysis.md`)
- Writeup drafted: `repo/WRITEUP_METACOGNITION.md` (1,154 words, under limit)

### ❌ Not Yet Done
- [ ] **Ian:** Create Writeup via "New Writeup" on competition page
- [ ] **Ian:** Select "Metacognition" track
- [ ] **Ian:** Paste writeup content from `repo/WRITEUP_METACOGNITION.md`
- [ ] **Ian:** Add cover image
- [ ] **Ian:** Attach benchmark via "Add a link" → select metacognition benchmark
- [ ] **Ian:** Click **"Submit"**

### Optional
- [ ] Re-run full 10-model Bedrock suite post-discrimination-fixes (Task 011)
- [ ] Submit additional tracks (priority: Attention > Learning > Executive Functions > Social Cognition)

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

### Key Insights (highlighted in writeup)
- **Bimodal metacognition:** Strong external monitoring (error detection, epistemic humility) but weak internal self-monitoring (calibration, JOL, FOK)
- **Near-universal calibration failure:** Only Claude Opus scores non-zero on BSS calibration
- **Epistemic humility ≠ model size:** Smaller models sometimes outperform larger ones at admitting uncertainty
- **Strong discriminatory power:** Clear gradient from Ministral 3B (weakest) through mid-tier to Opus (strongest)

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

## Competition Timeline
- March 17, 2026 — Start
- **April 16, 2026** — Final Submission Deadline (11:59 PM UTC)
- April 17 – May 31, 2026 — Judging Period
- June 1, 2026 — Anticipated Results
