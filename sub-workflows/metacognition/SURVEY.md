# SURVEY.md — Project Status & Action Plan

**Survey date:** 2026-04-09 ~19:00 UTC  
**Days remaining:** ~7 (deadline April 16, 2026)

---

## What Is Done ✅

### Code & Benchmarks
- **29 benchmarks** across all 5 tracks fully implemented with kbench SDK patterns
- **31 notebooks** total (29 benchmarks + overview + dashboard)
- All 81 code cells pass syntax validation
- All pass import validation
- Psychometric validation complete: α ≥ 0.70, good discriminant validity (4:1 within/between-track ratio)
- Contamination resistance: procedural generation + canary items
- Cognitive science rationale, interpretation guides, and references in all notebooks

### Notebooks by Track
| Track | Count | Notebooks |
|-------|:---:|---|
| Metacognition | 9 | calibration, canary, control, epistemic_humility, epistemic_revision, error_detection, fok, jol, learning_monitoring |
| Learning | 4 | curriculum, curves, interference, transfer |
| Attention | 4 | divided, instruction_update, selective, vigilance |
| Executive Functions | 5 | crt, nback, task_switch, tol, wcst |
| Social Cognition | 4 | emotional_prosody, false_belief, pragmatic, sarcasm |
| Sub-metrics | 3 | error_detection_submetrics, fok_submetrics, jol_submetrics |
| Overview/Dashboard | 2 | submission_overview, results_dashboard |

### Documentation
- SCORING_GUIDE.md, SUBMISSION_NARRATIVE.md, KAGGLE_DISCUSSION_DRAFT.md all written
- CB_SUBMISSION_GUIDE.md and KAGGLE_SUBMISSION_PLAYBOOK.md ready for Ian
- Competition landscape analysis with CASK comparison

### Preliminary Results
- Gemini 2.5 Flash spot tests: 8 tests, key findings on calibration failure and pragmatic literal bias
- Gemini 2.5 Flash-Lite: 8 tests (75%), 1st-order ToM failure, inconsistent pragmatics
- Predicted cognitive profiles for 4 frontier models
- **No actual Community Benchmarks scores yet** — all frontier model result cells are "—"

---

## What Is Missing / Blocked ❌

### Blocked on Ian (human required)
1. **4 notebooks need manual web UI upload** — CRT, Canary, Epistemic Humility, Emotional Prosody
2. **~70 ghost private notebooks need cleanup** via Kaggle web UI
3. **Make remaining notebooks public** — 18 still need pushing (API 429 persists)
4. **Community Benchmarks task registration** — entirely UI-driven, no API path
5. **Post discussion thread** on competition page (community upvotes = 15% of score)
6. **Gemini API billing** — free tier exhausted; no other model API keys

### Missing but Agent-Actionable
- **No actual frontier model benchmark scores** — FRONTIER_MODEL_RESULTS.md is all "—"
- Could run local benchmarks if Gemini API billing gets enabled (`scripts/run_benchmark_local.py`)

---

## Prioritized Action Plan

### 🔴 Critical Path (must happen before April 16)

| Priority | Action | Owner | Est. Time | Notes |
|:---:|---|:---:|:---:|---|
| 1 | Upload 4 missing notebooks via web UI | Ian | 15 min | CRT, Canary, Epistemic Humility, Emotional Prosody |
| 2 | Clean up ~70 ghost notebooks via web UI | Ian | 10 min | Delete "[Private Notebook]" / blank entries |
| 3 | Push 18 remaining notebooks (or upload via web if 429 persists) | Ian | 30 min | May need web UI if API stays rate-limited |
| 4 | Make all notebooks public | Ian | 5 min | Toggle in settings |
| 5 | Register all 25 core notebooks as CB tasks | Ian | 30 min | kaggle.com/benchmarks/tasks/new |
| 6 | Post discussion thread | Ian | 5 min | Copy KAGGLE_DISCUSSION_DRAFT.md; 15% of score |

### 🟡 High Value (significantly improves submission)

| Priority | Action | Owner | Est. Time | Notes |
|:---:|---|:---:|:---:|---|
| 7 | Enable Gemini API billing → run full benchmark suite locally | Ian (billing) + Agent (runs) | 1-2 hrs | Real scores >> mock data for narrative |
| 8 | Update FRONTIER_MODEL_RESULTS.md with actual scores | Agent | 30 min | After benchmarks run |
| 9 | Update SUBMISSION_NARRATIVE.md results section | Agent | 15 min | After scores available |

### 🟢 Nice to Have

| Priority | Action | Owner | Notes |
|:---:|---|:---:|---|
| 10 | Run benchmarks against multiple models (Claude, DeepSeek) | Agent | Need API keys or wait for CB platform |
| 11 | Refine predicted cognitive profiles with real data | Agent | After multi-model results |
| 12 | Add more items to benchmarks with low item counts | Agent | Marginal improvement |

---

## What Remaining Days Should Focus On

**The entire critical path is Ian-dependent.** The agent has completed all code, documentation, and validation work. The bottleneck is Kaggle web UI operations that only a human can perform.

### Recommended timeline:
- **Day 1-2 (now):** Ian does priorities 1-6 (total ~1.5 hrs of web UI work)
- **Day 2-3:** If Gemini billing enabled, agent runs full benchmark suite and updates results
- **Day 3-5:** Agent refines narrative with real scores; Ian monitors CB task execution
- **Day 5-7:** Buffer for any issues; final review and polish

### What the Agent Can Do Right Now
- ✅ Monitor and retry Kaggle API pushes (backoff cron already running)
- ✅ Run local benchmarks immediately if API billing is enabled
- ✅ Improve documentation, add more test items, refine predictions
- ✅ Prepare final submission narrative once real scores are available

### What Only Ian Can Do
- ❌ All Kaggle web UI operations (upload, cleanup, CB registration, discussion post)
- ❌ Enable API billing / provide API keys
- ❌ Final review and approval of submission
