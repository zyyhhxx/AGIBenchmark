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

## Benchmark 4: Attention to Instruction Updates

### Cognitive science basis
Task-switching paradigm (Monsell, 2003): when task instructions change mid-sequence,
there is a measurable switch cost reflecting cognitive flexibility. Perseveration
(continued application of now-invalid rules) is a hallmark of impaired executive attention.

### Design
1. Present initial classification instructions (e.g., categorise words by semantic category)
2. Model processes items under those instructions
3. Mid-sequence, instructions update subtly (woven into the stream, not a hard break)
4. Some trials have NO switch (catch trials) to test false alarm rate
5. Measure: pre-switch accuracy, post-switch accuracy, adaptation speed, perseveration rate

### Metrics
- Pre-switch accuracy (baseline)
- Post-switch accuracy (adaptation)
- Adaptation speed (trials to recover)
- Perseveration rate (applying old rules after switch)
- Catch trial accuracy (no false switches)

### Shortcut resistance
- Instructions are embedded in a continuous stream
- Updates are subtle — not "STOP! New rules!" but woven into the sequence
- Catch trials with no switch test for false positives
