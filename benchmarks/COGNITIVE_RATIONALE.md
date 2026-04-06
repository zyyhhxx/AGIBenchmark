# Cognitive Science Rationale — AGI Benchmark Suite

## Metacognition Track

### Theoretical Framework
Our metacognition benchmarks are grounded in the **Nelson & Narens (1990) metamemory monitoring framework**, which distinguishes:

- **Object-level**: Actual cognitive processes (answering questions, solving problems)
- **Meta-level**: Model of one's own cognitive state (confidence, awareness of knowledge limits)
- **Monitoring**: Information flow from object-level to meta-level ("How well do I know this?")
- **Control**: Information flow from meta-level to object-level ("Study this more")

### Benchmark 1: Retrospective Confidence Calibration (`task_calibration.py`)

**Construct measured**: Post-answer confidence calibration (Retrospective Confidence, RC)

**Cognitive science basis**: Metacognitive monitoring is operationalized as the correspondence between stated confidence and actual accuracy. Well-calibrated agents should report 80% confidence when they're correct ~80% of the time.

**Key references**:
- Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1982). Calibration of probabilities.
- Nelson & Narens (1990). Retrospective confidence as a monitoring judgment.

**Metric — ECE (Expected Calibration Error)**: Standard in both calibration literature and ML. Score = 1 - ECE, where human baseline ECE ≈ 0.10–0.20.

**Why this matters for AGI**: A system that cannot accurately assess its own certainty is fundamentally limited in safety-critical deployment. Calibration is necessary (though not sufficient) for trustworthy AI.

---

### Benchmark 2: Feeling-of-Knowing (`task_fok.py`)

**Construct measured**: Prospective metacognitive monitoring (FOK judgment)

**Cognitive science basis**: Hart (1965) showed that after failing to recall an answer, humans can predict their likelihood of recognizing it if given options. This "feeling of knowing" reflects access to partial information traces without complete retrieval — a form of metacognitive monitoring that is theoretically distinct from simply knowing the answer.

**Key innovation — Two-phase protocol**: 
1. Model rates confidence it CAN answer (Phase 1) 
2. Model actually answers (Phase 2, separate context)

This separation prevents post-hoc rationalization. If confidence were elicited alongside the answer, the model could simply assess answer quality rather than genuinely monitoring its knowledge state.

**Key references**:
- Hart, J. T. (1965). Memory and the feeling-of-knowing experience.
- Nelson, T. O. (1984). A comparison of current measures of the accuracy of FOK.
- Metcalfe, J. (1986). Premonitions of insight predict impending error.

**Metrics**:
- **Gamma correlation** (Goodman-Kruskal γ): Standard metamemory metric measuring ordinal association between confidence and accuracy. Human FOK γ ≈ 0.25–0.55.
- **ECE**: Absolute calibration accuracy.
- **AUC**: Discrimination — can the model separate things it knows from things it doesn't?

**Why this matters for AGI**: FOK-like ability is prerequisite for knowing when to seek help, when to verify, and when to express uncertainty to users. An AGI that cannot assess its own knowledge state before acting is dangerous.

---

### Benchmark 3: Judgment-of-Learning (`task_jol.py`)

**Construct measured**: Predictive monitoring of in-context learning (JOL)

**Cognitive science basis**: After studying new material, humans can predict how well they'll remember it (Arbuckle & Cuddy, 1969). This judgment drives study allocation — items judged as poorly learned get more study time.

**Key innovation — Novel stimuli**: All word-definition pairs and rule systems are invented. They cannot appear in any training corpus, forcing genuine in-context learning assessment rather than recognition of familiar material.

**Key references**:
- Arbuckle, T. Y., & Cuddy, L. L. (1969). Discrimination of item strength at time of presentation.
- Nelson, T. O., & Dunlosky, J. (1991). When people's judgments of learning (JOLs) are extremely accurate.
- Koriat, A. (1997). Monitoring one's own knowledge during study: A cue-utilization approach to JOLs.

**Study-Distract-Test paradigm**: Distractor questions between study and test create temporal distance, preventing simple echo effects and testing whether the model has truly encoded the associations.

---

### Benchmark 4: Error Detection (`task_error_detection.py`)

**Construct measured**: Metacognitive monitoring of reasoning processes

