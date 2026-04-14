# Community Benchmarks Submission Guide

## Key Finding: Submissions Are UI-Only

The Kaggle Community Benchmarks platform **cannot** be submitted to via the Kaggle CLI/API. The process requires the Kaggle web UI.

Per the official FAQ:
> "You must initiate the notebook via the 'Create Task' button on the benchmarks page at kaggle.com/benchmarks"

## Current State (2026-04-09)

### Notebooks Pushed to Kaggle (12 total)

| # | Kaggle Ref | Track | Status |
|---|-----------|-------|--------|
| 1 | `ianstudy/agi-bench-2026-emotional-prosody-v2` | Social Cognition | Pushed, needs CB submission |
| 2 | `ianstudy/agi-bench-2026-epistemic-humility-v2` | Metacognition | Pushed, needs CB submission |
| 3 | `ianstudy/agi-bench-2026-crt-v2` | Executive Functions | Pushed, needs CB submission |
| 4 | `ianstudy/agi-bench-2026-canary-metacog` | Metacognition | Pushed, needs CB submission |
| 5 | `ianstudy/epistemic-revision-benchmark-agi-2026a` | Metacognition | Pushed, public |
| 6 | `ianstudy/wcst-benchmark-agi-2026a` | Executive Functions | Pushed, public |
| 7 | `ianstudy/divided-attention-benchmark-agi-2026a` | Attention | Pushed, public |
| 8 | `ianstudy/sarcasm-detection-benchmark-agi-2026a` | Social Cognition | Pushed, public |
| 9 | `ianstudy/agi-bench-2026-tower-of-london-task` | Executive Functions | Pushed, public |
| 10 | `ianstudy/agi-bench-2026-instruction-update-task` | Attention | Pushed, public |
| 11 | `ianstudy/agi-bench-2026-vigilance-attention` | Attention | Pushed, public |
| 12 | `ianstudy/agi-bench-2026-learning-monitoring-task` | Learning/Metacognition | Pushed, public |

### Local Notebooks Not Yet Pushed (additional)

Many more notebooks exist locally in `repo/notebooks/` (31 total) that haven't been pushed to Kaggle.

## Submission Process (Manual Steps Required)

### Step 1: Create Task Notebooks on CB Platform
1. Go to **kaggle.com/benchmarks**
2. Click **"+ Create"** → **"Create Task"**
3. This opens a new notebook pre-loaded with the `kaggle_benchmarks` SDK
4. Copy the task code from our existing notebooks into this CB notebook
5. Ensure the notebook uses `@kbench.task()` decorators and `%choose task_name` in the final cell
6. **Run** the notebook — a successful run creates/updates the task on the CB platform

### Step 2: Create Benchmarks
1. Go to **kaggle.com/benchmarks**
2. Click **"+ Create"** → **"Create Benchmark"**
3. Group related tasks into a benchmark (e.g., "Metacognition Benchmark" with FOK, JOL, epistemic revision tasks)
4. Each benchmark must have 1+ tasks

### Step 3: Submit to Competition
1. Go to the [competition page](https://www.kaggle.com/competitions/kaggle-measuring-agi)
2. Submit the benchmark to the appropriate track
3. Include a high-quality writeup covering:
   - Problem Statement
   - Task & benchmark construction
   - Dataset provenance
   - Technical details
   - Results, insights, and conclusions
   - References & citations

### Important Notes
- **$50/day and $500/month** AI model quota provisioned for hackathon participants
- Notebooks **cannot** be submitted as Community Benchmarks via the API — must use the web UI "Create Task" flow
- Existing pushed notebooks are regular Kaggle kernels, NOT Community Benchmark tasks yet
- Each task must run successfully on Kaggle's infrastructure to be registered

## Notebooks NOT Yet on Kaggle (need push first, then CB submission)

These local notebooks could be additional submissions:
- `metacog_calibration.ipynb`
- `metacog_control.ipynb`
- `metacog_error_detection.ipynb` / `metacog_error_detection_submetrics.ipynb`
- `metacog_fok.ipynb` / `metacog_fok_submetrics.ipynb`
- `metacog_jol.ipynb` / `metacog_jol_submetrics.ipynb`
- `attention_selective.ipynb`
- `exec_func_nback.ipynb` / `exec_func_task_switch.ipynb`
- `learning_curriculum.ipynb` / `learning_curves.ipynb` / `learning_interference.ipynb` / `learning_transfer.ipynb`
- `social_cog_emotional_prosody.ipynb` / `social_cog_false_belief.ipynb` / `social_cog_pragmatic.ipynb`
