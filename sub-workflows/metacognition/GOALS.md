# GOALS.md — AGI Benchmark Hackathon

## Active Goal
Design high-quality cognitive ability benchmarks for the Kaggle "Measuring Progress Toward AGI" hackathon. Deadline: **April 16, 2026**.

## 🚨 First Task for Planner — Read This Before Generating Tasks

Before generating research or implementation tasks, the planner MUST first generate a single survey task:

**"Survey competition page and existing artifacts to decide what to do next"**

This task should instruct the executor to:
1. Check the competition page status and rules: https://www.kaggle.com/competitions/kaggle-measuring-agi/overview
2. Read `STATUS.md` in the repo root for current project status
3. Read `IAN_TODO.md` in the repo root for pending human action items
4. List all notebooks in `repo/notebooks/` and check which ones are complete
5. Check `repo/results/` for any existing benchmark run results
6. Based on the above, write a prioritized action plan to `sub-workflows/metacognition/SURVEY.md`
   — what's done, what's missing, what the remaining days should focus on

Only after this survey task passes validation should the planner generate execution tasks.

---

## Tracks (all five required)
1. Learning
2. Metacognition
3. Attention
4. Executive Functions
5. Social Cognition

## Success Criteria
- All benchmarks submitted to Kaggle Community Benchmarks platform before April 16
- Each benchmark has clear cognitive science rationale, contamination resistance, and documentation
- High-quality writeup covering methodology, dataset provenance, results, and insights
- Tested against frontier models via Kaggle platform (models run by Kaggle — no API key needed)

## Quality Standards
- Each benchmark must have a clear cognitive science rationale
- Must be resistant to shortcut solutions (data contamination, memorisation)
- Reproducible — anyone can run the evaluation
- Well-documented methodology

## Research Directions
- Investigate metacognitive monitoring paradigms from cognitive psychology (FOK, JOL, tip-of-tongue)
- Explore learning curve analysis methods from educational psychology
- Study attention benchmark designs from neuroscience (selective, sustained, divided attention)
- Research executive function tests (Wisconsin Card Sort, Tower of London, Stroop analogues)
- Investigate social cognition measures (theory of mind, pragmatic inference, sarcasm detection)
- Explore adversarial benchmark design to prevent shortcut solutions
- Study how existing AGI benchmarks (ARC, BIG-bench) handle contamination resistance
- Research calibration measurement techniques for LLM confidence estimation
- Investigate multi-step reasoning evaluation beyond single-turn Q&A
- Explore cross-cultural cognitive assessment methodologies

## Key Context
- Kaggle Community Benchmarks runs models on their side — **no API key needed**
- OpenAI models are NOT supported by the platform; focus on Gemini/Claude/Llama
- The platform is free to use; model evaluation happens when notebooks run as CB tasks
- Ian must manually submit notebooks to CB via Kaggle web UI (agent cannot do this)
