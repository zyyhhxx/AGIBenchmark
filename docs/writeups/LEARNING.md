# Can Language Models Learn From Examples Alone? Benchmarking In-Context Rule Induction, Transfer, and Interference

## Problem Statement

Human intelligence is defined not by what we know but by how we learn — acquiring rules from sparse examples, transferring knowledge across domains, resisting interference from competing patterns, and benefiting from structured curricula. These capacities, studied extensively in cognitive science, remain poorly benchmarked in large language models (LLMs). Existing evaluations typically assess static knowledge retrieval or single-turn reasoning rather than the dynamic process of learning itself.

This benchmark operationalizes four foundational learning constructs — structural transfer, rule induction under interference, learning curve dynamics, and curriculum sensitivity — as procedurally generated in-context tasks. Crucially, rules are never stated as text; models must induce them exclusively from input-output examples, mirroring the implicit learning paradigm central to human cognition (Newell & Rosenbloom, 1981). The benchmark asks: **How well can current LLMs learn?**

## Task & Benchmark Construction

| Task | Construct | Cognitive Foundation |
|------|-----------|---------------------|
| **Near & Far Transfer** | Structural transfer and abstraction | Thorndike & Woodworth (1901); Barnett & Ceci (2002); Anderson (1987) |
| **Rule Induction Under Interference** | Rule induction under competing interference | Underwood (1957); Luchins (1942) |
| **Learning Curves** | In-context learning dynamics and transfer | Newell & Rosenbloom (1981); Anderson (1982) |
| **Curriculum Sensitivity** | Sensitivity to example ordering | Bengio et al. (2009); Rohrer & Taylor (2007); Hattie (2009) |

### Key Design Choices

**Rule induction without explicit instruction.** Across all four tasks, transformation rules are presented only as input-output example pairs — never described in natural language. This forces models to perform genuine induction rather than instruction-following, and constitutes the benchmark's central design innovation. A model that cannot extract structural regularities from examples alone will fail regardless of its declarative knowledge.

**Procedural generation for contamination resistance.** Rule systems are generated algorithmically using parameterized grammars — coordinate-pair encodings, word-problem embeddings, and symbol transformations. Because each instance is unique, memorization of training-set patterns provides no advantage. The shared symbol pool across interference tiers further prevents shortcut strategies based on surface cues.

**Graded difficulty through tiered protocols.** Each task implements structured difficulty gradients:
- **Transfer** moves from identical-context to near-transfer to surface-dissimilar far-transfer domains, following Barnett & Ceci's (2002) taxonomy. Far transfer requires abstracting the underlying rule structure and re-deriving application steps for a completely different domain — testing Anderson's (1987) distinction between procedural and declarative transfer.
- **Interference** escalates from clean single-system trials (Tier 1, weight 0.10) through interleaved multi-system trials with an anti-pattern worked example from the wrong system presented immediately before the query (Tier 3, weight 0.35), to unlabeled clustering requiring unsupervised system identification (Tier 4, weight 0.30).
- **Curriculum Sensitivity** applies three difficulty levels — D1 simple (0.15), D2 contextual (0.35), D3 complex (0.50) — with heavier weighting on harder items.
- **Learning Curves** tests three conditions: standard acquisition (0.20), far-transfer after training (0.50), and steep learning from only 3 examples (0.30).

**Scoring:**
- **Transfer:** 0.30×identical + 0.35×near + 0.35×far transfer accuracy
- **Interference:** Tier-weighted accuracy (Clean 0.10, Labeled 0.25, Interleaved 0.35, Unlabeled 0.30)
- **Learning Curves:** 0.20×standard + 0.50×far_transfer + 0.30×steep
- **Curriculum:** Per difficulty level: 0.70×accuracy + 0.15×consistency + 0.15×curriculum_bonus

## Dataset

Each task generates instances through procedural rule-system construction. Transfer creates structurally isomorphic but surface-dissimilar domains via coordinate-pair encoding and word-problem embedding. Interference draws all competing rule systems from a shared symbol pool, ensuring that only structural understanding — not surface cues — can disambiguate systems. Learning Curves varies the number of provided examples to trace acquisition dynamics. Curriculum Sensitivity presents identical example sets and test items under four orderings, isolating the pure effect of presentation sequence. All generation is deterministic given a seed, enabling full reproducibility. No copyrighted datasets are used.

## Results, Insights, and Conclusions

