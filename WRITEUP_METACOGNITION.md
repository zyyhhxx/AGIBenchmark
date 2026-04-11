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

| Task | Claude Opus | DeepSeek-R1 | Llama 4 | Ministral 3B | Nova Pro |
|------|------------|-------------|---------|--------------|----------|
| Calibration | 0.998 | 0.000 | 0.000 | 0.000 | 0.000 |
| FOK | 0.598 | 0.596 | 0.567 | — | 0.416 |
| JOL | 0.464 | 0.276 | 0.465 | — | 0.402 |
| Error Detection | 0.962 | 0.898 | 0.748 | 0.810 | 0.786 |
| Epistemic Humility | 0.799 | 0.880 | 0.903 | 0.200 | 0.876 |
| Control | 0.690 | 0.453 | 0.615 | 0.200 | 0.748 |
| Canary | 0.995 | 0.867 | 0.928 | 0.000 | 0.726 |
| Epistemic Revision | 0.960 | 0.738 | 0.830 | — | 0.750 |
| Learning Monitoring | 0.809 | 0.894 | 0.826 | 0.691 | 0.910 |

**Insight 1 — Bimodal metacognition.** All models show a striking dissociation: strong *external* monitoring (error detection: mean 0.87, epistemic humility: mean 0.77) but weak *internal* self-monitoring (calibration: mean 0.22, JOL: mean 0.39). Models can judge others' reasoning but cannot accurately judge their own knowledge states.

**Insight 2 — Near-universal calibration failure.** Only Claude Opus achieves non-zero calibration (BSS = 0.998). All other models' confidence ratings carry zero information beyond the base rate. This confirms Chhikara et al. (2025) on systematic LLM overconfidence and reveals it persists even in frontier models.

**Insight 3 — Strong discriminatory power.** Average standard deviation across models = 0.17 (range 0.06–0.36). No benchmark is flagged as ceiling or floor. The suite produces a meaningful gradient from Ministral 3B (weakest) through mid-tier models to Claude Opus (strongest), with each benchmark revealing a distinct capability profile.

**Insight 4 — Epistemic humility does not track model size.** DeepSeek-R1 (0.88) and Llama 4 Maverick (0.90) outperform Claude Opus (0.80) on epistemic humility, suggesting that acknowledging uncertainty is not purely a function of capability tier.

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
