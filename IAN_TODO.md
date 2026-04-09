# 🚨 IAN'S ACTION ITEMS — Quick Reference
**Last updated:** 2026-04-09 03:56 UTC | **Deadline: April 16, 2026**

> **Agent update (3:56 UTC):** Hardened 8 benchmarks with structured output fallbacks (they would have crashed on some models). Added second rule system to epistemic revision for better reliability. Discussion post enhanced. All notebooks regenerated. Kaggle API still rate-limited.

## Priority 1: Upload 4 Missing Notebooks (10 min)
The Kaggle API is rate-limited and has been for ~6 hours. These 4 notebooks need manual upload.

**Go to:** https://www.kaggle.com/code → "New Notebook" → File → Upload Notebook

| # | File in `repo/notebooks/` | Suggested Title |
|---|---|---|
| 1 | `exec_func_crt.ipynb` | AGI Bench: Cognitive Reflection Test |
| 2 | `metacog_canary.ipynb` | AGI Bench: Contamination Canary |
| 3 | `metacog_epistemic_humility.ipynb` | AGI Bench: Epistemic Humility |
| 4 | `social_cog_emotional_prosody.ipynb` | AGI Bench: Emotional Prosody |

For each: Upload → Settings → **Make Public** → **Enable Internet** → Save

## Priority 2: Clean Up Duplicate Private Notebooks (5 min)
**Go to:** https://www.kaggle.com/ianstudy/code

There are ~32 private notebooks (duplicates from API retry failures). Delete any with:
- Dates of `2010-04-01` (phantom entries)
- Duplicate titles or slugs
- Keep only the ones with proper titles and 2026 dates

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
