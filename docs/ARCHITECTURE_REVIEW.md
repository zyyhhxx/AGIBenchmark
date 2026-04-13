# Architecture Review — AGI Benchmark Suite

**Date:** 2026-04-10  
**Scope:** Full repository structure, dependencies, interface consistency, redundancies

---

## 1. Structure

### Repository Layout

```
repo/
├── benchmarks/                    # Benchmark implementations (5 tracks)
│   ├── attention/                 # 4 tasks + data/attention_stimuli.py
│   ├── executive_functions/       # 5 tasks + data/{crt_items,nback_stimuli,task_switch_stimuli,tol_problems,wcst_stimuli}.py
│   ├── learning/                  # 4 tasks + data/rule_systems.py
│   ├── metacognition/             # 9 tasks + data/{calibration_questions,canary_items,error_detection_chains,fok_questions,jol_stimuli,procedural_calibration,procedural_error_chains,procedural_fok,rule_systems}.py
│   ├── social_cognition/          # 4 tasks + data/{false_belief_scenarios,pragmatic_items,sarcasm_items}.py
│   ├── *.py                       # Analysis utilities (correlation, reliability, sensitivity, shortcut, mock_validation, stratified_calibration)
│   ├── COGNITIVE_RATIONALE.md, HUMAN_BASELINES.md, METHODOLOGY.md, README.md
│   └── Each track has a DESIGN.md
├── notebooks/                     # 31 Kaggle notebooks (.ipynb)
├── scripts/                       # 30+ utility scripts (upload, push, validation, testing)
├── research/                      # 4 research/strategy notes
├── results/                       # Run results, analysis outputs, validation reports
├── sub-workflows/metacognition/   # Task queue and coordinator state
├── tests/                         # test_harness.py (single file)
├── .venv/                         # Python virtual environment
├── *.task.json (28)               # kbench task registration configs (root level)
├── *.run.json (19)                # kbench run results (root level)
└── *.md (12)                      # Documentation (README, STATUS, SUBMISSION_NARRATIVE, etc.)
```

### Counts
- **29 benchmark tasks** across 36 `@kbench.task()` decorators (some files define multiple sub-metric tasks)
- **31 notebooks** in `notebooks/`
- **28 .task.json** + **19 .run.json** files at repo root
- **30+ scripts** in `scripts/` (mostly one-off upload/push utilities)

---

## 2. Dependencies

### External Dependencies
All task files import:
- `kaggle_benchmarks as kbench` — SDK (universal)
- `dataclasses.dataclass` — data structures (universal)
- `numpy as np` — scoring math (27/29 tasks)
- `re`, `json` — response parsing (most tasks)
- `pandas` — only `task_calibration.py` (unique dependency)

### Internal Data Dependencies
Each track has a `data/` subpackage with stimuli/item generators. Imports are **relative** (`from data.X import Y`) in 22 files, with two exceptions using absolute imports:
- `benchmarks/attention/task_vigilance.py` → `from benchmarks.attention.data.attention_stimuli import ...`
- `benchmarks/learning/task_curriculum.py` → `from benchmarks.learning.data.rule_systems import ...`

### Cross-Track Data Sharing
- **`data/rule_systems.py`** is duplicated identically in both `benchmarks/metacognition/data/` and `benchmarks/learning/data/`. Both provide `generate_symbol_system()` and related functions.

### Metacognition Internal Dependencies
- `data/calibration_questions.py` imports from `data.procedural_calibration`
- `data/error_detection_chains.py` imports from `data.procedural_error_chains`
- `data/fok_questions.py` imports from `data.procedural_fok`

These are composition patterns (base items + procedural hardening items merged at import time).

---

## 3. Interface Consistency

### Decorator Usage ✅
All 29 benchmark files use `@kbench.task(name="...")` — consistent. Task names follow `{track}_{benchmark}` convention (e.g., `metacog_fok`, `exec_func_crt`).

### Return Types ✅
All task functions return `float` (score in [0,1]). One minor variant: `task_canary.py` wraps with `round(float(score), 4)` while others return bare `score`. Functionally equivalent.

### `.run()` Call Pattern ⚠️
All files call `.run(llm=kbench.llm)` at module level. **25 of 29 files have unguarded `.run()` calls** — they execute on import outside Kaggle notebooks. Only 4 files (`task_vigilance.py`, `task_instruction_update.py`, `task_curriculum.py`, `task_interference.py`) wrap in `if __name__ == '__main__':` guards.

**Impact:** Unguarded calls don't affect Kaggle notebook execution (code is pasted into cells, not imported), but they prevent `import` or `py_compile` from working without the kbench SDK providing a live `kbench.llm`. This is a known issue documented in KNOWLEDGE.

