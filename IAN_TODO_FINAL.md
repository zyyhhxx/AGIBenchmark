# 🚨 IAN'S FINAL CHECKLIST — Community Benchmarks Submission
**Created:** 2026-04-09 | **Deadline: April 16, 2026**  
**Estimated total time: ~1.5 hours**

---

## Phase 1: Clean Up Ghost Notebooks (~10 min)

1. Go to **https://www.kaggle.com/ianstudy/code**
2. Sort by newest. Delete any notebook that:
   - Shows as "[Private Notebook]" or has a blank/missing title
   - Is a duplicate (same title, older version)
   - Was created during the April 8–9 API retry storms
3. **Keep only** notebooks with proper "AGI Bench:" or "agi-bench-" titles and correct content
4. There are ~70 ghost entries — this is tedious but necessary before CB submission

---

## Phase 2: Make 6 Rate-Limited Notebooks Public (~5 min)

These were uploaded correctly but remain private due to API 429 errors. Toggle each to public:

| # | Notebook | Direct Link | Action |
|---|----------|-------------|--------|
| 1 | Epistemic Humility | https://www.kaggle.com/code/ianstudy/agi-bench-2026-epistemic-humility-v2 | Settings → Public |
| 2 | Error Detection Sub-metrics | https://www.kaggle.com/code/ianstudy/agi-bench-2026-error-detection-submetrics-v2 | Settings → Public |
| 3 | FOK | https://www.kaggle.com/code/ianstudy/agi-bench-2026-fok-v2 | Settings → Public |
| 4 | FOK Sub-metrics | https://www.kaggle.com/code/ianstudy/agi-bench-2026-fok-submetrics-v2 | Settings → Public |
| 5 | JOL | https://www.kaggle.com/code/ianstudy/agi-bench-2026-jol-v2 | Settings → Public |
| 6 | JOL Sub-metrics | https://www.kaggle.com/code/ianstudy/agi-bench-2026-jol-submetrics-v2 | Settings → Public |

For each: Open link → Settings → **Make Public** → Save.

---

## Phase 3: Register All Benchmarks as CB Tasks (~60 min)

**This is the core submission step.** Each benchmark must be created through the CB platform.

### How to create each task:
1. Go to **https://www.kaggle.com/benchmarks/tasks/new** (or click "+ Create" on kaggle.com/benchmarks)
2. A new notebook opens pre-loaded with kbench SDK
3. **Copy-paste all code cells** from the corresponding `.ipynb` file in `repo/notebooks/`
4. Set the title as shown below
5. **Run the notebook** — the `@kbench.task` decorator registers it as a CB task
6. Verify the task appears on your benchmarks page

### Metacognition Track (8 core + 1 canary = 9 tasks) — ~20 min

| # | Task Name | Notebook File | Track |
|---|-----------|--------------|-------|
| 1 | Feeling-of-Knowing (FOK) | `metacog_fok.ipynb` | metacognition |
| 2 | Judgment-of-Learning (JOL) | `metacog_jol.ipynb` | metacognition |
| 3 | Retrospective Calibration | `metacog_calibration.ipynb` | metacognition |
| 4 | Error Detection | `metacog_error_detection.ipynb` | metacognition |
| 5 | Learning Monitoring | `metacog_learning_monitoring.ipynb` | metacognition |
| 6 | Metacognitive Control | `metacog_control.ipynb` | metacognition |
| 7 | Epistemic Revision | `metacog_epistemic_revision.ipynb` | metacognition |
| 8 | Epistemic Humility | `metacog_epistemic_humility.ipynb` | metacognition |
| 9 | Contamination Canary | `metacog_canary.ipynb` | metacognition |

### Learning Track (4 tasks) — ~10 min

| # | Task Name | Notebook File | Track |
|---|-----------|--------------|-------|
| 10 | Learning Curves | `learning_curves.ipynb` | learning |
| 11 | Near vs. Far Transfer | `learning_transfer.ipynb` | learning |
| 12 | Proactive/Retroactive Interference | `learning_interference.ipynb` | learning |
| 13 | Curriculum Sensitivity | `learning_curriculum.ipynb` | learning |

### Attention Track (4 tasks) — ~10 min

| # | Task Name | Notebook File | Track |
|---|-----------|--------------|-------|
| 14 | Selective Attention | `attention_selective.ipynb` | attention |
| 15 | Vigilance/Sustained Attention | `attention_vigilance.ipynb` | attention |
| 16 | Divided Attention | `attention_divided.ipynb` | attention |
| 17 | Instruction Update | `attention_instruction_update.ipynb` | attention |

### Executive Functions Track (5 tasks) — ~12 min

| # | Task Name | Notebook File | Track |
|---|-----------|--------------|-------|
| 18 | Wisconsin Card Sorting (WCST) | `exec_func_wcst.ipynb` | exec_func |
| 19 | Tower of London | `exec_func_tol.ipynb` | exec_func |
| 20 | Task Switching | `exec_func_task_switch.ipynb` | exec_func |
| 21 | N-Back | `exec_func_nback.ipynb` | exec_func |
| 22 | Cognitive Reflection Test (CRT) | `exec_func_crt.ipynb` | exec_func |

