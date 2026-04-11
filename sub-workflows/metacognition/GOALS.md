# GOALS.md — AGI Benchmark Hackathon (Model Testing & Discriminatory Power)

## Active Goal
Test all benchmarks against 10 models via Bedrock, fix non-discriminatory benchmarks, and polish the final submission. Deadline: **April 16, 2026**.

## ⛔ Hard Rule
**DO NOT upload notebooks to Kaggle using the CLI or API.** Let the human handle all Kaggle uploads manually via the web UI.

## Context
- All 29 benchmarks are implemented across 5 tracks
- Notebooks uploaded to Kaggle, benchmarks run against 17 models on Kaggle CB
- Discussion thread posted
- The benchmarks use `kaggle_benchmarks` SDK (`kbench.llm`, `kbench.chats.new()`)
- For local testing, we need to adapt `scripts/run_benchmark_local.py` (currently Gemini-only) to support Amazon Bedrock models via `boto3`
- All test models are on Amazon Bedrock (us-east-1 region)
- Final benchmark results shown in the writeup can be placeholder — Ian will run on Kaggle for final numbers

## Task 1: Build a Bedrock-Compatible Local Test Runner
Extend or rewrite `scripts/run_benchmark_local.py` to support Amazon Bedrock models.
- The kbench SDK expects an LLM interface — study how `kbench.llm` works and create a compatible Bedrock adapter
- If kbench doesn't support custom LLM backends, build a standalone test harness that imports the benchmark logic directly and calls Bedrock via boto3's `converse` API
- Must support all 10 models listed below
- Output results as JSON: `results/{model_id}.json` with per-benchmark scores

### Target Models (Amazon Bedrock)
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

## Task 2: Run All Benchmarks Against All 10 Models
- Run each of the 29 benchmarks against each model
- Save results to `results/{model_id}.json`
- Create a summary matrix: `results/score_matrix.csv` (rows=benchmarks, columns=models)
- Note: some models may not support certain features (e.g., system prompts, tool use) — handle gracefully with error codes, don't crash
- **Model availability:** If a target model is unavailable on Bedrock (e.g., legacy, deprecated, or region-restricted), autonomously select a suitable substitute that preserves the test roster's diversity of providers and capability tiers. Document the substitution and rationale in `results/model_substitutions.md`.

## Task 3: Discriminatory Power Analysis
**Key competition requirement:** benchmarks must discriminate between models of different capability levels.
- For each benchmark, compute the score range across all 10 models
- Flag benchmarks where all models score > 0.9 (too easy) or all models score < 0.1 (too hard)
- Flag benchmarks where the standard deviation of scores across models is < 0.05 (non-discriminatory)
- For each flagged benchmark:
  - Analyze why it's non-discriminatory
  - Propose and implement fixes (harder items, different scoring, additional sub-tasks)
  - Re-test the fixed benchmark against at least 3 models (strongest, weakest, mid-tier) to confirm improved discrimination
- Produce `results/discriminatory_analysis.md` with findings

## Task 4: Competition Requirements Review & Writeup Polish
- Fetch and review: https://www.kaggle.com/competitions/kaggle-measuring-agi/overview
- Cross-reference all requirements against our submission
- Improve `SUBMISSION_NARRATIVE.md` and `KAGGLE_DISCUSSION_DRAFT.md`:
  - Add discriminatory power analysis results
  - Add cross-model comparison (use placeholder scores if final Kaggle results aren't available yet)
  - Ensure all required sections are present and strong
  - Add any missing sections identified in the requirements review
- Update `IAN_TODO.md` with final action items

## Task 5: Remove Sub-Metrics Notebooks
Kaggle Community Benchmarks outputs only one single score per benchmark, so sub-metrics notebooks are not useful.
- Delete these 3 notebooks from `repo/notebooks/`:
  - `metacog_error_detection_submetrics.ipynb`
  - `metacog_fok_submetrics.ipynb`
  - `metacog_jol_submetrics.ipynb`
- Remove any corresponding benchmark modules if they exist
- Update any references to these notebooks in other files (README, SUBMISSION_NARRATIVE, etc.)
- Do NOT delete them from Kaggle — Ian will handle that manually

## Quality Standards
- Benchmarks must show meaningful score variation across the 10 models
- The writeup must address discriminatory power explicitly (judges care about this)
- Test runner must be robust — retry on transient errors, timeout handling, rate limiting
- All results reproducible
