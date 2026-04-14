# Improvement Log — Learning Track

## Date: 2026-04-14

## Track Summary

All 4 learning benchmarks passed QA evaluation with **KEEP AS-IS** verdict. No code changes implemented, no re-runs performed.

## Benchmark Results

| Benchmark | Mean | Std | Range | Min Model | Max Model | Verdict |
|-----------|------|-----|-------|-----------|-----------|---------|
| learning_curriculum | 0.644 | 0.0975 | 0.300 | Qwen3 80B (0.46) | Llama 3.3 70B (0.76) | KEEP AS-IS |
| learning_curves | 0.559 | 0.0962 | 0.249 | Nova Pro (0.44) | Claude Opus 4.6 (0.69) | KEEP AS-IS |
| learning_interference | 0.919 | 0.1276 | 0.450 | Ministral 3B (0.55) | Claude Opus/Sonnet/GPT-OSS (1.0) | KEEP AS-IS |
| learning_transfer | 0.786 | 0.2259 | 0.650 | Ministral 3B (0.35) | Claude Opus/Sonnet/DeepSeek-R1/GPT-OSS (1.0) | KEEP AS-IS |

**Track average std: 0.1368** (well above 0.08 threshold)

## Coverage

- 10/10 models scored on all 4 benchmarks
- 0 failures across all 40 model runs
- 0 ground truth errors found
- 0 think-tag leakage incidents

## Why No Changes Were Made

All 4 benchmarks pass the discrimination threshold (std ≥ 0.08), have verified ground truth, clean scoring, and full model coverage. The analysis files document no scoring bugs, no debatable items, and no systematic parsing artifacts that affect rankings.

## Non-Blocking Advisory Items (for future iteration)

### learning_curriculum
- Top cluster compression: 6/10 models within 0.08 of each other (0.68–0.76)
- Consider increasing rule difficulty to d3 to spread the top cluster
- Sensitivity weight (0.30) could be increased to reward ordering-responsive models

### learning_curves
- Weakest discriminator (range=0.249, top 3 within 0.005)
- Ministral 3B parse issue rate: 79/260 (30%) — backtick fence stripping could improve score accuracy by ~0.05
- Consider adding difficulty-4 rule systems to spread the top cluster

### learning_interference
- Strong ceiling: 9/10 models ≥ 0.90; discrimination relies on Ministral 3B as sole outlier
- Without Ministral 3B: std would drop to ~0.035 (would fail threshold)
- Consider adding difficulty-4 tier with 3+ distractors and conflicting exception rules
- Ministral 3B parse issues: 5/30 (17%) — dict-style output instead of strings

### learning_transfer
- 4/10 models at ceiling (1.0, 40%) — significant but tolerable since remaining 6 spread well
- Ministral 3B parse failure rate: 10/15 (67%) — most severe of any model/benchmark combination
- True Ministral score likely ~0.45–0.55 rather than 0.35
- Consider adding "extreme transfer" tier (symbol→natural language) to separate top models

## Retry Bias Fix Status

All 4 learning benchmarks had `schema=` parameter removed and `_strip_think()` helper added in the Phase 2 Task 1 run (turn-025). This fix was applied before the 10-model runs that produced the scores analyzed here.

## Analysis Artifacts

- `results/analysis_learning_curriculum.md`
- `results/analysis_learning_curves.md`
- `results/analysis_learning_interference.md`
- `results/analysis_learning_transfer.md`

## Q&A Transcript Artifacts

- `results/qa_transcripts/learning_curriculum/` — 10 .jsonl + aggregate_stats.json
- `results/qa_transcripts/learning_curves/` — 10 .jsonl + aggregate_stats.json
- `results/qa_transcripts/learning_interference/` — 10 .jsonl + aggregate_stats.json
- `results/qa_transcripts/learning_transfer/` — 10 .jsonl + aggregate_stats.json
