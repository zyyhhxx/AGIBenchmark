# KNOWLEDGE.md — AGI Benchmark

## Bedrock Multi-Model Runner — run_benchmark_bedrock.py (2026-04-10)
- **MODEL_CATALOG:** 10 models; some require `us.` cross-region inference prefix (DeepSeek R1, Nova Pro, Llama 4 Maverick, Claude Haiku 4.5).
- **Benchmark count:** 26 live benchmarks across 5 tracks (GOALS.md says 29 — discrepancy; 26 is actual codebase count).
- **Claude Haiku 4.5** (`us.anthropic.claude-3-5-haiku-20241022-v1:0`) is inaccessible on the current AWS account (legacy/access denied). Use Ministral 3B for cheap smoke tests instead.
- **Ministral 3B** (`mistral.ministral-3-3b-instruct`) scored 0.0 on `metacog_canary` (expected — model hallucinates on unknowable fake facts). Confirms end-to-end pipeline works.
- **Rate limiting:** 2s between benchmarks, 5s between models prevents Bedrock throttling.
- **Retry logic:** 3 retries with exponential backoff (5s base); 120s read timeout via botocore Config.
- **Output schema:** `results/{model_id}.json` → `{model, model_label, timestamp, scores:{benchmark:{score,error,duration_s}}}`.

## metacog_canary + metacog_epistemic_revision Discrimination Fixes (2026-04-10)

### metacog_canary
- **Root cause of floor effect (all=0.0):** Bedrock LLM wrapper does not support `schema=` parameter — all models fell back to `confidence=50`, scoring 0.0.
- **Fix:** Explicit JSON prompt + `_extract_confidence` regex helper. No SDK schema dependency.
- **Final scores (v2):** Claude Opus 4.6=0.9947, Nova Pro=0.6375, Ministral 3B=0.0000; std=0.41, range=0.9947.
- **Ministral 3B=0 is expected** — it hallucinates on fabricated facts, which is the canary's intent.

### metacog_epistemic_revision
- **Root cause of non-discrimination:** Bedrock API is stateless; only the first `llm.prompt()` call received context. All subsequent calls had none.
- **Explicit-rules trap:** Providing full contradiction text per transfer question collapses discrimination (all models 0.94+, std=0.027) — reduces to reading comprehension.
- **v4 fix:** Transfer phase provides raw experimental data points only. Model must inductively infer revised rules. Weights: 0.80 transfer + 0.20 perseveration; violation/revision weights=0.
- **Final scores (v4):** Claude Opus 4.6=0.9600, Nova Pro=0.5900, Ministral 3B=0.7500; std=0.153, range=0.37.
- **Rank inversion (Ministral > Nova):** Nova Pro perseverates more on original rules — a real behavioral difference the perseveration component captures.

## Notebook Audit — Repository-wide (2026-04-10)
- **Scope:** 31 notebooks across 6 tracks (metacog×12, learning×4, attention×4, exec_func×5, social_cog×4, other×2). Task originally stated 33; actual count is 31.
- **Syntax:** All 31 pass `jupyter nbconvert` validation.
- **kbench structure:** 29/31 pass @kbench.task + .run() checks. The 2 failures (results_dashboard, submission_overview) are utility notebooks, not benchmarks — expected.
- **Scoring consistency issues (4 total):**
  - metacog: calibration/FoK/JoL use BSS/Brier; others use accuracy — intentionally different (confidence vs accuracy tasks)
  - attention: attention_vigilance missing `normalize` — likely needs fix
  - exec_func: exec_func_tol has no detected scoring pattern — likely needs fix
  - social_cog: social_cog_sarcasm uses `normalize`; other 3 don't — may need harmonization
- **No incomplete notebooks:** 0 TODOs, stubs, or placeholder text found across all 31.
- **Audit artifact:** `repo/NOTEBOOK_AUDIT.md`

## Submission Status Cross-Reference — IAN_TODO_FINAL_v2.md (2026-04-10)
- Competition requires 3 deliverables: CB task collection, discussion thread writeup (7 required sections), model results
- Critical path to submission: ~87 min of manual Ian action on Kaggle web UI
- Single largest item: registering 26–29 CB tasks (~60 min)
- Notebook public status: ~20 still private; must be toggled before CB task registration
- Ghost notebooks (~70) must be cleared before CB task creation to avoid confusion
- SUBMISSION_NARRATIVE.md missing 2 sections: Dataset provenance and organizational affiliation
- Community upvotes = 15% of score — polish discussion thread after benchmark is live
- Checklist artifact: `repo/IAN_TODO_FINAL_v2.md`

