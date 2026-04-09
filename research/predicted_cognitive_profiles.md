# Predicted Cognitive Profiles — Frontier Models

## Methodology
Predictions based on published benchmark results, architecture analysis, and cognitive science mapping.
Will be validated against actual CB platform results.

## Model Predictions

### GPT-4o (OpenAI)
- **Metacognition**: Medium-High. Known for reasonable calibration on factual questions (Kadavath et al. 2022 showed early GPT models had improving calibration). FOK gamma likely 0.4–0.6. JOL calibration moderate — tends toward overconfidence on hard items.
- **Learning**: Medium. Strong few-shot learning but learning curves may not follow clean power law due to in-context compression.
- **Attention**: High. Transformer attention mechanisms should handle selective attention well. Vigilance decrement unlikely (no fatigue). Divided attention may show dual-task cost due to context window competition.
- **Executive Functions**: Medium-High. WCST set-shifting should be good. CRT is the discriminator — may fall for intuitive traps despite chain-of-thought.
- **Social Cognition**: High. Strong ToM performance reported (Kosinski 2023, though debated). Pragmatic inference and sarcasm detection likely strong.
- **Predicted Weakness**: Epistemic humility (confabulation on unknowns), CRT intuitive traps.

### Claude 3.5 Sonnet (Anthropic)
- **Metacognition**: High. RLHF training with honesty emphasis may improve calibration. More likely to express uncertainty. FOK gamma predicted 0.5–0.7.
- **Learning**: Medium. Similar ICL capabilities to GPT-4o.
- **Attention**: High. Similar transformer architecture advantages.
- **Executive Functions**: Medium-High. Constitutional AI training may help with inhibitory control (resisting intuitive wrong answers).
- **Social Cognition**: High. Strong pragmatic understanding from RLHF.
- **Predicted Strength**: Epistemic humility — trained to acknowledge uncertainty.

### Gemini 1.5 Pro (Google)
- **Metacognition**: Medium. Calibration may differ due to different training approach.
- **Learning**: Medium-High. Long context window (1M tokens) may improve learning curve dynamics.
- **Attention**: High. Long-context training may help sustained attention tasks.
- **Executive Functions**: Medium.
- **Social Cognition**: Medium-High.
- **Predicted Strength**: Vigilance/sustained attention due to long-context training.

### DeepSeek-R1
- **Metacognition**: Medium-Low. Chain-of-thought reasoning may create overconfidence — explicit reasoning steps may not improve calibration and could amplify it.
- **Learning**: Medium. Strong reasoning but ICL dynamics may differ.
- **Attention**: Medium. May struggle with divided attention if reasoning chains are serial.
- **Executive Functions**: High. Explicit reasoning chain should help planning (Tower of London) and set-shifting.
- **Social Cognition**: Medium-Low. Reasoning-focused training may underweight social/pragmatic understanding.
- **Predicted Weakness**: Social cognition tasks requiring implicit understanding over explicit reasoning.

## Key Hypotheses to Test
1. **Calibration-reasoning tradeoff**: Models with explicit CoT (DeepSeek-R1) may show WORSE metacognitive calibration because they rationalize answers post-hoc.
2. **Honesty training → epistemic humility**: Models with constitutional AI / RLHF honesty emphasis (Claude) should score higher on epistemic humility.
3. **Context length → sustained attention**: Models trained on longer contexts (Gemini) should show less vigilance decrement.
4. **CRT as universal discriminator**: CRT performance should correlate poorly with standard benchmarks, revealing a new axis of model differentiation.
5. **Social cognition cluster**: False belief, pragmatic inference, and sarcasm should form a coherent cluster — models strong/weak on one should be strong/weak on all.

## Cross-Track Coherence Predictions
Based on Miyake et al. (2000) unity/diversity framework:
- Executive function tasks should show moderate intercorrelation (r ≈ 0.3–0.5)
- Metacognition and executive functions should correlate (both require monitoring)
- Social cognition may be relatively independent from other tracks
- Learning and attention should correlate (attention supports learning)
