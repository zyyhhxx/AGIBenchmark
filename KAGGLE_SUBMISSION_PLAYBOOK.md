# 🚀 Kaggle Submission Playbook

**Last updated:** 2026-04-09 04:55 UTC  
**Status:** ✅ **26 notebooks confirmed public on Kaggle.** 4 new notebooks (CRT, canary, epistemic humility, emotional prosody) may exist as orphaned private entries. API returns 409 Conflict when creating them (title taken) but can't find them by ref. ~70+ duplicate private notebooks from retry attempts. **All upload work is blocked on Ian using the web UI.**

## Critical Issue: 4 Notebooks Stuck in API Limbo

The Kaggle API is in an inconsistent state:
- **`kernels push` with new slug** → 409 Conflict ("title already taken")
- **`kernels push` with old slug** → "Notebook not found"
- **`kagglesdk` SaveKernel** → 409 Conflict  
- **API listing** → Shows as "[Private Notebook]" with no ref/slug
- **Rate limit** → 429 errors persist with ~60s cooldowns

### The simplest fix (Ian — web UI, 15 min):

**Option A (recommended): Upload fresh via web UI**
1. Go to `kaggle.com/code` → **"New Notebook"** → **File → Upload Notebook**
2. Upload these 4 files from `repo/notebooks/`:

| # | File | Title to use |
|---|---|---|
| 1 | `exec_func_crt.ipynb` | AGI Bench: Cognitive Reflection Test |
| 2 | `metacog_canary.ipynb` | AGI Bench: Contamination Canary |
| 3 | `metacog_epistemic_humility.ipynb` | AGI Bench: Epistemic Humility |
| 4 | `social_cog_emotional_prosody.ipynb` | AGI Bench: Emotional Prosody |

3. For each: **Settings → Make Public → Enable Internet → Save**

**Option B: Find and fix existing orphans**
1. Go to `kaggle.com/ianstudy/code` → sort by newest
2. Look for notebooks with titles matching the above (they may have no title displayed)
3. If found: edit title, make public, enable internet
4. If not found: do Option A

**Also: Delete ~70 duplicate private notebooks** — they're ghost entries from API retry loops. Delete any with no title or duplicate dates.

---

## Step 1: Make All Notebooks Public
Either via API retry or web UI (see above).

## Step 2: Submit to Community Benchmarks
The CB platform has **no API** — must use the web UI.

### For each benchmark notebook:
1. Go to **https://www.kaggle.com/benchmarks/tasks/new**
2. Select "Import from Notebook"
3. Search for the notebook (e.g., "agi-bench-feeling-of-knowing-fok")
4. The `@kbench.task` decorator auto-registers the task
5. Run the notebook — this creates the CB task

### Create the Benchmark Collection:
1. Go to **https://www.kaggle.com/benchmarks/new**
2. Name: "Cognitive Abilities Benchmark Suite — Measuring AGI"
3. Add all 25 core tasks (exclude canary, sub-metrics, overview, dashboard)
4. Add description from `SUBMISSION_NARRATIVE.md`
5. Optionally create 5 per-track benchmarks as well

### Recommended Task Order:
**Metacognition (8 tasks):** FOK, JOL, Calibration, Error Detection, Learning Monitoring, Metacognitive Control, Epistemic Revision, Epistemic Humility  
**Learning (4):** Learning Curves, Transfer, Interference, Curriculum  
**Attention (4):** Selective, Vigilance, Divided, Instruction Update  
**Executive Functions (5):** WCST, Tower of London, Task Switching, N-Back, CRT  
**Social Cognition (4):** False Belief ToM, Pragmatic Inference, Sarcasm Detection, Emotional Prosody

### Sub-metrics (submit separately, optional):
- FOK Sub-metrics (3 tasks: gamma, ECE, AUC)
- JOL Sub-metrics (3 tasks: gamma, ECE, recall)
- Error Detection Sub-metrics (4 tasks: F1, localization, ECE, gamma)

## Step 3: Run Against Models
Once tasks are on CB:
1. Select models: GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro
2. Platform runs each task automatically
3. Record scores → update `results/FRONTIER_MODEL_RESULTS.md`
4. Update `SUBMISSION_NARRATIVE.md` with real results

## Step 4: Final Polish
1. Update SUBMISSION_NARRATIVE.md with frontier model results
2. Git tag `v1.0-submission`
3. Push final clean commit

## Timeline (7 days to deadline)
- **April 9-10:** Get all notebooks public (rate limit should lift)
- **April 10-11:** Submit to CB platform, run against models
- **April 12-13:** Analyze results, update narrative
- **April 14-15:** Final polish, cross-validation
- **April 16:** Deadline ✅
