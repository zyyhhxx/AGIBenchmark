# Cognitive Abilities Benchmark Suite — Methodology & Writeup

## Problem Statement

Current AI benchmarks overwhelmingly test **what** models know, not **how** they learn and reason. A model that scores 95% on trivia but can't assess its own certainty, learn from novel examples, or detect errors in its own reasoning is missing fundamental cognitive abilities. We address this gap with a benchmark suite grounded in cognitive science that measures metacognition and learning — two abilities central to genuine intelligence.

### Why Metacognition and Learning?

**Metacognition** (thinking about thinking) is what separates an expert from a novice. Experts don't just know more — they know what they know and don't know. Nelson & Narens (1990) identified four key monitoring judgments:
- Feeling-of-Knowing (FOK): Can I answer this?
- Judgment-of-Learning (JOL): Will I remember this later?
- Retrospective Confidence: Was my answer right?
- Error Detection: Did my reasoning contain mistakes?

**Learning** is the ability to acquire new knowledge from experience. We measure this via:
- Learning curves (Bryan & Harter, 1897): How does performance improve with practice?
- Transfer (Thorndike & Woodworth, 1901): Can learned skills generalize?
- Interference (Underwood, 1957): How does competing knowledge interact?
- Curriculum sensitivity: Does example ordering affect learning?

## Benchmark Suite Architecture

### Metacognition Track (4 benchmarks + 1 cross-domain)

| Benchmark | Construct | Protocol | Primary Metric |
|-----------|-----------|----------|----------------|
| `metacog_calibration` | Retrospective Confidence | Answer + confidence | 1 - ECE |
| `metacog_fok` | Feeling-of-Knowing | Confidence BEFORE answering | γ correlation |
| `metacog_jol` | Judgment-of-Learning | Study → JOL → Distract → Test | γ correlation |
| `metacog_error_detection` | Error Monitoring | Review reasoning chains | F1 + localization |
| `metacog_learning_monitoring` | Monitoring During Learning | Incremental learning + self-assessment | γ (self-assessment vs actual) |

### Learning Track (4 benchmarks)

| Benchmark | Construct | Protocol | Primary Metric |
|-----------|-----------|----------|----------------|
| `learning_curves` | Sample Efficiency | Incremental examples → test | Curve shape |
| `learning_transfer` | Generalization | Train A → test A/near/far | Transfer gradient |
| `learning_interference` | Memory Interaction | Learn A, learn B, retest A | Interference index |
| `learning_curriculum` | Curriculum Sensitivity | Same content, different orderings | Ordering effect |

### Attention Track (3 benchmarks)

| Benchmark | Construct | Protocol | Primary Metric |
|-----------|-----------|----------|----------------|
| `attention_selective` | Selective Attention | Stroop-analogue interference | Interference score |
| `attention_vigilance` | Sustained Attention | Long-sequence target detection | Vigilance decrement |
| `attention_divided` | Divided Attention | Single vs dual-task cost | Dual-task cost |

## Task & Benchmark Construction

### Key Design Principles

1. **Two-phase protocols** (metacognition): Separate confidence elicitation from answer generation. This is critical — it prevents post-hoc rationalization and tests genuine metacognitive monitoring.

2. **Novel stimuli** (learning): All rule systems are procedurally generated. They cannot appear in any training corpus. This forces genuine in-context learning.

