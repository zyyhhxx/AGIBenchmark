# Frontier Model Results Summary

> **Status:** Metacognition track scored with Claude Sonnet 4 via Amazon Bedrock (2026-04-09).
> Other tracks awaiting Community Benchmarks execution on Kaggle.

## Benchmark Scores

### Metacognition Track

Model: **Claude Sonnet 4** (Amazon Bedrock, `us.anthropic.claude-sonnet-4-20250514-v1:0`)

| Benchmark | Claude Sonnet 4 | Human Baseline | Notes |
|-----------|----------------|----------------|-------|
| Canary Detection | **0.951** | — | Near-perfect fabrication detection |
| FOK (composite) | **0.449** | 0.60–0.80 | Below human; weak feeling-of-knowing discrimination |
| JOL (composite) | **0.465** | 0.50–0.70 | Low-end human range |
| Calibration (BSS) | **0.000** | 0.80–0.90 | Complete calibration failure (BSS=0) |
| Error Detection (F1) | **0.882** | 0.75–0.85 | Above human baseline |
| Learning Monitoring | **0.698** | 0.60–0.75 | Mid-range human |
| Metacog Control | **0.689** | 0.65–0.80 | Mid-range human |
| Epistemic Revision | **0.820** | 0.70–0.85 | Near top of human range |
| Epistemic Humility | **0.926** | — | Strong recognition of knowledge limits |

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
