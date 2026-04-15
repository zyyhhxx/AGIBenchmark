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
| **N-back** | Working memory updating | Continuous performance task spanning 2-back through 5-back with transformation variants and lure trials; measures capacity to maintain and update items in working memory (Kirchner, 1958) |
| **Task Switching** | Cognitive flexibility | Batch presentation with 4 compositional rules and post-stimulus cuing; measures switch cost (Rogers & Monsell, 1995; Monsell, 2003) |
| **Tower of London (ToL)** | Multi-step planning | Solve disc-rearrangement problems requiring optimal move sequences with look-ahead; measures planning depth (Shallice, 1982) |
| **WCST** | Set shifting / perseveration | Wisconsin Card Sorting Task with hidden sorting dimensions, probabilistic feedback, variable shift criteria, and multi-dimensional phases; measures ability to detect and adapt to implicit rule shifts (Grant & Berg, 1948; Miyake et al., 2000) |

**Difficulty calibration:** CRT includes 3 difficulty tiers (easy/hard/extreme) with extreme items requiring 3+ cognitive shifts (compound rates, recursive discounts, Bayesian reasoning). N-back scales from 2-back to 5-back with transformation variants (alphabet-shift matching) and ~15% lure trials at N±1 to test precision of position tracking. Task switching uses post-stimulus cuing in rapid/random blocks with congruency-aware item generation. ToL scales from easy to hard planning problems. WCST uses hidden dimensions (the model must discover which dimensions exist from feedback alone), probabilistic feedback (85% reliable), and multi-dimensional matching phases where two dimensions must be satisfied simultaneously.

**Contamination resistance:** CRT uses procedurally generated items with randomizable numeric seeds — classic bat-and-ball style items are replaced with novel algebraic-trap problems. WCST, ToL, N-back, and task switching all use novel stimuli configurations generated with seeded RNG.

### Dataset

All items are procedurally generated with deterministic seeds and inlined directly in the Kaggle notebooks (no external data dependencies). Per-task item counts: CRT (15 items across 3 difficulty tiers), N-back (80 items across 2-back through 5-back with transformation and lure conditions), task switching (40+ trials across baseline, slow-switch, rapid, and random block types), ToL (20 problems scaling in difficulty), WCST (6 blocks with variable shift criteria of 3–7 correct responses).

**Scoring:**
- **CRT:** Difficulty-weighted accuracy (extreme=3.0, hard=2.0, easy=1.0)
- **N-back:** Accuracy across all conditions (2-back through 5-back, standard and transformation variants)
- **Task switching:** Composite of 0.10×baseline + 0.25×slow-switch + 0.35×rapid + 0.30×switch-cost metric
- **ToL:** Move optimality (optimal moves / actual moves)
- **WCST:** Composite of accuracy (0.25), perseveration avoidance (0.45), and categories completed (0.30)

**Provenance:** All stimuli are synthetically generated. Classic CRT items are replaced with novel parametric variants to prevent training data contamination. No copyrighted datasets are used.

### Technical Details

All tasks use the `kaggle-benchmarks` SDK with `@kbench.task` decorators, creating fresh conversations per item. Key implementation details:

- **CRT:** Regex-based answer parser extracts final numeric answers from free-text responses. Parser handles patterns like `**Answer:**`, `=`, and bolded numbers. Multi-pattern extraction pipeline prevents truncation artifacts.
- **Task switching:** Batch presentation is critical — per-trial prompts with explicit rule restatement collapse switch cost to zero (rules are trivially solvable without switching). Computationally harder rules (prime check, position parity, divisibility, vowel proximity) with post-stimulus cuing (item shown before rule) prevent ceiling effects.
- **ToL:** 5-strategy response parser cascade (MOVES: line → numbered moves → compact move list → positional notation). Full-text regex fallback was removed because chain-of-thought models produce dozens of intermediate A→B tokens in reasoning traces.
- **N-back:** Batch presentation with segments of the sequence; model must answer for all positions without the N-back letter being given in the prompt. Transformation variants at higher N require checking alphabet-shifted matches rather than exact matches, adding a processing step on top of maintenance.
- **WCST:** Multi-block batch-prompt architecture with explicit Correct/Incorrect feedback chains. Models must discover sorting dimensions and infer rule changes from feedback patterns alone. Probabilistic feedback (85% reliable) means occasional incorrect signals even on correct responses, requiring models to aggregate evidence across multiple trials rather than updating on single data points.

### Results, Insights, and Conclusions

