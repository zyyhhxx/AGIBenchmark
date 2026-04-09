# Kaggle Notebook Audit Report
**Date:** 2026-04-09

## 4 Target Notebooks (need to be made public)

| # | Slug | Title | Status |
|---|------|-------|--------|
| 1 | `ianstudy/agi-bench-2026-crt-v2` | AGI Bench 2026 CRT v2 | Private |
| 2 | `ianstudy/agi-bench-2026-canary-metacog` | AGI Bench 2026 Canary Metacog | Private |
| 3 | `ianstudy/agi-bench-2026-epistemic-humility-v2` | AGI Bench 2026 Epistemic Humility v2 | Private |
| 4 | `ianstudy/agi-bench-2026-emotional-prosody-v2` | AGI Bench 2026 Emotional Prosody v2 | Private |

## API Visibility Toggle: FAILED

Attempted to toggle visibility by pulling each notebook, setting `is_private: false` in kernel-metadata.json, and pushing via `kaggle kernels push`. All attempts returned **429 Too Many Requests** on the `SaveKernel` endpoint. The account appears to be rate-limited from prior failed push attempts.

**Action for Ian:** Toggle these 4 notebooks to public via the Kaggle web UI:
1. https://www.kaggle.com/code/ianstudy/agi-bench-2026-crt-v2/settings
2. https://www.kaggle.com/code/ianstudy/agi-bench-2026-canary-metacog/settings
3. https://www.kaggle.com/code/ianstudy/agi-bench-2026-epistemic-humility-v2/settings
4. https://www.kaggle.com/code/ianstudy/agi-bench-2026-emotional-prosody-v2/settings

## Duplicate Private Notebooks: 33 ghost entries

Found 33 entries with empty slug/ref, id=0, title="[Private Notebook]", and lastRunTime of 2010-04-01. These are ghost artifacts from failed API pushes — they have no addressable identifier and **cannot be deleted via the Kaggle API**.

**Action for Ian:** Delete these manually from https://www.kaggle.com/ianstudy/notebooks (look for untitled/private notebooks with no content).

## Other Named Notebooks (already public, no action needed)

| Slug | Title |
|------|-------|
| `ianstudy/epistemic-revision-benchmark-agi-2026a` | Epistemic Revision Benchmark AGI 2026a |
| `ianstudy/wcst-benchmark-agi-2026a` | WCST Benchmark AGI 2026a |
| `ianstudy/divided-attention-benchmark-agi-2026a` | Divided Attention Benchmark AGI 2026a |
| `ianstudy/sarcasm-detection-benchmark-agi-2026a` | Sarcasm Detection Benchmark AGI 2026a |
| `ianstudy/agi-bench-2026-tower-of-london-task` | AGI Bench 2026 Tower of London Task |
| `ianstudy/agi-bench-2026-instruction-update-task` | AGI Bench 2026 Instruction Update Task |
| `ianstudy/agi-bench-2026-vigilance-attention` | AGI Bench 2026 Vigilance Attention |
| `ianstudy/agi-bench-2026-learning-monitoring-task` | AGI Bench 2026 Learning Monitoring Task |
