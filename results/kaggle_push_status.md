# Kaggle Push Status — 2026-04-09 Retry

## Summary
- **Total attempted:** 26 notebooks (18 v2-pending + 8 visibility-only re-pushes)
- **Successful:** 20/26
- **Failed (429 rate limit):** 6
- **Push method:** `kaggle kernels push` with `is_private: false`
- **Batching:** groups of 3 with 60s delays

## Successful Pushes (20)

### Batch 1 — Test push
| Notebook | Kaggle Slug | Result |
|----------|-------------|--------|
| attention_selective | ianstudy/agi-bench-selective-attention | ✅ v8, public |

### Batch 2 — v2 pending notebooks (17/17 success)
| Notebook | Kaggle Slug | Result |
|----------|-------------|--------|
| metacog_error_detection | ianstudy/agi-bench-2026-error-detection-metacog | ✅ v5, public |
| metacog_learning_monitoring | ianstudy/agi-bench-2026-learning-monitoring-task | ✅ v1, public |
| metacog_control | ianstudy/metacog-ctrl-test-apr08 | ✅ v1, public |
| metacog_epistemic_revision | ianstudy/epistemic-revision-benchmark-agi-2026a | ✅ v1, public |
| learning_curves | ianstudy/agi-bench-learning-curves | ✅ v7, public |
| learning_transfer | ianstudy/agi-bench-near-vs-far-transfer | ✅ v7, public |
| learning_interference | ianstudy/agi-bench-proactive-retroactive-interference | ✅ v7, public |
| learning_curriculum | ianstudy/agi-bench-curriculum-sensitivity | ✅ v8, public |
| attention_instruction_update | ianstudy/agi-bench-2026-instruction-update-task | ✅ v5, public |
| exec_func_task_switch | ianstudy/agi-bench-task-switching | ✅ v5, public |
| exec_func_nback | ianstudy/agi-bench-n-back | ✅ v5, public |
| exec_func_tol | ianstudy/agi-bench-2026-tower-of-london-task | ✅ v5, public |
| social_cog_false_belief | ianstudy/agi-bench-false-belief-tom | ✅ v5, public |
| social_cog_sarcasm | ianstudy/sarcasm-detection-benchmark-agi-2026a | ✅ v5, public |
| submission_overview | ianstudy/submission-overview-agi-bench-apr08 | ✅ v1, public |
| exec_func_wcst | ianstudy/wcst-benchmark-agi-2026a | ✅ v5, public |
| social_cog_pragmatic | ianstudy/agi-bench-pragmatic-inference | ✅ v5, public |

### Batch 3 — Visibility re-pushes (2/8 success before rate limit)
| Notebook | Kaggle Slug | Result |
|----------|-------------|--------|
| metacog_calibration | ianstudy/agi-bench-2026-calibration-v2 | ✅ v4, public |
| metacog_canary | ianstudy/agi-bench-2026-canary-metacog | ✅ v6, public |

## Failed Pushes — 429 Rate Limit (6)

These notebooks were already on Kaggle with correct content but need visibility toggled to public.
**Ian must toggle these to public via Kaggle web UI**, or wait for rate limit reset and retry.

| Notebook | Kaggle Slug | Current Status |
|----------|-------------|---------------|
| metacog_epistemic_humility | ianstudy/agi-bench-2026-epistemic-humility-v2 | Private, needs public toggle |
| metacog_error_detection_submetrics | ianstudy/agi-bench-2026-error-detection-submetrics-v2 | Private, needs public toggle |
| metacog_fok | ianstudy/agi-bench-2026-fok-v2 | Private, needs public toggle |
| metacog_fok_submetrics | ianstudy/agi-bench-2026-fok-submetrics-v2 | Private, needs public toggle |
| metacog_jol | ianstudy/agi-bench-2026-jol-v2 | Private, needs public toggle |
| metacog_jol_submetrics | ianstudy/agi-bench-2026-jol-submetrics-v2 | Private, needs public toggle |

## Not Attempted (5 notebooks)

These notebooks were not in the "v2 pending" list or already had correct versions:
- `attention_divided` — already public (divided-attention-benchmark-agi-2026a)
- `attention_vigilance` — already on Kaggle (agi-bench-2026-vigilance-attention)
- `exec_func_crt` — already on Kaggle (agi-bench-2026-crt-v2)
- `social_cog_emotional_prosody` — already on Kaggle (agi-bench-2026-emotional-prosody-v2)
- `results_dashboard` — not a benchmark notebook

## Push directories with `is_private: false` ready for retry
All 6 failed notebooks have updated `kernel-metadata.json` in `repo/kaggle_push/` with `is_private: false`.
To retry: `kaggle kernels push -p repo/kaggle_push/<notebook_name>`
