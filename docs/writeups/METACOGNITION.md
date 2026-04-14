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

Items use a mix of **handcrafted expert items** and **procedural generation**, with all data inlined directly in the Kaggle notebooks (no external data dependencies):

| Task | Data Source | Item Count | Contamination Resistance |
|------|------------|------------|-------------------------|
| Calibration | Handcrafted trivia (v2, 5 difficulty tiers) + procedurally generated arithmetic | ~132 items | Difficulty tiers target frontier model accuracy bands; procedural math prevents memorization |
| FOK | Handcrafted knowledge questions + procedural arithmetic | ~81 items | Two-phase protocol (confidence before answer) prevents post-hoc rationalization |
| JOL | Handcrafted word-definition pairs + procedurally generated pseudowords (seeded RNG) | ~20 pairs | Invented vocabulary cannot appear in training data |
| Error Detection | Handcrafted reasoning chains + procedurally generated arithmetic chains | ~72 items | Novel problem instances with programmatically placed errors |
| Learning Monitoring | Procedurally generated rule systems (seeded RNG, symbol and number domains) | 4 rule systems | Entirely generated at evaluation time; no memorization possible |
| Control | Handcrafted study passages with strategic re-reading prompts | ~15 items | Tests allocation strategy, not knowledge recall |
| Epistemic Humility | Handcrafted mix of answerable, unanswerable, and fabricated-entity questions | ~24 items | Fabricated entities (e.g., "Kingdom of Trevalia") are unknowable by construction |
| Epistemic Revision | Handcrafted fictional rule systems (e.g., "Zorblatt Chemistry") with belief-contradicting evidence | ~3 systems | Entirely fictional domains prevent prior knowledge from helping |
| Canary | Handcrafted fabricated facts mixed with real facts | ~60 items | Fabricated items use false premises that cannot be memorized |

**Item schema:** Each task produces items with task-specific fields. Model responses are parsed into structured `confidence` (0–100 integer) and `answer` fields via regex extraction, with conservative fallback scoring for malformed output.

**Scoring:** Each task uses a task-specific composite metric tailored to its construct:

- **Calibration:** 0.50 × extreme-item accuracy^1.5 + 0.25 × BSS + 0.25 × uncertainty awareness
- **FOK:** 0.40 × gamma correlation + 0.30 × BSS + 0.30 × AUC
- **JOL:** 0.40 × gamma correlation + 0.30 × BSS + 0.30 × recall rate
- **Error Detection:** 0.35 × F1 + 0.25 × localization accuracy + 0.20 × severity weighting + 0.20 × confidence calibration
- **Learning Monitoring:** 0.30 × gamma correlation + 0.30 × accuracy + 0.20 × confidence calibration + 0.20 × learning curve fit
- **Control:** 0.35 × selection relevance + 0.35 × strategic gain + 0.30 × accuracy
- **Epistemic Humility:** 0.35 × detection + 0.25 × (1 − confabulation) + 0.20 × confidence discrimination + 0.20 × appropriate refusal
- **Epistemic Revision:** 0.10 × violation detection + 0.10 × revision + 0.30 × rule accuracy + 0.25 × transfer + 0.25 × confidence tracking
- **Canary:** max(0, BSS) — pure calibration on fabricated vs. real items

Only FOK, JOL, and Learning Monitoring use gamma correlation. BSS was chosen over raw ECE where applicable because ECE rewards always-hedging-to-50% strategies, while BSS properly penalizes uninformative confidence.

**Provenance:** All benchmark data is self-contained within the Kaggle notebooks. Handcrafted items draw from public-domain knowledge across STEM, humanities, and logic domains. No copyrighted datasets are used. Fictional domains (Zorblatt Chemistry, Kingdom of Trevalia, invented vocabulary) ensure that no prior training data can provide an advantage.

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
| Calibration | 0.521 | 0.079 | 0.250 | Claude Sonnet (0.63) | Ministral 3B (0.38) |
| FOK | 0.571 | 0.088 | 0.281 | GPT-OSS-120B (0.67) | Ministral 3B (0.39) |
| JOL | 0.376 | 0.113 | 0.300 | Llama 3.3 70B (0.50) | DeepSeek-R1 (0.20) |
| Error Detection | 0.871 | 0.088 | 0.308 | Claude Sonnet (0.97) | Ministral 3B (0.66) |
| Epistemic Humility | 0.795 | 0.209 | 0.721 | Llama 3.3 70B (0.92) | Ministral 3B (0.20) |
| Control | 0.495 | 0.210 | 0.490 | Claude Opus (0.69) | Qwen3 Next 80B (0.20) |
| Canary | 0.546 | 0.266 | 0.875 | Claude Sonnet (0.87) | Ministral 3B (0.00) |
| Epistemic Revision | 0.794 | 0.108 | 0.330 | Claude Opus (0.96) | Ministral 3B (0.63) |
| Learning Monitoring | 0.814 | 0.088 | 0.277 | Qwen3 Next 80B (0.90) | Ministral 3B (0.62) |

**Insight 1 — Three-tier metacognition pattern.** Across all 10 models, scores cluster into three tiers: *external monitoring* (canary, epistemic humility, error detection; mean 0.74), *self-monitoring* (epistemic revision, control, learning monitoring; mean 0.70), and *prospective self-assessment* (FOK, JOL, calibration; mean 0.49). The 1.5:1 dissociation between external and prospective metacognition replicates across model families and scales, suggesting that evaluating external information is fundamentally easier than monitoring one's own future performance.

**Insight 2 — Universal overconfidence despite moderate calibration spread.** All 10 models achieve non-trivial calibration scores (range 0.38–0.63), but the tight spread (std = 0.079) indicates this is the hardest benchmark to discriminate on. All models report mean confidence of 94–99% across difficulty levels, confirming Chhikara et al. (2025) on systematic overconfidence. Claude Sonnet 4.6 leads (0.63) by modulating confidence most effectively (std = 10.1 across items), while Ministral 3B (0.38) reports near-constant high confidence. The benchmark's composite scoring — 50% extreme-item accuracy, 25% BSS, 25% uncertainty awareness — rewards models that can identify *which specific items* are hard, not just overall accuracy.

**Insight 3 — Strong discriminatory power.** Average cross-model standard deviation = 0.139 across 9 benchmarks (range 0.079–0.266). Canary (std = 0.266), control (std = 0.210), and epistemic humility (std = 0.209) are the strongest discriminators, while calibration (std = 0.079) shows the least spread. The suite produces a meaningful gradient from Ministral 3B (3B parameters, weakest overall) through mid-tier models (Nova Pro, Llama 4 Maverick) to frontier models (Claude Sonnet, Qwen3), with scale amplifying Tier 1 (external monitoring) performance but not Tier 3 (prospective self-assessment).

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