3. **Multiple metrics**: Each benchmark reports several metrics (γ, ECE, AUC, d') because no single number captures metacognitive quality. Composite scores are used for leaderboard placement.

4. **Controlled difficulty**: Questions/stimuli span easy to hard, creating the range necessary to measure monitoring resolution.

5. **Human baselines from literature**: We reference published human performance ranges for each metric.

### Shortcut Resistance

- **Data contamination**: Novel stimuli (invented words, generated rules) eliminate memorization
- **Response bias**: Balanced correct/incorrect chains in error detection; unanswerable questions in FOK
- **Post-hoc rationalization**: Two-phase FOK protocol separates confidence from answer
- **Ceiling/floor effects**: Deliberately varied difficulty levels

## Dataset

### Metacognition Data

- **FOK Questions** (40 items): 10 retrievable, 10 boundary, 10 obscure, 5 reasoning, 5 unanswerable
- **Calibration Questions** (40 items): 10 easy, 15 medium, 15 hard across 12+ domains
- **Error Detection Chains** (17 items): 10 correct, 7 with errors (arithmetic, logic, conceptual)
- **JOL Stimuli**: 15 invented word-definition pairs (3 difficulty × 5 each), 2 novel rule systems

### Learning Data

- **Rule Systems**: 6 systems for learning curves (2 types × 3 difficulties), plus systems for transfer, interference, and curriculum tests
- **System types**: Symbol transformation (pattern matching) and number systems (computation)
- **Generated with seeds**: Reproducible across runs

All data is included inline in the benchmark code for Kaggle notebook self-containment.

## Technical Details

### Implementation

- Built on `kaggle-benchmarks` SDK v0.3.0
- Each benchmark is a `@kbench.task` returning a float score (0-1)
- Uses `kbench.llm` for cross-model comparison
- Structured output via `@dataclass` schemas with JSON fallback parsing
- Separate `kbench.chats.new()` contexts for each probe (prevents information leakage)

### Metrics Implementation

- **Gamma correlation**: Goodman-Kruskal γ (standard metamemory metric)
- **ECE**: Expected Calibration Error with configurable bins
- **AUC**: Empirical ROC area under curve
- **d'**: Signal detection theory sensitivity
- **Power law fitting**: Log-linear regression for learning curves

### Composite Scoring

Each benchmark's composite score weights multiple metrics to capture different aspects of the cognitive ability:

```
metacog_fok:        0.40 × γ_norm + 0.30 × (1-ECE) + 0.30 × AUC
metacog_jol:        0.40 × γ_norm + 0.30 × (1-ECE) + 0.30 × recall_rate
metacog_error:      0.35 × F1 + 0.25 × localization + 0.20 × (1-ECE) + 0.20 × γ_norm
learning_curves:    0.30 × asymptotic + 0.30 × learning_rate + 0.20 × efficiency + 0.20 × curve_quality
```

## Results, Insights, and Conclusions

*(To be populated after running on frontier models)*

### Attention Track

Our attention benchmarks are grounded in foundational attention research:

**Selective Attention (Stroop Analogue)**: Based on Stroop (1935), we test whether models can follow precise instructions while ignoring conflicting information. The Stroop effect is one of the most replicated findings in cognitive psychology — even simple color-word conflicts cause significant interference in humans. Our analogue uses instruction-following with misleading context.

**Sustained Attention (Vigilance)**: Based on Mackworth's (1948) clock test, we present long sequences where the model must detect rare targets. Target frequency decreases across the sequence, testing whether models show the classic vigilance decrement (10-30% accuracy drop over time).

**Divided Attention (Dual-Task)**: Based on Pashler (1994) and Kahneman (1973), we measure the cost of performing two cognitive tasks simultaneously. The dual-task cost reveals attentional capacity limitations.

### Expected Findings

Based on prior work (Cacioli, 2026; Dai, 2026):
- LLM M-ratios (metacognitive efficiency) typically 0.62–0.92
- Overconfidence bias expected (models typically overcalibrated)
- FOK two-phase protocol should show lower γ than retrospective confidence (harder task)
- Learning curves should show improvement but potentially different shapes than human power law
- Transfer gradient: near > far (matching human pattern, but magnitude may differ)

### Key Questions

1. Do models show genuine metacognitive monitoring, or just post-hoc calibration?
2. Is there a relationship between learning quality and metacognitive accuracy?
3. Do different model families show different metacognitive profiles?
4. Which models are most sample-efficient learners?

## References

- Anderson, J. R. (1982). Acquisition of cognitive skill. *Psychological Review*.
- Arbuckle, T. Y., & Cuddy, L. L. (1969). Discrimination of item strength at time of presentation. *JVLVB*.
- Barnett, S. M., & Ceci, S. J. (2002). When and where do we apply what we learn? *Psychological Bulletin*.
- Bengio, Y., Louradour, J., Collobert, R., & Weston, J. (2009). Curriculum learning. *ICML*.
- Bryan, W. L., & Harter, N. (1897). Studies in the physiology and psychology of the telegraphic language. *Psychological Review*.
- Dunlosky, J., & Nelson, T. O. (1992). Importance of the kind of cue for judgments of learning. *Memory & Cognition*.
- Fleming, S. M., & Lau, H. C. (2014). How to measure metacognition. *Frontiers in Human Neuroscience*.
- Hart, J. T. (1965). Memory and the feeling-of-knowing experience. *Journal of Educational Psychology*.
- Koriat, A. (1997). Monitoring one's own knowledge during study: A cue-utilization approach. *JEP: General*.
- Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1982). Calibration of probabilities. *Decision Making and Change*.
- Maniscalco, B., & Lau, H. (2012). A signal detection theoretic approach for estimating metacognitive sensitivity. *Consciousness and Cognition*.
- Nelson, T. O., & Narens, L. (1990). Metamemory: A theoretical framework and new findings. *Psychology of Learning and Motivation*.
- Nelson, T. O., & Dunlosky, J. (1991). When people's judgments of learning are extremely accurate. *JEP: Learning, Memory, and Cognition*.
- Newell, A., & Rosenbloom, P. S. (1981). Mechanisms of skill acquisition and the law of practice. *Cognitive Skills and Their Acquisition*.
- Rohrer, D., & Taylor, K. (2007). The shuffling of mathematics problems improves learning. *Instructional Science*.
- Thorndike, E. L., & Woodworth, R. S. (1901). The influence of improvement in one mental function upon the efficiency of other functions. *Psychological Review*.
- Underwood, B. J. (1957). Interference and forgetting. *Psychological Review*.
- Yeung, N., & Summerfield, C. (2012). Metacognition in human decision-making. *Philosophical Transactions B*.
- Zimmerman, B. J. (2000). Self-efficacy: An essential motive to learn. *Contemporary Educational Psychology*.