We evaluated 8 models on the [Kaggle Community Benchmarks platform](https://www.kaggle.com/benchmarks/ianstudy/executive-functions-track), spanning frontier-class (Claude Opus 4.6, DeepSeek-R1, Gemini 2.5 Pro, GPT-5.4), mid-tier (Gemini 2.5 Flash, GPT-5.4 Nano), and small models (Gemma 3 4B, Gemma 3 1B). Results (scores 0–1, higher = better):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| CRT | 0.665 | 0.230 | 0.601 | Claude Opus 4.6 (0.92) | Gemma 3 1B (0.32) |
| N-back | 0.561 | 0.443 | 0.974 | Gemini 2.5 Pro / Claude Opus / Gemini Flash (1.00) | Gemma 3 1B (0.03) |
| Task Switching | 0.735 | 0.146 | 0.450 | Gemini 2.5 Pro / Gemini Flash / DeepSeek-R1 (0.84) | Gemma 3 1B (0.39) |
| Tower of London | 0.573 | 0.340 | 1.000 | Gemini 2.5 Pro (1.00) | Gemma 3 1B (0.00) |
| WCST | 0.450 | 0.136 | 0.494 | GPT-5.4 (0.77) | Gemma 3 4B (0.27) |

**Overall model ranking:** Gemini 2.5 Pro (0.835) > Claude Opus 4.6 (0.785) > Gemini 2.5 Flash (0.769) > DeepSeek-R1 (0.754) > GPT-5.4 (0.670) > GPT-5.4 Nano (0.423) > Gemma 3 4B (0.304) > Gemma 3 1B (0.233).

**Insight 1 — N-back produces the strongest model separation.** With std = 0.443 and range = 0.974, N-back is the most discriminating benchmark in the suite. A sharp cliff separates frontier models (Gemini 2.5 Pro, Claude Opus, Gemini Flash all at 1.00; DeepSeek-R1 at 0.99) from the rest (GPT-5.4: 0.29, GPT-5.4 Nano: 0.13, Gemma 3 4B: 0.05, Gemma 3 1B: 0.03). Three design choices prevent ceiling effects: extending to 5-back, adding transformation variants (alphabet-shift matching at higher N), and introducing ~15% lure trials at N±1 that test precision of position tracking rather than mere familiarity detection. Working memory updating at higher N appears to be a threshold capability that collapses sharply below frontier scale.

**Insight 2 — WCST is universally hard with hidden dimensions and probabilistic feedback.** With a mean of just 0.450, WCST is the hardest benchmark in the suite. Three design innovations drive this difficulty: (1) hidden sorting dimensions force models to discover the dimension space from feedback alone rather than selecting from an enumerated list, (2) probabilistic feedback (85% reliable) prevents simple rule-following — models must aggregate noisy signals to infer the active rule, and (3) multi-dimensional phases require matching on two dimensions simultaneously. GPT-5.4 (0.77) leads decisively, while even frontier models like Claude Opus (0.37) and Gemini Pro (0.47) struggle, suggesting that genuine set-shifting flexibility under uncertainty is a distinct capability from reasoning ability.

**Insight 3 — Tower of London confirms planning as a scale-dependent capability.** ToL (std = 0.340, range = 1.000) shows clean separation: Gemini 2.5 Pro achieves perfect planning (1.00), three frontier models cluster at 0.70–0.85, and small models collapse (Gemma 3 4B: 0.14, Gemma 3 1B: 0.00). The full-range spread from 0.00 to 1.00 makes ToL the benchmark with the widest absolute separation, confirming that multi-step look-ahead planning is a genuine capability gap that scales with model size.

**Insight 4 — No single model dominates across all executive functions.** Unlike metacognition where Claude Opus leads most tasks, executive functions reveal complementary strengths: Gemini 2.5 Pro leads ToL and ties for N-back/task switching, Claude Opus leads CRT, GPT-5.4 leads WCST, and three models tie on task switching. This suggests that the Miyake et al. (2000) componential model — which argues inhibition, shifting, and updating are separable constructs — holds for LLMs as well: models that excel at response inhibition (CRT) do not necessarily excel at set shifting (WCST) or planning (ToL).

**Insight 5 — Response parsing is a critical confound in executive function benchmarks.** Our iterative development revealed that parser bugs (truncation, greedy regex on chain-of-thought) can mask genuine capability differences. ToL scores jumped from mean 0.038 to 0.252 after parser fixes alone during initial development. CRT's multi-pattern extraction pipeline was refined to prevent regex from grabbing intermediate reasoning values. This underscores that executive function benchmarks for LLMs must carefully separate *response format* failures from *cognitive* failures.

**Average cross-benchmark std = 0.259**, the highest of all 5 cognitive tracks, confirming that executive functions produce the most meaningful model separation.

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
- Rogers, R. D. & Monsell, S. (1995). Costs of a predictable switch between simple cognitive tasks. *Journal of Experimental Psychology: General*, 124(2), 207–231.
- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
- Toplak, M. E. et al. (2011). The Cognitive Reflection Test as a predictor of performance on heuristics-and-biases tasks. *Memory & Cognition*, 39, 1275–1289.
- Owen, A. M. et al. (1990). Planning and spatial working memory following frontal lobe lesions in man. *Neuropsychologia*, 28(10), 1021–1034.
- Milner, B. (1963). Effects of different brain lesions on card sorting. *Archives of Neurology*, 9(1), 90–100.
- Barceló, F. (2003). The Madrid Card Sorting Test (MCST). *Neuropsychologia*, 41(12), 1553–1567.
- Meiran, N. (1996). Reconfiguration of processing mode prior to task performance. *Journal of Experimental Psychology: LMC*, 22(6), 1423–1442.
- Allport, A. et al. (1994). Shifting intentional set: Exploring the dynamic control of tasks. In C. Umiltà & M. Moscovitch (Eds.), *Attention and Performance XV* (pp. 421–452).
