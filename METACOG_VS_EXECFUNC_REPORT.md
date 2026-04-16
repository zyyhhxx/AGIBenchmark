# Metacognition vs. Executive Functions — Detailed Benchmark Comparison

**Data source:** Kaggle Community Benchmarks platform (official submission data)
**Models:** 8 models — Claude Opus 4.6, DeepSeek-R1, Gemini 2.5 Pro, Gemini 2.5 Flash, GPT-5.4, GPT-5.4 Nano, Gemma 3 4B, Gemma 3 1B
**Competition:** Measuring Progress Toward AGI — Cognitive Abilities (Google DeepMind)

---

## 1. Theoretical Foundations

### Metacognition Track (9 benchmarks)

Grounded in the **Nelson & Narens (1990) metamemory monitoring framework**, which distinguishes two information flows:

- **Monitoring:** Object-level → meta-level ("How well do I know this?")
- **Control:** Meta-level → object-level ("Study this more")

The track decomposes into three sub-categories:
- **Prospective assessment** — FOK, JOL, calibration (predicting one's own performance)
- **Self-monitoring** — learning monitoring, epistemic revision, metacognitive control (tracking and regulating cognition in real time)
- **External monitoring** — canary, epistemic humility, error detection (evaluating external claims and reasoning)

### Executive Functions Track (5 benchmarks)

Follows the **Miyake et al. (2000) unity/diversity framework** identifying three separable-but-correlated core executive functions, plus planning:

1. **Set-shifting** — flexibly switching between mental sets (WCST, task switching)
2. **Working memory updating** — monitoring and revising WM contents (N-back)
3. **Inhibition** — suppressing prepotent responses (CRT)
4. **Planning** — multi-step look-ahead under constraints (Tower of London)

Key distinction: metacognition is about *knowing what you know*; executive functions are about *controlling what you do*.

---

## 2. Benchmark Inventory

### Metacognition (9 benchmarks)

| Benchmark | Construct | Key Reference | Primary Metric |
|-----------|-----------|---------------|----------------|
| Retrospective Calibration | Post-answer confidence | Lichtenstein et al. (1982) | BSS + extreme-item accuracy |
| Feeling of Knowing (FOK) | Prospective monitoring | Hart (1965) | γ correlation |
| Judgment of Learning (JOL) | Learning prediction | Nelson & Dunlosky (1991) | γ correlation |
| Error Detection | Process monitoring | Yeung & Summerfield (2012) | F1 + localization |
| Contamination Canary | Known/unknown discrimination | Carlini et al. (2021) | Brier Skill Score |
| Metacognitive Control | Strategic regulation | Son & Metcalfe (2000) | Selection relevance + strategic gain |
| Epistemic Humility | Knowledge boundary recognition | Whitcomb et al. (2017) | Detection + (1−confabulation) |
| Epistemic Revision | Belief updating | Gärdenfors (1988) | Transfer accuracy + (1−perseveration) |
| Learning Monitoring | Online self-assessment | Dunlosky & Nelson (1992) | γ (self-assessment vs. actual) |

### Executive Functions (5 benchmarks)

| Benchmark | Construct | Key Reference | Primary Metric |
|-----------|-----------|---------------|----------------|
| Cognitive Reflection Test (CRT) | Response inhibition | Frederick (2005) | Difficulty-weighted accuracy |
| N-Back Working Memory | Working memory updating | Owen et al. (2005) | Accuracy across 2-back to 5-back |
| Task Switching | Cognitive flexibility | Rogers & Monsell (1995) | Switch cost + consistency |
| Tower of London (ToL) | Multi-step planning | Shallice (1982) | Move optimality |
| Wisconsin Card Sort (WCST) | Set-shifting / perseveration | Grant & Berg (1948) | Accuracy + perseveration avoidance |

---

## 3. Full Score Tables

### Metacognition — Per-Model Scores

| Task | Claude Opus 4.6 | DeepSeek-R1 | Gemini 2.5 Pro | Gemini 2.5 Flash | GPT-5.4 | GPT-5.4 Nano | Gemma 3 4B | Gemma 3 1B |
|------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Retrospective Calibration | 0.565 | 0.571 | **0.587** | 0.581 | 0.502 | 0.389 | 0.293 | 0.094 |
| Feeling of Knowing | 0.604 | 0.655 | 0.626 | 0.644 | **0.772** | 0.374 | 0.506 | 0.283 |
| Judgment of Learning | **0.790** | 0.787 | 0.600 | 0.777 | 0.600 | 0.735 | 0.282 | 0.326 |
| Error Detection | 0.947 | **0.981** | 0.915 | 0.969 | 0.856 | 0.794 | 0.707 | 0.401 |
| Contamination Canary | 0.848 | 0.814 | **0.992** | 0.990 | 0.920 | 0.683 | 0.000 | 0.000 |
| Metacognitive Control | **0.910** | 0.880 | 0.910 | 0.888 | 0.910 | 0.797 | 0.645 | 0.188 |
| Epistemic Humility | **0.879** | 0.784 | 0.821 | 0.870 | 0.791 | 0.775 | 0.426 | 0.451 |
| Epistemic Revision | **0.960** | 0.880 | 0.870 | 0.760 | 0.830 | 0.560 | 0.655 | 0.458 |
| Learning Monitoring | 0.918 | **0.965** | 0.948 | 0.838 | 0.820 | 0.410 | 0.253 | 0.263 |
| **Overall** | **0.825** | 0.813 | 0.808 | 0.813 | 0.778 | 0.613 | 0.419 | 0.274 |

### Executive Functions — Per-Model Scores

| Task | Claude Opus 4.6 | DeepSeek-R1 | Gemini 2.5 Pro | Gemini 2.5 Flash | GPT-5.4 | GPT-5.4 Nano | Gemma 3 4B | Gemma 3 1B |
|------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Cognitive Reflection Test | **0.921** | 0.698 | 0.866 | 0.892 | 0.786 | 0.479 | 0.356 | 0.320 |
| N-Back Working Memory | **1.000** | 0.993 | **1.000** | **1.000** | 0.288 | 0.131 | 0.049 | 0.026 |
| Task Switching | 0.790 | **0.844** | **0.844** | **0.844** | 0.817 | 0.644 | 0.702 | 0.394 |
| Tower of London | 0.842 | 0.850 | **1.000** | 0.700 | 0.690 | 0.360 | 0.140 | 0.000 |
| Wisconsin Card Sort | 0.374 | 0.385 | 0.465 | 0.409 | **0.768** | 0.499 | 0.274 | 0.425 |
| **Overall** | 0.785 | 0.754 | **0.835** | 0.769 | 0.670 | 0.423 | 0.304 | 0.233 |

---

## 4. Track-Level Statistics

| Metric | Metacognition (9 tasks) | Executive Functions (5 tasks) |
|--------|:-:|:-:|
| **Grand mean** | 0.668 | 0.597 |
| **Average cross-model std** | 0.216 | 0.259 |
| **Hardest benchmark** | Calibration (0.448) | WCST (0.450) |
| **Easiest benchmark** | Error Detection (0.821) | Task Switching (0.735) |
| **Best discriminator (highest std)** | Canary (0.417) | N-Back (0.474) |
| **Weakest discriminator (lowest std)** | FOK (0.161) | WCST (0.145) |
| **Benchmarks with floor effects** | Canary: 2/8 = 0.00 | ToL: 1/8 = 0.00; N-Back: 2/8 < 0.05 |
| **Benchmarks with ceiling effects** | None | N-Back: 3/8 = 1.00; ToL: 1/8 = 1.00 |
| **Human baseline gap** | Calibration: models 0.448 vs humans 0.80–0.90 | ToL: models 0.573 vs humans ~0.75 |

**Key contrast:** Executive functions has higher discrimination power (avg std 0.259 vs 0.216) but also more ceiling/floor effects — N-back and ToL produce near-binary splits between frontier and non-frontier models. Metacognition distributes difficulty more evenly across the spectrum, with no benchmark producing perfect scores.

---

## 5. Benchmark-by-Benchmark Technical Detail & Innovations

### 5.1 Metacognition Benchmarks

#### Retrospective Calibration

**Technique:** Answer diverse questions across 5 difficulty levels (d1–d5) + rate confidence 0–100. Composite score: 0.50 × extreme_accuracy^1.5 + 0.25 × BSS + 0.25 × uncertainty_awareness.

**Innovation — Difficulty-5 items:** Includes items on Catalan numbers, derangements, Stirling numbers, Euler totient, continued fractions, Bernoulli numbers, and the 1729 taxicab number. Extreme items (d≥4) = 31.8% of pool.

**Innovation — BSS over ECE:** BSS (Brier Skill Score) was chosen over raw ECE because ECE rewards always-hedging-to-50% strategies. BSS penalizes models that lack genuine discrimination.

**CB results:** mean=0.448, std=0.178, range=0.493. Frontier models cluster tightly at 0.50–0.59 while small models collapse (Gemma 3 1B: 0.09). **Universal overconfidence persists** — frontier models report 94–99% confidence even on the hardest items. This is the hardest metacognition benchmark and reveals that calibration remains a fundamental unsolved problem.

---

#### Feeling of Knowing (FOK)

**Technique:** Two-phase protocol. Phase 1 (separate conversation): rate confidence 0–100 that you CAN answer. Phase 2 (separate conversation): actually answer. Composite: 0.40 × γ + 0.30 × BSS + 0.30 × AUC.

**Innovation — Context separation:** The two phases run in separate `kbench.chats.new()` contexts. This prevents post-hoc rationalization — the model cannot assess answer quality because it hasn't answered yet. Direct implementation of Hart's (1965) FOK paradigm, rarely used in AI evaluation.

**CB results:** mean=0.558, std=0.161, range=0.489. GPT-5.4 leads (0.772), demonstrating strong prospective monitoring — accurately predicting its own performance before answering. Gemma 3 1B (0.283) shows poor discrimination between items it will answer correctly versus incorrectly. The two-phase isolation makes this the purest test of prospective metacognition.

---

#### Judgment of Learning (JOL)

**Technique:** Study → JOL → Distract → Test paradigm. 15 invented word-definition pairs (3 difficulty × 5 each) + 2 novel rule systems. Composite: 0.40 × γ + 0.30 × BSS + 0.30 × recall_rate.

**Innovation — Novel stimuli:** All word-definition pairs are invented. They cannot exist in any training corpus, forcing genuine in-context learning assessment.

**Innovation — Constant-confidence penalty:** `if np.std(all_jol_ratings) < 1.0: gamma_norm = 0.0`. Prevents gaming by reporting constant confidence.

**CB results:** mean=0.612, std=0.205, range=0.508. Claude Opus leads (0.790). Interestingly, GPT-5.4 Nano (0.735) nearly matches full GPT-5.4 (0.600) — JOL capability transfers well to smaller models. Gemma 3 4B collapses (0.282), suggesting a threshold below which learning prediction fails entirely.

---

#### Error Detection

**Technique:** Review 72 reasoning chains (correct + erroneous). Composite: 0.30 × weighted_detection + 0.10 × F1 + 0.25 × localization + 0.20 × (1−ECE) + 0.15 × γ.

**Innovation — Statistical fallacy expansion:** Includes ecological fallacy, Berkson's paradox, multiple comparisons/p-hacking, survivorship bias, regression to the mean, and misapplied Simpson's paradox at difficulty level 3.

**CB results:** mean=0.821, std=0.194, range=0.580. DeepSeek-R1 leads (0.981), closely followed by Gemini Flash (0.969). This is the easiest metacognition benchmark — models are generally good at spotting errors in others' reasoning. The statistical fallacy items are what separate frontier from mid-tier models.

---

#### Contamination Canary

**Technique:** Mix 10 fabricated "facts" with 10 well-known real facts. Score = max(0, BSS) — pure discrimination between real and fabricated items.

**Innovation — v2 discrimination design:** v1 used all-fabricated items → every model confabulated → BSS=0 (useless). v2 mixes real + fabricated, testing whether models can *discriminate* known from unknowable.

**CB results:** mean=0.656, std=0.417, range=0.992. **Best single discriminator in metacognition.** Gemini 2.5 Pro leads (0.992). Both Gemma models score exactly 0.000 — complete failure to distinguish fabricated from real facts, hallucinating with high confidence on every fabricated item. This bimodal split (frontier models at 0.81–0.99, small models at 0.00) creates the widest range of any metacognition benchmark.

---

#### Metacognitive Control

**Technique:** Allocation-of-study-time paradigm. Present 10-section passage → 5 questions → model chooses exactly 3 sections to "re-read" (limited budget) → answer questions. Composite: 0.35 × selection_relevance + 0.35 × strategic_gain + 0.30 × accuracy.

**Innovation:** Tests metacognitive *control* (regulation), not just *monitoring*. The budget constraint forces strategic allocation — random selection would yield ~30% relevance.

**CB results:** mean=0.766, std=0.251, range=0.723. Three frontier models tie at 0.91 (Claude Opus, Gemini Pro, GPT-5.4). Gemma 3 1B (0.188) shows essentially no strategic selection ability. The 0.723 range makes this the second-best discriminator in the metacognition track.

---

#### Epistemic Humility

**Technique:** Mix of 10 answerable + 14 genuinely unanswerable questions (future events, fabricated entities, underspecified, paradoxical, private info, subjective). Score: 0.35 × detection + 0.25 × (1−confabulation) + 0.20 × (1−false_refusal) + 0.20 × explanation_quality.

**Innovation:** Tests outright refusal vs. confabulation on genuinely unanswerable questions. Includes obscure-but-real answerable items to penalize over-refusal.

**CB results:** mean=0.725, std=0.181, range=0.453. Claude Opus leads (0.879). Notably, Gemma 3 1B (0.451) outscores Gemma 3 4B (0.426) — the only metacognition benchmark where the 1B model beats the 4B model, suggesting that epistemic humility may be partially independent of general capability.

---

#### Epistemic Revision

**Technique:** Teach 10 rules in 2 fictional systems ("Zorblatt Chemistry", "Nexari Ecology") with examples → present contradicting observations → model must revise beliefs and apply revised rules. Score: 0.80 × transfer_accuracy + 0.20 × (1−perseveration_rate).

**Innovation:** Tests belief *revision* under contradicting evidence, not just accumulation. Uses completely novel fictional systems.

**CB results:** mean=0.747, std=0.174, range=0.503. Claude Opus leads (0.960). The scoring heavily weights transfer accuracy (80%), measuring whether revised beliefs actually propagate to new scenarios rather than just being stated.

---

#### Learning Monitoring

**Technique:** Present novel rules one at a time → after each, test application AND self-assessment (0–100) → compute γ between self-assessment and actual performance.

**Innovation — Difficulty 3–4 rule systems:** Symbol d4 (3-pass with pair merging + count-based reversal + parity swap) and Number d4 (3 operators with mod arithmetic, wrap-around addition, nested expressions).

**CB results:** mean=0.677, std=0.312, range=0.712. DeepSeek-R1 leads (0.965). Sharp drop-off below frontier: GPT-5.4 Nano (0.410), Gemma 3 4B (0.253), Gemma 3 1B (0.263). This benchmark strongly separates models that can accurately track their own learning from those that cannot.

---

### 5.2 Executive Functions Benchmarks

#### Cognitive Reflection Test (CRT)

**Technique:** Procedurally generated problems with intuitive-but-wrong answers across 3 difficulty tiers (extreme=3.0×, hard=2.0×, easy=1.0× weight). Score: difficulty-weighted accuracy.

**Innovation — Novel items with randomizable seeds:** Replaces classic bat-and-ball items with novel algebraic-trap problems. Specific intuitive wrong answers are tracked — random errors ≠ trap errors.

**CB results:** mean=0.665, std=0.246, range=0.601. Claude Opus leads (0.921), dramatically exceeding human general public (~30%) and MIT students (~48%). Gemma 3 1B (0.320) falls near human baseline, suggesting it still falls for intuitive traps. The wide range makes CRT the second-best discriminator in the EF track.

---

#### N-Back Working Memory

**Technique:** 2-back through 5-back with transformation variants (alphabet-shift matching) and ~15% lure trials at N±1. Score: accuracy across all conditions.

**Innovation — Extended depth + transformation variants + lure trials:** Standard N-back benchmarks stop at 3-back, which most frontier models ace trivially. Extending to 5-back with transformation rules (e.g., "match if current letter is the letter 2 positions after the one 3-back") and lure trials (items matching at N±1 but not N) pushes frontier models harder.

**CB results:** mean=0.561, std=0.474, range=0.974. **Best single discriminator in executive functions** and across both tracks combined. Three frontier models score perfect 1.000 (Gemini Pro, Claude Opus, Gemini Flash), DeepSeek-R1 near-perfect (0.993), then a cliff: GPT-5.4 drops to 0.288, Gemma models collapse to <0.05. Human performance at 4-back (~50%) sits between frontier and mid-tier models, suggesting frontier LLMs have surpassed human working memory capacity.

---

#### Task Switching

**Technique:** Batch presentation with 4 compositional rules (prime check, position parity, divisibility, vowel proximity) and post-stimulus cuing. Score: 0.10 × baseline + 0.25 × slow-switch + 0.35 × rapid + 0.30 × switch-cost metric.

**Innovation — Post-stimulus cuing:** The stimulus appears before the rule in rapid/random blocks, forcing genuine task-set reconfiguration. Four compositional rules with congruency-aware item generation prevent ceiling effects.

**CB results:** mean=0.735, std=0.156, range=0.450. Three frontier models tie at 0.844 (Gemini Pro, Gemini Flash, DeepSeek-R1). This is the weakest discriminator among the EF benchmarks at the frontier tier (top 4 models within 0.054) but separates well at the bottom. The compositional rule design avoids the ceiling effects that plagued simpler task-switching paradigms.

---

#### Tower of London (ToL)

**Technique:** Disc-rearrangement problems requiring optimal move sequences. 3 pegs with capacity constraints. Score: move optimality (optimal moves / actual moves).

**Innovation — BFS-verified problems with capacity constraints:** All problems verified via breadth-first search for optimal move count. Capacity constraints prevent trivial solutions.

**Innovation — 5-strategy parser cascade:** Robust parsing separates response format failures from cognitive failures, handling diverse output formats while excluding chain-of-thought reasoning traces.

**CB results:** mean=0.573, std=0.363, range=1.000. Gemini 2.5 Pro achieves **perfect** planning (1.000). DeepSeek-R1 (0.850) and Claude Opus (0.842) are close behind. Gemma 3 1B scores exactly 0.000 — cannot produce a single valid solution. Against the human baseline of ~55% at 5-move depth, four frontier models exceed human planning ability. The full 0–1 range (1.000) makes ToL the widest-range benchmark in either track.

---

#### Wisconsin Card Sort (WCST)

**Technique:** Hidden sorting dimensions, probabilistic feedback (85% reliable), variable shift criteria, and multi-dimensional phases. Score: 0.25 × accuracy + 0.45 × perseveration_avoidance + 0.30 × categories_completed.

**Innovation — Probabilistic feedback + multi-dimensional phases:** Standard WCST uses deterministic feedback with single-dimension sorting. Adding 85% reliable feedback and phases requiring two dimensions simultaneously makes the task substantially harder and prevents rule-memorization shortcuts.

**CB results:** mean=0.450, std=0.145, range=0.494. **Hardest benchmark in either track.** GPT-5.4 leads decisively (0.768) — the only model above 0.50. Even frontier models struggle: Claude Opus (0.374), DeepSeek-R1 (0.385), Gemini Pro (0.465). Surprisingly, Gemma 3 1B (0.425) outscores Claude Opus, Gemma 3 4B, and DeepSeek-R1 — suggesting that WCST difficulty under uncertainty is not purely a function of scale.

---

## 6. Comparative Analysis

### 6.1 Difficulty Profile

| Difficulty Tier | Metacognition | Executive Functions |
|-----------------|---------------|---------------------|
| **Hard** (mean < 0.50) | Calibration (0.448) | WCST (0.450) |
| **Moderate** (0.50–0.70) | FOK (0.558), JOL (0.612), Canary (0.656), Learning Monitoring (0.677) | N-Back (0.561), ToL (0.573), CRT (0.665), GPT-5.4 (0.670) |
| **Easy** (> 0.70) | Epistemic Humility (0.725), Revision (0.747), Control (0.766), Error Detection (0.821) | Task Switching (0.735) |

Metacognition has more benchmarks in the "easy" tier (4 of 9 above 0.70) but its hardest benchmark (calibration, 0.448) is harder than EF's hardest (WCST, 0.450) in absolute terms. Executive functions has more benchmarks clustered in the moderate range with extreme bimodal splits.

### 6.2 Discrimination Power

| Benchmark | Track | Std | Range |
|-----------|-------|-----|-------|
| **N-Back Working Memory** | EF | **0.474** | 0.974 |
| **Contamination Canary** | MC | **0.417** | 0.992 |
| **Tower of London** | EF | 0.363 | **1.000** |
| Learning Monitoring | MC | 0.312 | 0.712 |
| Metacognitive Control | MC | 0.251 | 0.723 |
| CRT | EF | 0.246 | 0.601 |
| JOL | MC | 0.205 | 0.508 |
| Error Detection | MC | 0.194 | 0.580 |
| Epistemic Humility | MC | 0.181 | 0.453 |
| Retrospective Calibration | MC | 0.178 | 0.493 |
| Epistemic Revision | MC | 0.174 | 0.503 |
| FOK | MC | 0.161 | 0.489 |
| Task Switching | EF | 0.156 | 0.450 |
| WCST | EF | 0.145 | 0.494 |

The top 3 discriminators are split: 2 EF (N-Back, ToL), 1 MC (Canary). Executive functions achieves higher peak discrimination through its bimodal benchmarks (N-Back, ToL), while metacognition provides more uniform mid-range discrimination across its 9 benchmarks.

### 6.3 Model Rankings Compared

| Model | MC Rank | MC Score | EF Rank | EF Score | Rank Δ |
|-------|:-------:|:--------:|:-------:|:--------:|:------:|
| Claude Opus 4.6 | **1st** | 0.825 | 2nd | 0.785 | −1 |
| DeepSeek-R1 | 2nd | 0.813 | 4th | 0.754 | −2 |
| Gemini 2.5 Flash | 2nd | 0.813 | 3rd | 0.769 | −1 |
| Gemini 2.5 Pro | 4th | 0.808 | **1st** | 0.835 | +3 |
| GPT-5.4 | 5th | 0.778 | 5th | 0.670 | 0 |
| GPT-5.4 Nano | 6th | 0.613 | 6th | 0.423 | 0 |
| Gemma 3 4B | 7th | 0.419 | 7th | 0.304 | 0 |
| Gemma 3 1B | 8th | 0.274 | 8th | 0.233 | 0 |

**Key divergence:** Gemini 2.5 Pro ranks 4th in metacognition but 1st in executive functions — a 3-rank jump driven by perfect ToL (1.000) and perfect N-Back (1.000). Its metacognition weakness is JOL (0.600, 7th of 8). Conversely, DeepSeek-R1 ranks 2nd in metacognition but only 4th in EF, held back by weaker CRT (0.698) and N-Back (0.993 — near-perfect but not 1.000).

Bottom 4 ranks are identical across both tracks — the performance hierarchy is stable below frontier tier.

### 6.4 Qualitative Cognitive Differences

| Dimension | Metacognition | Executive Functions |
|-----------|---------------|---------------------|
| **What it measures** | Self-knowledge, monitoring accuracy, strategic regulation | Task control, flexibility, planning, inhibition |
| **Where models fail worst** | Calibration — knowing confidence levels | WCST — adapting under uncertainty with noisy feedback |
| **Ceiling effects** | None (no model scores 1.000 on any benchmark) | N-Back (3/8 = 1.000), ToL (1/8 = 1.000) |
| **Floor effects** | Canary (2/8 = 0.000) | ToL (1/8 = 0.000), N-Back (2/8 < 0.05) |
| **Distribution shape** | Gradual gradient from 0.27 to 0.83 | Bimodal cliff on N-Back and ToL |
| **Human gap** | Calibration: 0.448 vs 0.80–0.90 (severe) | ToL: 0.573 vs ~0.75 (moderate); N-Back: frontier exceeds human 4-back |

### 6.5 Cross-Track Findings

**1. No model dominates both tracks.** Claude Opus leads metacognition (0.825) but Gemini Pro leads executive functions (0.835). Only Gemini Flash is top-3 in both (2nd MC, 3rd EF).

**2. Two-tier metacognition dissociation.** Scores separate into *monitoring tasks* (canary, epistemic humility, error detection, epistemic revision, control, learning monitoring; mean 0.73) and *prospective self-assessment* (FOK, JOL, calibration; mean 0.54). This 1.4:1 ratio holds across all 8 models, suggesting that evaluating external information is fundamentally easier than predicting one's own future performance. This mirrors the Nelson & Narens (1990) monitoring→control distinction.

**3. N-Back reveals a frontier cliff.** The combination of 5-back depth, transformation variants, and lure trials creates a binary threshold: 4 models at ≥0.993, then GPT-5.4 drops to 0.288, and smaller models collapse below 0.15. No metacognition benchmark shows this kind of cliff — they degrade more gradually.

**4. WCST is the great equalizer.** With a mean of just 0.450, it's the only benchmark where a small model (Gemma 3 1B: 0.425) outscores multiple frontier models (Claude Opus: 0.374, DeepSeek-R1: 0.385). Set-shifting under probabilistic feedback and hidden multi-dimensional phases appears to be a genuinely distinct capability from both scale and general reasoning.

**5. Scaling reveals selective transfer.** GPT-5.4 Nano retains 79% of full GPT-5.4's metacognition performance (0.613 vs 0.778) but only 63% of its EF performance (0.423 vs 0.670). Within metacognition, Nano matches GPT-5.4 on JOL (0.735 vs 0.600 — Nano actually *exceeds* it) and control (0.797 vs 0.910), but collapses on learning monitoring (0.410 vs 0.820) and canary (0.683 vs 0.920). Some cognitive capabilities compress well; others require scale.

**6. Planning is the most scale-dependent ability.** ToL shows the widest range (1.000) and a clear size gradient: Gemini Pro 1.000 → DeepSeek-R1 0.850 → Claude Opus 0.842 → Gemini Flash 0.700 → GPT-5.4 0.690 → Nano 0.360 → Gemma 4B 0.140 → Gemma 1B 0.000. Multi-step look-ahead planning is the purest scale-dependent capability in either track.

---

## 7. Innovation Comparison

### Shared Technical Innovations

| Innovation | Description |
|------------|-------------|
| Procedurally generated stimuli | Seeded RNG, cannot appear in training data |
| Contamination resistance | Fictional domains, invented associations, novel items |
| Composite multi-metric scoring | Each benchmark combines multiple cognitive metrics |
| Robust output parsing | Multi-strategy fallback parsers separate format failures from cognitive failures |
| All data inlined | No external dependencies; deterministic reproducibility |

### Metacognition-Specific Innovations

| Innovation | Benchmark | Why Novel |
|------------|-----------|-----------|
| Two-phase confidence separation | FOK | Prevents post-hoc rationalization; separate `kbench.chats.new()` contexts |
| Invented word-definition pairs + distractor interval | JOL | Forces genuine in-context learning assessment |
| Constant-confidence penalty | JOL | Closes gaming vector (constant-zero → free γ_norm) |
| BSS over ECE | Calibration | ECE rewards always-hedging-to-50%; BSS penalizes lack of discrimination |
| Extreme-item accuracy weighting | Calibration | 50% weight on extreme items exposes overconfidence on hard questions |
| Discrimination-based canary (v2) | Canary | v1 was useless (all-fabricated = all-confabulate) |
| Allocation-of-study-time paradigm | Control | Tests regulation, not just monitoring; budget constraint forces strategy |
| Fictional world belief revision | Epistemic Revision | Separates revision from accumulation |
| Difficulty 3–4 rule scaling | Learning Monitoring | Complex rules dramatically improve model separation |
| Statistical fallacy items | Error Detection | Berkson's paradox, ecological fallacy, p-hacking as hard items |

### Executive Functions-Specific Innovations

| Innovation | Benchmark | Why Novel |
|------------|-----------|-----------|
| 5-back + transformation variants + lure trials | N-Back | Extends far beyond standard 3-back; lures test position-tracking precision |
| Post-stimulus cuing with compositional rules | Task Switching | Forces genuine reconfiguration; 4 rules prevent ceiling |
| BFS-verified problems with capacity constraints | ToL | Guarantees optimal solutions exist; prevents trivial approaches |
| 5-strategy parser cascade | ToL | Separates format failures from planning failures |
| Probabilistic feedback + multi-dimensional phases | WCST | 85% reliable feedback + 2-dimension phases prevent simple strategies |
| Novel algebraic-trap CRT items with seeds | CRT | Avoids contamination from published 3-item CRT; tracks specific traps |

---

## 8. Summary

**Metacognition is the more uniformly challenging track** — no model achieves a perfect score on any benchmark, difficulty distributes across a continuous gradient, and it reveals a fundamental 1.4:1 dissociation between monitoring and prospective self-assessment that holds across all model scales.

**Executive functions is the more dramatically discriminating track** — N-Back and ToL create cliff-edge separations between frontier and non-frontier models, and WCST exposes a capability (set-shifting under uncertainty) that appears orthogonal to model scale.

**The tracks test genuinely different cognitive faculties.** Gemini 2.5 Pro ranks 1st on executive functions but 4th on metacognition. Claude Opus ranks 1st on metacognition but 2nd on executive functions. No model dominates both — supporting the construct validity of separating these cognitive dimensions.

**The hardest open problems are calibration and set-shifting under uncertainty.** Calibration (MC mean=0.448 vs human 0.80–0.90) and WCST (EF mean=0.450) are the two benchmarks where even frontier models fall significantly short of human performance. These represent the most important targets for future model improvement.

---

*All data from Kaggle Community Benchmarks platform. 8 models × 14 benchmarks = 112 evaluation points, 100% coverage. Competition: Measuring Progress Toward AGI — Cognitive Abilities (Google DeepMind, April 2026).*
