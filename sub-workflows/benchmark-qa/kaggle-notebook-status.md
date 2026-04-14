# Kaggle Notebook Status Report
_Generated: 2026-04-09_

## 4 Target Notebooks

| Notebook | Ref | Current Status | API Toggle Result |
|----------|-----|---------------|-------------------|
| CRT v2 | `ianstudy/agi-bench-2026-crt-v2` | Private (metadata confirms `is_private: true`) | **BLOCKED** — 429 rate limit |
| Canary Metacog | `ianstudy/agi-bench-2026-canary-metacog` | Private | **BLOCKED** — 429 rate limit |
| Epistemic Humility v2 | `ianstudy/agi-bench-2026-epistemic-humility-v2` | Private | **BLOCKED** — 429 rate limit |
| Emotional Prosody v2 | `ianstudy/agi-bench-2026-emotional-prosody-v2` | Private | **BLOCKED** — 429 rate limit |

## API Visibility Toggle Approach
1. Pulled each notebook with `kaggle kernels pull` (succeeded)
2. Modified `kernel-metadata.json` to set `is_private: false`
3. Pushed with `kaggle kernels push` — all 4 failed with **429 Too Many Requests**
4. Waited 60s and retried — still 429. Rate limit appears to be daily quota, likely exhausted by prior duplicate pushes.

## Action Required by Ian
- **Make 4 notebooks public**: Go to each notebook on kaggle.com → Settings → Change visibility to Public
  - https://www.kaggle.com/code/ianstudy/agi-bench-2026-crt-v2
  - https://www.kaggle.com/code/ianstudy/agi-bench-2026-canary-metacog
  - https://www.kaggle.com/code/ianstudy/agi-bench-2026-epistemic-humility-v2
  - https://www.kaggle.com/code/ianstudy/agi-bench-2026-emotional-prosody-v2

## Duplicate Notebooks — 38 Phantom Entries
- 38 "[Private Notebook]" entries with `id=0`, empty ref/slug, date `2010-04-01`
- These are ghost entries — **cannot be deleted via API** (no addressable identifier)
- **Ian must delete these manually** via Kaggle web UI: https://www.kaggle.com/ianstudy/code → delete each phantom entry

## Prepared Metadata (ready for retry when rate limit clears)
Files saved at `/tmp/kaggle-agi-bench-2026-*/kernel-metadata.json` with `is_private: false`.
To retry later:
```bash
for nb in crt-v2 canary-metacog epistemic-humility-v2 emotional-prosody-v2; do
  kaggle kernels push -p /tmp/kaggle-agi-bench-2026-$nb
done
```
