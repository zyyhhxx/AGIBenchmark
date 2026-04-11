### Can AI Systems Plan, Inhibit, and Adapt? A 5-Task Executive Functions Benchmark Suite

### Team
Yiyang Zeng (Independent researcher)

### Problem Statement

Executive functions — the higher-order cognitive processes that enable goal-directed behavior through planning, inhibition, and cognitive flexibility — are central to intelligent action (Diamond, 2013). Miyake et al. (2000) identified three core executive components: *inhibition* (suppressing prepotent responses), *shifting* (flexibly switching between tasks or mental sets), and *updating* (maintaining and manipulating working memory). These components predict real-world outcomes from academic achievement to decision-making quality.

Current LLM benchmarks test reasoning products (correct answers) but not the executive *processes* that produce them. A model that reaches the right answer through brute-force search engages different cognitive machinery than one that plans ahead, inhibits impulsive responses, and flexibly adapts strategies. Without executive function benchmarks, we cannot distinguish genuine cognitive control from pattern matching.

This benchmark suite asks: **Can frontier models plan multi-step actions, inhibit prepotent responses, and flexibly shift cognitive strategies?**

### Task & Benchmark Construction

We constructed 5 tasks mapping onto the Miyake et al. (2000) three-component framework plus planning:

| Task | Construct | Protocol |
|------|-----------|----------|
| **Cognitive Reflection Test (CRT)** | Response inhibition | Procedurally generated problems with intuitive-but-wrong answers; models must inhibit heuristic responses (Frederick, 2005) |
| **N-back** | Working memory updating | 3-back and 4-back continuous performance task; measures capacity to maintain and update items in working memory (Kirchner, 1958) |
| **Task Switching** | Cognitive flexibility | Batch presentation with rule switches between digit-sum parity and letter-position comparison; measures switch cost (Monsell, 2003) |
| **Tower of London (ToL)** | Multi-step planning | Solve disc-rearrangement problems requiring 3–5 moves with look-ahead; measures planning depth (Shallice, 1982) |
| **WCST** | Set shifting / perseveration | Wisconsin Card Sorting Task with rule changes after consistent runs; measures ability to detect and adapt to implicit rule shifts (Grant & Berg, 1948; Miyake et al., 2000) |

**Difficulty calibration:** CRT includes 3 difficulty tiers (easy/hard/extreme) with extreme items requiring 3+ cognitive shifts (compound rates, recursive discounts, Bayesian reasoning). ToL scales from 3-move to 5-move problems. WCST uses 6 blocks with implicit rule changes and perseveration scoring.

**Contamination resistance:** CRT uses procedurally generated items with randomizable numeric seeds — classic bat-and-ball style items are replaced with novel algebraic-trap problems. WCST and ToL use novel stimuli configurations.

### Dataset

All items are procedurally generated with deterministic seeds. Per-task item counts: CRT (15 items across 3 difficulty tiers), N-back (140 items across 3-back and 4-back), task switching (40+ trials across 4 block types), ToL (20 problems, 3–5 moves), WCST (6 blocks of 10–15 trials each).

**Scoring:** CRT uses difficulty-weighted accuracy (extreme=3.0, hard=2.0, easy=1.0). N-back uses accuracy across both conditions. Task switching measures switch cost as accuracy difference between switch and non-switch trials. ToL scores move optimality (optimal moves / actual moves). WCST composites accuracy (0.25), perseveration avoidance (0.45), and categories completed (0.30).

**Provenance:** All stimuli are synthetically generated. Classic CRT items are replaced with novel parametric variants to prevent training data contamination.

### Technical Details

All tasks use the `kaggle-benchmarks` SDK with `@kbench.task` decorators. Key implementation details:

- **CRT:** Regex-based answer parser extracts final numeric answers from free-text responses. Parser handles patterns like `**Answer:**`, `=`, and bolded numbers. Original parser bug (20-char truncation) caused floor effects — fixed with multi-pattern extraction.
- **Task switching:** Batch presentation is critical — per-trial prompts with explicit rule restatement collapse switch cost to zero (rules are trivially solvable without switching). Computationally harder rules (digit-sum parity, letter-position ordinal reasoning) prevent ceiling effects.
- **ToL:** 5-strategy response parser cascade (MOVES: line → numbered moves → compact move list → positional notation). Full-text regex fallback was removed because chain-of-thought models produce dozens of intermediate A→B tokens in reasoning traces.
- **WCST:** 6-block batch-prompt architecture with explicit Correct/Incorrect feedback chains. Models must infer rule changes from feedback patterns alone.

