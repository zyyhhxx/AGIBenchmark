# Metacognition Benchmark Scores — GPT-4o

## Status: SCORES PENDING ON KAGGLE COMMUNITY BENCHMARKS PLATFORM

**Date:** 2026-04-09
**Iteration:** 4

## Summary

All 11 metacognition benchmark notebooks have been:
1. ✅ Fixed with `%choose <task_name>` cell (was previously commented out)
2. ✅ Pushed to Kaggle platform
3. ✅ All 11 notebooks ran to COMPLETE status
4. ✅ All 11 produced task.json registration files

**Root cause of previous failures:** The `%choose` magic command was commented out (`# %choose metacog_calibration`). Without this, the kbench SDK registered the task definition but never submitted it for scoring on the Community Benchmarks platform.

## How Scoring Works

The kbench SDK scoring pipeline:
1. `%choose task_name` → registers the task definition with Kaggle Community Benchmarks
2. Kaggle CB platform schedules the task to run against available models (GPT-4o, Gemini, etc.)
3. Scores appear on the Community Benchmarks leaderboard (web UI only)
4. **There is no API or CLI to retrieve CB scores** — only visible on Kaggle web UI

## Notebooks Pushed (11 of 12)

| Notebook | Kaggle Slug | %choose Task | Status |
|----------|-------------|-------------|--------|
| metacog_calibration | ianstudy/agi-bench-2026-calibration-v2 | metacog_calibration | COMPLETE |
| metacog_canary | ianstudy/agi-bench-2026-canary-metacog | metacog_canary | COMPLETE |
| metacog_control | ianstudy/agi-bench-2026-control-v2 | metacog_control | COMPLETE |
| metacog_epistemic_humility | ianstudy/agi-bench-2026-epistemic-humility-v2 | metacog_epistemic_humility | COMPLETE |
| metacog_error_detection | ianstudy/agi-bench-2026-error-detection-v2 | metacog_error_detection | COMPLETE |
| metacog_error_detection_submetrics | ianstudy/agi-bench-2026-error-detection-submetrics-v2 | metacog_error_detection_f1 | COMPLETE |
| metacog_fok | ianstudy/agi-bench-2026-fok-v2 | metacog_fok | COMPLETE |
| metacog_fok_submetrics | ianstudy/agi-bench-2026-fok-submetrics-v2 | metacog_fok_gamma | COMPLETE |
| metacog_jol | ianstudy/agi-bench-2026-jol-v2 | metacog_jol | COMPLETE |
| metacog_jol_submetrics | ianstudy/agi-bench-2026-jol-submetrics-v2 | metacog_jol_gamma | COMPLETE |
| metacog_learning_monitoring | ianstudy/agi-bench-2026-learning-monitoring | metacog_learning_monitoring | COMPLETE |

## Not Pushed (1 of 12)

| Notebook | Issue |
|----------|-------|
| metacog_epistemic_revision | No `@kbench.task` decorator — task definition missing. Needs task code added. |

## Submetrics Limitation

The kbench SDK only supports **one `%choose` per notebook**. For multi-task notebooks (submetrics), only one task is registered:
- error_detection_submetrics → only `metacog_error_detection_f1` (not ece, gamma, localization)
- fok_submetrics → only `metacog_fok_gamma` (not ece, auc)
- jol_submetrics → only `metacog_jol_gamma` (not ece, recall)

To register all submetric tasks, each would need its own notebook.

## Next Steps for Ian

1. **Check Community Benchmarks page** for each task to see if scores have appeared:
   - https://www.kaggle.com/benchmarks
   - Search for task names like "metacog_calibration"
2. **Note:** Notebooks must be **public** before CB tasks are scored
   - All notebooks were pushed as private
   - Ian needs to toggle them to public via Kaggle web UI
3. **Record scores** once visible on the CB leaderboard
4. **Fix epistemic_revision** — needs `@kbench.task` decorator and task code
5. **Split submetrics notebooks** if all sub-tasks need individual scores
