# Nelson & Narens (1990) Metacognitive Monitoring Framework
## Research Summary for AGI Benchmark Design

### Citation
Nelson, T. O., & Narens, L. (1990). Metamemory: A theoretical framework and new findings.
*The Psychology of Learning and Motivation*, 26, 125–173. Academic Press.

---

## Core Architecture

The framework proposes a **two-level system** with information flow between levels:

```
┌─────────────────────────────────┐
│         META-LEVEL              │
│  (metacognitive knowledge)      │
│                                 │
│  Contains: model of object-level│
│  processes, states, and goals   │
└────────┬──────────┬─────────────┘
         │          │
    CONTROL     MONITORING
    (↓ flow)    (↑ flow)
         │          │
┌────────┴──────────┴─────────────┐
│        OBJECT-LEVEL             │
│  (cognition, memory, behavior)  │
│                                 │
│  Contains: actual cognitive     │
│  processes and representations  │
└─────────────────────────────────┘
```

- **Monitoring** = information flows UP from object-level to meta-level (e.g., "How well do I know this?")
- **Control** = information flows DOWN from meta-level to object-level (e.g., "Study this item more")

## Monitoring Judgments (Key for Benchmarking)

### 1. Ease-of-Learning (EOL) Judgments
- **When**: Before learning begins
- **What**: Predictions about how easy/hard items will be to learn
- **LLM analogue**: Given a task description, can the model predict how well it will perform?

### 2. Judgments of Learning (JOL)
- **When**: During or immediately after study
- **What**: Predictions about likelihood of recalling studied items on a future test
- **Key finding**: "Delayed JOLs" (made after a delay) are more accurate than immediate JOLs
- **LLM analogue**: After in-context learning, can the model predict which items it has truly learned?

### 3. Feeling-of-Knowing (FOK) Judgments
- **When**: After failed recall attempt
- **What**: Prediction of likelihood of recognizing the answer if given options
- **Key mechanism**: FOK does NOT directly access the unrecalled item — it monitors "recallable aspects related to that item, such as the item's acquisition history or partial/related recalled components" (the "non-magic hypothesis")
- **LLM analogue**: When a model fails to answer, can it accurately predict whether it would recognize the correct answer among alternatives?

### 4. Retrospective Confidence (RC) Judgments
- **When**: After answering
- **What**: Confidence that a given response is correct
- **LLM analogue**: Post-answer confidence calibration (already implemented in task_calibration.py)

## Control Processes

| Process | Description | LLM Analogue |
|---------|-------------|--------------|
| Selection of kind of processing | Choosing study strategies | Selecting reasoning approach |
| Item selection | Deciding what to study next | Prioritizing which subproblems to tackle |
| Termination of study | Deciding when enough studying has occurred | Knowing when to stop iterating |
| Selection of search strategy | Choosing retrieval strategies | Choosing between different solution approaches |
| Termination of search | Deciding to stop looking for an answer | Knowing when to give up / say "I don't know" |

## Key Metrics from the Literature

### Gamma Correlation (Goodman-Kruskal γ)
- Standard metric in metamemory research
- Measures ordinal association between confidence ratings and accuracy
- Range: -1 to +1 (higher = better metacognitive resolution)
- Human FOK gamma typically: 0.25–0.55
- Human JOL gamma typically: 0.40–0.90 (delayed JOLs higher)

### Calibration (absolute accuracy)
- How well average confidence matches average accuracy
- Measured via ECE (Expected Calibration Error) — lower is better
- Human ECE typically: 0.10–0.20

### Resolution (relative accuracy)
- Can the judge distinguish items they know from items they don't?
- Measured via AUC / discrimination index
- This is what meta-d' / M-ratio captures (from SDT framework)

### Meta-d' and M-ratio (Signal Detection Theory extension)
- **meta-d'**: The Type-1 d' value an ideal observer would need to produce the observed confidence × accuracy pattern
- **M-ratio = meta-d'/d'**: Metacognitive efficiency
  - M = 1: Confidence captures all available information (optimal)
  - M < 1: Metacognitive loss — confidence is noisier than evidence supports
  - M > 1: Confidence accesses information beyond what drives the Type-1 decision
- Recent work (Cacioli, 2026; Dai, 2026) applies this to LLMs with M-ratios of 0.62–0.92

## Implications for Benchmark Design

### What makes a GOOD metacognition benchmark:
1. **Separates monitoring from performance**: Don't just test if the model is right — test if it *knows* whether it's right
2. **Uses the FOK paradigm**: Two-phase protocol (judge first, answer second) prevents post-hoc rationalization
3. **Varies difficulty deliberately**: Need items the model WILL and WON'T know to measure discrimination
4. **Includes unanswerable items**: Tests whether the model can recognize the limits of knowledge itself
5. **Uses multiple metrics**: Gamma, ECE, and meta-d' capture different aspects of metacognitive quality

### What makes a POOR metacognition benchmark:
1. Only measuring calibration (ECE alone conflates monitoring with performance level)
2. Using only easy or only hard questions (no spread = no resolution measurement)
3. Allowing post-hoc confidence (must elicit FOK BEFORE the answer)
4. Using questions that are trivially in training data (no genuine uncertainty)

### Benchmark Suite Mapping to Framework:
| Benchmark | Nelson & Narens Construct | Phase |
|-----------|---------------------------|-------|
| task_calibration.py | Retrospective Confidence (RC) | After answering |
| FOK benchmark (next) | Feeling-of-Knowing (FOK) | Before answering |
| JOL benchmark | Judgment-of-Learning (JOL) | After in-context learning |
| Error detection | Metacognitive monitoring of reasoning | During/after processing |

---

## References for Further Reading
- Hart, J. T. (1965). Memory and the feeling-of-knowing experience. *Journal of Educational Psychology*, 56(4), 208.
- Maniscalco, B., & Lau, H. (2012). A signal detection theoretic approach for estimating metacognitive sensitivity from confidence ratings. *Consciousness and Cognition*, 21(1), 422–430.
- Fleming, S. M., & Lau, H. C. (2014). How to measure metacognition. *Frontiers in Human Neuroscience*, 8, 443.
- Cacioli (2026). Full parametric SDT framework for LLM confidence evaluation.
- Dai (2026). Meta-d' applied to LLMs using prompted verbal confidence scales. M-ratios: 0.62–0.92.