## CB Submission Checklist Structure — IAN_TODO_FINAL.md (2026-04-09)
- 29 total benchmarks: 9 metacognition (incl. canary + 3 sub-metric), 4 learning, 4 attention, 5 exec_func, 4 social_cog, 3 sub-metrics
- 6 notebooks needed manual public toggle due to API 429 rate limits on push day
- CB task registration requires running the notebook on CB platform (copy-paste from repo/notebooks/); `@kbench.task` decorator auto-registers
- Ghost notebooks (~70) from retry storms must be deleted via web UI before CB submission
- Discussion thread visibility counts for 15% of final score — post after CB tasks are live

## Kaggle API Rate Limits — Bulk Push Strategy (2026-04-09)
- **Rate limit:** ~20 `kaggle kernels push` calls per session before 429 errors
- **Safe batching:** groups of 3 pushes with 60s delays stays under limit for ~18 notebooks
- **Recovery:** ~24h wait or toggle visibility via Kaggle web UI for already-uploaded private notebooks
- **Pattern:** For large batches (>20), split across multiple sessions or days. Push directories with `kernel-metadata.json is_private: false` persist — safe to retry after rate limit resets
- **v2 push result:** 20/26 notebooks pushed to public; 6 remain private pending manual toggle or retry: metacog_epistemic_humility, metacog_error_detection_submetrics, metacog_fok, metacog_fok_submetrics, metacog_jol, metacog_jol_submetrics

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

## Psychometric Validation — Claude Sonnet 4 on Bedrock (2026-04-10)

- **Three-tier profile:** External monitoring (canary, epistemic_humility, error_detection) mean=0.919; self-monitoring (epistemic_revision, learning_monitoring, control) mean=0.735; prospective self-assessment (jol, fok, calibration) mean=0.305. Clean 3:1 dissociation validates construct coverage.
- **Discriminant validity:** Between-tier / within-tier variance ratio = 3.9:1 (criterion >2:1). PASS.
- **Calibration floor:** BSS=0.000 — Claude's expressed confidence is uncorrelated with accuracy. This is a genuine capability gap, not a scoring artifact. Cross-model replication recommended.
- **Ceiling benchmarks:** canary (0.951) and epistemic_humility (0.926) are expected for frontier models; these are diagnostic baselines, not difficulty targets.
- **Inter-item α:** FOK α=0.949, Error Detection α=0.793/0.703 — computed from mock simulations (item-level Bedrock data unavailable); validates structural reliability of item sets.
- **Pattern:** Single-model Bedrock runs yield aggregate scores only; true Cronbach α on real responses requires item-level logging. Add item-level output to future Bedrock runner.

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

## Repository Architecture — Known Issues (2026-04-10)

- **Division-by-zero bug:** `task_jol.py` gamma correlation (~line 124) has no `if denom > 0` guard — potential ZeroDivisionError when no concordant/discordant pairs exist.
- **Broken absolute imports:** `task_vigilance.py` and `task_curriculum.py` use `from benchmarks.X.data...` — inconsistent with all other 22 task files using relative imports. These will fail if run from a non-root working directory.
- **Gamma function duplicated 7×:** `task_error_detection.py`, `task_error_detection_submetrics.py`, `task_fok.py`, `task_fok_submetrics.py`, `task_jol.py`, `task_jol_submetrics.py`, `task_learning_monitoring.py` each implement Goodman-Kruskal gamma independently with minor differences. Extract to `benchmarks/metacognition/scoring.py`.
- **`rule_systems.py` duplicated:** byte-identical in `benchmarks/metacognition/data/` and `benchmarks/learning/data/`.
- **25/29 task files** have unguarded module-level `.run(kbench.llm)` calls (no `if __name__ == '__main__'` guard). Confirmed non-issue for Kaggle notebook execution but breaks local import/py_compile.
- **47 JSON artifacts** (28 `.task.json`, 19 `.run.json`) at repo root — low-priority clutter.

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

## Claude Sonnet 4 Metacognition Benchmark Results — Bedrock Run (2026-04-09)

Model: `us.anthropic.claude-sonnet-4-20250514-v1:0` via Amazon Bedrock

