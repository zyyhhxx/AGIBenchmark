# Kaggle Discussion Post Draft
*Post this to the competition discussion when CB submission is live.*

---

## 🧠 Cognitive Abilities Benchmark Suite — 29 Benchmarks Across All 5 Tracks

### tl;dr
We built 29 benchmarks grounded in cognitive science that test *how* models think, not *what* they know. Each benchmark maps to established psychology constructs — metacognitive monitoring (FOK, JOL), learning dynamics, attentional control, executive function, and social cognition.

### What makes this different?

**1. Tests process, not product.** Most benchmarks ask "Did the model get the right answer?" We ask "Does the model know when it's likely to be wrong?" Our metacognition track measures calibration, error detection, and epistemic humility.

**2. Contamination-resistant by design.** We use procedurally generated stimuli (arithmetic with random parameters, invented rule systems, logic puzzles) that can't appear in training data. Plus a canary system that detects data contamination in real-time.

**3. Grounded in 50+ years of cognitive science.** Every benchmark references named theoretical frameworks: Nelson & Narens (1990) for metamemory, Miyake et al. (2000) for executive functions, Hart (1965) for FOK. These aren't ad hoc tests — they're adaptations of paradigms validated on humans.

**4. Psychometric validation.** Cronbach's α ≥ 0.70 across all tested benchmarks (FOK achieves α = 0.95). Discriminant validity: within-track correlations (r = 0.37) are 4× higher than between-track (r = 0.09).

### Tracks at a glance

| Track | # Benchmarks | Headline Finding |
|-------|:---:|---|
| Metacognition | 9 | Models show systematic overconfidence on hard items |
| Learning | 4 | In-context learning follows power-law curves (like humans!) |
| Attention | 4 | Vigilance degrades over long sequences |
| Executive Functions | 5 | Strong planning but weak inhibition (CRT) |
| Social Cognition | 4 | Literal bias in pragmatic inference |

### Try it yourself
All 29 benchmarks are available as Kaggle notebooks. Run them against your favorite model and compare!

**Benchmark link:** [link to CB benchmark]

### Full writeup
See our submission overview notebook for the complete methodology, cognitive science rationale, and results analysis.

### References
Key papers: Hart (1965), Nelson & Narens (1990), Miyake et al. (2000), Frederick (2005), Kruger & Dunning (1999), Rajpurkar et al. (2018). Full bibliography in the submission.

---

*Feedback and upvotes appreciated! 🙏*
