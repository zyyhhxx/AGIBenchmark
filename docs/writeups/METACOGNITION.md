# Does Your AI Know What It Doesn't Know? A 9-Task Metacognition Benchmark Suite

### Problem Statement

Current LLM evaluations measure what models *know* but not whether they know *what they know*. Metacognition — the ability to monitor and regulate one's own cognitive processes — is fundamental to trustworthy AI. Existing benchmarks treat confidence as a post-hoc annotation rather than an independently measurable cognitive faculty. We lack evaluations that isolate specific metacognitive processes — prospective monitoring, retrospective calibration, error detection, and strategic control. This benchmark suite addresses: **Can frontier models accurately monitor, evaluate, and regulate their own cognitive processes?**

### Task & Benchmark Construction

We constructed 9 tasks grounded in the Nelson & Narens (1990) metacognitive monitoring→control framework, each isolating a distinct metacognitive construct:

| Task | Construct | Protocol |
|------|-----------|----------|
| **Retrospective Calibration** | Retrospective monitoring | Answer diverse questions with 0–100 confidence ratings; score via Brier Skill Score (Fischhoff et al., 1977) |
| **Feeling of Knowing (FOK)** | Prospective monitoring | Two-phase: rate confidence *before* answering; measures gamma correlation between prediction and outcome (Hart, 1965) |
| **Judgment of Learning (JOL)** | Learning prediction | Study novel word-definition pairs → predict recall → distractor → test; all stimuli invented to prevent contamination (Nelson & Dunlosky, 1991) |
| **Error Detection** | Process monitoring | Review step-by-step solutions containing subtle errors; detect, localize, and rate confidence (Yeung & Summerfield, 2012) |
| **Learning Monitoring** | Online self-assessment | Learn incrementally presented rule system; rate understanding after each rule; compare self-assessment to actual performance (Dunlosky & Nelson, 1992) |
| **Metacognitive Control** | Strategic regulation | Given limited "re-read" budget, choose which passage sections to review before answering questions (Son & Metcalfe, 2000) |
| **Epistemic Humility** | Knowledge boundary recognition | Mix of answerable and genuinely unanswerable questions; measures confabulation vs. appropriate refusal (Whitcomb et al., 2017) |
| **Epistemic Revision** | Belief updating | Learn rules → encounter contradicting evidence → must revise beliefs rather than perseverate (Gärdenfors, 1988) |
| **Contamination Canary** | Metacognitive discrimination | Mix fabricated and real facts; measures whether confidence discriminates known from unknowable items (Carlini et al., 2021) |

**Key design choices:**

- **Pre-answer confidence elicitation** (FOK, JOL): Confidence is elicited *before* the model answers in a separate conversation, preventing post-hoc rationalization. This follows the Answer-Free Confidence Estimation approach.
- **Fictional domains** (JOL, learning monitoring): All stimuli are invented (novel word-definition pairs, synthetic rule systems), making training data contamination impossible.
- **Unanswerable questions** (epistemic humility): Genuinely unanswerable items (future events, unknowable facts) test whether models can recognize the boundaries of their knowledge rather than confabulate.
- **Raw experimental data** (epistemic revision): Transfer phase presents raw observations without explicit contradiction labels — models must inductively infer revised rules from data, testing genuine belief updating.

**Scoring:** Each task uses a task-specific composite. FOK, JOL, and Learning Monitoring use gamma correlation to measure confidence–accuracy alignment. BSS was chosen over raw ECE where applicable because ECE rewards always-hedging-to-50% strategies. Calibration weights extreme-item accuracy (50%), BSS (25%), and uncertainty awareness (25%). All scores normalized to [0, 1].

**Contamination resistance:** Procedurally generated stimuli with seeded RNG, fictional domains, and two-phase protocols where confidence is elicited before answers.

### Dataset

All data is inlined directly in the Kaggle notebooks with no external dependencies. Procedurally generated stimuli use seeded RNG for deterministic reproducibility. Non-procedural items were generated and verified for accuracy, then frozen at benchmark creation. Ground truth verification scripts independently validate all answer keys. No copyrighted datasets are used.

### Results, Insights, and Conclusions