### Scoring Methodology
- **Metacognition:** BSS (Brier Skill Score) for confidence tasks (FOK, JOL, calibration, canary); F1 + gamma for error detection; composite scores for revision/control/monitoring
- **Other tracks:** Accuracy-based scoring with task-specific weighting
- All scores normalized to [0, 1] ✅

### `import json as _json` Pattern
Some files (`task_canary.py`, `task_crt.py`, `task_nback.py`, `task_wcst.py`, `task_false_belief.py`, `task_pragmatic.py`, `task_sarcasm.py`) import `json as _json` (prefixed) while others import `json` directly. Mixed but harmless.

---

## 4. Redundancies

### Critical: Duplicated `rule_systems.py`
`benchmarks/metacognition/data/rule_systems.py` and `benchmarks/learning/data/rule_systems.py` are **byte-identical**. Should be a shared module to avoid drift.

**Recommendation:** Move to `benchmarks/shared/data/rule_systems.py` or have one import from the other.

### Critical: Duplicated Gamma Correlation Function
The Goodman-Kruskal gamma correlation function (concordant/discordant pair counting) is independently implemented in **4 files**:
1. `task_error_detection.py`
2. `task_fok.py`
3. `task_jol.py`
4. `task_learning_monitoring.py`

Minor implementation differences exist (e.g., `if denom > 0` vs `if denom`; `/ denom` without guard in `task_jol.py`). The `task_jol.py` version has a **potential division-by-zero bug** — no guard on `denom == 0`.

**Recommendation:** Extract to `benchmarks/metacognition/scoring.py` as a shared utility.

### Moderate: Root-Level JSON Clutter
28 `.task.json` and 19 `.run.json` files sit at the repo root alongside documentation. These are kbench registration artifacts. Consider moving to a `task_configs/` directory.

### Moderate: Script Proliferation
`scripts/` contains 30+ files, many of which are one-off upload/push scripts from the submission push process (8 variants of kaggle push/upload scripts). These served their purpose but add noise.

**Recommendation:** Archive superseded scripts to `scripts/archive/`.

### Low: `benchmarks/*.py` Analysis Scripts
6 analysis scripts (`correlation_analysis.py`, `reliability_analysis.py`, `sensitivity_analysis.py`, `shortcut_analysis.py`, `mock_validation.py`, `stratified_calibration.py`) sit alongside track directories in `benchmarks/`. These are analysis tools, not benchmarks.

**Recommendation:** Move to `scripts/analysis/` or `benchmarks/analysis/`.

---

## 5. Recommended Changes

### Must-Fix (affects correctness)
1. **`task_jol.py` gamma division-by-zero:** Add `if denom > 0 else 0.0` guard (line ~124)
2. **Import style inconsistency:** `task_vigilance.py` and `task_curriculum.py` use absolute imports (`from benchmarks.X.data...`) while all others use relative (`from data...`). These will **fail on Kaggle** where code runs from the notebook's directory, not the repo root. Verify these notebooks paste the absolute import or inline the data.

### Should-Fix (improves maintainability)
3. **Extract shared gamma function** to `benchmarks/metacognition/scoring.py` — 7 copies is a maintenance risk
4. **Deduplicate `rule_systems.py`** — identical file in two track data directories
5. **Guard remaining `.run()` calls** with `if __name__ == '__main__':` — 25 files still unguarded
6. **Move root `.task.json`/`.run.json`** files to `task_configs/` and `run_results/`

### Nice-to-Have (cleanup)
7. Archive one-off push scripts in `scripts/archive/`
8. Move `benchmarks/*.py` analysis scripts to `scripts/analysis/`
9. Standardize `import json` vs `import json as _json` across all task files
10. Add `benchmarks/__init__.py` for proper package structure (metacognition track is missing it)

---

## Summary Table

| Category | Finding | Severity | Files Affected |
|----------|---------|----------|----------------|
| Division by zero | `task_jol.py` gamma has no denom guard | **High** | 1 |
| Import style | 2 files use absolute imports (may break on Kaggle) | **High** | 2 |
| Code duplication | Gamma function copied 7 times | Medium | 7 |
| Code duplication | `rule_systems.py` identical in 2 tracks | Medium | 2 |
| Unguarded `.run()` | 25/29 task files lack `__main__` guard | Medium | 25 |
| Repo clutter | 47 JSON artifacts at root level | Low | 47 |
| Script proliferation | 8+ superseded upload scripts | Low | 8 |
| Missing `__init__.py` | `benchmarks/metacognition/` has no `__init__.py` | Low | 1 |
