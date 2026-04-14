# Self-Monitoring Tier Analysis

**Benchmarks:** epistemic_revision, learning_monitoring, control  
**Date:** 2026-04-13  
**Data source:** `score_matrix_metacog_v2.csv`, Q&A transcripts from `qa_transcripts/`

---

## 1. Per-Benchmark Statistics

### metacog_epistemic_revision
| Metric | Value |
|--------|-------|
| N | 10 |
| Mean | 0.7940 |
| Std | 0.1140 |
| Range | 0.3300 |
| Min | 0.6300 (Ministral 3B) |
| Max | 0.9600 (Claude Opus 4.6) |
| Ceiling (≥0.95) | 1/10 (10%) — Claude Opus only |
| Floor (≤0.10) | 0/10 (0%) |

**Rankings:**
1. Claude Opus 4.6: 0.9600
2. Qwen3 Next 80B: 0.9200
3. Claude Sonnet 4.6: 0.9200
4. Llama 4 Maverick 17B: 0.8300
5. Nova Pro: 0.7900
6. DeepSeek-R1: 0.7500
7. Llama 3.3 70B: 0.7500
8. GLM 4.7: 0.7500
9. GPT-OSS-120B: 0.6400
10. Ministral 3B: 0.6300

**Assessment:** Good spread (std=0.114). Mild ceiling on Claude Opus but no floor effect. The v4 design (transfer with raw data points only) works well — forces inductive inference rather than reading comprehension.

---

### metacog_learning_monitoring
| Metric | Value |
|--------|-------|
| N | 10 |
| Mean | 0.8144 |
| Std | 0.0926 |
| Range | 0.2768 |
| Min | 0.6232 (Ministral 3B) |
| Max | 0.9000 (Qwen3 Next 80B) |
| Ceiling (≥0.95) | 0/10 (0%) |
| Floor (≤0.10) | 0/10 (0%) |

**Rankings:**
1. Qwen3 Next 80B: 0.9000
2. Nova Pro: 0.8977
3. DeepSeek-R1: 0.8936
4. GLM 4.7: 0.8754
5. GPT-OSS-120B: 0.8665
6. Llama 4 Maverick 17B: 0.8041
7. Llama 3.3 70B: 0.7973
8. Claude Opus 4.6: 0.7814
9. Claude Sonnet 4.6: 0.7044
10. Ministral 3B: 0.6232

**Assessment:** Weakest discriminator in this tier (std=0.093, borderline ≥0.08). No ceiling/floor. Notably, Claude models rank below mid-tier — they overestimate or underestimate their learning confidence relative to actual performance, showing worse metacognitive calibration during learning than mid-sized models.

---

### metacog_control
| Metric | Value |
|--------|-------|
| N | 10 |
| Mean | 0.4949 |
| Std | 0.2209 |
| Range | 0.4900 |
| Min | 0.2000 (Qwen3 Next 80B) |
| Max | 0.6900 (Claude Opus 4.6) |
| Ceiling (≥0.95) | 0/10 (0%) |
| Floor (≤0.10) | 0/10 (0%) |

**Rankings:**
1. Claude Opus 4.6: 0.6900
2. GPT-OSS-120B: 0.6887
3. Llama 3.3 70B: 0.6617
4. GLM 4.7: 0.6617
5. Nova Pro: 0.6567
6. Llama 4 Maverick 17B: 0.6150
7. Claude Sonnet 4.6: 0.3500
8. DeepSeek-R1: 0.2125
9. Ministral 3B: 0.2125
10. Qwen3 Next 80B: 0.2000

**Assessment:** Best discriminator in this tier (std=0.221). Clear bimodal split: 6 models cluster 0.615–0.690 (strategic re-reading works), 4 models at 0.200–0.350 (strategic failure). No ceiling or floor effects. This is the flagship self-monitoring benchmark.

---

## 2. Tier-Level Summary

| Benchmark | Mean | Std | Range | Discrimination |
|-----------|------|-----|-------|---------------|
| epistemic_revision | 0.794 | 0.114 | 0.330 | Good |
| learning_monitoring | 0.814 | 0.093 | 0.277 | Borderline |
| control | 0.495 | 0.221 | 0.490 | Excellent |

