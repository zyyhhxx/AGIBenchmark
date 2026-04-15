### Can AI Systems Plan, Inhibit, and Adapt? A 5-Task Executive Functions Benchmark Suite

### Team
Yiyang Zeng (Independent researcher)

### Problem Statement

Executive functions — the higher-order cognitive processes that enable goal-directed behavior through planning, inhibition, and cognitive flexibility — are central to intelligent action (Diamond, 2013). Miyake et al. (2000) identified three core executive components: *inhibition* (suppressing prepotent responses), *shifting* (flexibly switching between tasks or mental sets), and *updating* (maintaining and manipulating working memory).

Current LLM benchmarks test reasoning products (correct answers) but not the executive *processes* that produce them. A model that reaches the right answer through brute-force search engages different cognitive machinery than one that plans ahead, inhibits impulsive responses, and flexibly adapts strategies. These components predict real-world outcomes from academic achievement to decision-making quality. This benchmark suite asks: **Can frontier models plan multi-step actions, inhibit prepotent responses, and flexibly shift cognitive strategies?**

### Task & Benchmark Construction

We constructed 5 tasks mapping onto the Miyake et al. (2000) three-component framework plus planning:

| Task | Construct | Protocol |
|------|-----------|----------|
| **Cognitive Reflection Test (CRT)** | Response inhibition | Procedurally generated problems with intuitive-but-wrong answers; models must inhibit heuristic responses. Human baseline: ~30% (general public), ~50% (MIT students) (Frederick, 2005) |
| **N-back** | Working memory updating | 2-back through 5-back with transformation variants and lure trials. Human baseline: ~90% at 2-back, ~50% at 4-back (Kirchner, 1958; Kane et al., 2007) |
| **Task Switching** | Cognitive flexibility | Batch presentation with 4 compositional rules and post-stimulus cuing (Rogers & Monsell, 1995) |
| **Tower of London (ToL)** | Multi-step planning | Disc-rearrangement problems requiring optimal move sequences with look-ahead. Human baseline: ~85% at 3 moves, ~55% at 5 moves (Shallice, 1982; Owen et al., 1990) |
| **WCST** | Set shifting / perseveration | Hidden sorting dimensions, probabilistic feedback, variable shift criteria, and multi-dimensional phases (Grant & Berg, 1948) |

**Key design choices** ensure we measure genuine executive processes rather than surface-level task completion:

- **Batch presentation** (task switching, N-back): Trials are presented in sequence within a single conversation. Per-trial prompts with explicit rule restatement collapse switch cost to zero — rules become trivially solvable without actual switching. N-back requires answering for all positions in a sequence segment without the target letter given in the prompt.
- **Post-stimulus cuing** (task switching): The stimulus is shown before the rule in rapid/random blocks, forcing genuine task-set reconfiguration rather than rule-primed responses. Four compositional rules (prime check, position parity, divisibility, vowel proximity) with congruency-aware item generation prevent ceiling effects.
- **Feedback-driven discovery** (WCST): Models receive Correct/Incorrect feedback but are never told which sorting dimensions exist. They must discover the dimension space, infer rules from noisy signals (85% reliable feedback), and adapt to multi-dimensional phases requiring two dimensions simultaneously.
- **Difficulty scaling** (CRT, N-back): CRT uses 3 difficulty tiers with extreme items requiring 3+ cognitive shifts. N-back extends to 5-back with transformation variants (alphabet-shift matching) and ~15% lure trials at N±1 testing position-tracking precision.

**Scoring:**
- **CRT:** Difficulty-weighted accuracy (extreme=3.0, hard=2.0, easy=1.0)
- **N-back:** Accuracy across all conditions (standard and transformation variants)
- **Task switching:** 0.10×baseline + 0.25×slow-switch + 0.35×rapid + 0.30×switch-cost metric
- **ToL:** Move optimality (optimal moves / actual moves)
- **WCST:** Accuracy (0.25) + perseveration avoidance (0.45) + categories completed (0.30)

**Response parsing:** Robust output parsing is essential for separating *response format* failures from *cognitive* failures. ToL uses a 5-strategy parser cascade to handle diverse response formats while excluding chain-of-thought reasoning traces. CRT uses a multi-pattern regex pipeline to extract final numeric answers without matching intermediate reasoning values.

**Contamination resistance:** All tasks use procedurally generated stimuli with seeded RNG. CRT replaces classic bat-and-ball items with novel algebraic-trap problems using randomizable numeric seeds.

### Dataset

All stimuli are procedurally generated with deterministic seeds and inlined directly in the Kaggle notebooks — no external data dependencies. Ground truth verification scripts independently compute expected outputs for every item and compare against stored answer keys. All randomness uses seeded RNG; scores are clipped to [0, 1]. No copyrighted datasets are used.

### Results, Insights, and Conclusions

