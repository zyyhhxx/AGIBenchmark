# Metacognition Benchmark Suite — Design Document

## Overview
Three benchmarks testing distinct metacognitive abilities, grounded in the Nelson & Narens (1990) framework.

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

## Implementation Plan
Each benchmark implemented as a kaggle-benchmarks task using the `@kbench.task` decorator.
Tasks return `tuple[float, float]` (score, confidence_interval) or `float` for leaderboard.
All use `kbench.llm` as the default model placeholder for cross-model comparison.
