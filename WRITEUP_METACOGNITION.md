### Does Your AI Know What It Doesn't Know? A 9-Task Metacognition Benchmark Suite

### Team
Yiyang Zeng (Independent researcher)

### Problem Statement

Current LLM evaluations measure what models *know* but not whether they know *what they know*. Metacognition — the ability to monitor and regulate one's own cognitive processes — is fundamental to trustworthy AI: a model that cannot gauge its own uncertainty will confidently confabulate rather than seek clarification.

Existing benchmarks treat confidence as a post-hoc annotation rather than an independently measurable cognitive faculty. We lack evaluations that isolate specific metacognitive processes — prospective monitoring (predicting future performance), retrospective calibration (matching confidence to accuracy), error detection, and strategic control. Without such benchmarks, we cannot determine whether a model's apparent self-awareness reflects genuine self-monitoring or surface-level hedging.

This benchmark suite addresses the question: **Can frontier models accurately monitor, evaluate, and regulate their own cognitive processes?**

### Task & Benchmark Construction

We constructed 9 tasks grounded in the Nelson & Narens (1990) metacognitive monitoring→control framework, each isolating a distinct metacognitive construct:

| Task | Construct | Protocol |
|------|-----------|----------|
| **Confidence Calibration** | Retrospective monitoring | Answer diverse questions with 0–100 confidence ratings; score via Brier Skill Score |
| **Feeling-of-Knowing (FOK)** | Prospective monitoring | Two-phase: rate confidence *before* answering; measures gamma correlation between prediction and outcome |
| **Judgment-of-Learning (JOL)** | Learning prediction | Study novel word-definition pairs → predict recall → distractor → test; all stimuli invented to prevent contamination |
| **Error Detection** | Process monitoring | Review step-by-step solutions containing subtle errors; detect, localize, and rate confidence |
| **Learning Monitoring** | Online self-assessment | Learn incrementally presented rule system; rate understanding after each rule; compare self-assessment to actual performance |
| **Metacognitive Control** | Strategic regulation | Given limited "re-read" budget, choose which passage sections to review before answering questions |
| **Epistemic Humility** | Knowledge boundary recognition | Mix of answerable and genuinely unanswerable questions; measures confabulation vs. appropriate refusal |
| **Epistemic Revision** | Belief updating | Learn rules → encounter contradicting evidence → must revise beliefs rather than perseverate |
| **Contamination Canary** | Metacognitive discrimination | Mix fabricated and real facts; measures whether confidence discriminates known from unknowable items |

**Key design principle — two-phase protocols:** For FOK and JOL, confidence is elicited *before* the model answers, preventing post-hoc rationalization. This follows the Answer-Free Confidence Estimation approach (NeurIPS 2024), which reduces overconfidence by 15–30% on hard items.

### Dataset

All items are **procedurally generated** at evaluation time using seeded random generators, ensuring:
- No contamination from training data (particularly JOL, which uses entirely invented vocabulary)
- Reproducible results across runs (deterministic seeds)
- Sufficient sample size (15–50 items per task depending on construct)

**Item schema:** Each task produces items with fields: `id` (unique identifier), `question` (prompt text), `expected_answer` (ground truth), `difficulty` (easy/medium/hard), `domain` (knowledge category). Model responses are parsed into structured `confidence` (0–100 integer) and `answer` fields.

**Scoring:** Primary metric per task is a composite of gamma correlation (resolution), Brier Skill Score (calibration + discrimination), and task-specific accuracy. BSS was chosen over raw ECE because ECE rewards always-hedging-to-50% strategies, while BSS properly penalizes uninformative confidence.

**Provenance:** Question content draws from public-domain knowledge across STEM, humanities, and logic domains. No copyrighted datasets are used. Novel stimuli (JOL word pairs, epistemic revision rules, canary fabrications) are generated programmatically.

### Technical Details

All tasks are implemented using the `kaggle-benchmarks` SDK with the `@kbench.task` decorator. Each task:
- Creates a fresh `kbench.chats.new()` conversation per evaluation item
- Parses structured confidence ratings via regex extraction from free-text responses
- Handles edge cases (refusal to answer, non-numeric confidence, malformed output) with conservative fallback scoring
- Uses `numpy` for statistical computation (gamma correlation, BSS, ECE)