### Social Cognition Track (4 tasks) — ~10 min

| # | Task Name | Notebook File | Track |
|---|-----------|--------------|-------|
| 23 | False-Belief Theory of Mind | `social_cog_false_belief.ipynb` | social_cog |
| 24 | Pragmatic Inference | `social_cog_pragmatic.ipynb` | social_cog |
| 25 | Sarcasm Detection | `social_cog_sarcasm.ipynb` | social_cog |
| 26 | Emotional Prosody | `social_cog_emotional_prosody.ipynb` | social_cog |

### Sub-metric Tasks (optional, 3 tasks) — ~8 min

| # | Task Name | Notebook File | Track |
|---|-----------|--------------|-------|
| 27 | FOK Sub-metrics | `metacog_fok_submetrics.ipynb` | metacognition |
| 28 | JOL Sub-metrics | `metacog_jol_submetrics.ipynb` | metacognition |
| 29 | Error Detection Sub-metrics | `metacog_error_detection_submetrics.ipynb` | metacognition |

### After all tasks are created — Create the Benchmark Collection:
1. Go to **https://www.kaggle.com/benchmarks/new**
2. Name: **"Cognitive Abilities Benchmark Suite — Measuring AGI"**
3. Add all 26 core tasks (items 1–26 above)
4. Add description from `repo/SUBMISSION_NARRATIVE.md`
5. Optionally create 5 per-track sub-benchmarks as well

---

## Phase 4: Post Discussion Thread (~5 min)

1. Go to **https://www.kaggle.com/competitions/kaggle-measuring-agi/discussion**
2. Click **"New Topic"**
3. Copy-paste the content from `repo/KAGGLE_DISCUSSION_DRAFT.md`
4. Update the `[link to CB benchmark]` placeholder with the actual benchmark URL from Phase 3
5. Post it — community upvotes count for **15% of the final score**

---

## Phase 5: Run Models & Collect Results (~10 min to start, runs async)

1. On the benchmark page, select models to evaluate (Gemini 2.5 Pro, Claude 3.5 Sonnet, Llama, etc.)
2. The platform runs each task automatically — no API keys needed
3. Check back for results; they populate the leaderboard
4. Quota: $50/day, $500/month in AI model quota for hackathon participants

---

## Time Budget Summary

| Phase | What | Est. Time |
|-------|------|-----------|
| 1 | Delete ~70 ghost notebooks | 10 min |
| 2 | Toggle 6 notebooks to public | 5 min |
| 3 | Register 29 CB tasks + create benchmark | 60 min |
| 4 | Post discussion thread | 5 min |
| 5 | Trigger model runs | 10 min |
| **Total** | | **~1.5 hours** |

---

## ✅ Verification Checklist

After completing all phases, confirm each item:

### Notebooks
- [ ] All 29 benchmark notebooks are **public** on Kaggle (check https://www.kaggle.com/ianstudy/code)
- [ ] No ghost/duplicate notebooks remain
- [ ] Each notebook has **Internet enabled** in settings

### CB Tasks
- [ ] All 26 core tasks appear on your **benchmarks page** (https://www.kaggle.com/benchmarks)
- [ ] Each task has the correct title and track assignment
- [ ] The benchmark collection "Cognitive Abilities Benchmark Suite" exists and contains all 26 tasks
- [ ] At least one model run has been triggered on the benchmark

### Verification per track:
- [ ] **Metacognition** (8 core + canary): FOK, JOL, Calibration, Error Detection, Learning Monitoring, Metacognitive Control, Epistemic Revision, Epistemic Humility, Canary
- [ ] **Learning** (4): Learning Curves, Transfer, Interference, Curriculum Sensitivity
- [ ] **Attention** (4): Selective, Vigilance, Divided, Instruction Update
- [ ] **Executive Functions** (5): WCST, Tower of London, Task Switching, N-Back, CRT
- [ ] **Social Cognition** (4): False Belief, Pragmatic Inference, Sarcasm, Emotional Prosody

### Discussion
- [ ] Discussion thread posted with benchmark link updated
- [ ] Thread appears on the competition discussion page

### Model Results
- [ ] At least one frontier model has completed evaluation
- [ ] Results visible on the CB leaderboard

---

## 🆘 If Something Goes Wrong

- **CB "Create Task" page not available?** → Check https://www.kaggle.com/benchmarks — the feature may require joining the competition first
- **Notebook won't run on CB?** → Ensure `!pip install kaggle-benchmarks` is in cell 0 and the notebook ends with `.run()`
- **Rate limited again?** → Wait 30 min between batches, or do other phases first
- **Can't find a notebook file?** → All notebooks are in `repo/notebooks/` — use `ls repo/notebooks/*.ipynb`
- **Ghost notebooks won't delete?** → Try: Code tab → three-dot menu → Delete. If no delete option, leave them (they won't interfere with CB tasks)
