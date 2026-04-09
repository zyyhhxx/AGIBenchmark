# KNOWLEDGE.md — AGI Benchmark

## Competition Framework
- Google DeepMind's "Measuring Progress Toward AGI: A Cognitive Taxonomy"
- 10 cognitive abilities identified; hackathon focuses on 5 with largest evaluation gaps:
  1. **Learning** — acquiring new knowledge through experience and instruction
  2. **Metacognition** — knowledge and monitoring of one's own cognitive processes
  3. **Attention** — focusing cognitive resources on what matters
  4. **Executive functions** — planning, inhibition and cognitive flexibility
  5. **Social cognition** — processing/interpreting social information and responding appropriately

## Evaluation Protocol (from paper)
1. Evaluate AI systems across cognitive tasks using held-out test sets (prevent data contamination)
2. Collect human baselines from demographically representative adults
3. Map AI performance relative to human performance distribution

## Kaggle Community Benchmarks Platform
- Submissions are Kaggle notebooks using the `kaggle-benchmarks` SDK (`kaggle_benchmarks` / `kbench`)
- Each task = a Python function decorated with `@kbench.task()`
- Tasks can use `llm.prompt()` for model calls, `kbench.assertions` for pass/fail, judge LLMs for subjective eval
- Return types: `bool` (pass/fail), `float`/`int` (score), `tuple[int,int]` (count), `tuple[float,float]` (score+CI)
- `.evaluate()` runs task over a pandas DataFrame dataset
- `%choose task_name` in final cell selects the main task for leaderboard
- Supports: multi-turn conversations, isolated judge chats, structured output schemas, multimodal inputs
- Models available: Gemini, Claude, Llama, DeepSeek, etc. via `kbench.llms["provider/model"]`
- Currently one task per notebook on leaderboard
- Submit benchmark = 1+ tasks grouped together

## Prize Structure
- $10,000 × 2 per track (top two submissions) = $100,000
- $25,000 × 4 grand prizes (best overall) = $100,000
- Total: $200,000
- Results announced June 1, 2026

## Paper Key Points (Measuring Progress Toward AGI: A Cognitive Framework)
- 10 cognitive faculties: Perception, Generation, Attention, Learning, Memory, Reasoning, Metacognition, Executive Functions, Problem Solving, Social Cognition
- First 8 are basic building blocks; Problem Solving and Social Cognition are "composite" faculties
- Three-stage evaluation protocol: (1) cognitive assessment on held-out tasks, (2) human baselines, (3) cognitive profiles mapping AI vs human distribution
- Task design principles: targeted to specific abilities, held-out, independently verified, varied difficulty, varied structure/format
- Existing gap areas (hackathon focus): Learning, Metacognition, Attention, Executive Functions, Social Cognition
- Paper acknowledges problem solving and perception already have decent benchmarks

## Key Learnings
- Kaggle pages require JS rendering — can't scrape directly, use search snippets instead
- The kaggle-benchmarks SDK cookbook is the essential reference for implementation
- Competition emphasizes going "beyond recall" — must test genuine cognitive ability not memorization
- Shortcut resistance is critical: tasks must not be solvable by pattern matching or data contamination

## Kaggle API Limitations (2026-04-09)
- `kaggle kernels list --mine` returns `is_private=None` for all notebooks — visibility field not populated by API
- Toggling notebook visibility via API (pull → set `is_private:false` → push) triggers `SaveKernel` endpoint; repeated failed pushes cause 429 rate-limiting that persists
- Failed API pushes create ghost notebook entries (id=0, empty slug/ref, title="[Private Notebook]") that cannot be deleted via API — must use web UI
- **Recommendation:** Toggle notebook visibility and delete ghost entries through Kaggle web UI, not the API
- 4 target notebooks (CRT v2, canary metacog, epistemic humility v2, emotional prosody v2) under `ianstudy/` account need manual public toggle
- 8 other named notebooks already public (epistemic revision, WCST, divided attention, sarcasm detection, tower of london, instruction update, vigilance attention, learning monitoring)

## Community Benchmarks Submission Process (2026-04-09)
- CB task registration is **entirely UI-driven** — no API or CLI path exists
- Must use "Create Task" button at kaggle.com/benchmarks/tasks/new for each notebook
- Notebooks must be PUBLIC before they can be registered as CB tasks
- 12 notebooks uploaded to Kaggle as regular kernels; 19 additional local-only notebooks not yet pushed
- Failed API pushes created ghost entries (id=0, empty slug) — cleanup requires web UI
- Full submission guide at `repo/CB_SUBMISSION_GUIDE.md` with step-by-step instructions for Ian

## Project Status Snapshot (2026-04-09)
- 29 benchmarks + 31 notebooks completed across all 5 cognitive tracks; all pass syntax validation
- Psychometric validation complete: Cronbach α ≥ 0.70, good discriminant validity (4:1 within/between ratio)
- Spot tests with Gemini 2.5 Flash/Flash-Lite revealed: calibration failure, pragmatic literal bias, 1st-order ToM failure, inconsistent pragmatics
- FRONTIER_MODEL_RESULTS.md has no actual scores — Gemini API free tier exhausted; no other keys available
- Entire critical path is Ian-blocked: 4 manual notebook uploads, ~70 ghost cleanup, 18 API-blocked pushes, CB task registration, discussion post
- Estimated ~1.5 hrs of Ian web UI work before CB platform can run models automatically
- Agent-actionable next: retry Kaggle API pushes (rate limit recovery), run benchmarks locally once billing enabled, update narrative with real scores
