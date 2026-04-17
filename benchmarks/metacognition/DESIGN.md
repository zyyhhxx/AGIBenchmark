# Metacognition Benchmark Suite — Design Document

## Overview
Seven benchmarks (plus sub-metric variants) testing distinct metacognitive abilities, grounded in the Nelson & Narens (1990) framework of metacognitive monitoring and control.

## Benchmark 1: Feeling-of-Knowing (FOK)

### Cognitive science basis
After failing to recall information, humans can predict their likelihood of recognizing it later (Hart, 1965; Nelson & Narens, 1990). This "feeling of knowing" reflects genuine access to partial memory traces.

### Design
1. Present model with questions spanning diverse domains and difficulties
2. **Phase 1 — FOK judgment**: Ask model to rate confidence (0-100) that it can answer correctly, WITHOUT answering yet
3. **Phase 2 — Answer**: Ask model to answer the question
4. **Scoring**: Measure calibration between FOK ratings and actual correctness

### Metrics
- **Gamma correlation**: Goodman-Kruskal gamma between FOK ratings and accuracy (standard in metamemory research)
- **ECE (Expected Calibration Error)**: Binned confidence-accuracy deviation
- **Resolution**: Can the model discriminate between items it knows vs doesn't?
- **Discrimination index**: AUC of FOK ratings predicting correct vs incorrect

### Shortcut resistance
- Questions are procedurally varied — can't memorize FOK patterns from training
- Mix of factual, reasoning, and novel inference questions
- Some questions have no correct answer (tests whether model can recognize unknowable questions)

## Benchmark 2: Judgment-of-Learning (JOL) Calibration

### Cognitive science basis
After studying material, humans can predict how well they'll remember it later (Arbuckle & Cuddy, 1969). Accurate JOLs are critical for effective learning regulation.

### Design
1. **Study phase**: Present model with novel associations (e.g., invented word-definition pairs, novel rule systems)
2. **JOL phase**: For each item, ask "How confident are you (0-100) that you could recall this if asked later in this conversation?"
3. **Distractor phase**: Interpose unrelated conversation turns to create temporal distance
4. **Test phase**: Test recall of the studied items
5. **Scoring**: Calibration between JOL ratings and actual recall accuracy

### Key innovation
Uses **novel stimuli** (invented associations) that cannot be in training data, forcing genuine in-context learning assessment.

### Metrics
- Gamma correlation between JOLs and recall
- Calibration curve slope and intercept
- Over/underconfidence bias

## Benchmark 3: Error Detection (Metacognitive Monitoring of Reasoning)

### Cognitive science basis
Metacognitive monitoring includes the ability to detect errors in one's own reasoning (Yeung & Summerfield, 2012). This is critical for self-correction.

### Design
1. Model generates step-by-step solutions to reasoning problems
2. Some solutions are then **corrupted** (specific reasoning steps altered to introduce errors)
3. Model must review reasoning chains and:
   a. Identify whether each chain contains an error (binary)
   b. Localize the error (which step)
   c. Rate confidence in error judgment (0-100)
4. Control condition: model reviews its OWN prior reasoning (not corrupted) — tests genuine self-monitoring

