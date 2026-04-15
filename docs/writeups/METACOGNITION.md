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

Items use a mix of **LLM-generated question sets** and **procedural generation**, with all data inlined directly in the Kaggle notebooks (no external data dependencies). Total item counts range from ~15 (control) to ~132 (calibration). Contamination resistance is achieved through three mechanisms: (1) procedurally generated stimuli with seeded RNG (learning monitoring, JOL pseudowords, arithmetic chains), (2) fictional domains that cannot appear in training data (Zorblatt Chemistry, Kingdom of Trevalia, invented vocabulary), and (3) two-phase protocols where confidence is elicited before answers (FOK, JOL).

All non-procedural items were generated using Claude, then verified for factual accuracy and logical consistency. Items are frozen at benchmark creation time. No copyrighted datasets are used.

**Scoring:** Each task uses a task-specific composite metric. FOK, JOL, and Learning Monitoring use gamma correlation to measure confidence–accuracy alignment. BSS was chosen over raw ECE where applicable because ECE rewards always-hedging-to-50% strategies, while BSS properly penalizes uninformative confidence. All scores are normalized to [0, 1].

### Technical Details

All tasks use the `kaggle-benchmarks` SDK, creating a fresh conversation per evaluation item. Confidence ratings are parsed via regex extraction from free-text responses, with conservative fallback scoring for malformed output.

### Results, Insights, and Conclusions

We evaluated 8 models on the [Kaggle Community Benchmarks platform](https://www.kaggle.com/benchmarks/ianstudy/metacognition-track), spanning frontier-class (Claude Opus 4.6, DeepSeek-R1, Gemini 2.5 Pro, GPT-5.4), mid-tier (Gemini 2.5 Flash, GPT-5.4 Nano), and small models (Gemma 3 4B, Gemma 3 1B). Results (scores 0–1, higher = better):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| Calibration | 0.448 | 0.178 | 0.493 | Gemini 2.5 Pro (0.59) | Gemma 3 1B (0.09) |
| FOK | 0.450 | 0.170 | 0.525 | Claude Opus 4.6 (0.62) | Gemini 2.5 Pro (0.09) |
| JOL | 0.612 | 0.205 | 0.508 | Claude Opus 4.6 (0.79) | Gemma 3 4B (0.28) |
| Error Detection | 0.821 | 0.194 | 0.580 | DeepSeek-R1 (0.98) | Gemma 3 1B (0.40) |
| Epistemic Humility | 0.725 | 0.181 | 0.453 | Claude Opus 4.6 (0.88) | Gemma 3 4B (0.43) |
| Control | 0.766 | 0.251 | 0.723 | Claude Opus 4.6 (0.91) | Gemma 3 1B (0.19) |
| Canary | 0.656 | 0.417 | 0.992 | Gemini 2.5 Pro (0.99) | Gemma 3 4B (0.00) |
| Epistemic Revision | 0.747 | 0.174 | 0.502 | Claude Opus 4.6 (0.96) | Gemma 3 1B (0.46) |
| Learning Monitoring | 0.677 | 0.312 | 0.712 | DeepSeek-R1 (0.97) | Gemma 3 4B (0.25) |

**Overall model ranking:** Claude Opus 4.6 (0.826) > DeepSeek-R1 (0.808) > Gemini 2.5 Flash (0.799) > GPT-5.4 (0.753) > Gemini 2.5 Pro (0.748) > GPT-5.4 Nano (0.612) > Gemma 3 4B (0.410) > Gemma 3 1B (0.290).

**Insight 1 — Two-tier metacognition pattern.** Scores separate into *monitoring tasks* (canary, epistemic humility, error detection, epistemic revision, control, learning monitoring; mean 0.73) and *prospective self-assessment* (FOK, JOL, calibration; mean 0.50). This 1.5:1 dissociation holds across all 8 models, suggesting that evaluating external information and monitoring ongoing cognition is fundamentally easier than predicting one's own future performance. Even the mid-tier GPT-5.4 Nano maintains a monitoring mean of 0.67 versus a prospective mean of 0.50.

**Insight 2 — Calibration reveals systematic overconfidence.** All frontier models cluster tightly on calibration (0.50–0.59), while small models collapse (Gemma 3 4B: 0.29, Gemma 3 1B: 0.09). The spread (std = 0.178) is driven primarily by the small-model floor effect. Frontier models universally report high confidence (94–99%) even on difficulty-5 items, confirming Chhikara et al. (2025) on systematic overconfidence. The benchmark's composite scoring — 50% extreme-item accuracy, 25% BSS, 25% uncertainty awareness — rewards models that can identify *which specific items* are hard, not just overall accuracy.

**Insight 3 — Strong discriminatory power across the model spectrum.** Average cross-model standard deviation = 0.232 across 9 benchmarks (range 0.170–0.417). Canary (std = 0.417) and learning monitoring (std = 0.312) are the strongest discriminators. Notably, the suite separates not just frontier from small models, but creates a clear four-tier hierarchy: frontier (0.75–0.83), mid-tier (0.61), small-capable (0.41), and small-floor (0.29). Both Gemma models score 0.00 on canary (complete failure to distinguish fabricated from real facts).

**Insight 4 — FOK anomaly for Gemini 2.5 Pro.** Gemini 2.5 Pro scores 0.09 on Feeling-of-Knowing — dramatically lower than its strong performance on other tasks (0.59–0.99). This suggests a specific failure in two-phase prospective monitoring (rating confidence *before* answering), possibly due to training that discourages expressing low confidence. This is not a parsing artifact: the model produces valid structured responses but with poorly calibrated pre-answer confidence.

**Insight 5 — Scaling reveals diminishing metacognitive returns.** GPT-5.4 Nano (a smaller variant of GPT-5.4) scores 0.612 overall — 81% of the full GPT-5.4's score (0.753). However, the gap is concentrated in prospective tasks: Nano matches GPT-5.4 on JOL (0.73 vs 0.60 — Nano actually exceeds it) and metacognitive control (0.80 vs 0.91), but collapses on learning monitoring (0.41 vs 0.82) and canary (0.68 vs 0.92). This suggests that some metacognitive capabilities (strategic control, learning judgment) transfer well to smaller models, while others (online learning monitoring, contamination discrimination) require scale.

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
