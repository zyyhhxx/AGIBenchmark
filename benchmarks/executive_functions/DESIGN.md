# Executive Functions Track — Design Document

## Cognitive Science Framework

Executive functions (EFs) are top-down control processes that regulate thought and action. We follow the **Miyake et al. (2000) unity/diversity framework**, which identifies three core EFs:

1. **Set-Shifting** — Flexibly switching between tasks or mental sets
2. **Working Memory Updating** — Monitoring and revising working memory contents
3. **Inhibition** — Suppressing prepotent responses (partially captured across benchmarks)

These three factors are separable but correlated (unity/diversity), making them suitable for a multi-benchmark track.

### Key References
- Miyake, A., Friedman, N. P., Emerson, M. J., Witzki, A. H., Howerter, A., & Wager, T. D. (2000). The unity and diversity of executive functions. *Cognitive Psychology, 41*(1), 49–100.
- Berg, E. A. (1948). A simple objective technique for measuring flexibility in thinking. *Journal of General Psychology, 39*, 15–22.
- Shallice, T. (1982). Specific impairments of planning. *Philosophical Transactions of the Royal Society B, 298*, 199–209.
- Owen, A. M., McMillan, K. M., Laird, A. R., & Bullmore, E. (2005). N-back working memory paradigm. *Human Brain Mapping, 25*(1), 46–59.
- Rogers, R. D., & Monsell, S. (1995). Costs of a predictable switch between simple cognitive tasks. *Journal of Experimental Psychology: General, 124*(2), 207–231.

---

## Benchmark 1: Wisconsin Card Sort Test (WCST) Analogue

### What it tests
**Cognitive flexibility / set-shifting.** The model must infer a hidden sorting rule from feedback, then detect and adapt when the rule silently changes.

### Design
- 80 trials with 4 reference cards (fixed) and variable target cards
- 3 sorting dimensions: color, shape, number
- Rule switches every 10 trials (8 rule episodes)
- Model receives "Correct"/"Incorrect" feedback after each response
- Single conversational session preserves trial history

### Scoring
| Metric | Weight | What it measures |
|--------|--------|-----------------|
| Accuracy | 0.30 | Overall sorting correctness |
| 1 - Perseveration rate | 0.40 | Ability to abandon old rules (key EF metric) |
| Shift efficiency | 0.30 | Speed of adaptation after rule switch |

### Shortcut Resistance
- Rules are never stated; must be inferred from feedback
- Target cards match different references on different dimensions (no one-dimensional matching)
- Silent rule switches require active monitoring
- Perseveration metric specifically catches rigid strategies

### Human Baselines
- Healthy adults: ~85% accuracy, ~10-15% perseveration rate
- Frontal patients: ~50-60% accuracy, ~40-60% perseveration rate

---

## Benchmark 2: Tower of London (ToL) Planning

### What it tests
**Multi-step planning and look-ahead.** The model must find optimal move sequences to rearrange balls on pegs.

### Design
- 15 problems: 5 each at 3-move, 4-move, and 5-move optimal depths
- Classic Shallice (1982) setup: 3 pegs with capacity constraints (3, 2, 1)
- 3 colored balls (red, blue, green)
- Model provides full move sequence and reasoning

### Scoring
| Metric | Weight | What it measures |
|--------|--------|-----------------|
| Optimality ratio | 0.50 | optimal_moves / actual_moves |
| Validity rate | 0.30 | Proportion of legal, goal-reaching solutions |
| Depth scaling bonus | 0.20 | Performance degrades with depth (human-like) |

### Shortcut Resistance
- Procedurally generated (not from standard batteries)
- Capacity constraints prevent trivial solutions
- Optimal move count given but solution must be found
- Depth scaling separates planning from guessing

### Human Baselines
- 3-move: ~90% optimal, ~95% valid
- 4-move: ~75% optimal, ~90% valid
- 5-move: ~55% optimal, ~80% valid

---

## Benchmark 3: Task-Switching

### What it tests
**Cognitive flexibility through rapid task alternation.** Measures the cost of switching between task rules.

### Design
- 40 trials with numbers 1-9 (excluding 5)
- Two rules alternate every 4 trials:
  - Rule A: Odd/Even classification
  - Rule B: Greater/Less than 5
- Rules are explicitly stated each trial (tests execution, not memory)
- Key metric: accuracy drop on switch trials vs. repeat trials

### Scoring
| Metric | Weight | What it measures |
|--------|--------|-----------------|
| Overall accuracy | 0.40 | Basic task competence |
| Switch trial accuracy | 0.30 | Performance under cognitive load |
| Consistency | 0.30 | Stable performance across blocks |

### Shortcut Resistance
- Rules explicitly stated each trial — can't fail from forgetting
- Switch cost isolates cognitive flexibility from knowledge
- Randomized numbers prevent position-based strategies

### Human Baselines
- Overall accuracy: ~95%
- Switch cost: ~5-10% accuracy drop on switch trials
- RT increase: ~150-300ms on switch trials

---

## Benchmark 4: N-back Working Memory

### What it tests
**Working memory updating.** The model must continuously monitor a sequence and detect when the current item matches the one N positions back.

### Design
- 60-item letter sequences per N level
- N = 1, 2, 3 (increasing difficulty)
- 25% target rate per level
- Consonants only (no word formation cues)
- Signal detection theory analysis (d-prime)

### Scoring
| Metric | Weight | What it measures |
|--------|--------|-----------------|
| d-prime (N=1) | 0.20 | Basic match detection |
| d-prime (N=2) | 0.30 | Moderate WM load |
| d-prime (N=3) | 0.50 | High WM load (most discriminating) |

d-prime normalized: 0 → 0.0, 4.0 → 1.0

### Shortcut Resistance
- Procedurally generated sequences
- Controlled target rate prevents frequency-based shortcuts
- N-back item explicitly shown (tests comparison, not memory for text)
- d-prime accounts for response bias (liberal vs. conservative)

### Human Baselines
- 1-back d': ~3.5 (near ceiling)
- 2-back d': ~2.5
- 3-back d': ~1.5

---

## Track-Level Design Notes

### Inter-benchmark Independence
These four benchmarks target theoretically separable executive functions:
- WCST → set-shifting
- ToL → planning
- Task-switching → shifting (cognitive flexibility)
- N-back → working memory updating

WCST and task-switching both involve shifting but differ: WCST requires rule *inference* while task-switching provides rules explicitly.

### Contamination Resistance
All stimuli are procedurally generated with fixed seeds. No items are drawn from published test batteries. The WCST uses a novel card set, ToL problems are BFS-verified, and N-back sequences use consonant-only alphabets.

### Scoring Philosophy
Each benchmark composite score is in [0, 1]. We weight metrics that are most diagnostic of the target executive function most heavily (e.g., perseveration for WCST, d-prime at high N for N-back).
