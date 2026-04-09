# KNOWLEDGE.md — AGI Benchmark

## Import Fixes — attention_vigilance, learning_curriculum, attention_instruction_update (2026-04-09)

- **Problem 1:** `from data import ...` relative imports in `task_vigilance.py` and `task_curriculum.py` failed when modules were loaded from repo root; rewritten as absolute imports.
- **Problem 2:** Module-level `.run(kbench.llm)` calls in all three files executed on import outside a Kaggle notebook, causing errors. Wrapped in `if __name__ == '__main__'` guards.
- **Pattern:** All benchmark `.py` files must guard `.run()` calls — the kaggle-benchmarks SDK only provides `kbench.llm` inside a running notebook kernel.
- All three files now pass `py_compile` and import cleanly with `kaggle-benchmarks` installed.

## Learning Interference Scoring v2 — task_interference.py (2026-04-09)

- **Root cause of v1 collapse:** `0.40 * (1 - retroactive) + 0.30 * baseline_A + 0.30 * baseline_B` — when model can't learn (baselines=0), retroactive=0, all strategies score 0.4 identically.
- **Fix:** 4 independent sub-metrics each weighted 0.25: (1) retroactive interference normalized to control_A, (2) proactive interference normalized to control_A, (3) compartmentalization = post_interf_A / control_A, (4) control_A accuracy.
- **Key insight:** Must normalize interference magnitudes by control_A (no-interference baseline) to avoid denominator-zero collapse. Guard with `if control_A > 0 else 0.0`.
- **Mock validation results:** perfect_compartmentalizer=0.5000, full_retroactive_forgetter=0.4500, proactive_blocker=0.6375, cant_learn_anything=0.0000. 5/6 pairs >0.1 separation, 3 distinct clusters.
- **Pattern:** When a benchmark scores constant across conditions, look for unguarded zero denominators and unnormalized magnitudes.

## BSS Scoring Fix — FOK, JOL, Calibration, Canary (2026-04-09)

- **Root cause:** ECE-based scoring (1-ECE) was inverted: always-uncertain agents (constant 50%) outscored perfect metacognitors because low ECE ≠ good discrimination.
- **Fix:** Replaced 1-ECE with Brier Skill Score (BSS = 1 - BS/BS_ref) in all four benchmarks.
  - BS_ref = base_rate × (1 - base_rate) for FOK/JOL/Calibration; BS_ref = 0.25 (uniform) for Canary.
- **Validated (N=60 mock):** Perfect metacognitor: FOK 0.963, JOL 0.858, Calibration 0.927, Canary 0.958. Always-uncertain: FOK 0.350, JOL 0.380, Calibration 0.000, Canary 0.000.
- **Pattern:** BSS is the correct scoring rule for confidence-outcome alignment benchmarks. ECE alone lacks resolution discrimination and rewards hedging.
- **Negative BSS** clamped to 0 (floor) in all tasks. ECE retained as a diagnostic-only metric.
- FOK/JOL composite: `0.40 * gamma_norm + 0.30 * max(0, BSS) + 0.30 * AUC`.

## Contamination Hardening — Metacognition Benchmarks (2026-04-09)

### Risk ratings across 8 benchmarks
- **LOW** (already safe): canary (fabricated items), control (fictional Lake Vordak passage), epistemic_revision (synthetic Zorblatt chemistry), jol (invented pseudowords), learning_monitoring (procedural rule systems)
- **HIGH → MITIGATED**: calibration — was 100% well-known trivia; added 40 procedural questions (arithmetic, unit conversions, physics formulas) → now 50% procedural
- **MEDIUM → MITIGATED**: error_detection — was standard textbook problems; added 16 procedural chains with randomized parameters → 37 total chains
- **MEDIUM (acceptable)**: fok — 30 trivia + 30 procedural; ecological validity requires real-world known/unknown facts. epistemic_humility — trivia by design (measuring meta-knowledge about known facts, not knowledge itself)

### Implementation patterns
- `procedural_calibration.py`: 40 questions in 3 tiers (easy/medium/hard) using math, physics formulas, logic — fully deterministic from parameters
- `procedural_error_chains.py`: 16 chains using randomized numeric parameters so answers differ from textbook examples
- `task_calibration.py` had inline `CALIBRATION_QUESTIONS` bypassing the data module — fixed to import from data module
- Pattern: always check task files for inline data that may shadow the data module

## Difficulty Calibration Findings — Spot Test Analysis (2026-04-09)

### Ceiling Effect Benchmarks (score ≥90%, models trivially pass)
- **CRT classic items**: 100% for Flash and Flash-Lite — contaminated in training data; must replace with procedurally generated variants
- **Stroop**: trivially passed by LLMs (no perceptual interference in text); redesign as semantic Stroop
- **N-back (short)**: 5-item 2-back is trivial with full context windows; needs 50+ items and 3-back/4-back conditions
- **Epistemic revision (simple)**: 3/3 perfect — add partial/ambiguous revision items and multi-step revision chains
- **2nd-order ToM**: both models pass; upgrade to 3rd/4th-order nested belief scenarios
- **Epistemic humility fabricated names**: too easy (models learned "if unrecognized → say I don't know"); add near-miss items with real-but-obscure entities
- **WCST single-trial**: trivial; needs full 128-card protocol with perseveration error scoring