### Results, Insights, and Conclusions

We evaluated 10 models via Amazon Bedrock (9 for N-back due to Qwen3 OOM):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| CRT | 0.681 | 0.150 | 0.460 | Claude Opus (0.91) | Ministral 3B (0.45) |
| N-back | 0.889 | 0.182 | 0.486 | Claude Opus (1.00) | Ministral 3B (0.51) |
| Task Switching | 0.881 | 0.116 | 0.288 | Claude Opus (1.00) | Nova Pro (0.71) |
| Tower of London | 0.252 | 0.280 | 0.800 | Claude Opus (0.80) | Claude Sonnet (0.00) |
| WCST | 0.607 | 0.237 | 0.739 | Claude Opus (1.00) | Ministral 3B (0.26) |

**Insight 1 — Tower of London is the hardest benchmark.** Mean score 0.252, with 3 models scoring 0.000, makes ToL the most challenging task across all 5 tracks. Multi-step planning with look-ahead appears to be a genuine capability gap — even mid-tier models (Nova Pro: 0.28, Qwen3: 0.29) barely exceed chance. Only Claude Opus (0.80) and GPT-OSS-120B (0.68) demonstrate reliable planning depth, suggesting that planning may emerge only at the largest scales.

**Insight 2 — WCST reveals perseveration differences.** The 0.45 weight on perseveration avoidance exposes a clear scale gradient: Ministral 3B (0.26) perseverates heavily on outdated rules, while Claude Opus (1.00) and Qwen3 (1.00) detect rule changes promptly. The bimodal distribution (two models at 1.00, rest clustered 0.45–0.70) suggests set-shifting may be a threshold capability rather than a continuous gradient.

**Insight 3 — CRT contamination resistance works.** With procedurally generated items replacing classic CRT problems, no model achieves perfect scores. Claude Opus (0.91) still leads, but the gap to mid-tier (0.60–0.74) is meaningful. The extreme-difficulty items (compound rate + spoilage, recursive discounts) remain challenging even for frontier models, validating the difficulty tiering.

**Insight 4 — Response parsing is a critical confound.** Our iterative development revealed that parser bugs (truncation, greedy regex on chain-of-thought) can mask genuine capability differences. ToL scores jumped from mean 0.038 to 0.252 after parser fixes alone. This underscores that executive function benchmarks for LLMs must carefully separate *response format* failures from *cognitive* failures.

**Average cross-benchmark std = 0.193**, the highest of all 5 tracks, confirming that executive functions produce the most meaningful model separation.

### Organizational Affiliations

Independent submission — no organizational affiliation.

### References & Citations

- Miyake, A. et al. (2000). The unity and diversity of executive functions and their contributions to complex "frontal lobe" tasks. *Cognitive Psychology*, 41(1), 49–100.
- Diamond, A. (2013). Executive functions. *Annual Review of Psychology*, 64, 135–168.
- Frederick, S. (2005). Cognitive reflection and decision making. *Journal of Economic Perspectives*, 19(4), 25–42.
- Shallice, T. (1982). Specific impairments of planning. *Philosophical Transactions of the Royal Society B*, 298(1089), 199–209.
- Grant, D. A. & Berg, E. A. (1948). A behavioral analysis of degree of reinforcement and ease of shifting to new responses in a Weigl-type card-sorting problem. *Journal of Experimental Psychology*, 38(4), 404–411.
- Monsell, S. (2003). Task switching. *Trends in Cognitive Sciences*, 7(3), 134–140.
- Kirchner, W. K. (1958). Age differences in short-term retention. *Journal of Experimental Psychology*, 55(4), 352–358.
- Botvinick, M. M. et al. (2001). Conflict monitoring and cognitive control. *Psychological Review*, 108(3), 624–652.