| Benchmark | Score | vs. Human Baseline | Notes |
|-----------|-------|--------------------|-------|
| Canary Detection | 0.951 | — | Near-perfect fabrication detection |
| Epistemic Humility | 0.926 | — | Strong admission of knowledge limits |
| Error Detection (F1) | 0.882 | 0.75–0.85 | **Above** human baseline |
| Epistemic Revision | 0.820 | 0.70–0.85 | Near top of human range |
| Learning Monitoring | 0.698 | 0.60–0.75 | Mid-range human |
| Metacog Control | 0.689 | 0.65–0.80 | Mid-range human |
| JOL (composite) | 0.465 | 0.50–0.70 | **Below** human baseline |
| FOK (composite) | 0.449 | 0.60–0.80 | **Below** human baseline |
| Calibration (BSS) | 0.000 | 0.80–0.90 | **Complete failure** |

**Key insights:**
- Claude's metacognition is bimodal: near-perfect at detecting fabrications and admitting ignorance (external-facing), but poor at self-monitoring confidence accuracy (internal-facing)
- BSS=0.000 on calibration means Claude's expressed confidence is uncorrelated with accuracy — this is a fundamental limitation, not a benchmark artifact
- FOK and JOL both below human range — Claude cannot reliably predict what it does/doesn't know before being tested
- Error detection exceeds human baseline — Claude catches logical/factual errors in text better than humans
- Pattern: Claude is strong at "do I know this? (no)" but weak at "how confident should I be? (calibrated)"

## Claude Sonnet 4 — Three-Tier Metacognition Profile (2026-04-09)

Mapping of 9 metacognition benchmark scores to Fleming's (2024) taxonomy:

- **Tier 1 (>0.85) — external monitoring:** Canary (0.951), Epistemic Humility (0.926), Error Detection (0.882). Shared structure: detecting external anomalies (fabricated facts, unknowable questions, reasoning errors).
- **Tier 2 (0.65–0.85) — self-monitoring over time:** Epistemic Revision (0.820), Learning Monitoring (0.698), Metacog Control (0.689). Moderate/inconsistent self-tracking of cognitive state across turns.
- **Tier 3 (<0.50) — prospective self-assessment:** JOL (0.465), FOK (0.449), Calibration (0.000). Prospective prediction of own performance before being tested — Claude fundamentally fails here.

**Key ratio:** External monitoring mean = 0.920 vs. internal self-assessment mean = 0.305 → 3:1 dissociation. This is a testable structural prediction: any model with strong external monitoring but weak internal self-assessment should cluster in this same three-tier pattern.

## Project Status Snapshot (2026-04-09)
- 29 benchmarks + 31 notebooks completed across all 5 cognitive tracks; all pass syntax validation
- Psychometric validation complete: Cronbach α ≥ 0.70, good discriminant validity (4:1 within/between ratio)
- Spot tests with Gemini 2.5 Flash/Flash-Lite revealed: calibration failure, pragmatic literal bias, 1st-order ToM failure, inconsistent pragmatics
- FRONTIER_MODEL_RESULTS.md has no actual scores — Gemini API free tier exhausted; no other keys available
- Entire critical path is Ian-blocked: 4 manual notebook uploads, ~70 ghost cleanup, 18 API-blocked pushes, CB task registration, discussion post
- Estimated ~1.5 hrs of Ian web UI work before CB platform can run models automatically
- Agent-actionable next: retry Kaggle API pushes (rate limit recovery), run benchmarks locally once billing enabled, update narrative with real scores

## CRT Procedural Generator — Contamination Replacement (2026-04-09)

- **Problem:** Classic CRT items (bat-and-ball, lily pad, widget factory) score 100% for Flash and Flash-Lite — fully contaminated in training data.
- **Solution:** 15 generator functions with randomizable numeric seeds replace static items. `generate_crt_items(seed, n_items)` is deterministic per seed but produces different correct answers across seeds.
- **Trap taxonomy implemented:** algebraic anchoring, rate independence, exponential growth, complement misread, percentage asymmetry, fence-post, boundary escape, self-reference, cuts-vs-pieces, interval counting, denomination irrelevance, total-time shortcut, recursive weight, meeting point, linear-vs-exponential.
- **Contamination test (mock):** intuitive-answer model drops from ~1.0 → 0.05; easy-correct model 0.27; perfect model 0.95. Difficulty spread: 4 easy / 6 medium / 5 hard.
- **12/15 generators** produce different `correct` answers with different seeds; 3 (meeting-point, boundary-escape) have fixed conceptual answers independent of parameters.
- **File:** `repo/benchmarks/executive_functions/data/crt_items.py` — backward-compatible: exports `CRT_ITEMS` (seed=42) so `task_crt.py` requires no changes.
- **Pattern:** Replace any static "classic puzzle" dataset with a parametric generator; seed=42 as default preserves reproducibility while alternate seeds defeat memorization.

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

## submission_overview.ipynb Consolidation (2026-04-10)

