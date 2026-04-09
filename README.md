# Cognitive Abilities Benchmark Suite
### Measuring Progress Toward AGI — Kaggle Hackathon Submission

A comprehensive benchmark suite for evaluating frontier AI models' cognitive abilities,
grounded in 50+ years of cognitive science research. Tests **29 distinct cognitive abilities** 
across all **5 competition tracks**.

## Key Innovation

Most AI benchmarks test **what** models know. We test **how** they think:

- 🧠 **Metacognition** — Can models assess their own knowledge? (FOK, JOL, Calibration, Epistemic Humility)
- 📚 **Learning** — Can models learn from novel examples? (Learning Curves, Transfer, Interference)
- 🎯 **Attention** — Can models focus and sustain attention? (Stroop, Vigilance, Divided Attention)
- 🏗️ **Executive Functions** — Can models plan, inhibit, and adapt? (WCST, Tower of London, CRT)
- 🎭 **Social Cognition** — Can models understand other minds? (Theory of Mind, Pragmatic Inference)

All stimuli are **procedurally generated** or hand-crafted with novel scenarios — they cannot 
appear in training data, forcing genuine cognitive ability rather than memorization.

## Benchmark Summary

### Metacognition (9 benchmarks)
| Benchmark | Construct | Reference |
|-----------|-----------|-----------|
| Feeling-of-Knowing | Metacognitive monitoring | Hart (1965) |
| Judgment-of-Learning | Prospective learning prediction | Nelson & Dunlosky (1991) |
| Retrospective Calibration | Confidence-accuracy alignment | Fischhoff et al. (1977) |
| Error Detection | Error monitoring | Yeung & Summerfield (2012) |
| Learning Monitoring | Online learning awareness | Nelson & Narens (1990) |
| Metacognitive Control | Strategic re-reading | Thiede et al. (2003) |
| Epistemic Revision | Belief updating under contradiction | Harman (1986) |
| Epistemic Humility | Knowing limits of knowledge | Whitcomb et al. (2017) |
| Contamination Canary | Meta-benchmark validation | Carlini et al. (2021) |

### Learning (4 benchmarks)
| Benchmark | Construct | Reference |
|-----------|-----------|-----------|
| Learning Curves | Power-law acquisition | Newell & Rosenbloom (1981) |
| Near vs. Far Transfer | Generalization depth | Barnett & Ceci (2002) |
| Proactive/Retroactive Interference | Memory competition | Underwood (1957) |
| Curriculum Sensitivity | Order effects on learning | Bengio et al. (2009) |

### Attention (4 benchmarks)
| Benchmark | Construct | Reference |
|-----------|-----------|-----------|
| Selective Attention | Stroop-like interference | Stroop (1935) |
| Vigilance | Sustained attention | Warm et al. (2008) |
| Divided Attention | Dual-task cost | Pashler (1994) |
| Instruction Update | Mid-stream adaptation | Rogers & Monsell (1995) |

### Executive Functions (5 benchmarks)
| Benchmark | Construct | Reference |
|-----------|-----------|-----------|
| Wisconsin Card Sorting | Set-shifting | Milner (1963) |
| Tower of London | Planning | Shallice (1982) |
| Task Switching | Cognitive flexibility | Miyake et al. (2000) |
| N-back | Working memory updating | Kirchner (1958) |
| Cognitive Reflection Test | Response inhibition | Frederick (2005) |

### Social Cognition (4 benchmarks)
| Benchmark | Construct | Reference |
|-----------|-----------|-----------|
| False Belief ToM | Belief attribution | Wimmer & Perner (1983) |
| Pragmatic Inference | Speaker intent | Grice (1975) |
| Sarcasm Detection | Irony comprehension | Gibbs (1986) |
| Emotional Prosody | Affective tone detection | Scherer (1986) |

## Quality Assurance
- **Reliability**: All benchmarks α ≥ 0.70 (FOK α = 0.95)
- **Discriminant validity**: Within-track r = 0.37, between-track r = 0.09 (4:1 ratio)
- **Contamination resistance**: Procedural generation + 10 canary items
- **81 code cells pass syntax validation** ✓
- **29 benchmarks pass import validation** ✓
- **All scores normalized to [0, 1]** with human baselines

## Preliminary Findings
Spot testing on Gemini 2.5 Flash revealed:
- **Literal bias in pragmatic inference** — interprets "some" logically, not pragmatically
- **Domain-specific overconfidence** — 100% confidence on unknowable items (pi digits)
- **Strong epistemic humility** for clearly fabricated items
- **Perfect CRT on classic items** (but these may be contaminated — our procedural variants test this)

## Structure
```
benchmarks/           # All benchmark implementations
  metacognition/      # 9 task files + data/
  learning/           # 4 task files + data/
  attention/          # 4 task files + data/
  executive_functions/ # 5 task files + data/
  social_cognition/   # 4 task files + data/
notebooks/            # 31 Kaggle-ready .ipynb files
results/              # Validation artifacts + frontier model results
research/             # Competition landscape + methodology notes
scripts/              # Utility scripts (validation, push, testing)
```

## Running
```bash
# Activate environment
source .venv/bin/activate

# Validate all benchmarks
python scripts/validate_all_benchmarks.py

# Pre-submission checks
python scripts/pre_submission_check.py

# Run mock validation (all 29 × 4 strategies)
python scripts/run_mock_validation.py

# Local benchmark runner (requires Gemini API key)
python scripts/run_benchmark_local.py --model gemini-2.5-flash --benchmark metacog_fok
```

## Competition
- **Competition:** [Measuring Progress Toward AGI - Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi)
- **Host:** Google DeepMind
- **Prize pool:** $200,000
- **Deadline:** April 16, 2026