We evaluated 8 models on the [Kaggle Community Benchmarks platform](https://www.kaggle.com/benchmarks/ianstudy/learning-track), spanning frontier (Claude Opus 4.6, DeepSeek-R1, Gemini 2.5 Pro, GPT-5.4), mid-tier (Gemini 2.5 Flash, GPT-5.4 Nano), and small models (Gemma 3 4B, Gemma 3 1B):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| Interference | 0.326 | 0.170 | 0.510 | Claude Opus 4.6 (0.56) | Gemma 3 4B (0.05) |
| Transfer | 0.439 | 0.258 | 0.670 | Gemini 2.5 Flash (0.73) | Gemma 3 1B (0.06) |
| Learning Curves | 0.504 | 0.264 | 0.729 | Gemini 2.5 Flash (0.80) | Gemma 3 1B (0.07) |
| Curriculum | 0.446 | 0.206 | 0.492 | Gemini 2.5 Flash (0.68) | Gemma 3 4B (0.19) |

**Overall ranking:** Gemini 2.5 Flash (0.664) > Claude Opus 4.6 (0.629) > Gemini 2.5 Pro (0.581) > GPT-5.4 (0.550) > DeepSeek-R1 (0.540) > GPT-5.4 Nano (0.181) > Gemma 3 1B (0.164) > Gemma 3 4B (0.144).

**Insight 1 — Learning remains profoundly difficult for LLMs.** The highest overall score is 0.66 (Gemini 2.5 Flash), meaning even the best model fails roughly one-third of learning challenges. No model exceeds 0.80 on any individual task. This ceiling suggests that current architectures, despite massive scaling, have not solved the problem of flexible in-context learning from examples alone.

**Insight 2 — A sharp capability cliff separates frontier from small models.** Frontier models cluster between 0.54 and 0.66, while sub-10B models score between 0.14 and 0.18 — a 3.7× performance ratio. GPT-5.4 Nano (0.18) — despite being a distillation of GPT-5.4 (0.55) — collapses to small-model performance levels, scoring only 33% of its parent. This discontinuity suggests that in-context rule induction may require a minimum representational capacity that smaller architectures and distilled models lack.

**Insight 3 — Interference is universally the hardest facet of learning.** With a mean of just 0.326, Interference is the most difficult task — even the top scorer (Claude Opus 4.6, 0.56) leaves nearly half of interference challenges unsolved. The Einstellung anti-pattern design (Tier 3) is particularly effective: presenting a worked example from the *wrong* system immediately before the query creates genuine proactive interference that even frontier models cannot fully overcome. This directly parallels Underwood's (1957) finding that proactive interference is among the most debilitating phenomena in human learning, and Luchins' (1942) demonstration that prior solution strategies actively impair performance on structurally novel problems.

**Insight 4 — Transfer and Learning Curves provide the strongest discrimination.** These tasks show the highest standard deviations (0.258 and 0.264), with score ranges spanning 0.670 and 0.729. This makes them particularly effective at separating models by learning capability and thus valuable diagnostics for tracking future progress.

**Insight 5 — Model size does not monotonically predict interference resistance.** Gemma 3 1B scores 0.31 on Interference — substantially above Gemma 3 4B's 0.05. Similarly, on Transfer, Gemma 3 4B (0.21) outperforms Gemma 3 1B (0.06). These crossed non-monotonic relationships suggest that different learning sub-processes depend on distinct architectural or training factors beyond raw parameter count, and that the four tasks in this suite genuinely measure separable learning constructs.

**Average cross-benchmark std = 0.225**, confirming strong model separation driven primarily by transfer and learning curves.

## References

- Anderson, J. R. (1982). Acquisition of cognitive skill. *Psychological Review*, 89(4), 369–406.
- Anderson, J. R. (1987). Skill acquisition: Compilation of weak-method problem solutions. *Psychological Review*, 94(2), 192–210.
- Barnett, S. M. & Ceci, S. J. (2002). When and where do we apply what we learn? A taxonomy for far transfer. *Psychological Bulletin*, 128(4), 612–637.
- Bengio, Y. et al. (2009). Curriculum learning. *Proceedings of the 26th ICML*, 41–48.
- Hattie, J. (2009). *Visible Learning: A Synthesis of Over 800 Meta-Analyses Relating to Achievement*. Routledge.
- Luchins, A. S. (1942). Mechanization in problem solving: The effect of Einstellung. *Psychological Monographs*, 54(6), i–95.
- Newell, A. & Rosenbloom, P. S. (1981). Mechanisms of skill acquisition and the law of practice. In J. R. Anderson (Ed.), *Cognitive Skills and Their Acquisition* (pp. 1–55). Erlbaum.
- Rohrer, D. & Taylor, K. (2007). The shuffling of mathematics problems improves learning. *Instructional Science*, 35(6), 481–498.
- Thorndike, E. L. & Woodworth, R. S. (1901). The influence of improvement in one mental function upon the efficiency of other functions. *Psychological Review*, 8(3), 247–261.
- Underwood, B. J. (1957). Interference and forgetting. *Psychological Review*, 64(1), 49–60.
