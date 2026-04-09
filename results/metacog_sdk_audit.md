# Metacognition Notebooks — kbench SDK Compatibility Audit

**Date:** 2026-04-09  
**Audited:** 12 notebooks in `repo/notebooks/metacog_*.ipynb`  
**Result:** ✅ 12/12 PASS (after 1 fix)

## Audit Criteria

For each notebook, verified:
1. `!pip install kaggle-benchmarks` in cell 0
2. `@kbench.task()` decorator on main task function(s)
3. Valid return types (bool/float/tuple)
4. `llm.prompt()` calls via kbench SDK (no direct openai/anthropic imports)
5. `%choose <task_name>` in final code cell selecting the main leaderboard task
6. `jupyter nbconvert --to notebook` passes without errors

## Issues Found & Fixed

### metacog_epistemic_revision.ipynb — CRITICAL (FIXED)
- **Problem:** Notebook was a stub — contained only markdown cells and a comment `# .run() removed — use %choose instead`. No `@kbench.task()` function, no `%choose` cell, no implementation code.
- **Root cause:** The implementation existed in `repo/benchmarks/metacognition/task_epistemic_revision.py` but was never ported to the notebook format.
- **Fix:** Rebuilt notebook from the .py source:
  - Preserved existing markdown cells (rationale, score interpretation, references)
  - Added full implementation as code cell (30,450 chars) with `@kbench.task()` decorator
  - Removed trailing `.run()` call (replaced by `%choose`)
  - Added `%choose metacog_epistemic_revision` as final cell

### All Other Notebooks — PASS (no issues)
The remaining 11 notebooks had correct structure:
- pip install in cell 0
- Proper `@kbench.task()` decorators
- `%choose` in final code cell
- No direct API client imports

## Notebook Summary

| Notebook | Tasks | Choose Target | Status |
|----------|-------|--------------|--------|
| metacog_calibration | metacog_calibration | metacog_calibration | ✅ |
| metacog_canary | metacog_canary | metacog_canary | ✅ |
| metacog_control | metacog_control | metacog_control | ✅ |
| metacog_epistemic_humility | metacog_epistemic_humility | metacog_epistemic_humility | ✅ |
| metacog_epistemic_revision | metacog_epistemic_revision | metacog_epistemic_revision | ✅ (fixed) |
| metacog_error_detection | metacog_error_detection | metacog_error_detection | ✅ |
| metacog_error_detection_submetrics | 4 sub-tasks (f1, localization, ece, gamma) | metacog_error_detection_f1 | ✅ |
| metacog_fok | metacog_fok | metacog_fok | ✅ |
| metacog_fok_submetrics | 3 sub-tasks (gamma, ece, auc) | metacog_fok_gamma | ✅ |
| metacog_jol | metacog_jol | metacog_jol | ✅ |
| metacog_jol_submetrics | 3 sub-tasks (gamma, ece, recall) | metacog_jol_gamma | ✅ |
| metacog_learning_monitoring | metacog_learning_monitoring | metacog_learning_monitoring | ✅ |

## Validation

All 12 notebooks pass `jupyter nbconvert --to notebook` without errors.
