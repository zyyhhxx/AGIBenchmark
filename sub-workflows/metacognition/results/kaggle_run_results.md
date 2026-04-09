# Metacognition Benchmark Kaggle Run Results

**Date:** 2026-04-09
**Model:** GPT-4o (Kaggle default model via kbench SDK)

## Run Status

All 12 metacognition benchmark notebooks executed successfully on the Kaggle platform.

| # | Notebook | Kaggle Slug | Status | Tasks |
|---|----------|-------------|--------|-------|
| 1 | metacog_calibration | ianstudy/agi-bench-2026-calibration-v2 | ✅ COMPLETE | metacog_calibration |
| 2 | metacog_canary | ianstudy/agi-bench-2026-canary-metacog | ✅ COMPLETE | metacog_canary |
| 3 | metacog_control | ianstudy/agi-bench-2026-control-v2 | ✅ COMPLETE | metacog_control |
| 4 | metacog_epistemic_humility | ianstudy/agi-bench-2026-epistemic-humility-v2 | ✅ COMPLETE | metacog_epistemic_humility |
| 5 | metacog_epistemic_revision | ianstudy/agi-bench-2026-epistemic-revision | ✅ COMPLETE | metacog_epistemic_revision |
| 6 | metacog_error_detection | ianstudy/agi-bench-2026-error-detection-v2 | ✅ COMPLETE | metacog_error_detection |
| 7 | metacog_error_detection_submetrics | ianstudy/agi-bench-2026-error-detection-submetrics-v2 | ✅ COMPLETE | metacog_error_detection_f1, _localization, _ece, _gamma |
| 8 | metacog_fok | ianstudy/agi-bench-2026-fok-v2 | ✅ COMPLETE | metacog_fok |
| 9 | metacog_fok_submetrics | ianstudy/agi-bench-2026-fok-submetrics-v2 | ✅ COMPLETE | metacog_fok_gamma, _ece, _auc |
| 10 | metacog_jol | ianstudy/agi-bench-2026-jol-v2 | ✅ COMPLETE | metacog_jol |
| 11 | metacog_jol_submetrics | ianstudy/agi-bench-2026-jol-submetrics-v2 | ✅ COMPLETE | metacog_jol_gamma, _ece, _recall |
| 12 | metacog_learning_monitoring | ianstudy/agi-bench-2026-learning-monitoring | ✅ COMPLETE | metacog_learning_monitoring |

## Score Retrieval

Actual GPT-4o scores are recorded by the kbench SDK internally and visible on each notebook's Kaggle page. 
The Kaggle API does not expose benchmark scores programmatically — scores must be viewed on the notebook output page or competition leaderboard.

**To view scores:** Open each notebook URL on Kaggle (e.g., `https://www.kaggle.com/code/ianstudy/agi-bench-2026-calibration-v2`) and check the task output section.

## Key Fixes Applied

1. **Replaced `.run(llm=kbench.kaggle.load_default_model())` with `%choose task_name`** — The `load_default_model()` call raises RuntimeError because `MODEL_PROXY_URL` isn't directly set. The correct pattern (matching working competition notebooks) uses `%choose` magic which lets the platform inject the model.

2. **Pushed as private notebooks** — Public notebook push quota was exhausted (daily rate limit). All notebooks pushed as private with `competition_sources: kaggle-measuring-agi` to get access to the kbench runtime.

3. **Title conflicts resolved** — 8 notebooks had title conflicts with existing private notebooks. Created with "-v2" suffix titles to avoid 409 errors.

## Notebook URLs

- https://www.kaggle.com/code/ianstudy/agi-bench-2026-calibration-v2
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-canary-metacog
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-control-v2
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-epistemic-humility-v2
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-epistemic-revision
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-error-detection-v2
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-error-detection-submetrics-v2
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-fok-v2
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-fok-submetrics-v2
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-jol-v2
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-jol-submetrics-v2
- https://www.kaggle.com/code/ianstudy/agi-bench-2026-learning-monitoring

## Notes

- All notebooks currently private (public push daily quota hit)
- Ian needs to make notebooks public for competition submission
- epistemic_revision completed but didn't produce a task.json — may need investigation
- Scores are only visible on Kaggle UI, not through API
