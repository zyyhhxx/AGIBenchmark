# Kaggle Discussion Post Draft
*Post this to the competition discussion when CB submission is live.*

---

**Title:** 🧠 29 Cognitive Benchmarks Across All 5 Tracks — Testing How Models Think, Not What They Know

---

### tl;dr
We built **29 benchmarks grounded in 50+ years of cognitive science** that test *how* models think — not what they memorize. Each maps to an established psychology construct: metacognitive monitoring (FOK, JOL), in-context learning dynamics, attentional control, executive function, and social cognition. All benchmarks use **procedurally generated, contamination-resistant stimuli**.

---

### The Problem with Current Benchmarks

Most LLM benchmarks ask: *"Did the model get the right answer?"*

But cognitive science tells us intelligence isn't just about answers — it's about **knowing what you know**, **learning from experience**, **sustaining attention**, **planning ahead**, and **understanding other minds**. These are the abilities that separate genuine cognition from pattern matching.

Our suite asks harder questions:
- Does the model **know when it's likely to be wrong**? (Metacognition)
- Does its **learning curve follow the same power-law pattern as human learning**? (Learning)
- Does its **performance degrade on long sequences** the way human vigilance does? (Attention)
- Can it **inhibit intuitive but wrong answers**? (Executive Functions)
- Can it **infer what someone believes** even when that belief is false? (Social Cognition)

---

### What Makes This Different?

**1. Process over product.**
Most benchmarks measure outputs. We measure the *cognitive process*. Our metacognition track tests whether models have accurate self-models — can they predict their own performance? We use two-phase protocols (confidence rating → answer generation) that prevent post-hoc rationalization, a known confound in LLM calibration.

**2. Contamination-resistant by design.**
- Procedurally generated stimuli: arithmetic with random parameters, invented rule systems, novel logic puzzles — impossible to memorize from training data
- **Canary system**: 5 fabricated "facts" (fictional physical constants, prizes, treaties) embedded across benchmarks. If a model shows high confidence on canaries, something's wrong.
- Learning benchmarks use *invented* rule systems like "Zorblatt Chemistry" — not Wikipedia facts

**3. Grounded in established cognitive science.**
Every benchmark references named theoretical frameworks validated on humans:
- **Hart (1965)** — Feeling-of-Knowing: "I can't recall it, but I'd recognize it"
- **Nelson & Narens (1990)** — Metamemory monitoring and control
- **Miyake et al. (2000)** — Unity and diversity of executive functions
- **Frederick (2005)** — Cognitive Reflection Test: intuition vs. deliberation
- **Kruger & Dunning (1999)** — Calibration failures and overconfidence

These aren't ad hoc tests — they're careful adaptations of paradigms with decades of human data for comparison.

**4. Psychometric validation.**
We ran the full suite through reliability and validity analyses:
- **Reliability**: Cronbach's α ≥ 0.70 across all tested benchmarks (FOK achieves α = 0.95)
- **Discriminant validity**: Within-track correlations (r = 0.37) are **4× higher** than between-track (r = 0.09) — confirming the cognitive taxonomy is meaningful for LLMs, not just humans
- **Difficulty calibration**: ECE increases from 0.26 (easy) → 0.30 (hard) — models don't adequately downgrade confidence on harder problems

---

### Track Overview

| Track | # Benchmarks | What It Tests | Headline Finding |
|-------|:---:|---|---|
| **Metacognition** | 9 | Self-knowledge, calibration, error detection | Systematic overconfidence on hard items |
| **Learning** | 4 | In-context learning curves, transfer, interference | Learning follows power-law curves (like humans!) |
| **Attention** | 4 | Selective filtering, sustained focus, dual-task | Vigilance degrades over long sequences |
| **Executive Functions** | 5 | Planning, inhibition, set-shifting, working memory | Strong planning but weak inhibition on CRT |
| **Social Cognition** | 4 | Theory of mind, pragmatics, sarcasm, emotion | Literal bias in pragmatic inference |

