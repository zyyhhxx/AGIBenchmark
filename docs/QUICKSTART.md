# 🚀 Quick Start: What Ian Needs to Do

**Time needed:** ~30 min | **Deadline:** April 16, 2026

## Step 1: Upload 4 Notebooks (10 min)
Go to https://www.kaggle.com/code → **New Notebook** → **File → Upload Notebook**

Upload each file from `repo/notebooks/`:
1. `exec_func_crt.ipynb` → Title: "AGI Bench: Cognitive Reflection Test"
2. `metacog_canary.ipynb` → Title: "AGI Bench: Contamination Canary"
3. `metacog_epistemic_humility.ipynb` → Title: "AGI Bench: Epistemic Humility"
4. `social_cog_emotional_prosody.ipynb` → Title: "AGI Bench: Emotional Prosody"

**For each:** Settings → ✅ Make Public → ✅ Enable Internet → Save

## Step 2: Delete Ghost Notebooks (5 min)
Go to https://www.kaggle.com/ianstudy/code → Delete any notebooks with:
- No title / "[Private Notebook]"
- "error-det-bench-private-test" 
- "test-notebook-apr-08-2026"
- "notebook37fccd987c"

**Keep all notebooks starting with "AGI Bench"** or matching benchmark names.

## Step 3: Submit to Community Benchmarks (15 min)
Go to https://www.kaggle.com/benchmarks/tasks/new

For each of the 25 core benchmark notebooks:
1. "Import from Notebook" → search title
2. The `@kbench.task` decorator handles registration
3. Click Run

**See `KAGGLE_SUBMISSION_PLAYBOOK.md` for full order and details.**

## Step 4: Post Discussion (2 min)
Copy content from `KAGGLE_DISCUSSION_DRAFT.md` to:
https://www.kaggle.com/competitions/kaggle-measuring-agi/discussion

Community upvotes = **15% of final score!**

---
*All code is committed and pushed. Agent is running hourly cron to update notebooks on Kaggle.*
