# 🚀 Kaggle Submission Playbook

**Last updated:** 2026-04-09 06:10 UTC  
**Status:** ✅ **8/26 notebooks updated on Kaggle.** 18 remaining (rate limited). 4 new notebooks need manual web UI upload. Backoff cron running every 30 min to push remaining. **Preliminary Gemini results obtained** (CRT 3/3, literal bias in pragmatic inference, calibration overconfidence).

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
The CB platform requires notebooks to be created via the benchmarks page.

### IMPORTANT: Task creation flow
1. Go to **https://www.kaggle.com/benchmarks**
2. Click **"+ Create"** (or "Create Task")
3. This opens a NEW notebook pre-loaded with the kbench SDK
4. **Copy-paste the content from our .ipynb file** into this new notebook
5. The `@kbench.task` decorator auto-registers the task when the notebook runs
6. Run the notebook — this creates the CB task

**Note:** You MUST create via the benchmarks page — regular notebooks won't work as tasks.

**Quota:** All hackathon participants get $50/day and $500/month in AI model quota.

### Process for each benchmark:
1. Click "+ Create" on kaggle.com/benchmarks
2. In the new notebook, paste the code from our .ipynb file (all code cells)
3. Set the title (e.g., "AGI Bench: Feeling-of-Knowing")
4. Run the notebook to register the task
5. Verify the task appears on your benchmarks page

### Alternative: Import from existing notebook
If the "Create Task" page allows importing from existing notebooks:
1. Select "Import from Notebook"
2. Search for the notebook slug
3. This should auto-import the code

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