### Broken/Inverted Scoring Benchmarks
- **FOK, JOL, Calibration, Canary mock scores**: perfect metacognition agent scores LOWER than always-uncertain baseline
- **Root cause**: scoring calibration alone (1-ECE) rewards uncertainty over accuracy; need resolution component (Brier skill score or Murphy decomposition) that rewards discrimination
- **Learning interference**: all four mock strategies score identically at 0.4 — benchmark cannot discriminate any behavior; scoring must measure proactive/retroactive interference magnitude from baseline
- **Import failures**: `attention_vigilance`, `learning_curriculum`, `attention_instruction_update` all fail with import errors — must fix `from data import ...` paths before these benchmarks can run

### Working Benchmarks (good discrimination between models)
- domain-specific calibration, pragmatic inference, 1st-order ToM, sarcasm, error detection, Tower of London
- 1st-order ToM and scalar implicature discriminate between Flash vs Flash-Lite by model size
- Tower of London and domain calibration challenge even Flash (genuine failures)

### Stratified Calibration Issue
- Easy ECE: 0.260, Medium: 0.194, Hard: 0.300 — medium tier is actually easiest
- Difficulty tiers don't align with actual calibration difficulty; should derive empirically from model accuracy

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

## Metacognition Notebook Suite — SDK Audit (2026-04-09)
- 12 metacognition notebooks in `repo/notebooks/metacog_*.ipynb`: all pass kbench SDK compatibility after one fix
- Pattern: implementation `.py` files in `repo/benchmarks/metacognition/` may be ahead of their notebook counterparts — always cross-check stubs against these sources
- `metacog_epistemic_revision.ipynb` was a stub with no code; rebuilt from `task_epistemic_revision.py` (30K chars)
- Audit checklist: `!pip install kaggle-benchmarks` in cell 0, `@kbench.task()` decorator, `%choose <task>` as final cell, no direct openai/anthropic imports
- `jupyter nbconvert --to notebook` is a reliable notebook syntax validator

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

## SUBMISSION_NARRATIVE.md — Theoretical Grounding Update (2026-04-09)
- Track 1 metacognition section rewritten with 4 paragraphs citing Nelson & Narens (1990), Fleming (2024), Koriat (1997), Steyvers & Peters (2025), Chhikara et al. (2025), Vuorre & Metcalfe (2021), AFCE NeurIPS 2024
- Benchmark table now includes "Theoretical Basis" column linking each of 9 benchmarks to named frameworks
- Section 5 split into 5.1 (vs. traditional benchmarks) and 5.2 (vs. CASK) with 7-dimension comparison table
- Key CASK differentiation: CASK tests 1 construct (context-sensitivity of calibration); our suite tests 9 constructs with Fleming sensitivity/bias/efficiency decomposition
- Section 8 rewritten: contamination canaries, sub-metric decomposition (gamma + ECE + Brier), and procedural generation highlighted as unique differentiators
- 10 new references added: Botvinick, Chhikara, Dunlosky & Rawson, Fleming ×2, Koriat, Mercier & Sperber, Nelson & Dunlosky, Steyvers & Peters, Vuorre & Metcalfe

## Project Status Snapshot (2026-04-09)
- 29 benchmarks + 31 notebooks completed across all 5 cognitive tracks; all pass syntax validation
- Psychometric validation complete: Cronbach α ≥ 0.70, good discriminant validity (4:1 within/between ratio)
- Spot tests with Gemini 2.5 Flash/Flash-Lite revealed: calibration failure, pragmatic literal bias, 1st-order ToM failure, inconsistent pragmatics
- FRONTIER_MODEL_RESULTS.md has no actual scores — Gemini API free tier exhausted; no other keys available
- Entire critical path is Ian-blocked: 4 manual notebook uploads, ~70 ghost cleanup, 18 API-blocked pushes, CB task registration, discussion post
- Estimated ~1.5 hrs of Ian web UI work before CB platform can run models automatically
- Agent-actionable next: retry Kaggle API pushes (rate limit recovery), run benchmarks locally once billing enabled, update narrative with real scores

## Local Model Testing — Use Bedrock via kbench SDK (2026-04-09)

- **Context:** Previous research loop got stuck trying to test against GPT-4o (not supported) and Gemini (free tier exhausted, billing not enabled).
- **Solution:** Use AWS Bedrock via the local kbench runner. The `kbench` SDK supports custom model backends; configure it to call Bedrock's Claude Sonnet.
- **Supported on Kaggle CB platform:** `anthropic/claude-sonnet-4`, `google/gemini-2.5-flash`, `google/gemini-2.5-pro`, `meta/llama-3.1-70b`. OpenAI is NOT supported.
- **For local testing when a real model is needed:**
  - Use `scripts/run_benchmark_local.py` with a Bedrock-backed Claude model
  - The VPS has AWS credentials and Bedrock access (us-east-1, Claude Sonnet/Opus)
  - Preferred local test model: `amazon-bedrock/us.anthropic.claude-sonnet-4-6` (cost-effective, matches CB platform's Claude Sonnet tier)
  - Do NOT attempt to obtain or use Google API keys — Gemini is unavailable locally; use Bedrock instead
  - Do NOT attempt GPT-4o or any OpenAI model — not available on CB platform or locally
- **Pattern:** Any task that requires "run a benchmark against a real model" should default to Bedrock Claude Sonnet locally. Results can be reported as "Claude Sonnet 4.6 (Amazon Bedrock)" in the narrative.
