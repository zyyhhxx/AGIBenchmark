### Does Your AI Know What It Doesn't Know? A 9-Task Metacognition Benchmark Suite

### Team
Yiyang Zeng (Independent researcher)

### Problem Statement

Current LLM evaluations measure what models *know* but not whether they know *what they know*. Metacognition — the ability to monitor and regulate one's own cognitive processes — is fundamental to trustworthy AI: a model that cannot gauge its own uncertainty will confidently confabulate rather than seek clarification.

Existing benchmarks treat confidence as a post-hoc annotation rather than an independently measurable cognitive faculty. We lack evaluations that isolate specific metacognitive processes — prospective monitoring (predicting future performance), retrospective calibration (matching confidence to accuracy), error detection, and strategic control. Without such benchmarks, we cannot determine whether a model's apparent self-awareness reflects genuine self-monitoring or surface-level hedging.

This benchmark suite addresses: **Can frontier models accurately monitor, evaluate, and regulate their own cognitive processes?**

### Task & Benchmark Construction

We constructed 9 tasks grounded in the Nelson & Narens (1990) metacognitive monitoring→control framework, each isolating a distinct metacognitive construct:

| Task | Construct | Protocol |
|------|-----------|----------|
| **Retrospective Calibration** | Retrospective monitoring | Answer diverse questions with 0–100 confidence ratings; score via Brier Skill Score |
| **Feeling of Knowing (FOK)** | Prospective monitoring | Two-phase: rate confidence *before* answering; measures gamma correlation between prediction and outcome |
| **Judgment of Learning (JOL)** | Learning prediction | Study novel word-definition pairs → predict recall → distractor → test; all stimuli invented to prevent contamination |
| **Error Detection** | Process monitoring | Review step-by-step solutions containing subtle errors; detect, localize, and rate confidence |
| **Learning Monitoring** | Online self-assessment | Learn incrementally presented rule system; rate understanding after each rule; compare self-assessment to actual performance |
| **Metacognitive Control** | Strategic regulation | Given limited "re-read" budget, choose which passage sections to review before answering questions |
| **Epistemic Humility** | Knowledge boundary recognition | Mix of answerable and genuinely unanswerable questions; measures confabulation vs. appropriate refusal |
| **Epistemic Revision** | Belief updating | Learn rules → encounter contradicting evidence → must revise beliefs rather than perseverate |
| **Contamination Canary** | Metacognitive discrimination | Mix fabricated and real facts; measures whether confidence discriminates known from unknowable items |

**Key design principle:** For FOK and JOL, confidence is elicited *before* the model answers, preventing post-hoc rationalization. This follows the Answer-Free Confidence Estimation approach (NeurIPS 2024).

### Dataset

Items use a mix of **LLM-generated question sets** and **procedural generation**, with all data inlined directly in the Kaggle notebooks (no external data dependencies). Total item counts range from ~15 (control) to ~132 (calibration). Contamination resistance is achieved through: (1) procedurally generated stimuli with seeded RNG, (2) fictional domains that cannot appear in training data, and (3) two-phase protocols where confidence is elicited before answers.

All non-procedural items were generated using Claude, then verified for accuracy and consistency. Items are frozen at benchmark creation. No copyrighted datasets are used.

**Scoring:** Each task uses a task-specific composite metric. FOK, JOL, and Learning Monitoring use gamma correlation to measure confidence–accuracy alignment. BSS was chosen over raw ECE where applicable because ECE rewards always-hedging-to-50% strategies, while BSS properly penalizes uninformative confidence. All scores are normalized to [0, 1].

### Technical Details

All tasks use the `kaggle-benchmarks` SDK, creating fresh conversations per item. Confidence ratings are parsed via regex from free-text responses, with fallback scoring for malformed output.

### Results, Insights, and Conclusions

