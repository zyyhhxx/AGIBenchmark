# Metacognition Track — Discriminatory Analysis Summary

| Rank | Benchmark | Mean | Std | Range | CV | N | Top Model | Bottom Model |
|------|-----------|------|-----|-------|----|---|-----------|--------------|
| 1 | epistemic_humility | 0.7968 | 0.2452 | 0.7214 | 0.3078 | 8 | Llama 3.3 70B (0.9214) | Ministral 3B (0.2000) |
| 2 | control | 0.5542 | 0.1829 | 0.5354 | 0.3300 | 9 | Nova Pro (0.7479) | Ministral 3B (0.2125) |
| 3 | calibration | 0.0735 | 0.1644 | 0.3676 | 2.2361 | 5 | Claude Sonnet 4.6 (0.3676) | Nova Pro (0.0000) |
| 4 | jol | 0.4127 | 0.0969 | 0.2647 | 0.2348 | 7 | Llama 3.3 70B (0.4647) | GPT-OSS-120B (0.2000) |
| 5 | learning_monitoring | 0.8055 | 0.0932 | 0.2272 | 0.1156 | 4 | Nova Pro (0.9156) | Claude Sonnet 4.6 (0.6884) |
| 6 | error_detection | 0.8623 | 0.0881 | 0.2393 | 0.1022 | 8 | Claude Sonnet 4.6 (0.9742) | Nova Pro (0.7349) |
| 7 | fok | 0.5272 | 0.0695 | 0.1205 | 0.1319 | 3 | Llama 4 Maverick 17B (0.5674) | Nova Pro (0.4469) |
| 8 | epistemic_revision | 0.8071 | 0.0132 | 0.0325 | 0.0163 | 8 | Llama 3.3 70B (0.8225) | Claude Sonnet 4.6 (0.7900) |
| 9 | canary | 0.0000 | 0.0000 | 0.0000 | inf | 10 | Nova Pro (0.0000) | Nova Pro (0.0000) |

**Top-3 most discriminating:** epistemic_humility, control, calibration

**Bottom-3 least discriminating:** fok, epistemic_revision, canary

## Interpretation

The most discriminating metacognition benchmarks are **epistemic_humility**, **control**, and **calibration**, which show the widest performance spread across models (std ≥ 0.1644). These benchmarks are most useful for differentiating frontier model capabilities in metacognitive reasoning. In contrast, **fok**, **epistemic_revision**, and **canary** show relatively low variance, suggesting either ceiling/floor effects or that current models perform similarly on these tasks. The **canary** benchmark (all zeros) serves as a control and confirms models are not gaming the evaluation.
