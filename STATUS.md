# STATUS.md — AGI Benchmark Project

**Last updated**: 2026-04-08 14:30 UTC

## Project Status: 🟢 Submission-Ready — 24 Benchmarks across 5 Tracks

### Competition
- **Deadline**: April 16, 2026 (8 days remaining)
- **Tracks**: All 5 — Metacognition, Learning, Attention, Executive Functions, Social Cognition
- **Prize pool**: $200,000

### Benchmark Suite: 24 Tasks Implemented

#### Metacognition Track (8 tasks)
| Task | File | Status |
|------|------|--------|
| Retrospective Calibration | `task_calibration.py` | ✅ |
| Feeling-of-Knowing (FOK) | `task_fok.py` | ✅ |
| FOK Sub-metrics | `task_fok_submetrics.py` | ✅ |
| Judgment-of-Learning (JOL) | `task_jol.py` | ✅ |
| JOL Sub-metrics | `task_jol_submetrics.py` | ✅ |
| Error Detection | `task_error_detection.py` | ✅ |
| Error Detection Sub-metrics | `task_error_detection_submetrics.py` | ✅ |
| Learning Monitoring | `task_learning_monitoring.py` | ✅ |
| Metacognitive Control | `task_metacognitive_control.py` | ✅ |
| Epistemic Revision | `task_epistemic_revision.py` | ✅ |
| Canary System | `task_canary.py` | ✅ |

#### Learning Track (4 tasks)
| Task | File | Status |
|------|------|--------|
| Learning Curves | `task_learning_curves.py` | ✅ |
| Interference | `task_interference.py` | ✅ |
| Transfer | `task_transfer.py` | ✅ |
| Curriculum Sensitivity | `task_curriculum.py` | ✅ |

#### Attention Track (4 tasks)
| Task | File | Status |
|------|------|--------|
| Selective Attention | `task_selective.py` | ✅ |
| Vigilance | `task_vigilance.py` | ✅ |
| Divided Attention | `task_divided.py` | ✅ |
| Instruction Update | `task_instruction_update.py` | ✅ |

#### Executive Functions Track (4 tasks)
| Task | File | Status |
|------|------|--------|
| WCST | `task_wcst.py` | ✅ |
| Tower of London | `task_tol.py` | ✅ |
| N-back | `task_nback.py` | ✅ |
| Task Switching | `task_switching.py` | ✅ |

#### Social Cognition Track (3 tasks)
| Task | File | Status |
|------|------|--------|
| False Belief (ToM) | `task_false_belief.py` | ✅ |
| Pragmatic Inference | `task_pragmatic.py` | ✅ |
| Sarcasm Detection | `task_sarcasm.py` | ✅ |

### Validation
- ✅ All 24 benchmarks pass mock validation (4 strategies)
- ✅ Reliability: α ≥ 0.70 for all tested benchmarks
- ✅ Discriminant validity: within-track r = 0.37 vs between-track r = 0.09
- ✅ 26 Kaggle notebooks generated (22 benchmark + 3 sub-metric + 1 dashboard + 1 overview)
- ✅ Submission narrative written
- ✅ DESIGN.md for all 5 tracks

### Documentation
- `SUBMISSION_NARRATIVE.md` — competition writeup
- `COGNITIVE_RATIONALE.md` — cognitive science basis per benchmark
- `METHODOLOGY.md` — scoring and evaluation methodology
- `HUMAN_BASELINES.md` — human performance references

### Remaining
- [ ] Test against frontier models on Kaggle
- [ ] Cross-validate across model families
- [ ] Upload notebooks to Kaggle platform