**Tier mean:** 0.701 — consistent with the three-tier metacognition profile (Tier 2 ≈ 0.68 in KNOWLEDGE).

---

## 3. Q&A Transcript Review (5 transcripts per benchmark)

### 3.1 metacog_epistemic_revision

**Models reviewed:** Claude Opus (0.96), Ministral 3B (0.63), Llama 4 Maverick (0.83), GPT-OSS-120B (0.64), Nova Pro (0.79)

**Observations:**
- **Scoring:** Composite score appears only on the final item (qid=41). Individual items (qid 0–40) show the multi-turn learning → verification → contradiction → transfer protocol. Score=None on intermediate items is by design (they feed the final composite).
- **Correct scoring confirmed:** Claude Opus correctly identifies rule violations and applies revised rules in transfer phase. Ministral 3B perseverates on original rules (expected for 3B model).
- **GPT-OSS-120B (0.64 — surprisingly low for 120B):** Transcript shows the model correctly identifies contradictions (R6, R4) but then over-applies revisions — e.g., revises rules that weren't contradicted, creating inconsistencies in transfer answers. This is a genuine epistemic revision failure: the model has difficulty scoping which rules to revise.
- **No parsing artifacts detected** — all responses are well-formed JSON or natural text matching the expected output format.
- **No incorrect scoring detected** — score differences align with observable behavioral differences in transcripts.

### 3.2 metacog_learning_monitoring

**Models reviewed:** Qwen3 80B (0.90), Ministral 3B (0.62), Llama 4 Maverick (0.80), Claude Sonnet (0.70), GLM 4.7 (0.88)

**Observations:**
- **Protocol:** 39 items across 3 rule systems (2 symbol transform, 1 number system). Each item tests both answer correctness and learning_confidence calibration. Composite computed at final item.
- **Claude Sonnet (0.70 — below average):** Transcript reveals Sonnet reports confidence 55–72 throughout, never adjusting upward even as it masters rules. Actual accuracy is high but reported confidence remains conservative → poor gamma correlation between confidence and accuracy, dragging down monitoring score. This is a genuine Sonnet behavioral trait (hedging), not a scoring bug.
- **Ministral 3B (0.62):** Makes rule application errors (e.g., qid=19: answers 4 instead of 5 for flim(1,4), acknowledges confusion in reasoning). Also reports confidence=50-70 regardless of performance. Both learning AND monitoring are poor.
- **Qwen3 80B (0.90):** Gives well-calibrated confidence (20 for 1/5 rules known, 60 for 2/3 rules, 95 for 5/5 rules). Answers are also correct. Strong correlation → high gamma.
- **No parsing artifacts** — JSON parsing works cleanly across all models, including GLM 4.7's markdown-wrapped JSON (```json blocks).
- **Scoring correct** — differences clearly driven by (1) answer accuracy and (2) confidence calibration, not parsing.

### 3.3 metacog_control

**Models reviewed:** Claude Opus (0.69), Qwen3 80B (0.20), Llama 4 Maverick (0.615), DeepSeek-R1 (0.2125), GLM 4.7 (0.66)