---

### Spotlight: Three Benchmarks We're Most Excited About

**🔮 Feeling-of-Knowing (FOK)**
Inspired by Hart's (1965) classic paradigm. We ask models to rate their confidence *before* answering, using procedurally generated questions they couldn't have memorized. The gamma correlation between confidence and accuracy reveals whether the model has an accurate self-model. Humans typically achieve γ ≈ 0.3–0.5.

**🧪 Epistemic Revision**
We teach models an invented science ("Zorblatt Chemistry" — 10 rules) then present contradictory evidence for 3 rules. The benchmark measures: Can the model update its beliefs when evidence conflicts with what it just learned? Stubborn adherence = low score. Appropriate revision + transfer to novel problems = high score.

**🎭 Cognitive Reflection Test (CRT)**
Adapted from Frederick (2005). These are questions where the intuitive answer is wrong — you need to override System 1 with System 2 thinking. Famous example: "A bat and ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost?" (It's not $0.10.) Our version uses procedurally generated variants to defeat memorization.

---

### Technical Details

- Built on the **Kaggle Community Benchmarks SDK** (`@kbench.task`)
- All 29 benchmarks are self-contained Python notebooks with inline documentation
- Structured output schemas for reliable response parsing + fallback parsing
- All scores normalized to [0, 1] with clear cognitive interpretations
- Full source code, methodology docs, and cognitive rationale available

---

### Full Benchmark List

**Metacognition:** Feeling-of-Knowing · Judgment-of-Learning · Retrospective Calibration · Error Detection · Learning Monitoring · Metacognitive Control · Epistemic Revision · Epistemic Humility · Contamination Canary

**Learning:** Learning Curves · Near vs. Far Transfer · Proactive/Retroactive Interference · Curriculum Sensitivity

**Attention:** Selective Attention (Stroop-like) · Vigilance/Sustained · Divided Attention · Instruction Update

**Executive Functions:** Wisconsin Card Sorting · Tower of London · Task Switching · N-Back · Cognitive Reflection Test

**Social Cognition:** False-Belief Theory of Mind · Pragmatic Inference · Sarcasm Detection · Emotional Prosody

---

### Try It Yourself
All benchmarks are available as Kaggle notebooks. Run them against your favorite model and see how it scores!

**🔗 Benchmark link:** [link to CB benchmark]

See our **submission overview notebook** for the complete methodology, cognitive science rationale, and detailed analysis.

---

### Design Principles: What We Learned Building 29 Benchmarks

After building this suite, here are principles we believe make cognitive benchmarks robust:

1. **Separate signal from noise with control questions.** Our ToM benchmarks use reality/memory controls. If the model fails controls, we know it didn't understand the scenario — not that it lacks ToM.

2. **Use two-phase protocols.** Asking confidence and answers in the same prompt lets models adjust one based on the other. Separate chats prevent this confound.

3. **Design for the cognitive process, not the answer.** A model that scores 100% on our FOK benchmark doesn't just know answers — it knows *which* answers it knows. That's a fundamentally different measurement.

4. **Contamination resistance isn't optional.** Any benchmark using fixed text will be contaminated within months. Procedural generation is the only sustainable approach for cognitive evaluation.

5. **Validate psychometric properties.** Reliability (α) and discriminant validity aren't just academic checkboxes — they tell you whether your benchmark measures something real and distinct.

---

### References
Hart (1965) · Nelson & Narens (1990) · Miyake et al. (2000) · Frederick (2005) · Kruger & Dunning (1999) · Rajpurkar et al. (2018) · Fischhoff et al. (1977) · Dunlosky & Metcalfe (2009) · Barrett et al. (2019) · Scherer (1986) · Whitcomb et al. (2017) · Gross (2015). Full bibliography in the submission.

---

*Feedback, questions, and upvotes very welcome! We'd love to hear what cognitive abilities you think are most important for AGI. 🙏*
