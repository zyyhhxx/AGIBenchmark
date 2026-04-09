# 🚨 IAN'S ACTION ITEMS — Quick Reference
**Last updated:** 2026-04-09 05:55 UTC | **Deadline: April 16, 2026**

> **Agent update (05:55 UTC):** Kaggle API still rate limited (429). Expanded divided attention items 5→15. Created local benchmark runner — confirmed Gemini API works with kbench SDK! Free tier quota exhausted though. **Key discovery: we can run benchmarks locally against Gemini if billing is enabled.** All Kaggle web UI work still needs Ian.

## Priority 1: Upload 4 Missing Notebooks (15 min)
The Kaggle API cannot create or find these notebooks. Upload fresh via web UI.

**Go to:** https://www.kaggle.com/code → "New Notebook" → File → Upload Notebook

| # | File in `repo/notebooks/` | Suggested Title |
|---|---|---|
| 1 | `exec_func_crt.ipynb` | AGI Bench: Cognitive Reflection Test |
| 2 | `metacog_canary.ipynb` | AGI Bench: Contamination Canary |
| 3 | `metacog_epistemic_humility.ipynb` | AGI Bench: Epistemic Humility |
| 4 | `social_cog_emotional_prosody.ipynb` | AGI Bench: Emotional Prosody |

For each: Upload → Settings → **Make Public** → **Enable Internet** → Save

## Priority 2: Clean Up ~70 Duplicate Private Notebooks (10 min)
**Go to:** https://www.kaggle.com/ianstudy/code

There are ~70 private notebooks (ghost entries from API retry loops). Delete any with:
- Title showing as "[Private Notebook]" or blank
- Duplicate titles or slugs
- Keep only the ones with proper "AGI Bench:" titles and 2026 dates

## Priority 3: Make 6 Rate-Limited Notebooks Public (2 min)
**These notebooks were uploaded correctly but remain private due to API rate limits.**

**Go to:** https://www.kaggle.com/ianstudy/code → find each notebook → Settings → Make Public

| # | Kaggle Slug | Direct Link |
|---|-------------|-------------|
| 1 | agi-bench-2026-epistemic-humility-v2 | https://www.kaggle.com/code/ianstudy/agi-bench-2026-epistemic-humility-v2 |
| 2 | agi-bench-2026-error-detection-submetrics-v2 | https://www.kaggle.com/code/ianstudy/agi-bench-2026-error-detection-submetrics-v2 |
| 3 | agi-bench-2026-fok-v2 | https://www.kaggle.com/code/ianstudy/agi-bench-2026-fok-v2 |
| 4 | agi-bench-2026-fok-submetrics-v2 | https://www.kaggle.com/code/ianstudy/agi-bench-2026-fok-submetrics-v2 |
| 5 | agi-bench-2026-jol-v2 | https://www.kaggle.com/code/ianstudy/agi-bench-2026-jol-v2 |
| 6 | agi-bench-2026-jol-submetrics-v2 | https://www.kaggle.com/code/ianstudy/agi-bench-2026-jol-submetrics-v2 |

For each: Settings → **Make Public** → Save. That's all — content is already correct.

## Priority 4: Submit to Community Benchmarks (30 min)
**Go to:** https://www.kaggle.com/benchmarks/tasks/new

For each of the 25 core benchmark notebooks:
1. "Import from Notebook" → search by title
2. The `@kbench.task` decorator handles registration
3. Run the notebook to create the CB task

**Do NOT submit:** submission_overview, dashboard, test notebooks

See `KAGGLE_SUBMISSION_PLAYBOOK.md` for full details and recommended order.

## Priority 5: Post Discussion (5 min)
Copy `KAGGLE_DISCUSSION_DRAFT.md` content to a new discussion post on:
https://www.kaggle.com/competitions/kaggle-measuring-agi/discussion

Community upvotes = **15% of the final score**.

---

## What's Already Done (no action needed)
- ✅ 29 benchmarks implemented and validated
- ✅ 26 notebooks already public on Kaggle
- ✅ All notebooks have pip installs, @kbench.task, .run() calls
- ✅ Submission narrative, methodology, cognitive rationale written
- ✅ Psychometric validation complete
- ✅ All DESIGN.md files up to date
- ✅ Local benchmark runner ready: `scripts/run_benchmark_local.py`
- ✅ Expanded divided attention items (5→15)
- ✅ Predicted cognitive profiles for frontier models

## NEW: Get Frontier Model Results Locally
The agent discovered that benchmarks can run locally against Gemini via the kbench SDK.
**If billing is enabled on the Gemini API key:**
```bash
cd repo
.venv/bin/python3 scripts/run_benchmark_local.py --model gemini-2.5-flash --benchmark metacog_canary
# Or run all:
.venv/bin/python3 scripts/run_benchmark_local.py --model gemini-2.5-pro --benchmark all --output results/gemini_2.5_pro.json
```
This would give us actual frontier model results for the narrative — a major differentiator vs just mock data.