We evaluated 8 models on the [Kaggle Community Benchmarks platform](https://www.kaggle.com/benchmarks/ianstudy/metacognition-track), spanning frontier (Claude Opus 4.6, DeepSeek-R1, Gemini 2.5 Pro, GPT-5.4), mid-tier (Gemini 2.5 Flash, GPT-5.4 Nano), and small models (Gemma 3 4B, Gemma 3 1B):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| Retrospective Calibration | 0.448 | 0.166 | 0.493 | Gemini 2.5 Pro (0.59) | Gemma 3 1B (0.09) |
| FOK | 0.558 | 0.151 | 0.489 | GPT-5.4 (0.77) | Gemma 3 1B (0.28) |
| JOL | 0.612 | 0.192 | 0.508 | Claude Opus 4.6 (0.79) | Gemma 3 4B (0.28) |
| Error Detection | 0.821 | 0.182 | 0.580 | DeepSeek-R1 (0.98) | Gemma 3 1B (0.40) |
| Epistemic Humility | 0.725 | 0.169 | 0.453 | Claude Opus 4.6 (0.88) | Gemma 3 4B (0.43) |
| Control | 0.766 | 0.235 | 0.723 | Claude Opus 4.6 / Gemini 2.5 Pro / GPT-5.4 (0.91) | Gemma 3 1B (0.19) |
| Canary | 0.656 | 0.390 | 0.992 | Gemini 2.5 Pro (0.99) | Gemma 3 4B / Gemma 3 1B (0.00) |
| Epistemic Revision | 0.747 | 0.163 | 0.503 | Claude Opus 4.6 (0.96) | Gemma 3 1B (0.46) |
| Learning Monitoring | 0.677 | 0.292 | 0.712 | DeepSeek-R1 (0.97) | Gemma 3 4B (0.25) |

**Overall ranking:** Claude Opus 4.6 (0.825) > DeepSeek-R1 (0.813) = Gemini 2.5 Flash (0.813) > Gemini 2.5 Pro (0.808) > GPT-5.4 (0.778) > GPT-5.4 Nano (0.613) > Gemma 3 4B (0.419) > Gemma 3 1B (0.274).

**Insight 1 — Two-tier metacognition pattern.** Scores separate into *monitoring tasks* (canary, epistemic humility, error detection, epistemic revision, control, learning monitoring; mean 0.73) and *prospective self-assessment* (FOK, JOL, calibration; mean 0.54). This 1.4:1 dissociation holds across all 8 models, suggesting that evaluating external information is fundamentally easier than predicting one's own future performance. This mirrors the Nelson & Narens (1990) monitoring→control distinction: monitoring external stimuli engages different processes than prospective self-assessment. Even mid-tier GPT-5.4 Nano maintains a monitoring mean of 0.67 versus a prospective mean of 0.50.

**Insight 2 — Calibration reveals systematic overconfidence.** Frontier models cluster tightly on calibration (0.50–0.59), while small models collapse (Gemma 3 4B: 0.29, Gemma 3 1B: 0.09). Frontier models universally report 94–99% confidence even on the hardest items, confirming Chhikara et al. (2025). The composite scoring rewards models that identify *which specific items* are hard, not just overall accuracy.

**Insight 3 — Strong discriminatory power across the model spectrum.** Average cross-model std = 0.216 across 9 benchmarks (range 0.151–0.390). Canary (std = 0.390) and learning monitoring (std = 0.312) are the strongest discriminators. The suite creates a clear four-tier hierarchy: frontier (0.78–0.83), mid-tier (0.61), small-capable (0.42), and small-floor (0.27). Both Gemma models score 0.00 on canary — complete failure to distinguish fabricated from real facts.

**Insight 4 — FOK reveals the purest test of prospective metacognition.** GPT-5.4 achieves the highest FOK score (0.77), demonstrating strong prospective monitoring — accurately predicting its own performance before answering. Gemma 3 1B scores 0.28, showing poor discrimination between items it will answer correctly versus incorrectly. The two-phase protocol (confidence elicitation in a separate conversation from the answer attempt) isolates prospective monitoring from post-hoc rationalization.

**Insight 5 — Scaling reveals selective metacognitive transfer.** GPT-5.4 Nano scores 0.613 overall — 79% of full GPT-5.4 (0.778). The gap concentrates in specific tasks: Nano collapses on learning monitoring (0.41 vs 0.82) and canary (0.68 vs 0.92), but matches GPT-5.4 on JOL (0.73 vs 0.60) and control (0.80 vs 0.91). Some metacognitive capabilities transfer well to smaller models; others require scale.

### References & Citations

- Nelson, T. O. & Narens, L. (1990). Metamemory: A theoretical framework. *Psych. of Learning and Motivation*, 26, 125–173.
- Hart, J. T. (1965). Memory and the feeling-of-knowing experience. *J. Educ. Psych.*, 56(4), 208–216.
- Nelson, T. O. & Dunlosky, J. (1991). When people's judgments of learning are extremely accurate. *Psych. Science*, 2(4), 267–270.
- Dunlosky, J. & Nelson, T. O. (1992). Importance of the kind of cue for JOLs. *Memory & Cognition*, 20, 374–380.
- Kruger, J. & Dunning, D. (1999). Unskilled and unaware of it. *J. Personality and Social Psych.*, 77(6), 1121–1134.
- Son, L. K. & Metcalfe, J. (2000). Metacognitive and control strategies in study-time allocation. *J. Exp. Psych.: LMC*, 26(1), 204–221.
- Zimmerman, B. J. (2000). Self-efficacy: An essential motive to learn. *Contemporary Educ. Psych.*, 25(1), 82–91.
- Thiede, K. W. & Anderson, M. C. M. (2003). Summarizing can improve metacomprehension accuracy. *Contemporary Educ. Psych.*, 28(2), 129–160.
- Dunlosky, J. & Metcalfe, J. (2009). *Metacognition*. Sage.
- Yeung, N. & Summerfield, C. (2012). Metacognition in human decision-making. *Phil. Trans. R. Soc. B*, 367, 1310–1321.
- Rajpurkar, P. et al. (2018). Know what you don't know: Unanswerable questions for SQuAD. *Proc. ACL*, 784–789.
- Carlini, N. et al. (2021). Extracting training data from large language models. *USENIX Security*.
- Harman, G. (1986). *Change in View: Principles of Reasoning*. MIT Press.
- Fischhoff, B., Slovic, P. & Lichtenstein, S. (1977). Knowing with certainty. *J. Exp. Psych.: HPP*, 3(4), 552–564.
- Whitcomb, D. et al. (2017). Intellectual humility. *Phil. and Phenom. Research*, 94(3), 509–539.
- Gärdenfors, P. (1988). *Knowledge in Flux: Modeling the Dynamics of Epistemic States*. MIT Press.
- Fleming, S. M. (2024). Metacognition and confidence in AI systems. *Trends in Cognitive Sciences*.
- Chhikara, P. et al. (2025). Overconfidence in large language models. *TMLR*.
