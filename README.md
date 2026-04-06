# Cognitive Abilities Benchmark Suite
### Measuring Progress Toward AGI — Kaggle Hackathon Submission

A comprehensive benchmark suite for evaluating frontier AI models' cognitive abilities,
grounded in cognitive science research. Tests **12 distinct cognitive abilities** across
**3 tracks**: Metacognition, Learning, and Attention.

## Key Innovation

Most AI benchmarks test **what** models know. We test **how** they think:

- 🧠 **Can models assess their own knowledge?** (Feeling-of-Knowing, Calibration)
- 📚 **Can models learn from novel examples?** (Learning Curves, Transfer)
- 🎯 **Can models focus while ignoring distractions?** (Stroop, Vigilance)

All novel stimuli are **procedurally generated** — they cannot appear in training data,
forcing genuine cognitive ability rather than memorization.

## Benchmark Summary

### Metacognition Track (5 tasks)

| Benchmark | What it tests | Key innovation |
|-----------|--------------|----------------|
| **Calibration** | Confidence-accuracy alignment | ECE across 40 questions, 14 domains |
| **Feeling-of-Knowing** | Prospective metacognitive monitoring | **Two-phase protocol**: confidence rated *before* answering |
| **Judgment-of-Learning** | Prediction of future recall | **Invented stimuli** that can't be memorized |
| **Error Detection** | Reasoning error identification | Balanced correct/incorrect chains with localization |
| **Learning Monitoring** | Self-assessment during learning | **Cross-domain**: metacognition + learning combined |

### Learning Track (4 tasks)

| Benchmark | What it tests | Key innovation |
|-----------|--------------|----------------|
| **Learning Curves** | Sample efficiency | **Generated rule systems** with controlled complexity |
| **Near vs. Far Transfer** | Generalization ability | Three transfer distances (identical/near/far) |
| **Interference** | Resistance to forgetting | Tests proactive and retroactive interference |
| **Curriculum Sensitivity** | Effect of training order | Four orderings: random/easy-hard/hard-easy/interleaved |

### Attention Track (3 tasks)

| Benchmark | What it tests | Key innovation |
|-----------|--------------|----------------|
| **Selective Attention** | Filtering distractors | Stroop-analogue with congruent/incongruent conditions |
| **Vigilance** | Sustained monitoring | Target detection over long sequences |
| **Divided Attention** | Multitasking cost | Single vs. dual-task performance comparison |

## Cognitive Science Foundation

Every benchmark maps to established constructs from cognitive psychology:

- **Nelson & Narens (1990)**: Metamemory monitoring framework (metacognition track)
- **Newell & Rosenbloom (1981)**: Power law of practice (learning curves)
- **Thorndike & Woodworth (1901)**: Transfer of practice (transfer benchmark)
- **Stroop (1935)**: Selective attention interference (attention track)
- **Mackworth (1948)**: Vigilance decrement (sustained attention)

Full references in [METHODOLOGY.md](benchmarks/METHODOLOGY.md).

## Human Baselines

| Benchmark | Metric | Human Range |
|-----------|--------|-------------|
| Calibration | ECE | 0.10–0.20 |
| FOK | Gamma | 0.25–0.55 |
| JOL | Gamma | 0.40–0.90 |
| Error Detection | d' | 1.5–3.0 |
| Learning Curves | Power law exponent | 0.3–0.5 |

See [HUMAN_BASELINES.md](benchmarks/HUMAN_BASELINES.md) for complete reference data.

## Technical Details

- Built on `kaggle-benchmarks` SDK v0.3.0
- Each benchmark: `@kbench.task` returning float score (0-1)
- Self-contained Kaggle notebooks in `notebooks/`
- Zero external dependencies beyond the SDK

## Repository Structure

```
benchmarks/
├── metacognition/    # 5 metacognition benchmarks
├── learning/         # 4 learning benchmarks
├── attention/        # 3 attention benchmarks
├── METHODOLOGY.md    # Full writeup
├── COGNITIVE_RATIONALE.md  # Cognitive science basis
└── HUMAN_BASELINES.md      # Human performance reference
notebooks/            # 12 self-contained Kaggle notebooks
tests/                # Local test harness
```

## Running Locally

```bash
# Verify all tasks parse correctly
python3 -c "import ast; ast.parse(open('benchmarks/metacognition/task_fok.py').read())"

# Run with mock LLM (local testing)
python3 tests/test_harness.py

# Generate Kaggle notebooks
python3 generate_notebooks.py
```

## On Kaggle

Upload any notebook from `notebooks/` directory. Each is fully self-contained.

## References

See [METHODOLOGY.md](benchmarks/METHODOLOGY.md) for complete bibliography.

---

*Submission for the [Measuring Progress Toward AGI - Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi) Kaggle hackathon.*