**Cognitive science basis**: Error monitoring is a key metacognitive function (Yeung & Summerfield, 2012). Detecting errors in reasoning chains requires:
1. Understanding the correct procedure
2. Tracking the actual procedure
3. Comparing the two (monitoring)

**Key references**:
- Yeung, N., & Summerfield, C. (2012). Metacognition in human decision-making.
- Rabbitt, P. (1966). Error correction time without external error signals.

**Design features**:
- Balanced mix of correct and incorrect chains (prevents response bias)
- Errors vary in type: arithmetic, logical fallacy, conceptual
- Some errors produce coincidentally correct answers (tests deep monitoring)
- Confidence ratings enable meta-d' analysis (metacognitive efficiency)

---

## Learning Track

### Theoretical Framework
Our learning benchmarks draw from **cognitive learning theory** and **educational psychology**, focusing on measurable learning phenomena that any genuine learning system should exhibit.

### Benchmark 5: Learning Curves (`task_learning_curves.py`)

**Construct measured**: Sample efficiency and learning dynamics

**Cognitive science basis**: The **power law of practice** (Newell & Rosenbloom, 1981) describes how performance improves with experience. Genuine learning shows characteristic curves: rapid initial improvement followed by deceleration.

**Key references**:
- Bryan, W. L., & Harter, N. (1897). Studies in the physiology and psychology of the telegraphic language.
- Newell, A., & Rosenbloom, P. S. (1981). Mechanisms of skill acquisition and the law of practice.
- Anderson, J. R. (1982). Acquisition of cognitive skill.

**Design**: Incrementally provide training examples (0, 2, 4, 8, 12) for procedurally generated rule systems and measure accuracy at each checkpoint. The curve shape reveals learning dynamics.

**Why novel rule systems?**: All systems are algorithmically generated with controlled complexity. They cannot be in training data, ensuring we measure genuine in-context learning rather than retrieval of memorized patterns.

### Benchmark 6: Near vs. Far Transfer (`task_transfer.py`)

**Construct measured**: Generalization ability across similarity distances

**Cognitive science basis**: Thorndike & Woodworth (1901) established that transfer depends on shared elements between learning and test contexts. Barnett & Ceci (2002) proposed a taxonomy of transfer distances.

**Key references**:
- Thorndike, E. L., & Woodworth, R. S. (1901). The influence of improvement in one mental function upon the efficiency of other functions.
- Barnett, S. M., & Ceci, S. J. (2002). When and where do we apply what we learn?

**Design**: Train on one rule system, then test at three transfer distances:
- **Identical**: Same system, new items (baseline)
- **Near**: Same type, different specifics
- **Far**: Different domain, analogous structure

### Benchmark 7: Proactive & Retroactive Interference (`task_interference.py`)

**Construct measured**: Resistance to catastrophic forgetting and interference

**Cognitive science basis**: Learning similar material can impair retention (Underwood, 1957; Postman, 1961). This is a fundamental phenomenon in human memory that constrains learning.

**Key references**:
- Underwood, B. J. (1957). Interference and forgetting.
- Anderson, M. C. (2003). Rethinking interference theory.

---

## Cross-Cutting Design Principles

1. **Contamination resistance**: All dynamic stimuli are procedurally generated and cannot appear in training data
2. **Cognitive validity**: Each benchmark maps to established constructs from cognitive psychology
3. **Multiple metrics**: No single number captures metacognition — we use gamma, ECE, AUC, d' where appropriate
4. **Human baselines**: Where possible, we reference human performance ranges from the literature
5. **Shortcut resistance**: Two-phase protocols, novel stimuli, and balanced designs prevent gaming

## Human Performance Reference Ranges

| Benchmark | Metric | Human Range | Source |
|-----------|--------|-------------|--------|
| Calibration | ECE | 0.10–0.20 | Lichtenstein et al. (1982) |
| FOK | Gamma | 0.25–0.55 | Nelson (1984) |
| JOL | Gamma | 0.40–0.90 | Nelson & Dunlosky (1991) |
| Error Detection | d' | 1.5–3.0 | Yeung & Summerfield (2012) |
| Learning Curves | Power law exponent | 0.3–0.5 | Newell & Rosenbloom (1981) |