### Metrics
- Error detection accuracy (F1)
- Error localization accuracy
- Metacognitive sensitivity (meta-d') for error detection confidence
- Self vs. other monitoring comparison

## Benchmark 4: Retrospective Confidence Calibration

### Cognitive science basis
Retro­spective confidence — rating confidence *after* answering — is the most common paradigm in metacognition research (Nelson & Narens, 1990). Well-calibrated agents should be right ~80 % of the time when they say 80 % confident.

### Design
1. Present diverse questions across domains and difficulty levels
2. Model answers AND rates confidence (0-100) in the same turn
3. Bin answers by confidence level
4. Compute Expected Calibration Error (ECE) = weighted |accuracy_bin − confidence_bin|

### Metrics
- **ECE** (primary): Lower is better; score = 1 − ECE
- **Gamma correlation**: Rank-order relationship between confidence and accuracy
- Human baseline ECE: 0.10–0.20

---

## Benchmark 5: Metacognitive Monitoring During Learning

### Cognitive science basis
Good learners monitor their own learning accurately (Dunlosky & Nelson, 1992; Zimmerman, 2000). Poor learners overestimate their understanding (Dunning-Kruger adjacent).

### Design
1. Present a novel rule system one rule at a time
2. After each new rule, test application AND ask self-assessment ("How well do you understand so far?", 0-100)
3. Compute tracking accuracy: does self-assessment track the actual learning curve?

### Metrics
- Learning accuracy (how well the rules are applied)
- Monitoring calibration (correlation between self-assessment and actual performance)
- Combined composite score

### Key innovation
Measures metacognition *during* learning rather than in isolation, capturing the self-regulated learning cycle.

---

## Benchmark 6: Metacognitive Control (Strategic Re-Reading)

### Cognitive science basis
Metacognitive *control* is the regulation of cognition based on monitoring output (Nelson & Narens, 1990). The allocation-of-study-time paradigm (Son & Metcalfe, 2000) tests whether learners strategically distribute study effort.

### Design
1. Present a 10-section passage on an unfamiliar topic
2. Present 5 questions (each maps to 1–2 relevant sections)
3. Model chooses exactly 3 sections to "re-read" (limited study budget)
4. Model answers the 5 questions

### Metrics
- **Selection relevance**: proportion of chosen sections relevant to questions
- **Answer accuracy**: proportion correct
- **Strategic gain**: accuracy on re-read-relevant questions vs. non-re-read questions

### Shortcut resistance
Two distinct passage topics. Questions require specific section knowledge, not general gist.

---

## Benchmark 7: Epistemic Revision (Belief Updating)

### Cognitive science basis
Rational agents must revise beliefs when confronted with contradicting evidence (Gärdenfors, 1988; AGM postulates). Cognitive flexibility (Miyake & Friedman, 2012) is the ability to adapt mental representations.

### Design
1. Teach 10 rules in 2 novel systems ("Zorblatt Chemistry" and "Nexari Ecology") with 3 examples each
2. Test comprehension (10 verification questions)
3. Present 3 contradicting observations
4. Model must: (a) identify violated rules, (b) propose revised rules consistent with all evidence
5. Test with 10 new questions that differentiate original vs. revised rules

### Metrics
- Violation detection accuracy
- Rule revision quality
- Transfer accuracy under revised rules
- Perseveration rate (sticking with original rules despite revision)

### Key innovation
Tests belief *revision* rather than just accumulation — a critical component of metacognitive regulation.

---

## Sub-Metric Benchmarks

Three additional notebooks break out fine-grained sub-metrics for leaderboard visibility:
- **FOK Sub-metrics**: fok_gamma, fok_ece, fok_resolution, fok_discrimination
- **JOL Sub-metrics**: jol_gamma, jol_ece, jol_recall_accuracy
- **Error Detection Sub-metrics**: error_f1, error_localization, error_ece, error_gamma

---

## Benchmark 8: Epistemic Humility

### Cognitive science basis
Epistemic humility — recognizing the limits of one's own knowledge (Whitcomb et al., 2017). Related to calibration under ignorance (Fischhoff et al., 1977) and the Dunning-Kruger effect. Distinct from FOK/JOL in that it tests outright refusal vs confabulation on genuinely unanswerable questions.

### Design
1. Present mix of answerable (10) and genuinely unanswerable (14) questions
2. Unanswerable categories: future events, fabricated entities, underspecified, paradoxical, private info, subjective
3. Model must classify each as answerable or not, provide answer or explanation of why not
4. Answerable questions include obscure-but-real items to test against over-refusal

### Metrics
- **Unanswerable detection rate**: Sensitivity to genuinely unanswerable questions
- **Confabulation rate**: Fraction of unanswerable questions answered with high confidence
- **False refusal rate**: Fraction of answerable questions incorrectly refused
- **Explanation quality**: How well the model explains WHY it cannot answer

### Score formula
`0.35 * detection + 0.25 * (1 - confabulation) + 0.20 * (1 - false_refusal) + 0.20 * explanation_quality`

### Files
- `task_epistemic_humility.py`

---

## Implementation Plan
Each benchmark implemented as a kaggle-benchmarks task using the `@kbench.task` decorator.
Tasks return `float` score in [0, 1] for leaderboard.
All use `kbench.llm` as the default model placeholder for cross-model comparison.
11 total Kaggle notebooks for this track (8 benchmarks + 3 sub-metric notebooks).