**Observations:**
- **Protocol:** 2 passages × (section selection + 5 questions) = 12 items. Model reads passage, selects 3 sections to re-read, then answers 5 questions with limited information.
- **DeepSeek-R1 (0.21 — surprisingly low for a reasoning model):** Key failure mode identified — DeepSeek's chain-of-thought reasoning leads it to *confabulate* when it lacks information. For passage 2 (Kethrani music), it fabricated answers about Indian classical music (tala, avartan) instead of the fictional Kethrani system. This is a genuine metacognitive control failure: the model cannot distinguish "I don't have this information" from "I'll reason about something similar."
- **Qwen3 80B (0.20 — lowest):** Similar confabulation pattern. Selects sections but then answers questions about topics not covered in selected sections, hallucinating plausible-sounding details.
- **Claude Opus (0.69 — highest):** Better section selection strategy. When it lacks information (didn't re-read the relevant section), it sometimes admits uncertainty rather than confabulating. But still makes strategic errors (e.g., selecting S1 overview instead of more targeted sections).
- **GLM 4.7 (0.66):** Solid section selection, reasonable answers. Confabulates on questions outside selected sections but less severely than DeepSeek/Qwen3.
- **No parsing artifacts** — JSON responses parse cleanly.
- **Scoring appears correct** — bimodal split reflects genuine behavioral difference: models that confabulate when missing context vs. models that either select better sections or admit uncertainty.

---

## 4. Ground Truth Validity Assessment

### metacog_epistemic_revision
- **Ground truth design:** Synthetic Zorblatt Chemistry and Nexari Ecology rule systems with planted contradictions. Transfer questions have deterministic correct answers under revised rules.
- **Debatable items: NONE.** All contradictions are unambiguous (e.g., observation shows Colony entering Bloom phase, contradicting R6 "Colony organisms cannot enter Bloom"). Transfer answers follow deterministically from revised rules.
- **Contamination risk: LOW.** Entirely fictional domain.

### metacog_learning_monitoring
- **Ground truth design:** Procedurally generated symbol-transform and number systems with deterministic answers. Monitoring accuracy measured via gamma correlation between reported confidence and actual accuracy.
- **Debatable items: NONE.** All test items have single correct answers (apply known rules to input → output). Confidence calibration scoring via gamma is a standard psychometric approach.
- **Contamination risk: LOW.** Systems are procedurally generated with seeds.

### metacog_control
- **Ground truth design:** Fictional passages (Lake Vordak ecology, Kethrani ceremonial music) with 10 sections each. Questions map to specific sections. Correct answers are explicitly stated in specific sections.
- **Debatable items: NONE.** All answers are directly extractable from the passage text. The challenge is *which sections to re-read*, not ambiguity in the answers themselves.
- **Potential concern — scoring of confabulated answers:** When a model doesn't have the relevant section and confabulates a plausible-sounding answer, the scoring must distinguish between "correct by lucky guess" and "correct because of good section selection." Current scoring handles this via the strategic gain component (credit for accuracy *on questions whose sections were re-read*).
- **Contamination risk: LOW.** Passages are entirely fictional.

---

## 5. Recommendations

### metacog_epistemic_revision — **KEEP AS-IS**
- std=0.114 provides good discrimination
- No ceiling/floor effects (only Claude Opus at 0.96 is borderline ceiling)
- Clean transcript review: scoring is accurate, no parsing artifacts
- v4 design (inductive inference from raw data) is working as intended
- No items to revise

### metacog_learning_monitoring — **KEEP AS-IS with monitoring note**
- std=0.093 is borderline (threshold ≥0.08, passes)
- No ceiling/floor effects
- Scoring is correct and captures genuine behavioral differences
- The relatively compressed range (0.277) is a minor concern but acceptable for a combined learning+monitoring benchmark where both components must vary simultaneously
- **Future consideration:** Could increase difficulty of rule systems (difficulty=3 or 4 for all systems instead of mixed 2-3) to create more learning errors and thus more monitoring signal. Not urgent — current design passes all thresholds.

### metacog_control — **KEEP AS-IS**
- std=0.221 is excellent, best in tier
- Bimodal split reveals a genuine cognitive capability boundary
- DeepSeek-R1 and Qwen3 confabulation patterns are valuable diagnostic signals for understanding how reasoning models handle metacognitive control
- Fictional passages eliminate contamination risk
- No items to revise

---

## 6. Cross-Benchmark Patterns

1. **Claude hedging penalty persists:** Claude Sonnet scores below average on learning_monitoring (0.70) due to conservative confidence reporting — same pattern observed in epistemic_humility (KNOWLEDGE). Claude models are systematically under-confident.

2. **Reasoning models ≠ metacognitive models:** DeepSeek-R1 (a reasoning-focused model) scores 0.21 on control — one of the lowest. Extended chain-of-thought reasoning actually *hurts* metacognitive control because the model confabulates instead of recognizing information gaps.

3. **Confabulation as metacognitive failure:** The control benchmark reveals a clear split between models that confabulate when missing information (DeepSeek-R1, Qwen3, Ministral 3B — all score ≤0.35) vs. models that either select better sections or degrade more gracefully (Claude Opus, GPT-OSS, Llama 3.3, GLM 4.7 — all score ≥0.61).

4. **Self-monitoring tier coherence:** Mean scores (revision=0.79, monitoring=0.81, control=0.49) show control is substantially harder than the other two. This is expected: control requires both monitoring accuracy (which sections do I need?) AND strategic action (choosing correctly under constraint).
