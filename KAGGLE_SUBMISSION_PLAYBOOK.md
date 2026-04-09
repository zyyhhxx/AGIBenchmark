# 🚀 Kaggle Submission Playbook

**Last updated:** 2026-04-09 00:55 UTC  
**Status:** ✅ **26 notebooks confirmed public on Kaggle.** 4 new notebooks (CRT, canary, epistemic humility, emotional prosody) exist as private — need manual web UI toggle. ~28 duplicate private notebooks from retry attempts (safe to delete via web UI).

## Current Issue: New Notebooks Created as Private

The Kaggle API `kernels push` with `is_private: false` **still creates private notebooks**. The 4 new benchmarks were pushed successfully but are private. They must be made public via the web UI.

### To fix (Ian — web UI required):
1. Go to `kaggle.com/ianstudy/kernels` 
2. Find the 4 new notebooks (sort by newest): CRT, Canary, Epistemic Humility, Emotional Prosody
3. For each: Settings → Change visibility to Public
4. Delete any obvious duplicates (~28 duplicate private notebooks from retry attempts)

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
