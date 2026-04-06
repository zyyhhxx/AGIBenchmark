# Attention Benchmark Suite — Design Document

## Overview
Benchmarks testing attention mechanisms in LLMs, grounded in cognitive
psychology models of attention. Focus on selective, sustained, and divided
attention, plus attentional control.

## Benchmark 1: Selective Attention (Stroop Analogue)

### Cognitive science basis
The Stroop effect (Stroop, 1935) demonstrates that irrelevant information
can interfere with processing relevant information. Selective attention
is the ability to focus on relevant stimuli while ignoring distractors.

### Design
1. Present model with instructions to follow specific rules
2. Include conflicting/misleading information alongside the task
3. Measure: Can the model attend to relevant info and ignore distractors?

### Conditions
a. **Congruent**: Relevant and irrelevant info align → easy
b. **Incongruent**: Relevant and irrelevant info conflict → hard
c. **Neutral**: No conflicting info → baseline

### Metrics
- Stroop interference score: accuracy(congruent) - accuracy(incongruent)
- Response accuracy across conditions
- Interference resistance ratio

## Benchmark 2: Sustained Attention (Vigilance)

### Cognitive science basis
Sustained attention/vigilance decrement (Mackworth, 1948): Performance
on monotonous monitoring tasks degrades over time.

### Design
1. Present a long sequence of items (100+ tokens)
2. Model must monitor for specific targets embedded in noise
3. Targets become rarer as sequence progresses
4. Measure: Does accuracy drop for targets late in the sequence?

### Metrics
- Detection accuracy across sequence positions (early vs. middle vs. late)
- Vigilance decrement: accuracy drop from first to last third
- False alarm rate

## Benchmark 3: Divided Attention (Dual-Task)

### Cognitive science basis
Humans struggle to perform two attention-demanding tasks simultaneously
(Pashler, 1994). Dual-task costs reveal attentional capacity limits.

### Design
1. Single task: Perform task A alone
2. Single task: Perform task B alone
3. Dual task: Perform both A and B simultaneously (interleaved in prompt)
4. Measure: Performance drop from single to dual task

### Metrics
- Dual-task cost: single_accuracy - dual_accuracy
- Cost asymmetry: which task suffers more?