We evaluated 8 models on the [Kaggle Community Benchmarks platform](https://www.kaggle.com/benchmarks/ianstudy/executive-functions-track), spanning frontier (Claude Opus 4.6, DeepSeek-R1, Gemini 2.5 Pro, GPT-5.4), mid-tier (Gemini 2.5 Flash, GPT-5.4 Nano), and small models (Gemma 3 4B, Gemma 3 1B):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| CRT | 0.665 | 0.230 | 0.601 | Claude Opus 4.6 (0.92) | Gemma 3 1B (0.32) |
| N-back | 0.561 | 0.443 | 0.974 | Gemini 2.5 Pro / Claude Opus / Gemini Flash (1.00) | Gemma 3 1B (0.03) |
| Task Switching | 0.735 | 0.146 | 0.450 | Gemini 2.5 Pro / Gemini Flash / DeepSeek-R1 (0.84) | Gemma 3 1B (0.39) |
| Tower of London | 0.573 | 0.340 | 1.000 | Gemini 2.5 Pro (1.00) | Gemma 3 1B (0.00) |
| WCST | 0.450 | 0.136 | 0.494 | GPT-5.4 (0.77) | Gemma 3 4B (0.27) |

**Overall ranking:** Gemini 2.5 Pro (0.835) > Claude Opus 4.6 (0.785) > Gemini 2.5 Flash (0.769) > DeepSeek-R1 (0.754) > GPT-5.4 (0.670) > GPT-5.4 Nano (0.423) > Gemma 3 4B (0.304) > Gemma 3 1B (0.233).

**Insight 1 — N-back reveals a frontier cliff in working memory.** A sharp divide separates frontier models (three at 1.00, DeepSeek-R1 at 0.99) from the rest (GPT-5.4: 0.29, down to Gemma 3 1B: 0.03). The combination of 5-back depth, transformation variants, and lure trials creates a threshold that collapses sharply below frontier scale.

**Insight 2 — WCST is universally hard under uncertainty.** With a mean of just 0.450, WCST is the hardest benchmark. Hidden dimensions, probabilistic feedback, and multi-dimensional phases make this difficult even for frontier models (Claude Opus: 0.37, Gemini Pro: 0.47). GPT-5.4 (0.77) leads decisively, suggesting set-shifting flexibility under uncertainty is a distinct capability from general reasoning.

**Insight 3 — Planning scales with model size.** ToL shows the widest absolute separation (range = 1.000): Gemini 2.5 Pro achieves perfect planning, three frontier models cluster at 0.70–0.85, and small models collapse (Gemma 3 4B: 0.14, Gemma 3 1B: 0.00). Multi-step look-ahead planning appears to be a genuine scale-dependent capability.

**Insight 4 — No single model dominates all executive functions.** Gemini 2.5 Pro leads ToL, Claude Opus leads CRT, GPT-5.4 leads WCST, and three models tie on task switching. This supports the Miyake et al. (2000) componential model: inhibition, shifting, and updating are separable constructs for LLMs as well. Models that excel at response inhibition (CRT) do not necessarily excel at set shifting (WCST) or planning (ToL).

**Insight 5 — Clear four-tier performance hierarchy.** The overall ranking reveals a clean separation: frontier models (0.75–0.84), GPT-5.4 as a mid-frontier outlier (0.67), mid-tier (GPT-5.4 Nano: 0.42), and small models (Gemma 3 4B: 0.30, Gemma 3 1B: 0.23). The 3.6× ratio between the top and bottom models (0.835 vs 0.233) demonstrates that executive function benchmarks provide a strong performance gradient across the model spectrum — neither ceiling nor floor effects dominate.

**Average cross-benchmark std = 0.259**, confirming strong model separation.

### References & Citations

- Miyake, A. et al. (2000). The unity and diversity of executive functions. *Cognitive Psychology*, 41(1), 49–100.
- Diamond, A. (2013). Executive functions. *Annual Review of Psychology*, 64, 135–168.
- Frederick, S. (2005). Cognitive reflection and decision making. *Journal of Economic Perspectives*, 19(4), 25–42.
- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
- Toplak, M. E. et al. (2011). The Cognitive Reflection Test as a predictor of performance on heuristics-and-biases tasks. *Memory & Cognition*, 39, 1275–1289.
- Kirchner, W. K. (1958). Age differences in short-term retention. *Journal of Experimental Psychology*, 55(4), 352–358.
- Kane, M. J. et al. (2007). Working memory, attention control, and the N-back task. *Journal of Experimental Psychology: LMC*, 33(3), 615–622.
- Owen, A. M. et al. (2005). N-back working memory paradigm: A meta-analysis of normative functional neuroimaging studies. *Human Brain Mapping*, 25(1), 46–59.
- Rogers, R. D. & Monsell, S. (1995). Costs of a predictable switch. *Journal of Experimental Psychology: General*, 124(2), 207–231.
- Meiran, N. (1996). Reconfiguration of processing mode prior to task performance. *Journal of Experimental Psychology: LMC*, 22(6), 1423–1442.
- Allport, A. et al. (1994). Shifting intentional set. In C. Umiltà & M. Moscovitch (Eds.), *Attention and Performance XV* (pp. 421–452).
- Shallice, T. (1982). Specific impairments of planning. *Phil. Trans. R. Soc. B*, 298(1089), 199–209.
- Owen, A. M. et al. (1990). Planning and spatial working memory following frontal lobe lesions. *Neuropsychologia*, 28(10), 1021–1034.
- Grant, D. A. & Berg, E. A. (1948). A behavioral analysis of reinforcement and shifting. *Journal of Experimental Psychology*, 38(4), 404–411.
- Milner, B. (1963). Effects of different brain lesions on card sorting. *Archives of Neurology*, 9(1), 90–100.
- Barceló, F. (2003). The Madrid Card Sorting Test. *Neuropsychologia*, 41(12), 1553–1567.
