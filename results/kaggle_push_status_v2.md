# Kaggle Push Status v2 — 2026-04-09 Retry

## Summary
- **Attempted:** 6 notebooks (the ones that failed with 429 in v1)
- **Successful:** 0/6
- **Failed (429 rate limit):** 6/6
- **Rate limit status:** Still active — API returns `429 Too Many Requests`

## Test Results

| # | Notebook | Kaggle Slug | Result |
|---|----------|-------------|--------|
| 1 | metacog_epistemic_humility | ianstudy/agi-bench-2026-epistemic-humility-v2 | ❌ 429 rate limit |
| 2 | metacog_canary (control test) | ianstudy/agi-bench-2026-canary-metacog | ❌ Different error (already public) |

Remaining 5 not attempted — rate limit confirmed still active:

| Notebook | Kaggle Slug | Status |
|----------|-------------|--------|
| metacog_error_detection_submetrics | ianstudy/agi-bench-2026-error-detection-submetrics-v2 | Private, needs manual toggle |
| metacog_fok | ianstudy/agi-bench-2026-fok-v2 | Private, needs manual toggle |
| metacog_fok_submetrics | ianstudy/agi-bench-2026-fok-submetrics-v2 | Private, needs manual toggle |
| metacog_jol | ianstudy/agi-bench-2026-jol-v2 | Private, needs manual toggle |
| metacog_jol_submetrics | ianstudy/agi-bench-2026-jol-submetrics-v2 | Private, needs manual toggle |

## Conclusion

The Kaggle API rate limit has **not reset** since the initial batch push. All 6 notebooks have correct content uploaded but remain private. The only path forward is:

1. **Manual toggle via Kaggle web UI** — Ian toggles each notebook's visibility from Private → Public
2. **Wait longer** — rate limit may need 24-48h to fully reset, then retry via API

All 6 push directories in `repo/kaggle_push/` have `is_private: false` set and are ready for retry once the rate limit clears.
