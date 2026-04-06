# STATUS.md — AGI Benchmark Project

**Last updated**: 2026-04-06 06:20 UTC

## Project Status: 🟢 Strong Progress — 12 Benchmarks across 3 Tracks

### Competition
- **Deadline**: April 16, 2026 (10 days remaining)
- **Tracks**: Metacognition (#1), Learning (#2), Attention (#3)
- **Prize pool**: $200,000

### Benchmark Suite: 12 Tasks Implemented

#### Metacognition Track (5 tasks)
| Task | File | Status | Score Range |
|------|------|--------|-------------|
| Retrospective Calibration | `task_calibration.py` | ✅ Implemented | 0-1 (1-ECE) |
| Feeling-of-Knowing (FOK) | `task_fok.py` | ✅ Implemented | 0-1 (composite) |
| Judgment-of-Learning (JOL) | `task_jol.py` | ✅ Implemented | 0-1 (composite) |
| Error Detection | `task_error_detection.py` | ✅ Implemented | 0-1 (composite) |
| Learning Monitoring | `task_learning_monitoring.py` | ✅ Implemented | 0-1 (composite) |

#### Learning Track (4 tasks)
| Task | File | Status | Score Range |
|------|------|--------|-------------|
| Learning Curves | `task_learning_curves.py` | ✅ Implemented | 0-1 (composite) |
| Near vs. Far Transfer | `task_transfer.py` | ✅ Implemented | 0-1 (weighted) |
| Interference | `task_interference.py` | ✅ Implemented | 0-1 (composite) |
| Curriculum Sensitivity | `task_curriculum.py` | ✅ Implemented | 0-1 (composite) |

### Documentation
- ✅ `COGNITIVE_RATIONALE.md` — Cognitive science basis for each benchmark
- ✅ `METHODOLOGY.md` — Full writeup (problem, tasks, datasets, technical details)
- ✅ `DESIGN.md` — Design documents for each track
- ✅ `RESEARCH_NELSON_NARENS.md` — Framework research notes
- ✅ `competition_landscape.md` — Competitor analysis

### Remaining Work (Priority Order)
1. **Test on frontier models** — Run all benchmarks on Kaggle platform
2. **Cross-validate** — Run across model families
3. **Documentation polish** — Competition writeup finalization with results
4. **Create submission notebook** — Final polished Kaggle submission

### Attention Track (3 tasks)
| Task | File | Status | Score Range |
|------|------|--------|-------------|
| Selective (Stroop) | `task_selective.py` | ✅ Implemented | 0-1 (interference) |
| Vigilance | `task_vigilance.py` | ✅ Implemented | 0-1 (decrement) |
| Divided (Dual-Task) | `task_divided.py` | ✅ Implemented | 0-1 (dual cost) |

### Kaggle Notebooks
All 12 benchmarks have self-contained Kaggle notebooks in `notebooks/`.

### File Tree
```
benchmarks/
├── COGNITIVE_RATIONALE.md
├── METHODOLOGY.md
├── metacognition/
│   ├── DESIGN.md
│   ├── RESEARCH_NELSON_NARENS.md
│   ├── task_calibration.py
│   ├── task_fok.py
│   ├── task_jol.py
│   ├── task_error_detection.py
│   ├── task_learning_monitoring.py
│   └── data/
│       ├── fok_questions.py (40 questions, 5 categories)
│       ├── calibration_questions.py (40 questions, 3 tiers)
│       ├── jol_stimuli.py (15 word pairs, 2 rule systems)
│       ├── error_detection_chains.py (17 chains, 7 with errors)
│       └── rule_systems.py (generator for novel rule systems)
├── learning/
│   ├── DESIGN.md
│   ├── task_learning_curves.py
│   ├── task_transfer.py
│   ├── task_interference.py
│   ├── task_curriculum.py
│   └── data/
│       └── rule_systems.py (procedural rule system generator)
├── attention/
│   ├── DESIGN.md
│   ├── task_selective.py
│   ├── task_vigilance.py
│   ├── task_divided.py
│   └── data/
│       └── attention_stimuli.py (Stroop, vigilance, dual-task data)
└── shortcut_analysis.py
```
