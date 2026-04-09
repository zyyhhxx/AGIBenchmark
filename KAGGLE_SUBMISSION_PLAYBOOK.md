# 🚀 Kaggle Submission Playbook

**Last updated:** 2026-04-09 00:30 UTC  
**Status:** 10/30 notebooks public. 20 blocked by Kaggle SaveKernel 429 rate limit.

## Current Blocker: Rate Limit

The Kaggle API `SaveKernel` endpoint has a daily quota. We've been hitting 429 since ~18:00 UTC on April 8. The limit appears to be ~10-15 saves/day.

### To Retry Pushing (run periodically):
```bash
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
.venv/bin/python3 scripts/kaggle_push_retry.py
```
This script is idempotent — tracks what's already pushed in `scripts/.kaggle_pushed_public.txt`.

### Alternative: Manual Web UI Push
If API stays blocked, notebooks can be made public via kaggle.com:
1. Go to `kaggle.com/ianstudy/<notebook-slug>/settings`
2. Change visibility from Private → Public
3. This does NOT count against the API rate limit

### Notebooks Still Private (20):
See `scripts/.kaggle_pushed_public.txt` for the pushed list. Everything in `scripts/kaggle_batch_ops.py` DESIRED_STATE that's NOT in that file needs pushing.

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
