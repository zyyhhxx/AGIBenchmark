### Can AI Systems Learn from Experience? A 4-Task Learning Benchmark Suite

### Team
Yiyang Zeng (Independent researcher)

### Problem Statement

Learning — the ability to acquire, retain, and transfer knowledge through experience — is perhaps the most fundamental cognitive faculty. Yet LLM evaluations almost exclusively test *what* models already know, not *how* they learn. Pre-trained models are tested on static knowledge; their ability to acquire new information within context, resist interference from competing knowledge, and transfer learned rules to novel situations remains largely unmeasured.

The learning sciences distinguish several key processes: *transfer* (applying learned rules to new domains; Thorndike, 1932), *interference* (competing information disrupting retention; Underwood, 1957), *curriculum effects* (ordering of material affecting acquisition; Ausubel, 1968), and *learning curves* (rate of improvement with exposure; Newell & Rosenbloom, 1981). These processes are well-characterized in human learners but poorly understood in LLMs operating in-context.

This benchmark suite asks: **Can frontier models acquire new knowledge in-context, resist interference, and transfer learning to novel domains?**

### Task & Benchmark Construction

We constructed 4 tasks grounded in learning science theory, each isolating a distinct learning process:

| Task | Construct | Protocol |
|------|-----------|----------|
| **Learning Transfer** | Far transfer / analogical reasoning | Learn a rule system in one domain → apply it to a structurally isomorphic but surface-dissimilar domain (Thorndike, 1932; Gentner, 1983) |
| **Learning Interference** | Proactive & retroactive interference | Learn multiple competing rule systems presented simultaneously; apply only the target system while ignoring distractors (Underwood, 1957) |
| **Learning Curriculum** | Curriculum sequencing effects | Learn the same material under different presentation orders; measures sensitivity to pedagogical structure (Ausubel, 1968) |
| **Learning Curves** | Acquisition rate | Track performance improvement across increasing exposure to a novel system; measures learning speed and asymptote (Newell & Rosenbloom, 1981) |

**Difficulty tiering:** Interference uses 3 tiers: easy (1 dissimilar distractor, weight 0.15), medium (1 similar distractor, weight 0.35), hard (2 similar distractors with interleaved examples, weight 0.50). Transfer tests near transfer (same domain structure) and far transfer (cross-domain mapping).

**Contamination resistance:** All rule systems are procedurally generated — invented symbol-to-output mappings, novel number systems, and synthetic grammars that cannot exist in training data. Seeds ensure reproducibility.

### Dataset

All items use procedurally generated rule systems with deterministic seeds. Per-task item counts: transfer (20 test items across 2 transfer distances), interference (30 items across 3 difficulty tiers), curriculum (24 items across 3 orderings), learning curves (40 items across 8 exposure levels).

**Scoring:** Transfer uses accuracy on novel-domain items. Interference composites 0.30 × control accuracy + 0.70 × interference accuracy, weighted by tier. Curriculum measures accuracy variance across orderings. Learning curves fit power-law improvement and extract learning rate parameters.

**Provenance:** All stimuli are synthetically generated rule systems. No real-world datasets or copyrighted educational materials are used.

### Technical Details

All tasks use the `kaggle-benchmarks` SDK with `@kbench.task` decorators. Key implementation choices:

- **Transfer:** Models learn a complete rule system (e.g., symbol→digit mapping) through worked examples, then must apply the same structural rules to a new surface domain (e.g., color→letter mapping). Both near and far transfer are tested.
- **Interference:** Competing rule systems are presented *in the same prompt* — not across separate turns. This is critical: Bedrock's stateless API means cross-turn interference would fail (each call is independent). Co-presenting distractors in-context creates genuine proactive/retroactive interference.
- **Learning curves:** Multiple exposure levels are tested by varying the number of worked examples provided before test items. We fit improvement trajectories to detect whether models show human-like power-law learning or step-function acquisition.
- Context length constraints required capping interference hard tier at 4 examples (from 6) to prevent Ministral 3B context overflow.

### Results, Insights, and Conclusions

We evaluated 10 models via Amazon Bedrock (9 for learning_curves due to Qwen3 OOM):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| Transfer | 0.785 | 0.255 | 0.720 | Claude Opus (1.00) | Ministral 3B (0.28) |
| Interference | 0.547 | 0.272 | 0.880 | Claude Sonnet (1.00) | Claude Opus (0.12) |
| Curriculum | 0.638 | 0.112 | 0.300 | Llama 3.3 70B (0.76) | Nova Pro (0.46) |
| Learning Curves | 0.654 | 0.068 | 0.180 | Claude Opus (0.73) | Llama 3.3 70B (0.55) |

**Insight 1 — Interference is the strongest discriminator.** With range 0.880 and std 0.272, interference resistance shows the widest model separation. Remarkably, Claude Opus (0.12) — the strongest model on most other tasks — scores lowest, while Claude Sonnet (1.00) achieves perfect scores. This suggests that larger models may be *more susceptible* to interference from co-present competing information, possibly due to stronger associative retrieval from all context.

**Insight 2 — Transfer scales with model size, interference does not.** Transfer shows a clean scaling relationship (Ministral 3B: 0.28, mid-tier: ~0.75, frontier: 1.00), consistent with Thorndike's (1932) theory that transfer requires abstraction capacity. Interference resistance shows no such scaling, suggesting it depends on a distinct cognitive mechanism — possibly attentional gating rather than raw reasoning ability.

**Insight 3 — Curriculum sensitivity is surprisingly low.** All models score between 0.46–0.76 regardless of presentation order, with std of only 0.112. Unlike human learners, where curriculum structure strongly affects acquisition (Ausubel, 1968), LLMs appear relatively order-insensitive within their context window. This may reflect the parallel nature of transformer attention vs. sequential human encoding.

**Insight 4 — Learning curves are flat rather than power-law.** Most models show rapid acquisition (near-asymptotic after 2–3 examples) rather than the gradual power-law improvement seen in humans (Newell & Rosenbloom, 1981). This "step function" learning pattern — either the model grasps the rule or it doesn't — is a qualitative departure from human learning dynamics. The narrow range (0.180) reflects this: more examples help little once the pattern is identified.

**Average cross-benchmark std = 0.177**, confirming meaningful model separation, driven primarily by transfer and interference.

### Organizational Affiliations

Independent submission — no organizational affiliation.

### References & Citations

- Thorndike, E. L. (1932). *The Fundamentals of Learning*. Teachers College Press.
- Ausubel, D. P. (1968). *Educational Psychology: A Cognitive View*. Holt, Rinehart & Winston.
- Underwood, B. J. (1957). Interference and forgetting. *Psychological Review*, 64(1), 49–60.
- Newell, A. & Rosenbloom, P. S. (1981). Mechanisms of skill acquisition and the law of practice. In J. R. Anderson (Ed.), *Cognitive Skills and Their Acquisition* (pp. 1–55). Erlbaum.
- Gentner, D. (1983). Structure-mapping: A theoretical framework for analogy. *Cognitive Science*, 7(2), 155–170.
- Anderson, J. R. (1982). Acquisition of cognitive skill. *Psychological Review*, 89(4), 369–406.
- Bjork, R. A. (1994). Memory and metamemory considerations in the training of human beings. In J. Metcalfe & A. Shimamura (Eds.), *Metacognition* (pp. 185–205). MIT Press.