We evaluated 8 models on the [Kaggle Community Benchmarks platform](https://www.kaggle.com/benchmarks/ianstudy/metacognition-track), spanning frontier-class (Claude Opus 4.6, DeepSeek-R1, Gemini 2.5 Pro, GPT-5.4), mid-tier (Gemini 2.5 Flash, GPT-5.4 Nano), and small models (Gemma 3 4B, Gemma 3 1B). Results (scores 0–1, higher = better):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| Retrospective Calibration | 0.448 | 0.178 | 0.493 | Gemini 2.5 Pro (0.59) | Gemma 3 1B (0.09) |
| FOK | 0.558 | 0.161 | 0.489 | GPT-5.4 (0.77) | Gemma 3 1B (0.28) |
| JOL | 0.612 | 0.205 | 0.508 | Claude Opus 4.6 (0.79) | Gemma 3 4B (0.28) |
| Error Detection | 0.821 | 0.194 | 0.580 | DeepSeek-R1 (0.98) | Gemma 3 1B (0.40) |
| Epistemic Humility | 0.725 | 0.181 | 0.453 | Claude Opus 4.6 (0.88) | Gemma 3 4B (0.43) |
| Control | 0.766 | 0.251 | 0.723 | Claude Opus 4.6 (0.91) | Gemma 3 1B (0.19) |
| Canary | 0.656 | 0.417 | 0.992 | Gemini 2.5 Pro (0.99) | Gemma 3 4B (0.00) |
| Epistemic Revision | 0.747 | 0.174 | 0.502 | Claude Opus 4.6 (0.96) | Gemma 3 1B (0.46) |
| Learning Monitoring | 0.677 | 0.312 | 0.712 | DeepSeek-R1 (0.97) | Gemma 3 4B (0.25) |

**Overall model ranking:** Claude Opus 4.6 (0.825) > DeepSeek-R1 (0.813) = Gemini 2.5 Flash (0.813) > Gemini 2.5 Pro (0.808) > GPT-5.4 (0.778) > GPT-5.4 Nano (0.613) > Gemma 3 4B (0.419) > Gemma 3 1B (0.274).

**Insight 1 — Two-tier metacognition pattern.** Scores separate into *monitoring tasks* (canary, epistemic humility, error detection, epistemic revision, control, learning monitoring; mean 0.73) and *prospective self-assessment* (FOK, JOL, calibration; mean 0.55). This 1.3:1 dissociation holds across all 8 models, suggesting that evaluating external information and monitoring ongoing cognition is fundamentally easier than predicting one's own future performance. Even the mid-tier GPT-5.4 Nano maintains a monitoring mean of 0.67 versus a prospective mean of 0.50.

**Insight 2 — Calibration reveals systematic overconfidence.** Frontier models cluster tightly on calibration (0.50–0.59), while small models collapse (Gemma 3 4B: 0.29, Gemma 3 1B: 0.09). Frontier models universally report 94–99% confidence even on difficulty-5 items, confirming Chhikara et al. (2025). The composite scoring — 50% extreme-item accuracy, 25% BSS, 25% uncertainty awareness — rewards models that identify *which specific items* are hard, not just overall accuracy.

**Insight 3 — Strong discriminatory power across the model spectrum.** Average cross-model standard deviation = 0.215 across 9 benchmarks (range 0.161–0.417). Canary (std = 0.417) and learning monitoring (std = 0.312) are the strongest discriminators. Notably, the suite separates not just frontier from small models, but creates a clear four-tier hierarchy: frontier (0.78–0.83), mid-tier (0.61), small-capable (0.42), and small-floor (0.27). Both Gemma models score 0.00 on canary (complete failure to distinguish fabricated from real facts).

**Insight 4 — FOK reveals prompt sensitivity in confidence elicitation.** GPT-5.4 achieves the highest FOK score (0.77), demonstrating strong prospective monitoring — accurately predicting its own performance before answering. In contrast, Gemma 3 1B scores 0.28, showing poor discrimination between items it will answer correctly versus incorrectly. The FOK benchmark's two-phase protocol (confidence elicitation in a separate conversation from the answer attempt) makes it the purest test of prospective metacognition in the suite.

**Insight 5 — Scaling reveals diminishing metacognitive returns.** GPT-5.4 Nano scores 0.612 overall — 81% of full GPT-5.4 (0.753). The gap concentrates in monitoring tasks: Nano collapses on learning monitoring (0.41 vs 0.82) and canary (0.68 vs 0.92), but matches or exceeds GPT-5.4 on JOL (0.73 vs 0.60) and control (0.80 vs 0.91). Some metacognitive capabilities transfer well to smaller models; others require scale.

### Organizational Affiliations

Independent submission — no organizational affiliation.

### References & Citations

- Nelson, T. O. & Narens, L. (1990). Metamemory: A theoretical framework and new findings. *Psych. of Learning and Motivation*, 26, 125–173.
- Hart, J. T. (1965). Memory and the feeling-of-knowing experience. *J. Educ. Psych.*, 56(4), 208–216.
- Nelson, T. O. & Dunlosky, J. (1991). When people's judgments of learning are extremely accurate. *Psych. Science*, 2(4), 267–270.
- Dunlosky, J. & Nelson, T. O. (1992). Importance of the kind of cue for JOLs and the delayed-JOL effect. *Memory & Cognition*, 20, 374–380.
- Kruger, J. & Dunning, D. (1999). Unskilled and unaware of it. *J. Personality and Social Psych.*, 77(6), 1121–1134.
- Son, L. K. & Metcalfe, J. (2000). Metacognitive and control strategies in study-time allocation. *J. Exp. Psych.: LMC*, 26(1), 204–221.
- Zimmerman, B. J. (2000). Self-efficacy: An essential motive to learn. *Contemporary Educ. Psych.*, 25(1), 82–91.
- Thiede, K. W. & Anderson, M. C. M. (2003). Summarizing can improve metacomprehension accuracy. *Contemporary Educ. Psych.*, 28(2), 129–160.
- Dunlosky, J. & Metcalfe, J. (2009). *Metacognition*. Sage.
- Yeung, N. & Summerfield, C. (2012). Metacognition in human decision-making: Confidence and error monitoring. *Phil. Trans. R. Soc. B*, 367, 1310–1321.
- Rajpurkar, P. et al. (2018). Know what you don't know: Unanswerable questions for SQuAD. *Proc. ACL*, 784–789.
- Carlini, N. et al. (2021). Extracting training data from large language models. *USENIX Security*.
- Harman, G. (1986). *Change in View: Principles of Reasoning*. MIT Press.
- Fischhoff, B., Slovic, P. & Lichtenstein, S. (1977). Knowing with certainty. *J. Exp. Psych.: HPP*, 3(4), 552–564.
- Whitcomb, D. et al. (2017). Intellectual humility: Owning our limitations. *Phil. and Phenom. Research*, 94(3), 509–539.
- Fleming, S. M. (2024). Metacognition and confidence in AI systems. *Trends in Cognitive Sciences*.
- Chhikara, P. et al. (2025). Overconfidence in large language models. *TMLR*.
