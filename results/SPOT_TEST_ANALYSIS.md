# Spot Test Analysis — Gemini 2.5 Flash

**Date:** 2026-04-09  
**Model:** Gemini 2.5 Flash (free tier, ~20 requests/day)  
**Method:** Direct API calls with natural language prompting  

## Summary of Results

| # | Cognitive Ability | Test | Result | Implication |
|---|---|---|:---:|---|
| 1 | Response Inhibition (CRT) | Classic bat & ball | ✓ (3/3) | CoT enables System 2 override; need procedural variants to test |
| 2 | Selective Attention (Stroop) | Ink color identification | ✓ | Strong selective filtering |
| 3 | Theory of Mind (2nd order) | Green cupboard scenario | ✓ | Can track nested beliefs |
| 4 | Epistemic Humility | Fabricated substance | ✓ | Correctly expresses uncertainty |
| 5 | Epistemic Revision | Zorblatt Chemistry | ✓ (3/3) | Good belief updating |
| 6 | Working Memory (N-back) | 2-back, 5 items | ✓ (5/5) | Perfect on short sequence |
| 7 | **Calibration** | Pi digit confidence | **✗** | 100% confidence on unknowable — **overconfident** |
| 8 | **Pragmatic Inference** | Scalar implicature | **✗** | Literal "some" interpretation — **pragmatic blindness** |

## Key Cognitive Insights

### 1. Pragmatic Literal Bias (Social Cognition Gap)
When told "Some of the students passed the exam," Gemini interprets "some" **logically** (compatible with "all passed") rather than **pragmatically** (implying "not all passed").

**Why this matters:** In human communication, "some" almost always implies "not all" via Grice's maxim of quantity. Adults get this right ~95% of the time. This reveals a fundamental gap in social cognition — the model processes language logically but misses communicative intent.

**Our benchmark captures this:** The pragmatic inference benchmark has 25 items across 5 pragmatic types (scalar implicature, indirect requests, irony, understatement, relevance implicature), providing granular measurement of this gap.

### 2. Domain-Specific Calibration Failure (Metacognition Gap)
The model shows **asymmetric calibration**:
- ✓ Correctly says "I don't know" for fabricated substances (Zorblattium-7)
- ✗ Claims 100% confidence for the 47th digit of pi

**Hypothesis:** Models have a "knowability heuristic" — they assess confidence based on whether the question *seems* answerable (pi digits = math = knowable) rather than genuine metacognitive assessment. Our FOK benchmark with 81 items across 9 difficulty levels would quantify this precisely.

### 3. Strong Classical Reasoning, Weak Metacognitive Monitoring
The model excels at tasks requiring step-by-step reasoning:
- 3/3 CRT classic items (100% vs. human 30-48%)
- Perfect epistemic revision (3/3 downstream inferences)
- Perfect 2nd-order ToM

But fails at **self-monitoring** — knowing what it knows vs. what it doesn't. This pattern (strong performance + poor calibration) is exactly what our metacognition track is designed to measure.

### 4. Contamination Concerns
Classic CRT items (bat & ball, lily pads, machines) are widely known. The model's 100% accuracy likely reflects memorization, not genuine cognitive reflection. Our **procedurally generated CRT variants** with novel numbers and problem structures test whether the model truly engages System 2 or just pattern-matches familiar problems.

## Predicted Model Profiles

Based on these findings and the cognitive science literature:

| Model | Metacognition | Learning | Attention | Exec Func | Social Cog |
|-------|:---:|:---:|:---:|:---:|:---:|
| **Gemini 2.5 Flash** | ⬇️ 0.55 | ➡️ 0.70 | ⬆️ 0.85 | ⬆️ 0.75 | ⬇️ 0.60 |
| **GPT-4o (predicted)** | ➡️ 0.65 | ⬆️ 0.75 | ⬆️ 0.80 | ⬆️ 0.80 | ➡️ 0.70 |
| **Claude 3.5 Sonnet (predicted)** | ⬆️ 0.75 | ➡️ 0.70 | ➡️ 0.75 | ➡️ 0.70 | ⬆️ 0.75 |
| **DeepSeek-R1 (predicted)** | ⬇️ 0.45 | ⬆️ 0.80 | ➡️ 0.70 | ⬆️ 0.85 | ⬇️ 0.50 |

**Reasoning:**
- **Claude** should excel at metacognition and social cognition due to RLHF honesty training
- **DeepSeek-R1** should excel at executive functions (explicit reasoning) but struggle with metacognition (the "can't stop reasoning" hypothesis — DeepSeek-R1 shows a +0.534 calibration swing under adversarial context in CASK)
- **Gemini** shows strong attention/exec but weak metacognition (our spot test confirms overconfidence)

## Limitations
- Only ~20 requests available per model per day (free tier)
- Spot tests are not statistically powered — need full benchmark runs for reliable conclusions
- Single-item tests can't measure composite metrics like gamma, ECE, or AUC
- Need at minimum 3+ models for meaningful cognitive profiles
