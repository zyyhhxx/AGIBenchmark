# Learning Benchmark Suite — Design Document

## Overview
Benchmarks testing genuine in-context learning ability, grounded in educational
psychology and learning science. Focus on learning curves, transfer, and interference.

## Benchmark 1: Novel Rule System Learning Curves

### Cognitive science basis
Learning curves (Bryan & Harter, 1897; Newell & Rosenbloom, 1981) describe how
performance improves with practice. Genuine learning shows characteristic curves:
initial rapid improvement, then deceleration (power law of practice).

### Design
1. Present a novel symbolic rule system (invented language, game rules, etc.)
2. Give the model N training examples in sequence
3. After every k examples, test on held-out problems
4. Plot accuracy vs. number of training examples seen
5. Measure: Does the model show a learning curve? How steep? Does it plateau?

### Metrics
- **Learning rate**: Slope of accuracy vs. examples (early phase)
- **Asymptotic performance**: Final accuracy level
- **Sample efficiency**: Examples needed to reach 80% accuracy
- **Curve shape**: Does it match power law? (genuine learning pattern)

### Key innovation
Rule systems are procedurally generated with controlled complexity. Cannot be
in training data. Tests whether the model genuinely learns from examples.

## Benchmark 2: Near vs. Far Transfer

### Cognitive science basis
Transfer of learning (Thorndike & Woodworth, 1901; Barnett & Ceci, 2002):
- Near transfer: Apply learned rules to similar problems
- Far transfer: Apply learned principles to structurally different domains

### Design
1. Train model on a rule system with 10 examples
2. Test on three conditions:
   a. **Identical**: Same problem type, different values
   b. **Near transfer**: Same rule structure, different surface features
   c. **Far transfer**: Same underlying principle, completely different domain
3. Measure accuracy drop-off across transfer distance

### Metrics
- Transfer ratio: accuracy(far) / accuracy(near)
- Transfer gradient: slope of accuracy vs. transfer distance

## Benchmark 3: Proactive and Retroactive Interference

### Cognitive science basis
When learning multiple things:
- Proactive interference: old learning hurts new learning
- Retroactive interference: new learning hurts recall of old learning

### Design
1. Teach rule system A → test A
2. Teach rule system B (similar to A) → test B, then re-test A
3. Compare: test A accuracy before vs. after learning B (retroactive)
4. Compare: learning rate of B vs. A (proactive)

### Metrics
- Retroactive interference index: accuracy(A_before) - accuracy(A_after)
- Proactive interference index: learning_rate(B) - learning_rate(A)

## Implementation Plan
Each benchmark uses `@kbench.task` decorator. Rule systems are generated
algorithmically with controlled difficulty parameters.
