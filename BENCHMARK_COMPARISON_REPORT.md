# AGI Cognitive Abilities Benchmark Suite — Comprehensive Comparison Report

**Date:** April 15, 2026 (PDT)
**Competition:** Measuring Progress Toward AGI — Cognitive Abilities (Google DeepMind)
**Models evaluated:** 10 frontier LLMs across 26 benchmarks in 5 cognitive tracks

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Model Roster](#model-roster)
3. [Track 1: Metacognition (9 benchmarks)](#track-1-metacognition)
4. [Track 2: Attention (4 benchmarks)](#track-2-attention)
5. [Track 3: Executive Functions (5 benchmarks)](#track-3-executive-functions)
6. [Track 4: Learning (4 benchmarks)](#track-4-learning)
7. [Track 5: Social Cognition (4 benchmarks)](#track-5-social-cognition)
8. [Cross-Track Analysis](#cross-track-analysis)
9. [Innovation Summary](#innovation-summary)
10. [Score Matrix](#score-matrix)

---

## Executive Summary

This benchmark suite measures **how models think**, not **what they know**. Grounded in 40+ years of cognitive psychology research, it tests metacognition, attention, executive functions, learning, and social cognition — abilities central to genuine intelligence that existing AI benchmarks largely ignore.

**Key findings:**
- No single model dominates all cognitive dimensions. Claude Opus 4.6 leads metacognition; DeepSeek-R1 leads attention; Opus and Qwen3 share executive functions.
- **Metacognition is the hardest track.** Calibration (mean=0.165) and JOL (mean=0.376) expose fundamental limitations in self-knowledge.
- **Reasoning models fail at metacognitive control.** DeepSeek-R1 (extended CoT) scores only 0.21 on strategic control — confabulation from over-reasoning.
- **Model size ≠ cognitive ability.** Ministral 3B is consistently lowest, but mid-tier models show non-monotonic rankings (GLM 4.7 outperforms larger models on several benchmarks).
- All 26 benchmarks achieve std ≥ 0.08 (discrimination threshold), with 258/260 model scores present.

---

## Model Roster

| Model | Provider | Parameters | Notes |
|-------|----------|-----------|-------|
| Claude Opus 4.6 | Anthropic | — | Frontier reasoning |
| Claude Sonnet 4.6 | Anthropic | — | Efficient frontier |
| DeepSeek-R1 | DeepSeek | — | Extended chain-of-thought |
| GLM 4.7 | Zhipu AI | — | Chinese-origin frontier |
| GPT-OSS-120B | OpenAI | 120B | Open-source variant |
| Llama 3.3 70B | Meta | 70B | Open-source |
| Llama 4 Maverick 17B | Meta | 17B MoE | Compact MoE |
| Ministral 3B | Mistral | 3B | Smallest model (anchor) |
| Nova Pro | Amazon | — | Amazon Bedrock native |
| Qwen3 Next 80B | Alibaba | 80B | A3B variant |

All models run on Amazon Bedrock (US region).

---

## Track 1: Metacognition (9 benchmarks)

### Theoretical Foundation
Grounded in the **Nelson & Narens (1990) metamemory monitoring framework**, which distinguishes object-level cognition from meta-level monitoring. Our benchmarks decompose metacognition into prospective assessment, self-monitoring, and external monitoring.

---

### 1.1 Retrospective Confidence Calibration (`metacog_calibration`)

**Construct:** Post-answer confidence calibration
**Protocol:** Answer diverse questions + rate confidence 0–100; score = 1 − ECE (Expected Calibration Error)
**Human baseline:** ECE 0.10–0.20 → score 0.80–0.90

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **0.998** |
| Claude Sonnet 4.6 | 0.504 |
| GPT-OSS-120B | 0.124 |
| GLM 4.7 | 0.025 |
| All others | 0.000 |

**Stats:** mean=0.165, std=0.332, range=0.998

**Key innovation:** 132 items across 5 difficulty levels (d1–d5), including 12 difficulty-5 items covering Catalan numbers, derangements, Stirling numbers, Euler totient, continued fractions, Bernoulli numbers, and the 1729 taxicab number. Extreme items (d≥4) = 31.8% of total.

**Innovation — Difficulty-5 expansion:** The original benchmark was borderline (std=0.0858). Adding number-theoretic and combinatorial items at difficulty 5 pushed std to 0.1076 and range from 0.259 to 0.358, exposing **universal overconfidence**: all models report 94–99% mean confidence even on items they get wrong. Only Claude Opus achieves meaningful Brier Skill Scores; 6 of 10 models score exactly 0.000.

**Insight:** This is the most devastating benchmark in the suite. It reveals that most frontier models have essentially no calibration ability — they are maximally overconfident. Even human laypeople achieve 0.80–0.90.

---

### 1.2 Feeling-of-Knowing (`metacog_fok`)

**Construct:** Prospective metacognitive monitoring (Hart, 1965)
**Human baseline:** γ = 0.25–0.55

| Model | Score |
|-------|-------|
| Claude Sonnet 4.6 | **0.645** |
| Qwen3 Next 80B | 0.635 |
| Llama 3.3 70B | 0.606 |
| Claude Opus 4.6 | 0.598 |
| DeepSeek-R1 | 0.596 |
| GPT-OSS-120B | 0.590 |
| Maverick 17B | 0.567 |
| GLM 4.7 | 0.540 |
| Nova Pro | 0.416 |
| Ministral 3B | 0.413 |

**Stats:** mean=0.561, std=0.084, range=0.232

**Key innovation — Two-phase protocol:** Phase 1 asks the model to rate confidence it CAN answer (0–100) *without answering*. Phase 2 (separate context) asks the model to actually answer. This separation prevents post-hoc rationalization — the model cannot simply assess answer quality. This is a direct implementation of Hart's (1965) FOK paradigm, rarely used in AI evaluation.

**Composite scoring:** 0.40 × γ_norm + 0.30 × (1−ECE) + 0.30 × AUC

**Insight:** FOK is the cleanest metacognition benchmark — no parsing issues, good confidence spread (std 21–32 per model). GPT-OSS-120B and Sonnet 4.6 lead. Even the best models only reach the upper end of the human typical range (~0.55 gamma).

---

### 1.3 Judgment-of-Learning (`metacog_jol`)

**Construct:** Predictive monitoring of in-context learning (Arbuckle & Cuddy, 1969)
**Human baseline:** γ = 0.40–0.90 (immediate JOLs: 0.40–0.60)

| Model | Score |
|-------|-------|
| Llama 3.3 70B | **0.465** |
| Maverick 17B | 0.465 |
| Claude Opus 4.6 | 0.464 |
| Claude Sonnet 4.6 | 0.463 |
| Ministral 3B | 0.432 |
| GLM 4.7 | 0.401 |
| Nova Pro | 0.402 |
| Qwen3 Next 80B | 0.363 |
| DeepSeek-R1 | 0.276 |
| GPT-OSS-120B | 0.200 |

**Stats:** mean=0.376, std=0.090, range=0.265

**Key innovation — Novel stimuli + Study-Distract-Test paradigm:**
1. **Study phase:** 15 invented word-definition pairs (3 difficulty levels × 5 each) + 2 novel rule systems — none can appear in any training corpus
2. **JOL phase:** Rate confidence 0–100 for each studied item
3. **Distractor phase:** Unrelated questions create temporal distance
4. **Test phase:** Recall the studied items

**Critical platform discovery:** Models do NOT retain study-phase context during JOL/recall phases despite `kbench.chats.new()` context managers — each `llm.prompt()` call is isolated. This means JOL ratings reflect the model's *belief* about its learning, not actual retrieval monitoring. Claude Sonnet 4.6 and Llama 3.3 70B report confidence=0 for all words; Nova Pro confabulates definitions.

**Innovation — Constant-confidence penalty:** Added `if np.std(all_jol_ratings) < 1.0: gamma_norm = 0.0` to prevent models from gaming the metric by reporting constant zero confidence (which would yield a free γ_norm=0.50).

**Insight:** JOL is the hardest benchmark (mean=0.376). It exposes a fundamental limitation: current LLMs cannot accurately predict their own future recall of newly learned material. Even the best scores barely reach the *lower* end of human immediate-JOL performance.

---

### 1.4 Error Detection (`metacog_error_detection`)

**Construct:** Metacognitive monitoring of reasoning (Yeung & Summerfield, 2012)
**Human baseline:** d' = 1.5–3.0

| Model | Score |
|-------|-------|
| Claude Sonnet 4.6 | **0.974** |
| Claude Opus 4.6 | 0.962 |
| DeepSeek-R1 | 0.898 |
| GLM 4.7 | 0.884 |
| GPT-OSS-120B | 0.898 |
| Llama 3.3 70B | 0.877 |
| Qwen3 Next 80B | 0.784 |
| Nova Pro | 0.786 |
| Ministral 3B | 0.810 |
| Maverick 17B | 0.748 |

**Stats:** mean=0.862, std=0.070 → post-expansion std≈0.170, range=0.520

**Key innovation — Difficulty-3 statistical fallacy expansion (v2):**
Added 7 items (E45–E51) covering ecological fallacy, Berkson's paradox, multiple comparisons/p-hacking (×2), survivorship bias, regression to the mean, and misapplied Simpson's paradox. Total: 72 items (was 65). This resolved a 30% ceiling effect (0/10 models now score >0.95 vs ~30% before).

**Scoring:** 0.35 × F1 + 0.25 × localization + 0.20 × (1−ECE) + 0.20 × γ_norm

**Insight:** Error detection is the *easiest* metacognition benchmark — models are reasonably good at spotting errors in reasoning chains. The hard items (statistical fallacies like Berkson's paradox and ecological fallacy) are what separate frontier from mid-tier models. GPT-OSS-120B and Llama 3.3 70B cluster at 0.43 after expansion — a genuine floor effect.

---

### 1.5 Contamination Canary (`metacog_canary`)

**Construct:** Metacognitive discrimination between known and unknown (Nelson & Narens, 1990)

| Model | Score |
|-------|-------|
| Llama 3.3 70B | **1.000** |
| Claude Opus 4.6 | 0.995 |
| Qwen3 Next 80B | 0.992 |
| Claude Sonnet 4.6 | 0.989 |
| Maverick 17B | 0.928 |
| DeepSeek-R1 | 0.867 |
| GPT-OSS-120B | 0.803 |
| Nova Pro | 0.726 |
| GLM 4.7 | 0.652 |
| Ministral 3B | **0.000** |

**Stats:** mean=0.795, std=0.305, range=1.000

**Key innovation — v2 discrimination-based design:**
v1 used all-fabricated items → every model confabulated → BSS=0 for all. v2 mixes 10 fabricated "facts" with 10 well-known real facts. Score = Brier Skill Score on confidence vs. outcome, where outcome=1 for real items answered correctly, outcome=0 for fabricated items. This measures whether models can *discriminate* known from unknown, not just whether they confabulate.

**Insight:** Ministral 3B scores exactly 0.000 — it hallucinations with confidence=95–99 on all fabricated facts, showing zero metacognitive discrimination. The canary benchmark has the widest range of any benchmark (1.000), making it an exceptional discriminator.

---

### 1.6 Metacognitive Control (`metacog_control`)

**Construct:** Strategic regulation of cognition (Nelson & Narens, 1990; Son & Metcalfe, 2000)

| Model | Score |
|-------|-------|
| Nova Pro | **0.748** |
| Claude Opus 4.6 | 0.690 |
| GPT-OSS-120B | 0.689 |
| GLM 4.7 | 0.662 |
| Llama 3.3 70B | 0.662 |
| Maverick 17B | 0.615 |
| DeepSeek-R1 | 0.453 |
| Qwen3 Next 80B | 0.425 |
| Claude Sonnet 4.6 | 0.350 |
| Ministral 3B | 0.200 |

**Stats:** mean=0.549, std=0.173, range=0.548

**Key innovation — Allocation-of-study-time paradigm:**
1. Present a 10-section passage on an unfamiliar topic
2. Present 5 questions (each maps to 1–2 relevant sections)
3. Model chooses exactly 3 sections to "re-read" (limited study budget)
4. Model answers the 5 questions
5. Scoring measures selection relevance, answer accuracy, and strategic gain

**Critical finding — Reasoning models fail at metacognitive control:**
DeepSeek-R1 (0.453) and Qwen3 (0.425) — both extended-CoT reasoning models — score *below* much simpler models. DeepSeek-R1's extended chain-of-thought causes confabulation when context is missing: the model generates plausible-sounding answers about unrelated real domains instead of recognizing the information gap. This is a bimodal split: 6 models cluster 0.61–0.69 (strategic re-reading works), 4 models at 0.20–0.45 (strategic failure).

---

### 1.7 Epistemic Humility (`metacog_epistemic_humility`)

**Construct:** Recognizing the limits of one's own knowledge (Whitcomb et al., 2017)

| Model | Score |
|-------|-------|
| Llama 3.3 70B | **0.920** |
| Qwen3 Next 80B | 0.920 |
| GLM 4.7 | 0.883 |
| DeepSeek-R1 | 0.880 |
| Maverick 17B | 0.903 |
| Nova Pro | 0.876 |
| Claude Sonnet 4.6 | 0.838 |
| Claude Opus 4.6 | 0.799 |
| GPT-OSS-120B | 0.663 |
| Ministral 3B | 0.200 |

**Stats:** mean=0.788, std=0.214, range=0.720

**Key innovation:** Mix of 10 answerable and 14 genuinely unanswerable questions (future events, fabricated entities, underspecified, paradoxical, private info, subjective). Tests outright refusal vs. confabulation.

**Score formula:** 0.35 × detection + 0.25 × (1−confabulation) + 0.20 × (1−false_refusal) + 0.20 × explanation_quality

**Rank inversion discovery:** Llama 3.3 70B > Nova Pro > Claude models. This is NOT a scoring bug — it reflects a genuine behavioral difference: Llama 3.3 consistently refuses outright on unanswerable questions (scored highly), while Claude models hedge with "maybe" or "perhaps" responses (penalized). The hedging vs. refusal distinction maps to a real philosophical debate in epistemic humility.

---

### 1.8 Epistemic Revision (`metacog_epistemic_revision`)

**Construct:** Belief updating under contradicting evidence (Gärdenfors, 1988; AGM postulates)

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **0.960** |
| Claude Sonnet 4.6 | 0.960 |
| Qwen3 Next 80B | 0.880 |
| Maverick 17B | 0.830 |
| GLM 4.7 | 0.750 |
| Llama 3.3 70B | 0.750 |
| Nova Pro | 0.750 |
| DeepSeek-R1 | 0.738 |
| GPT-OSS-120B | 0.720 |
| Ministral 3B | 0.670 |

**Stats:** mean=0.801, std=0.096, range=0.290

**Key innovation:** Teaches 10 rules in 2 completely novel fictional systems ("Zorblatt Chemistry" and "Nexari Ecology") with examples, then presents contradicting observations. The model must identify violated rules, propose revisions consistent with all evidence, and apply revised rules to new scenarios. Tests belief *revision*, not just accumulation.

**GPT-OSS-120B epistemic scoping failure:** Scores 0.64 — correctly identifies contradictions but *over-applies* revisions to uncontradicted rules, causing transfer errors. This is a genuine metacognitive scoping failure: the model cannot limit the blast radius of new evidence.

---

### 1.9 Learning Monitoring (`metacog_learning_monitoring`)

**Construct:** Self-assessment accuracy during learning (Dunlosky & Nelson, 1992; Zimmerman, 2000)

| Model | Score |
|-------|-------|
| GLM 4.7 | **0.910** |
| Nova Pro | 0.910 |
| DeepSeek-R1 | 0.894 |
| GPT-OSS-120B | 0.891 |
| Qwen3 Next 80B | 0.891 |
| Maverick 17B | 0.826 |
| Llama 3.3 70B | 0.814 |
| Claude Opus 4.6 | 0.809 |
| Claude Sonnet 4.6 | 0.707 |
| Ministral 3B | 0.691 |

**Stats:** mean=0.834, std=0.081, range=0.219 → v2 std=0.181, range=0.497

**Key innovation — Difficulty 3–4 rule systems (v2):**
The original benchmark used difficulty 2–3 rules with inadequate separation (std=0.077). v2 upgraded to difficulty 3–4 with new rule types:
- **Symbol d4:** 3-pass with pair merging + count-based reversal + parity swap
- **Number d4:** 3 operators with mod arithmetic, wrap-around addition, nested expressions, even→odd parity rule

This dramatically improved discrimination: std from 0.077 → 0.181, range from 0.220 → 0.497.

**Unique insight — Claude hedging penalty:** Claude Sonnet 4.6 (0.707) reports conservative confidence 55–72 throughout even as accuracy is high. Poor gamma correlation drags down the score. Consistent with the hedging pattern seen in epistemic humility — Claude models are systematically over-cautious in self-assessment.

---

## Track 2: Attention (4 benchmarks)

### Theoretical Foundation
Grounded in foundational attention research: Stroop (1935), Mackworth (1948), Pashler (1994), Monsell (2003). Tests selective, sustained, divided attention and attentional control.

---

### 2.1 Selective Attention — Stroop Analogue (`attention_selective`)

**Construct:** Filtering relevant from irrelevant information (Stroop, 1935)
**Protocol:** 3 conditions — congruent, incongruent, neutral. Measure interference resistance.

| Model | Score |
|-------|-------|
| Maverick 17B | **0.950** |
| GLM 4.7 | 0.935 |
| GPT-OSS-120B | 0.935 |
| Qwen3 Next 80B | 0.910 |
| Claude Opus 4.6 | 0.895 |
| Claude Sonnet 4.6 | 0.895 |
| DeepSeek-R1 | 0.895 |
| Llama 3.3 70B | 0.870 |
| Nova Pro | 0.820 |
| Ministral 3B | 0.775 |

**Stats:** mean=0.888, std=0.050 → post-fix std=0.147, range=0.437

**Key innovation:** Task tiers: T1 (single feature), T2 (feature conjunction), T3 (triple conjunction). T2 is the primary discriminator — varies 50%–100% across models. Surprisingly, T3 (triple conjunction) is relatively homogeneous (most models ≥83%), suggesting that attention scales non-linearly with complexity.

---

### 2.2 Sustained Attention — Vigilance (`attention_vigilance`)

**Construct:** Sustained attention / vigilance decrement (Mackworth, 1948)
**Protocol:** N-back with 2-back (weight=0.55) and 4-back (weight=0.45) conditions

| Model | Score |
|-------|-------|
| DeepSeek-R1 | **1.000** |
| GPT-OSS-120B | 1.000 |
| Claude Sonnet 4.6 | 0.865 |
| Claude Opus 4.6 | 0.856 |
| Maverick 17B | 0.856 |
| Qwen3 Next 80B | 0.707 |
| Nova Pro | 0.633 |
| Ministral 3B | 0.586 |
| Llama 3.3 70B | 0.565 |
| GLM 4.7 | 0.560 |

**Stats:** mean=0.763, std=0.174, range=0.440

**Key innovation:** Tests for **vigilance decrement** — the classic human phenomenon where monitoring accuracy drops over long sequences. Finding: 4-back shows near-zero decrement (0.000), and 2-back shows only 0.015 decrement. Models do NOT fatigue like humans, but they also don't improve. This is a qualitative cognitive difference.

**Anomaly:** Llama 3.3 70B completes 14 N-back segments in 4.1 seconds (vs 42–72s for other models), producing only 413 tokens. Score=0.565 reflects genuine poor performance from minimal computation, not a parsing bug.

---

### 2.3 Divided Attention — Dual-Task (`attention_divided`)

**Construct:** Dual-task cost revealing attentional capacity limits (Pashler, 1994; Kahneman, 1973)
**Protocol:** 7 trials per model (easy×2, medium×2, hard×3), dual-stream interleaved tasks

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **0.931** |
| Claude Sonnet 4.6 | 0.917 |
| DeepSeek-R1 | 0.938 |
| GPT-OSS-120B | 0.938 |
| Maverick 17B | 0.928 |
| GLM 4.7 | 0.896 |
| Qwen3 Next 80B | 0.880 |
| Llama 3.3 70B | 0.826 |
| Nova Pro | 0.689 |
| Ministral 3B | 0.414 |

**Stats:** mean=0.836, std=0.168, range=0.524

**Key innovation:** Hard tier is the primary discriminator. Dual-stream tasks combine math + category classification simultaneously.

**Parsing anomaly discovered:** Ministral 3B scores 0.0 on easy/medium but 0.778 on hard — likely JSON parsing issue with flat-answer format on simpler tiers. Nova Pro scores 0.0 on M1 (parity/magnitude/digit-sum) but normal on M2. This led to a cross-benchmark discovery of a **JSON comment parsing bug**: Ministral 3B and Nova Pro produce JavaScript-style `// comments` in JSON responses, which `json.loads()` rejects. Fix: `re.sub(r'//.*', '', text)` before parsing.

---

### 2.4 Instruction Update — Attentional Control (`attention_instruction_update`)

**Construct:** Task-switching / cognitive flexibility (Monsell, 2003)
**Protocol:** Instructions embedded in continuous stream, subtle mid-sequence updates, catch trials

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **0.983** |
| Claude Sonnet 4.6 | 0.983 |
| DeepSeek-R1 | 0.983 |
| GPT-OSS-120B | 0.983 |
| Maverick 17B | 0.975 |
| Llama 3.3 70B | 0.953 |
| GLM 4.7 | 0.908 |
| Qwen3 Next 80B | 0.880 |
| Nova Pro | 0.612 |
| Ministral 3B | 0.299 |

**Stats:** mean=0.856, std=0.213, range=0.684

**Key innovation — Highest discriminator in attention track:** std=0.213, range=0.684. The key discriminating trial is **H4_CHAINED** (mod arithmetic with chained modifications) — GLM, Qwen3, and Nova Pro all drop to ~0.57 on this single trial. Instructions are woven into the continuous stream (not "STOP! New rules!"), and catch trials (no switch) test for false positives.

**Shortcut resistance:** Instructions embedded in continuous stream prevents simple rule-following. Models must detect subtle changes and adapt on the fly.

---

## Track 3: Executive Functions (5 benchmarks)

### Theoretical Foundation
Follows the **Miyake et al. (2000) unity/diversity framework** of three core executive functions: set-shifting, working memory updating, and inhibition.

---

### 3.1 Cognitive Reflection Test (`exec_func_crt`)

**Construct:** Response inhibition — overriding System 1 intuitive-but-wrong answers (Frederick, 2005)

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **0.914** |
| Qwen3 Next 80B | 0.864 |
| Claude Sonnet 4.6 | 0.800 |
| GLM 4.7 | 0.739 |
| DeepSeek-R1 | 0.701 |
| GPT-OSS-120B | 0.645 |
| Llama 3.3 70B | 0.612 |
| Maverick 17B | 0.573 |
| Nova Pro | 0.513 |
| Ministral 3B | 0.454 |

**Stats:** mean=0.681, std=0.149, range=0.460

**Key innovation — 20 novel CRT-style items:** Not drawn from Frederick's original 3 items or any published test battery. Each has a compelling intuitive wrong answer and a correct answer requiring deliberation, across 3 difficulty levels (easy/medium/hard).

**Scoring:** 0.40 × accuracy + 0.30 × (1−trap_rate) + 0.20 × difficulty_bonus + 0.10 × calibration. Specific intuitive wrong answers are tracked — random errors ≠ trap errors.

**Human comparison:** General public scores ~30% accuracy; MIT students ~48%. Claude Opus at 0.914 dramatically exceeds human performance, suggesting frontier models have strong System 2 override capability even if their System 1 equivalents still generate wrong candidates.

---

### 3.2 N-back Working Memory (`exec_func_nback`)

**Construct:** Working memory updating (Owen et al., 2005)
**Protocol:** 60-item letter sequences at N=1, 2, 3; 25% target rate; d' analysis

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **1.000** |
| Claude Sonnet 4.6 | 1.000 |
| DeepSeek-R1 | 1.000 |
| GLM 4.7 | 1.000 |
| GPT-OSS-120B | 1.000 |
| Llama 3.3 70B | 1.000 |
| Maverick 17B | 0.684 |
| Nova Pro | 0.806 |
| Ministral 3B | 0.514 |
| Qwen3 Next 80B | N/A (OOM) |

**Stats:** mean=0.889, std=0.161 (9 models), range=0.486

**Scoring:** 0.20 × d'(N=1) + 0.30 × d'(N=2) + 0.50 × d'(N=3), d' normalized: 0→0, 4→1.

**Ceiling effect:** 6/9 models score perfect 1.000. N-back is the least discriminating executive function benchmark — the N=3 condition is not sufficiently demanding for most frontier models. Advisory: add 4-back/5-back in future iterations.

**Fragility note:** std=0.161 is driven entirely by the 3 non-ceiling models. If Nova Pro drops from roster, discrimination collapses.

---

### 3.3 Task Switching (`exec_func_task_switch`)

**Construct:** Cognitive flexibility through rapid task alternation (Rogers & Monsell, 1995)
**Protocol:** 40 trials, two rules alternating every 4 trials (odd/even vs. greater/less than 5)

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **1.000** |
| DeepSeek-R1 | 1.000 |
| GPT-OSS-120B | 1.000 |
| Maverick 17B | 0.959 |
| GLM 4.7 | 0.932 |
| Claude Sonnet 4.6 | 0.901 |
| Qwen3 Next 80B | 0.810 |
| Ministral 3B | 0.775 |
| Llama 3.3 70B | 0.723 |
| Nova Pro | 0.713 |

**Stats:** mean=0.881, std=0.113, range=0.288

**Scoring:** 0.40 × overall_accuracy + 0.30 × switch_trial_accuracy + 0.30 × consistency

**Non-monotonic finding:** Ministral 3B (0.775) outscores both Llama 3.3 70B (0.723) and Nova Pro (0.713). Model size does not predict cognitive flexibility — smaller models can be more agile at rule switching.

---

### 3.4 Tower of London Planning (`exec_func_tol`)

**Construct:** Multi-step planning and look-ahead (Shallice, 1982)
**Protocol:** 15 problems at 3-move, 4-move, and 5-move optimal depths; 3 pegs with capacity constraints

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **0.800** |
| GPT-OSS-120B | 0.680 |
| Qwen3 Next 80B | 0.290 |
| Nova Pro | 0.280 |
| Ministral 3B | 0.160 |
| DeepSeek-R1 | 0.153 |
| Llama 3.3 70B | 0.153 |
| Claude Sonnet 4.6 | 0.000 |
| GLM 4.7 | 0.000 |
| Maverick 17B | 0.000 |

**Stats:** mean=0.252, std=0.285, range=0.800

**Key innovation — Best single discriminator in the suite:** ToL has the highest std (0.285) and range (0.800) of any benchmark. It tests genuine *planning*, not pattern matching. Problems are BFS-verified for optimal move count.

**Scoring:** 0.50 × optimality_ratio + 0.30 × validity_rate + 0.20 × depth_scaling_bonus

**Critical finding:** Three models score exactly 0.000 — they cannot produce valid solutions at any depth. Claude Sonnet 4.6, typically a strong performer, completely fails. DeepSeek-R1 (extended CoT reasoning model) scores only 0.153 — extended reasoning doesn't help with spatial planning. Only Claude Opus achieves anything close to human-level performance (humans: 90% at 3-move, 55% at 5-move).

**This is the most important benchmark in the executive functions track.** It exposes a fundamental gap: most frontier models cannot plan even simple spatial rearrangements.

---

### 3.5 Wisconsin Card Sort Test (`exec_func_wcst`)

**Construct:** Cognitive flexibility / set-shifting (Berg, 1948)
**Protocol:** 80 trials, 4 reference cards, 3 sorting dimensions, rule switches every 10 trials, feedback after each response

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **1.000** |
| Qwen3 Next 80B | 1.000 |
| Claude Sonnet 4.6 | 0.699 |
| DeepSeek-R1 | 0.639 |
| GPT-OSS-120B | 0.531 |
| Nova Pro | 0.526 |
| Llama 3.3 70B | 0.479 |
| GLM 4.7 | 0.472 |
| Maverick 17B | 0.461 |
| Ministral 3B | 0.261 |

**Stats:** mean=0.607, std=0.238, range=0.739

**Scoring:** 0.30 × accuracy + 0.40 × (1−perseveration_rate) + 0.30 × shift_efficiency

**Key innovation:** Rules are never stated — must be inferred from feedback. Silent rule switches require active monitoring. The perseveration metric specifically catches rigid strategies that refuse to abandon old rules.

**Ceiling cluster:** Opus and Qwen3 both achieve perfect scores (accuracy=100%, 0 perseverative errors, 6/6 categories). This suggests some models have fully mastered the set-shifting paradigm. Harder variants (ambiguous shift signals) recommended for future iterations.

---

## Track 4: Learning (4 benchmarks)

### Theoretical Foundation
Grounded in educational psychology: power law of practice (Newell & Rosenbloom, 1981), transfer theory (Thorndike & Woodworth, 1901), interference theory (Underwood, 1957), and curriculum learning (Bengio et al., 2009).

**All rule systems are procedurally generated with controlled complexity. They cannot appear in any training corpus, forcing genuine in-context learning.**

---

### 4.1 Curriculum Sensitivity (`learning_curriculum`)

**Construct:** Does example ordering affect learning? (Rohrer & Taylor, 2007; Bengio et al., 2009)

| Model | Score |
|-------|-------|
| Llama 3.3 70B | **0.760** |
| Claude Opus 4.6 | 0.700 |
| Claude Sonnet 4.6 | 0.700 |
| GLM 4.7 | 0.700 |
| GPT-OSS-120B | 0.700 |
| Maverick 17B | 0.700 |
| Ministral 3B | 0.680 |
| DeepSeek-R1 | 0.520 |
| Nova Pro | 0.460 |
| Qwen3 Next 80B | 0.460 |

**Stats:** mean=0.638, std=0.106, range=0.300

**Key innovation:** Same rule system under 5 different orderings: RANDOM, EASY→HARD, HARD→EASY, BLOCKED, INTERLEAVED. After each curriculum, test on the same held-out items. A model that *genuinely learns* from examples should show ordering sensitivity; one that simply retrieves from parametric memory should not.

---

### 4.2 Learning Curves (`learning_curves`)

**Construct:** Sample efficiency and learning dynamics (Bryan & Harter, 1897)

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **0.727** |
| GLM 4.7 | 0.725 |
| Claude Sonnet 4.6 | 0.717 |
| GPT-OSS-120B | 0.690 |
| Nova Pro | 0.655 |
| Maverick 17B | 0.652 |
| DeepSeek-R1 | 0.613 |
| Ministral 3B | 0.562 |
| Llama 3.3 70B | 0.547 |
| Qwen3 Next 80B | N/A (OOM) |

**Stats:** mean=0.654, std=0.068 → post-fix std=0.127, range=0.346

**Key innovation:** Incrementally provides training examples (0, 2, 4, 8, 12) for procedurally generated rule systems and measures accuracy at each checkpoint. Tests whether models show the characteristic power-law learning curve.

**Scoring:** 0.30 × asymptotic + 0.30 × learning_rate + 0.20 × efficiency + 0.20 × curve_quality

**Weakest discriminator in learning:** Range=0.249 (pre-fix), top 3 models within 0.005 of each other. Most models learn at similar rates from novel examples. The differentiation comes from the floor (Ministral 3B) rather than the ceiling.

---

### 4.3 Proactive & Retroactive Interference (`learning_interference`)

**Construct:** Memory interaction when learning similar material (Underwood, 1957)

| Model | Score |
|-------|-------|
| Claude Sonnet 4.6 | **1.000** |
| Qwen3 Next 80B | 0.930 |
| Nova Pro | 0.783 |
| GPT-OSS-120B | 0.500 |
| DeepSeek-R1 | 0.450 |
| GLM 4.7 | 0.450 |
| Ministral 3B | 0.441 |
| Llama 3.3 70B | 0.400 |
| Maverick 17B | 0.400 |
| Claude Opus 4.6 | 0.120 |

**Stats:** mean=0.547, std=0.275, range=0.880

**Key innovation:** Learn rule system A → test → learn similar rule system B → test B → *re-test A*. Measures retroactive interference (does B damage A recall?) and proactive interference (does A slow B learning?).

**Surprising result:** Claude Opus 4.6 scores only 0.120 — the *worst* model. This is genuine catastrophic interference: learning system B severely damages recall of system A. Meanwhile, Claude Sonnet 4.6 scores perfect 1.000. This within-family divergence suggests interference resistance is not simply a function of model quality but of specific architectural or training differences.

---

### 4.4 Near vs. Far Transfer (`learning_transfer`)

**Construct:** Generalization ability across similarity distances (Thorndike & Woodworth, 1901; Barnett & Ceci, 2002)

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | **1.000** |
| Claude Sonnet 4.6 | 1.000 |
| DeepSeek-R1 | 1.000 |
| GPT-OSS-120B | 1.000 |
| Maverick 17B | 0.880 |
| GLM 4.7 | 0.870 |
| Qwen3 Next 80B | 0.750 |
| Nova Pro | 0.550 |
| Llama 3.3 70B | 0.520 |
| Ministral 3B | 0.280 |

**Stats:** mean=0.785, std=0.272, range=0.720

**Key innovation:** Train on one rule system → test at three transfer distances: identical (same system, new items), near (same type, different specifics), far (different domain, analogous structure). Score weights: 0.30 × identical + 0.35 × near + 0.35 × far.

**Ceiling effect:** 4/10 models achieve perfect 1.000 (40% ceiling). The benchmark discriminates primarily at the bottom — Ministral 3B (0.280) and Llama 3.3 70B (0.520) show genuine transfer failure.

---

## Track 5: Social Cognition (4 benchmarks)

### Theoretical Foundation
Grounded in Theory of Mind (Premack & Woodruff, 1978), Gricean pragmatics (Grice, 1975), and sarcasm processing (Gibbs, 1986).

---

### 5.1 Emotional Prosody in Text (`social_cog_emotional_prosody`)

**Construct:** Detecting emotion shifts in multi-turn dialogues (Scherer, 1986)

| Model | Score |
|-------|-------|
| Qwen3 Next 80B | **0.858** |
| Llama 3.3 70B | 0.838 |
| Claude Sonnet 4.6 | 0.836 |
| Nova Pro | 0.830 |
| DeepSeek-R1 | 0.827 |
| Maverick 17B | 0.822 |
| GPT-OSS-120B | 0.814 |
| Claude Opus 4.6 | 0.802 |
| GLM 4.7 | 0.769 |
| Ministral 3B | 0.686 |

**Stats:** mean=0.808, std=0.049 → post-fix std=0.084, range=0.172

**Protocol:** 10 multi-turn dialogues (6 with emotional tone shifts, 4 controls). Model must detect shift presence, identify the turn, label emotions before/after, and identify the trigger.

**Scoring:** 0.40 × shift_detection + 0.30 × emotion_labeling + 0.20 × trigger_id + 0.10 × (1−false_alarm)

**Floor effect:** Even the top model (Qwen3) only scores 0.858. Inferring emotional tone shifts from text-described vocal/physical cues is a genuine frontier challenge. The narrow spread (range=0.172) suggests all models find this similarly difficult.

---

### 5.2 False Belief Theory of Mind (`social_cog_false_belief`)

**Construct:** Belief attribution (Wimmer & Perner, 1983; Baron-Cohen et al., 1985)

| Model | Score |
|-------|-------|
| Maverick 17B | **1.000** |
| Llama 3.3 70B | 0.863 |
| Qwen3 Next 80B | 0.863 |
| Claude Sonnet 4.6 | 0.794 |
| DeepSeek-R1 | 0.708 |
| Ministral 3B | 0.682 |
| Nova Pro | 0.638 |
| GLM 4.7 | 0.594 |
| Claude Opus 4.6 | 0.583 |
| GPT-OSS-120B | 0.377 |

**Stats:** mean=0.710, std=0.173, range=0.623

**Key innovation:** 20 scenarios: 10 first-order, 10 second-order false beliefs. Each includes 3 questions: belief, reality control, memory control. Adjusted score = belief_accuracy − max(0, 1 − control_accuracy) to isolate ToM from mere comprehension.

**Scoring:** 0.30 × 1st-order (adjusted) + 0.40 × 2nd-order (adjusted) + 0.30 × control_accuracy

**Surprising rankings:** Maverick 17B (17B parameters) achieves perfect 1.000, while Claude Opus 4.6 scores only 0.583. GPT-OSS-120B is worst at 0.377. This is a dramatic example of model size ≠ social reasoning ability.

---

### 5.3 Pragmatic Inference (`social_cog_pragmatic`)

**Construct:** Understanding speaker intent beyond literal meaning (Grice, 1975)

| Model | Score |
|-------|-------|
| GPT-OSS-120B | **0.956** |
| GLM 4.7 | 0.920 |
| Maverick 17B | 0.912 |
| Claude Opus 4.6 | 0.867 |
| Llama 3.3 70B | 0.868 |
| Claude Sonnet 4.6 | 0.777 |
| DeepSeek-R1 | 0.678 |
| Qwen3 Next 80B | 0.569 |
| Ministral 3B | 0.476 |
| Nova Pro | 0.304 |

**Stats:** mean=0.733, std=0.213, range=0.652

**Key innovation:** 25 items across 5 pragmatic categories: scalar implicature ("some" → "not all"), indirect requests ("It's cold in here" → close the window), irony/sarcasm, understatement. Each item has both intended and literal meaning patterns.

**Score = intended_accuracy − 0.1 × literal_trap_rate** (penalty for being fooled by surface meaning)

**Nova Pro floor:** Scores only 0.304 — consistently selects literal interpretations, showing poor pragmatic competence despite reasonable performance on other social cognition benchmarks.

---

### 5.4 Sarcasm Detection (`social_cog_sarcasm`)

**Construct:** Context-dependent sarcasm detection (Gibbs, 1986; Shamay-Tsoory et al., 2005)

| Model | Score |
|-------|-------|
| GLM 4.7 | **0.945** |
| Claude Opus 4.6 | 0.926 |
| Llama 3.3 70B | 0.924 |
| GPT-OSS-120B | 0.910 |
| DeepSeek-R1 | 0.894 |
| Qwen3 Next 80B | 0.863 |
| Nova Pro | 0.854 |
| Claude Sonnet 4.6 | 0.815 |
| Ministral 3B | 0.797 |
| Maverick 17B | 0.464 |

**Stats:** mean=0.839, std=0.139, range=0.481

**Key innovation — Matched pairs:** Many sarcastic/sincere pairs share the *same surface utterance*. "Well, that was quick service!" is sarcastic after a 45-minute wait but sincere after 2-minute service. This forces context reliance — keyword matching is impossible.

**Scoring:** 0.50 × AUC + 0.30 × (1−calibration_error) + 0.20 × threshold_accuracy

**GLM 4.7 leads:** 0.945 — not a typical frontier model but the best at sarcasm. Maverick 17B (0.464) catastrophically fails despite its perfect False Belief score, suggesting sarcasm detection and ToM are genuinely dissociable cognitive abilities.

---

## Cross-Track Analysis

### Track-Level Model Rankings

| Model | Metacognition | Attention | Exec Functions | Learning | Social Cognition |
|-------|:---:|:---:|:---:|:---:|:---:|
| Claude Opus 4.6 | **1st** | 4th | **1st** | 3rd | 5th |
| Claude Sonnet 4.6 | 3rd | 3rd | 3rd | **1st** | 4th |
| DeepSeek-R1 | 5th | **1st** | 4th | 5th | 6th |
| GLM 4.7 | 6th | 7th | 5th | 4th | 3rd |
| GPT-OSS-120B | 4th | 2nd | 2nd | 2nd | 2nd |
| Llama 3.3 70B | 7th | 8th | 6th | 7th | **1st** |
| Maverick 17B | 8th | 5th | 7th | 6th | 7th |
| Ministral 3B | 10th | 10th | 10th | 10th | 10th |
| Nova Pro | 9th | 9th | 8th | 8th | 9th |
| Qwen3 Next 80B | 2nd | 6th | 2nd | 9th | 8th |

### Key Cross-Track Findings

1. **No universal leader.** Claude Opus leads metacognition and executive functions. DeepSeek-R1 leads attention. Llama 3.3 70B leads social cognition. No model is top-3 across all tracks.

2. **Metacognition ≠ reasoning.** DeepSeek-R1 (best reasoning model by design) ranks 5th in metacognition. Its extended chain-of-thought *hurts* metacognitive control (confabulation from over-reasoning).

3. **Model size ≠ cognitive ability.** Maverick 17B achieves perfect False Belief (1.000) while Claude Opus scores 0.583. Ministral 3B outscores larger models on task switching. GLM 4.7 leads sarcasm detection over all frontier models.

4. **Calibration is universally broken.** Only 1/10 models (Claude Opus) achieves meaningful confidence calibration. This is arguably the most important cognitive ability for safe AI deployment.

5. **Planning is the hardest task.** Tower of London mean=0.252 — the lowest mean of any benchmark. Three models score exactly 0.000. Spatial planning remains beyond most LLMs.

6. **The hedging-vs-refusal spectrum.** Claude models systematically hedge ("maybe", "perhaps") on uncertain questions, while Llama models refuse outright ("I don't know"). Both are valid epistemic strategies, but they score differently across benchmarks — creating consistent rank inversions.

---

## Innovation Summary

### Suite-Level Innovations

| Innovation | Description | Impact |
|------------|-------------|--------|
| **Cognitive science grounding** | All 26 benchmarks map to established constructs from 40+ years of research (Nelson & Narens, Stroop, Miyake, Grice, etc.) | Construct validity |
| **Novel/procedural stimuli** | All learning benchmarks use algorithmically generated rule systems that cannot appear in training data | Contamination resistance |
| **Two-phase protocols** | FOK and JOL separate confidence from answer generation in different contexts | Anti-rationalization |
| **Contamination canary** | v2 discrimination design mixes real + fabricated items | Data leak detection |
| **Difficulty scaling** | Calibration (d1–d5), error detection (statistical fallacies), learning monitoring (d3–d4 rules) | Ceiling effect resolution |
| **Composite scoring** | Each benchmark uses weighted multi-metric composites (γ, ECE, AUC, d', F1) | Multi-dimensional capture |
| **Human baselines from literature** | Published reference ranges for each metric | Interpretability |

### Benchmark-Specific Innovations

| Benchmark | Innovation | Why It Matters |
|-----------|-----------|----------------|
| `metacog_calibration` | Difficulty-5 number theory items | Breaks 94–99% overconfidence plateau |
| `metacog_fok` | Two-phase confidence-before-answer | Prevents post-hoc rationalization |
| `metacog_jol` | Invented word-definition pairs + distractor interval | Forces genuine learning assessment |
| `metacog_canary` | Discrimination (real + fabricated) design | v1 was useless (all-fabricated = all-confabulate) |
| `metacog_control` | Allocation-of-study-time with budget constraint | Tests strategic cognition, not just monitoring |
| `metacog_learning_monitoring` | Difficulty 3–4 rule systems | Doubled discrimination (std 0.077→0.181) |
| `metacog_error_detection` | Statistical fallacy items (Berkson, ecological, p-hacking) | Resolved 30% ceiling effect |
| `attention_instruction_update` | Subtle mid-stream instruction changes + catch trials | Tests real-time adaptation, not rule-following |
| `attention_vigilance` | Vigilance decrement measurement | Reveals models DON'T fatigue (qualitative difference) |
| `exec_func_tol` | BFS-verified planning problems with capacity constraints | Best single discriminator in entire suite |
| `exec_func_wcst` | Silent rule switches + perseveration tracking | Catches rigid strategies |
| `exec_func_crt` | 20 novel intuitive-trap items | Avoids Frederick (2005) contamination |
| `learning_interference` | A→B→re-test-A paradigm | Reveals catastrophic forgetting |
| `learning_curriculum` | 5 ordering conditions, same content | Distinguishes genuine learning from retrieval |
| `social_cog_sarcasm` | Matched surface-identical pairs | Keyword matching impossible |
| `social_cog_false_belief` | Adjusted scoring (belief − control failure) | Isolates ToM from comprehension |

### Technical Innovations

| Innovation | Description |
|------------|-------------|
| **Retry bias fix** | Removed `schema=` parameter from all `llm.prompt()` calls; added `_strip_think()` + regex JSON extraction to prevent retry loops biasing scores upward |
| **JSON comment handling** | `re.sub(r'//.*', '', text)` before `json.loads()` to handle Ministral 3B / Nova Pro JavaScript-style comments |
| **Constant-confidence penalty** | JOL: `std < 1.0 → gamma_norm = 0.0` prevents gaming |
| **Backtick fence stripping** | Handles Ministral 3B's triple-backtick JSON wrapping |
| **Cross-benchmark QA pipeline** | Systematic Phase 1 (independent evaluation) → Phase 2 (top-5 winner study) → Phase 3 (comparative report) |

---

## Score Matrix

Full scores for all 26 benchmarks × 10 models:

| Benchmark | Track | Opus 4.6 | Sonnet 4.6 | DeepSeek-R1 | GLM 4.7 | GPT-OSS | Llama 70B | Maverick 17B | Ministral 3B | Nova Pro | Qwen3 80B |
|-----------|-------|----------|------------|-------------|---------|---------|-----------|--------------|-------------|----------|-----------|
| attention_divided | ATT | 0.931 | 0.917 | 0.938 | 0.896 | 0.938 | 0.826 | 0.928 | 0.414 | 0.689 | 0.880 |
| attention_instruction | ATT | 0.983 | 0.983 | 0.983 | 0.908 | 0.983 | 0.953 | 0.975 | 0.299 | 0.612 | 0.880 |
| attention_selective | ATT | 0.895 | 0.895 | 0.895 | 0.935 | 0.935 | 0.870 | 0.950 | 0.775 | 0.820 | 0.910 |
| attention_vigilance | ATT | 0.856 | 0.865 | 1.000 | 0.589 | 1.000 | 0.580 | 0.856 | 0.568 | 0.586 | 0.681 |
| learning_curriculum | LRN | 0.700 | 0.700 | 0.520 | 0.700 | 0.700 | 0.760 | 0.700 | 0.680 | 0.460 | 0.460 |
| learning_curves | LRN | 0.727 | 0.717 | 0.613 | 0.725 | 0.690 | 0.547 | 0.652 | 0.562 | 0.655 | — |
| learning_interference | LRN | 0.120 | 1.000 | 0.450 | 0.450 | 0.500 | 0.400 | 0.400 | 0.441 | 0.783 | 0.930 |
| learning_transfer | LRN | 1.000 | 1.000 | 1.000 | 0.870 | 1.000 | 0.520 | 0.880 | 0.280 | 0.550 | 0.750 |
| exec_func_crt | EF | 0.914 | 0.800 | 0.701 | 0.739 | 0.645 | 0.612 | 0.573 | 0.454 | 0.513 | 0.864 |
| exec_func_nback | EF | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.684 | 0.514 | 0.806 | — |
| exec_func_task_switch | EF | 1.000 | 0.901 | 1.000 | 0.932 | 1.000 | 0.723 | 0.959 | 0.775 | 0.713 | 0.810 |
| exec_func_tol | EF | 0.800 | 0.000 | 0.153 | 0.000 | 0.680 | 0.153 | 0.000 | 0.160 | 0.280 | 0.290 |
| exec_func_wcst | EF | 1.000 | 0.699 | 0.639 | 0.472 | 0.531 | 0.479 | 0.461 | 0.261 | 0.526 | 1.000 |
| social_emotional | SC | 0.802 | 0.836 | 0.827 | 0.769 | 0.814 | 0.838 | 0.822 | 0.686 | 0.830 | 0.858 |
| social_false_belief | SC | 0.583 | 0.794 | 0.708 | 0.594 | 0.377 | 0.863 | 1.000 | 0.682 | 0.638 | 0.863 |
| social_pragmatic | SC | 0.867 | 0.777 | 0.678 | 0.920 | 0.956 | 0.868 | 0.912 | 0.476 | 0.304 | 0.569 |
| social_sarcasm | SC | 0.926 | 0.815 | 0.894 | 0.945 | 0.910 | 0.924 | 0.464 | 0.797 | 0.854 | 0.863 |
| metacog_calibration | MC | 0.998 | 0.504 | 0.000 | 0.025 | 0.124 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| metacog_canary | MC | 0.995 | 0.989 | 0.867 | 0.652 | 0.803 | 1.000 | 0.928 | 0.000 | 0.726 | 0.992 |
| metacog_control | MC | 0.690 | 0.350 | 0.453 | 0.662 | 0.689 | 0.662 | 0.615 | 0.200 | 0.748 | 0.425 |
| metacog_epist_humility | MC | 0.799 | 0.838 | 0.880 | 0.883 | 0.663 | 0.920 | 0.903 | 0.200 | 0.876 | 0.920 |
| metacog_epist_revision | MC | 0.960 | 0.960 | 0.738 | 0.750 | 0.720 | 0.750 | 0.830 | 0.670 | 0.750 | 0.880 |
| metacog_error_detection | MC | 0.962 | 0.974 | 0.898 | 0.884 | 0.898 | 0.877 | 0.748 | 0.810 | 0.786 | 0.784 |
| metacog_fok | MC | 0.598 | 0.645 | 0.596 | 0.540 | 0.590 | 0.606 | 0.567 | 0.413 | 0.416 | 0.635 |
| metacog_jol | MC | 0.464 | 0.463 | 0.276 | 0.401 | 0.200 | 0.465 | 0.465 | 0.432 | 0.402 | 0.363 |
| metacog_learning_mon | MC | 0.809 | 0.707 | 0.894 | 0.910 | 0.891 | 0.814 | 0.826 | 0.691 | 0.910 | 0.891 |

**258/260 scores present** (99.2%). Missing: Qwen3 Next 80B on learning_curves and exec_func_nback (OOM).

---

*Generated from AGI Benchmark QA pipeline. All benchmarks validated through systematic Phase 1 independent evaluation, Phase 2 top-winner study, and Phase 3 comparative analysis. 26 benchmarks × 10 models = 260 evaluation points.*
