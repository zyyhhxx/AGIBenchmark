# Community Benchmarks Submission Guide

## How to Submit Our Benchmarks

### Step 1: Create Each Task
For each of our 26 benchmark notebooks (excluding submission_overview and results_dashboard):

1. Go to **https://www.kaggle.com/benchmarks/tasks/new**
2. Paste the notebook content (or import from uploaded kernel)
3. Run the notebook — this registers the `@kbench.task` with the CB platform
4. The task will appear at `kaggle.com/benchmarks/tasks/<task_name>`

### Step 2: Create the Benchmark
1. Go to **https://www.kaggle.com/benchmarks/new**
2. Add all 26 tasks to a single benchmark (or create 5 per-track benchmarks)
3. Name it: "Cognitive Abilities Benchmark Suite — Measuring AGI"
4. Add description from SUBMISSION_NARRATIVE.md

### Step 3: Run Against Models
1. Select models to evaluate (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, etc.)
2. The platform runs each task against each model automatically
3. Results appear on the leaderboard

## Important Notes
- `kbench.llm` is the model placeholder — it gets replaced by the actual model at runtime
- `kbench.chats.new()` creates isolated conversation contexts per trial
- Notebooks must be PUBLIC to be used as CB tasks
- The `@kbench.task` decorator + `.run()` at the end is required

## Notebook Order for Submission
### Priority 1: Core benchmarks (22 tasks)
See KAGGLE_KERNELS.md for full list of uploaded notebooks.

### Priority 2: Sub-metric variants (3 tasks)
- metacog_fok_submetrics
- metacog_jol_submetrics  
- metacog_error_detection_submetrics

### Priority 3: Special
- metacog_canary (contamination detection)

## Current Blockers
- Kaggle API rate limited (429 errors) — need to wait for daily quota reset
- 17 notebooks still private — need to make public before CB submission
- New canary notebook not yet uploaded