**Contamination hardening:** The canary benchmark explicitly tests whether models confabulate on fabricated items. JOL uses entirely invented stimuli. Calibration questions span diverse domains so no single-domain memorization helps. Error detection chains use novel problem instances with procedurally placed errors.

### Results, Insights, and Conclusions

We evaluated 10 models via Amazon Bedrock. Key metacognition results (scores 0–1, higher = better):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| Calibration | 0.183 | 0.327 | 0.998 | Claude Opus (1.00) | 6 models (0.00) |
| FOK | 0.561 | 0.078 | 0.232 | Claude Sonnet (0.65) | Ministral 3B (0.41) |
| JOL | 0.393 | 0.086 | 0.265 | Llama 3.3 70B (0.47) | GPT-OSS-120B (0.20) |
| Error Detection | 0.862 | 0.073 | 0.226 | Claude Sonnet (0.97) | Llama 4 (0.75) |
| Epistemic Humility | 0.788 | 0.209 | 0.720 | Llama 3.3 70B (0.92) | Ministral 3B (0.20) |
| Control | 0.549 | 0.172 | 0.548 | Nova Pro (0.75) | Ministral 3B (0.20) |
| Canary | 0.795 | 0.290 | 1.000 | Llama 3.3 70B (1.00) | Ministral 3B (0.00) |
| Epistemic Revision | 0.801 | 0.097 | 0.290 | Claude Opus (0.96) | Ministral 3B (0.67) |
| Learning Monitoring | 0.834 | 0.077 | 0.220 | Nova Pro (0.91) | Ministral 3B (0.69) |

**Insight 1 — Three-tier metacognition pattern.** Across all 10 models, scores cluster into three tiers: *external monitoring* (canary, epistemic humility, error detection; mean 0.82), *temporal self-tracking* (epistemic revision, control, learning monitoring; mean 0.73), and *prospective self-assessment* (FOK, JOL, calibration; mean 0.39). This 2:1 dissociation between external and internal metacognition replicates across model families and scales.

**Insight 2 — Near-universal calibration failure.** Only Claude Opus achieves meaningful calibration (BSS = 1.00); Claude Sonnet scores 0.50; the remaining 7 models score ≤0.12. Most LLMs' expressed confidence carries zero information beyond the base rate, confirming Chhikara et al. (2025) on systematic overconfidence.

**Insight 3 — Strong discriminatory power.** Average cross-model standard deviation = 0.16 across 9 benchmarks (range 0.07–0.33). The suite produces a meaningful gradient from Ministral 3B (3B parameters, weakest overall) through mid-tier models (Nova Pro, Llama 4) to frontier models (Claude Opus, Qwen3), with each benchmark revealing a distinct capability profile.

**Insight 4 — Epistemic humility does not track model size.** Llama 3.3 70B (0.92), Qwen3 80B (0.92), and Llama 4 Maverick 17B (0.90) outperform Claude Opus (0.80) on epistemic humility, while Ministral 3B collapses to 0.20. This suggests that acknowledging uncertainty is shaped by training methodology (e.g., RLHF calibration) rather than raw scale.

### Organizational Affiliations

Independent submission — no organizational affiliation.

### References & Citations

- Nelson, T. O. & Narens, L. (1990). Metamemory: A theoretical framework and new findings. *Psychology of Learning and Motivation*, 26, 125–173.
- Hart, J. T. (1965). Memory and the feeling-of-knowing experience. *Journal of Educational Psychology*, 56(4), 208–216.
- Koriat, A. (1997). Monitoring one's own knowledge during study. *Journal of Experimental Psychology: General*, 126(4), 349–370.
- Fleming, S. M. (2024). Metacognition and confidence in AI systems. *Trends in Cognitive Sciences*.
- Chhikara, P. et al. (2025). Overconfidence in large language models. *TMLR*.
- Steyvers, M. & Peters, M. A. J. (2025). LLM and human metacognition. *Current Directions in Psychological Science*.
- Fischhoff, B., Slovic, P. & Lichtenstein, S. (1977). Knowing with certainty. *Journal of Experimental Psychology: Human Perception and Performance*.
- Whitcomb, D. et al. (2017). Intellectual humility: Owning our limitations. *Philosophy and Phenomenological Research*.
- Botvinick, M. M. et al. (2001). Conflict monitoring and cognitive control. *Psychological Review*, 108(3), 624–652.
