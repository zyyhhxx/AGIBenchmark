# Notebook Audit Report

**Total notebooks:** 31

## Notebooks by Track

- **metacog**: 12 — metacog_calibration, metacog_canary, metacog_control, metacog_epistemic_humility, metacog_epistemic_revision, metacog_error_detection, metacog_error_detection_submetrics, metacog_fok, metacog_fok_submetrics, metacog_jol, metacog_jol_submetrics, metacog_learning_monitoring
- **learning**: 4 — learning_curriculum, learning_curves, learning_interference, learning_transfer
- **attention**: 4 — attention_divided, attention_instruction_update, attention_selective, attention_vigilance
- **exec_func**: 5 — exec_func_crt, exec_func_nback, exec_func_task_switch, exec_func_tol, exec_func_wcst
- **social_cog**: 4 — social_cog_emotional_prosody, social_cog_false_belief, social_cog_pragmatic, social_cog_sarcasm
- **other**: 1 — results_dashboard (submission_overview merged into SUBMISSION_NARRATIVE.md)

## Per-Notebook Results

| Notebook | Syntax | pip install | @kbench.task | %choose/.run() | No direct imports | TODOs | Stubs | Overall |
|----------|--------|-------------|--------------|----------------|-------------------|-------|-------|---------|
| attention_divided | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| attention_instruction_update | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| attention_selective | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| attention_vigilance | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| exec_func_crt | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| exec_func_nback | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| exec_func_task_switch | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| exec_func_tol | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| exec_func_wcst | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| learning_curriculum | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| learning_curves | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| learning_interference | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| learning_transfer | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_calibration | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_canary | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_control | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_epistemic_humility | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_epistemic_revision | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_error_detection | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_error_detection_submetrics | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_fok | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_fok_submetrics | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_jol | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_jol_submetrics | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| metacog_learning_monitoring | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| results_dashboard | ✅ | ✅ | ❌ | ❌ | ✅ | 0 | 0 | ❌ FAIL |
| social_cog_emotional_prosody | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| social_cog_false_belief | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| social_cog_pragmatic | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| social_cog_sarcasm | ✅ | ✅ | ✅ | ✅ | ✅ | 0 | 0 | ✅ PASS |
| submission_overview | ✅ | ✅ | ❌ | ❌ | ✅ | 0 | 0 | ❌ FAIL |

## Scoring Consistency

### metacog (⚠️ Inconsistent)

- metacog_calibration: `BSS/Brier+normalize`
- metacog_canary: `BSS/Brier`
- metacog_control: `accuracy+normalize`
- metacog_epistemic_humility: `+normalize`
- metacog_epistemic_revision: `accuracy`
- metacog_error_detection: `accuracy`
- metacog_error_detection_submetrics: `accuracy+normalize`
- metacog_fok: `BSS/Brier+normalize`
- metacog_fok_submetrics: `accuracy+normalize`
- metacog_jol: `BSS/Brier+normalize`
- metacog_jol_submetrics: `accuracy+normalize`
- metacog_learning_monitoring: `accuracy+normalize`

### learning (✅ Consistent)

- learning_curriculum: `accuracy+normalize`
- learning_curves: `accuracy+normalize`
- learning_interference: `accuracy+normalize`
- learning_transfer: `accuracy+normalize`

### attention (⚠️ Inconsistent)

- attention_divided: `accuracy+normalize`
- attention_instruction_update: `accuracy+normalize`
- attention_selective: `accuracy+normalize`
- attention_vigilance: `accuracy`

### exec_func (⚠️ Inconsistent)

- exec_func_crt: `accuracy+normalize`
- exec_func_nback: `accuracy+normalize`
- exec_func_task_switch: `accuracy+normalize`
- exec_func_tol: `None`
- exec_func_wcst: `accuracy+normalize`

### social_cog (⚠️ Inconsistent)

- social_cog_emotional_prosody: `accuracy`
- social_cog_false_belief: `accuracy`
- social_cog_pragmatic: `accuracy`
- social_cog_sarcasm: `accuracy+normalize`

## Issues to Fix

### results_dashboard

- Add `@kbench.task()` decorator
- Add `%choose` or `.run()` to final cell

### submission_overview

- Add `@kbench.task()` decorator
- Add `%choose` or `.run()` to final cell


---
*Audit generated automatically. 4 total issues across 31 notebooks.*
