# 🚨 IAN'S ACTION ITEMS — Quick Reference
**Last updated:** 2026-04-09 04:55 UTC | **Deadline: April 16, 2026**

> **Agent update (04:55 UTC):** Fixed mock_validate.py (all 5 tests pass now). Tried multiple Kaggle API approaches (old CLI, new kagglesdk) — all fail with 409 Conflict or rate limits. The 4 notebooks exist as orphaned private entries that can't be accessed via API. ~70 "[Private Notebook]" ghost entries on the account. **All Kaggle work needs web UI.**

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

## Priority 3: Make Any Private Benchmarks Public (2 min)
If any of the 26 existing benchmark notebooks show as private, toggle them to public via Settings.

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
