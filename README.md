# Cognitive Abilities Benchmark Suite

### Measuring Progress Toward AGI — Kaggle Hackathon Submission

A comprehensive benchmark suite for evaluating frontier AI models' cognitive abilities,
grounded in 50+ years of cognitive science research. Tests **26 distinct cognitive abilities**
across all **5 competition tracks**.

## Key Innovation

Most AI benchmarks test **what** models know. We test **how** they think:

- 🧠 **Metacognition** — Can models assess their own knowledge? (FOK, JOL, Calibration, Epistemic Humility)
- 📚 **Learning** — Can models learn from novel examples? (Learning Curves, Transfer, Interference)
- 🎯 **Attention** — Can models focus and sustain attention? (Selective, Vigilance, Divided Attention)
- 🏗️ **Executive Functions** — Can models plan, inhibit, and adapt? (WCST, Tower of London, CRT)
- 🎭 **Social Cognition** — Can models understand other minds? (Theory of Mind, Pragmatic Inference)

All stimuli are **procedurally generated** or hand-crafted with novel scenarios — they cannot
appear in training data, forcing genuine cognitive ability rather than memorization.

## Benchmarks

### Metacognition (9 benchmarks)
| Benchmark | Construct | Reference |
|-----------|-----------|-----------|
| [Feeling-of-Knowing](notebooks/metacog_fok.ipynb) | Metacognitive monitoring | Hart (1965) |
| [Judgment-of-Learning](notebooks/metacog_jol.ipynb) | Prospective learning prediction | Nelson & Dunlosky (1991) |
| [Retrospective Calibration](notebooks/metacog_calibration.ipynb) | Confidence-accuracy alignment | Fischhoff et al. (1977) |
| [Error Detection](notebooks/metacog_error_detection.ipynb) | Error monitoring | Yeung & Summerfield (2012) |
| [Learning Monitoring](notebooks/metacog_learning_monitoring.ipynb) | Online learning awareness | Nelson & Narens (1990) |
| [Metacognitive Control](notebooks/metacog_control.ipynb) | Strategic re-reading | Thiede et al. (2003) |
| [Epistemic Revision](notebooks/metacog_epistemic_revision.ipynb) | Belief updating under contradiction | Harman (1986) |
| [Epistemic Humility](notebooks/metacog_epistemic_humility.ipynb) | Knowing limits of knowledge | Whitcomb et al. (2017) |
| [Contamination Canary](notebooks/metacog_canary.ipynb) | Meta-benchmark validation | Carlini et al. (2021) |

### Learning (4 benchmarks)
| Benchmark | Construct | Reference |
|-----------|-----------|-----------|
| [Learning Curves](notebooks/learning_curves.ipynb) | Power-law acquisition | Newell & Rosenbloom (1981) |
| [Near vs. Far Transfer](notebooks/learning_transfer.ipynb) | Generalization depth | Barnett & Ceci (2002) |
| [Proactive/Retroactive Interference](notebooks/learning_interference.ipynb) | Memory competition | Underwood (1957) |
| [Curriculum Sensitivity](notebooks/learning_curriculum.ipynb) | Order effects on learning | Bengio et al. (2009) |

### Attention (4 benchmarks)
| Benchmark | Construct | Reference |
|-----------|-----------|-----------|
| [Selective Attention](notebooks/attention_selective.ipynb) | Stroop-like interference | Stroop (1935) |
| [Vigilance](notebooks/attention_vigilance.ipynb) | Sustained attention | Warm et al. (2008) |
| [Divided Attention](notebooks/attention_divided.ipynb) | Dual-task cost | Pashler (1994) |
| [Instruction Update](notebooks/attention_instruction_update.ipynb) | Mid-stream adaptation | Rogers & Monsell (1995) |

### Executive Functions (5 benchmarks)
| Benchmark | Construct | Reference |
|-----------|-----------|-----------|
| [Wisconsin Card Sorting](notebooks/exec_func_wcst.ipynb) | Set-shifting | Milner (1963) |
| [Tower of London](notebooks/exec_func_tol.ipynb) | Planning | Shallice (1982) |
| [Task Switching](notebooks/exec_func_task_switch.ipynb) | Cognitive flexibility | Miyake et al. (2000) |
| [N-back](notebooks/exec_func_nback.ipynb) | Working memory updating | Kirchner (1958) |
| [Cognitive Reflection Test](notebooks/exec_func_crt.ipynb) | Response inhibition | Frederick (2005) |

### Social Cognition (4 benchmarks)
| Benchmark | Construct | Reference |
|-----------|-----------|-----------|
| [False Belief ToM](notebooks/social_cog_false_belief.ipynb) | Belief attribution | Wimmer & Perner (1983) |
| [Pragmatic Inference](notebooks/social_cog_pragmatic.ipynb) | Speaker intent | Grice (1975) |
| [Sarcasm Detection](notebooks/social_cog_sarcasm.ipynb) | Irony comprehension | Gibbs (1986) |
| [Emotional Prosody](notebooks/social_cog_emotional_prosody.ipynb) | Affective tone detection | Scherer (1986) |

## Structure

```
benchmarks/              # Benchmark implementations (26 tasks across 5 tracks)
  metacognition/         # 9 task files + data/
  learning/              # 4 task files + data/
  attention/             # 4 task files + data/
  executive_functions/   # 5 task files + data/
  social_cognition/      # 4 task files + data/
notebooks/               # 26 Kaggle-ready .ipynb files
docs/                    # Per-track detailed writeups
scripts/                 # Benchmark runner, validators
tests/                   # Mock LLM test harness for offline validation
```

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Validate all benchmarks (no API key needed)
python scripts/validate_all_benchmarks.py

# Verify ground truth data integrity
python scripts/verify_ground_truth.py

# Run benchmarks via Amazon Bedrock
python scripts/run_benchmark_bedrock.py --model anthropic.claude-sonnet-4-6 --benchmark metacog_fok

# Run with mock LLM (no API key)
python -m pytest tests/test_harness.py
```

## Competition

- **Competition:** [Measuring Progress Toward AGI - Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi)
- **Host:** Google DeepMind
- **Prize pool:** $200,000
