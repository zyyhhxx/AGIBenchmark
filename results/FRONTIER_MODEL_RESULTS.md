# Frontier Model Results Summary

> **Status:** Awaiting Community Benchmarks execution on Kaggle.
> Kaggle API rate limits prevented notebook publication on 2026-04-08.
> Will be updated with actual scores once notebooks are public and run on the CB platform.

## Benchmark Scores

### Metacognition Track

| Benchmark | GPT-4o | Claude 3.5 | Gemini 1.5 Pro | Human Baseline |
|-----------|--------|-------------|----------------|----------------|
| FOK (gamma) | — | — | — | 0.60–0.80 |
| JOL (composite) | — | — | — | 0.50–0.70 |
| Calibration (1-ECE) | — | — | — | 0.80–0.90 |
| Error Detection (F1) | — | — | — | 0.75–0.85 |
| Learning Monitoring | — | — | — | 0.60–0.75 |
| Metacog Control | — | — | — | 0.65–0.80 |
| Epistemic Revision | — | — | — | 0.70–0.85 |

### Learning Track

| Benchmark | GPT-4o | Claude 3.5 | Gemini 1.5 Pro | Human Baseline |
|-----------|--------|-------------|----------------|----------------|
| Learning Curves | — | — | — | Power law fit |
| Transfer (near/far) | — | — | — | 0.80/0.50 |
| Interference | — | — | — | 0.15–0.25 decrement |
| Curriculum Sensitivity | — | — | — | Ordering effects |

### Attention Track

| Benchmark | GPT-4o | Claude 3.5 | Gemini 1.5 Pro | Human Baseline |
|-----------|--------|-------------|----------------|----------------|
| Selective (Stroop) | — | — | — | 0.85–0.95 |
| Vigilance | — | — | — | d' 2.0–3.0 |
| Divided | — | — | — | 10–20% dual-task cost |
| Instruction Update | — | — | — | 5–15% switch cost |

### Executive Functions Track

| Benchmark | GPT-4o | Claude 3.5 | Gemini 1.5 Pro | Human Baseline |
|-----------|--------|-------------|----------------|----------------|
| WCST | — | — | — | 0.85 acc, 10–15% persev |
| Tower of London | — | — | — | 55–90% optimal |
| Task Switching | — | — | — | 0.90–0.95 |
| N-Back | — | — | — | d' 1.5–3.5 |
| CRT | — | — | — | 30–48% accuracy |

### Social Cognition Track

| Benchmark | GPT-4o | Claude 3.5 | Gemini 1.5 Pro | Human Baseline |
|-----------|--------|-------------|----------------|----------------|
| False Belief ToM | — | — | — | 0.80–0.95 |
| Pragmatic Inference | — | — | — | 0.90–0.95 |
| Sarcasm Detection | — | — | — | AUC 0.90–0.95 |

## Notes

- All scores are in [0, 1] unless otherwise noted
- Human baselines from published cognitive psychology literature (see HUMAN_BASELINES.md)
- "—" indicates score pending Community Benchmarks execution
- Cross-model comparison will reveal model-specific strengths/weaknesses across cognitive domains

## Psychometric Validation (from Mock Runs)

- **Reliability:** All tested benchmarks α ≥ 0.70 (FOK: 0.95, Error Det: 0.79, Attention: 0.73)
- **Discriminant validity:** Within-track r = 0.37, between-track r = 0.09 (good separation)
- **Difficulty stratification:** ECE scales with difficulty (easy 0.26 → hard 0.30)
- **Learning curve sensitivity:** [0, 2, 4, 8, 12] example config validated (monotonic, spread 0.37)
