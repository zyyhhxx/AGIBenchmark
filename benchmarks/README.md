# AGI Benchmark Suite — Code Structure

## Tracks

### `metacognition/` — 9 benchmarks
Tests whether models have accurate self-models — knowing what they know and don't know.

| File | Benchmark | Construct |
|------|-----------|-----------|
| `task_fok.py` | Feeling-of-Knowing | Metacognitive monitoring (Hart 1965) |
| `task_jol.py` | Judgment-of-Learning | Prospective learning prediction |
| `task_calibration.py` | Retrospective Calibration | Confidence-accuracy correspondence |
| `task_error_detection.py` | Error Detection | Error monitoring in reasoning chains |
| `task_learning_monitoring.py` | Learning Monitoring | Online tracking of learning |
| `task_metacognitive_control.py` | Metacognitive Control | Strategic resource allocation |
| `task_epistemic_revision.py` | Epistemic Revision | Belief updating under contradiction |
| `task_epistemic_humility.py` | Epistemic Humility | Knowing limits of knowledge |
| `task_canary.py` | Contamination Canary | Meta-benchmark validation |

### `learning/` — 4 benchmarks
Tests in-context learning dynamics using procedurally generated rule systems.

| File | Benchmark | Construct |
|------|-----------|-----------|
| `task_learning_curves.py` | Learning Curves | Power-law acquisition (Newell & Rosenbloom 1981) |
| `task_transfer.py` | Near vs. Far Transfer | Generalization depth |
| `task_interference.py` | Interference | Proactive/retroactive memory competition |
| `task_curriculum.py` | Curriculum Sensitivity | Order effects on learning |

### `attention/` — 4 benchmarks
Adapts cognitive neuroscience attention paradigms for LLMs.

| File | Benchmark | Construct |
|------|-----------|-----------|
| `task_selective.py` | Selective Attention | Stroop-like interference (Stroop 1935) |
| `task_vigilance.py` | Sustained Attention | Signal detection over long sequences |
| `task_divided.py` | Divided Attention | Dual-task cost (Pashler 1994) |
| `task_instruction_update.py` | Instruction Update | Mid-stream adaptation |

### `executive_functions/` — 5 benchmarks
Tests planning, inhibition, flexibility — the Miyake et al. (2000) framework.

| File | Benchmark | Construct |
|------|-----------|-----------|
| `task_wcst.py` | Wisconsin Card Sorting | Set-shifting (Milner 1963) |
| `task_tol.py` | Tower of London | Planning (Shallice 1982) |
| `task_switching.py` | Task Switching | Cognitive flexibility |
| `task_nback.py` | N-back | Working memory updating |
| `task_crt.py` | Cognitive Reflection Test | Response inhibition (Frederick 2005) |

### `social_cognition/` — 4 benchmarks
Tests understanding of other minds and communicative intent.

| File | Benchmark | Construct |
|------|-----------|-----------|
| `task_false_belief.py` | False Belief ToM | Belief attribution (Wimmer & Perner 1983) |
| `task_pragmatic.py` | Pragmatic Inference | Speaker intent (Grice 1975) |
| `task_sarcasm.py` | Sarcasm Detection | Irony comprehension |
| `task_emotional_prosody.py` | Emotional Prosody | Affective tone detection |

## Data Structure
Each track has a `data/` subdirectory with:
- Stimulus items (Python dicts with `id`, `question`/`scenario`, `answer`, `accept_patterns`)
- Procedural generators (deterministic, `seed=2026`)
- Imported by task files at runtime

## Running
```bash
# Validate all benchmarks
python scripts/validate_all_benchmarks.py

# Verify ground truth data integrity
python scripts/verify_ground_truth.py

# Run benchmarks via Amazon Bedrock
python scripts/run_benchmark_bedrock.py --model anthropic.claude-sonnet-4-6 --benchmark metacog_fok

# Run with mock LLM (no API key)
python -m pytest tests/test_harness.py
```