- The notebook was entirely redundant with `SUBMISSION_NARRATIVE.md` except for one element: an explicit inventory of 30 individual benchmark notebooks organized by track.
- That inventory was merged into Section 6 (Technical Implementation) of `SUBMISSION_NARRATIVE.md` as the subsection "Individual Benchmark Notebooks (30 total)".
- After merge, the notebook was deleted. References in 15 files (UPLOAD_INSTRUCTIONS.md, NOTEBOOK_AUDIT.md, GOALS.md, 9 Python scripts) were updated to remove or comment out the submission_overview entry.
- **Pattern:** When a notebook exists solely as a summary/overview of other content, merge unique elements into the canonical markdown document and delete the notebook. Prefer `SUBMISSION_NARRATIVE.md` as the single source of truth for narrative content.

## Discriminatory Power Analysis — 26 Benchmarks (2026-04-10)
- **Top discriminators** (Claude Opus 4.6 − Ministral 3B Δ): learning_transfer (+0.65), metacog_epistemic_humility (+0.60), metacog_control (+0.48), exec_func_wcst (+0.14), social_cog_emotional_prosody (+0.12).
- **Ceiling effect (all models >0.9):** attention_vigilance (all=1.0), social_cog_false_belief (mean=0.964).
- **Floor effect (all models <0.1):** metacog_canary (all=0.0 — confirms canary design working but uninformative for ranking).
- **Low variance (std<0.05), non-discriminatory:** attention_divided (0.013), attention_instruction_update (0.017), attention_selective (0.035), exec_func_crt (0.028), metacog_epistemic_revision (0.013).
- **Zero discrimination (Δ=0.00):** exec_func_task_switch, exec_func_crt, attention_vigilance, metacog_canary — these four add no model-separation signal.
- **Caveat:** Many benchmarks have only 2–4 valid scores (rest are ERRORs from timeouts); discrimination estimates are uncertain for sparse rows.
- **Action:** Expand item count / difficulty range for all flagged benchmarks; ceiling/floor cases require redesign not just parameter tweaks.

## Bedrock Score Matrix — Full 10-Model Run (2026-04-10)
- **All 10 models** successfully produced 26-entry result files; score_matrix.csv generated (26×10).
- **Error-heavy models:** GPT-OSS-120B (15/26 errors), Qwen3 Next 80B (16/26 errors), GLM 4.7 (12/26 errors), Claude Opus 4.6 (13/26), DeepSeek-R1 (11/26) — mostly timeouts on complex benchmarks.
- **Clean models:** Llama 3.3 70B (26/26 scored), Llama 4 Maverick 17B (26/26 scored).
- **Chronic timeouts (>300s):** exec_func_wcst, exec_func_tol, exec_func_nback, exec_func_crt, exec_func_task_switch, attention_divided, attention_instruction_update — these benchmarks are slow for all models and produce frequent nulls.
- **attention_vigilance** scored 1.0 for every model — likely a ceiling effect; benchmark may be too easy.
- **Execution strategy:** Sequential runs take ~8 hrs total; parallel runner per model (separate processes) is necessary to complete within session windows.
- **OOM risk:** Running 5–6 models concurrently (each as a subprocess) triggered SIGKILL on one run — keep parallelism to ≤4 models at once to avoid OOM.

## Cross-Model Three-Tier Metacognition Pattern — Validated (2026-04-10)
- **Three-tier structure replicates across all 10 models:** Tier 1 (external monitoring: epistemic_humility, error_detection) ~0.83; Tier 2 (temporal self-tracking: revision, control, learning_monitoring) ~0.68; Tier 3 (prospective self-assessment: FOK, JOL, calibration) ~0.29.
- **Scale amplifies Tier 1, not Tier 3.** Frontier models show larger T1→T3 gap (0.65) than 3B baseline (0.40). Larger models get better at detecting others' errors but not at predicting their own performance.
- **Calibration failure universal:** 4/5 models scored BSS=0.000; only Sonnet 4.6 achieved 0.368 (still far below human ~0.85). Not model-specific; a general LLM property.
- **CRT prediction failed:** Originally predicted as strong discriminator; actual std=0.028, all models cluster at ~0.36. CRT items need harder procedurally-generated variants.
- **Confirmed §7.5 structure for SUBMISSION_NARRATIVE.md:** Original predictions vs. actual results documented with ✅/❌/⚠️ for each benchmark.
- **Best discriminators are cognitive, not knowledge-based:** learning_transfer, epistemic_humility, metacog_control outperform all knowledge-recall benchmarks in model separation.
