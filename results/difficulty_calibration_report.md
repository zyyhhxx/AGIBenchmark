# Difficulty Calibration Report

**Date:** 2026-04-09  
**Data Sources:** SPOT_TEST_ANALYSIS.md, spot_test_results.jsonl, mock_validation_full.json, mock_validation.json, stratified_calibration.json, stress_test_results.json

## Executive Summary

Analysis of spot tests (Gemini 2.5 Flash/Flash-Lite) and mock validation results reveals several benchmarks with ceiling effects, inverted scoring anomalies, and a few with floor-like behavior. This report identifies each issue and proposes specific calibration adjustments.

---

## 1. Ceiling Effects (Score ≥ 90% or Perfect Performance)

### 1.1 CRT — Classic Items (Executive Functions)
- **Evidence:** Gemini Flash-Lite 3/3 (100%), Flash 3/3 on classic bat-and-ball variants
- **Problem:** Classic CRT items are massively contaminated in training data. Human baseline is 30–48%; models hitting 100% means the benchmark measures recall, not inhibition.
- **Recommendation:**
  - Drop classic CRT items entirely from scored benchmark
  - Use only procedurally generated variants with novel numbers and structures
  - Add "adversarial lure" variants where the intuitive-but-wrong answer is numerically close to correct
  - Increase from 3 to 8+ items with varied trap structures (not just "X costs $Y more than Z")

### 1.2 Stroop — Selective Attention (Attention)
- **Evidence:** Flash passes trivially (correct: "Red")
- **Problem:** Text-based Stroop has no genuine interference for LLMs — there's no perceptual conflict in reading "the word RED written in blue ink." The model just extracts the stated ink color.
- **Recommendation:**
  - Redesign as **semantic Stroop**: present conflicting semantic content (e.g., "The word meaning 'happy' is associated with the category NEGATIVE. What category?")
  - Add **multi-dimensional conflict** items where multiple attributes conflict simultaneously
  - Include congruent/incongruent/neutral conditions with ≥20 items each to measure interference magnitude, not just pass/fail

### 1.3 N-back — Working Memory (Executive Functions)
- **Evidence:** Flash perfect 5/5 on 2-back with 5 items; Flash also perfect on 3-item 2-back
- **Problem:** Short sequences with small N are trivial for models with full context windows. No working memory pressure exists.
- **Recommendation:**
  - Increase sequence length to 50+ items
  - Use 3-back and 4-back conditions
  - Add **interleaved distractor tasks** between items to simulate interference
  - Measure d' with enough trials (≥40 targets + 40 non-targets) for statistical reliability
  - Consider **updating N-back** where the target rule changes mid-sequence

### 1.4 Epistemic Revision (Metacognition)
- **Evidence:** Flash 3/3 perfect on Zorblatt chemistry revision
- **Problem:** Current items may be too transparent — the new evidence directly contradicts old belief with explicit cues.
- **Recommendation:**
  - Add **partial revision** items where new evidence is ambiguous or probabilistic
  - Include **anchoring resistance** items: strong initial evidence followed by weak contradicting evidence (should NOT fully revise)
  - Add items requiring **multi-step revision chains** (A→B, then B is revised, check if A inference is also updated)
  - Increase to 15+ items across difficulty tiers

### 1.5 2nd-Order ToM — False Belief (Social Cognition)
- **Evidence:** Both Flash and Flash-Lite pass 2nd-order ToM (Green cupboard scenario)
- **Problem:** Standard false belief scenarios are well-known in NLP literature and likely in training data.
- **Recommendation:**
  - Use **3rd-order and 4th-order** nested belief scenarios
  - Add **pragmatic false belief** items where understanding requires both belief tracking AND social inference
  - Include **belief revision through communication** scenarios (A tells B, but A was lying)

### 1.6 Epistemic Humility — Fabricated Items (Metacognition)  
- **Evidence:** Both Flash and Flash-Lite correctly say "I don't know" for Zorblattium-7
- **Problem:** Fabricated-name detection is easy — models have learned "if I don't recognize it, say I don't know"
- **Recommendation:**
  - Add **near-miss items**: real substances with slightly altered names (e.g., "Beryllium-9" is real, "Beryllium-11" exists but is rare)
  - Include **obscure-but-real items** that models should know but might not (tests undersensitivity)
  - Add **confidently-wrong bait**: plausible-sounding but false claims about real entities

### 1.7 WCST — Set Shifting (Executive Functions)
- **Evidence:** Flash passes single WCST trial correctly
- **Problem:** Single-trial WCST is trivial pattern matching
- **Recommendation:**
  - Full WCST requires **128-card sequence** with rule shifts after 10 consecutive correct
  - Measure **perseverative errors** (continuing old rule after shift), not just accuracy
  - Add **ambiguous cards** that match multiple rules to increase difficulty

---

## 2. Floor Effects / Broken Scoring

### 2.1 Mock Validation — Inverted Scoring (Multiple Metacognition Benchmarks)
- **Evidence from mock_validation_full.json:**
  - **FOK:** Perfect (0.376) < Uncertain (0.553) — ⚠️ inverted
  - **JOL:** Perfect (0.275) < Uncertain (0.485) — ⚠️ inverted  
  - **Calibration:** Perfect (0.250) < Uncertain (0.950) — ⚠️ inverted
  - **Canary:** Perfect (0.000) < Uncertain (1.000) — ⚠️ inverted
- **Problem:** These aren't floor effects per se — the scoring functions are rewarding the wrong behavior. A "perfect" metacognitive agent scores lower than one that's always uncertain. This means the scoring metric doesn't properly capture what good metacognition looks like.
- **Recommendation:**
  - **FOK/JOL:** Review gamma correlation calculation. Perfect metacognition = high confidence on items you get right, low confidence on items you get wrong. The "perfect" mock strategy may not be implementing this correctly.
  - **Calibration:** 1-ECE scoring with "always uncertain" gives 0.95 because predicting 50% on everything yields low ECE for a 50/50 correct/incorrect mix. Need to add a **resolution component** (Brier skill score or Murphy decomposition) that rewards discrimination, not just calibration.
  - **Canary:** By design, canary items are all fabricated, so "always uncertain" is literally the correct answer. This is working as intended but the "perfect" strategy mock should match "always uncertain."

### 2.2 Learning Interference (Learning)
- **Evidence:** All four strategies produce identical score (0.4) — ⚠️ no discrimination
- **Problem:** The benchmark cannot distinguish between any response strategy. It measures nothing.
- **Recommendation:**
  - Redesign scoring to measure **proactive/retroactive interference magnitude** (performance drop from baseline)
  - Use paired-associate learning with AB-AC paradigm where interference is measurable
  - Score should reflect List 2's impact on List 1 recall, not raw accuracy

### 2.3 Learning Transfer (Learning)
- **Evidence:** All strategies score ≈ 0.0 except always_confident (0.07)
- **Problem:** Near-floor scores for all strategies suggest the task is either too hard or scoring is broken.
- **Recommendation:**
  - Check if the scoring function correctly handles the transfer measurement
  - Consider separate near-transfer and far-transfer scores
  - Ensure baseline (no-transfer) condition is achievable

### 2.4 Stress Test Failures (Multiple)
- **Evidence:** attention_vigilance, learning_curriculum, attention_instruction_update all fail with import errors
- **Problem:** Module import paths are broken — these benchmarks literally cannot run.
- **Recommendation:**
  - Fix `from data import ...` to use proper relative/absolute imports
  - Verify all benchmarks can at minimum import and initialize without errors

---

## 3. Moderate Difficulty — Benchmarks Working Well

These show appropriate difficulty levels (neither ceiling nor floor):

| Benchmark | Evidence | Status |
|-----------|----------|--------|
| **Calibration (domain-specific)** | Flash overconfident on pi digits (100% on unknowable) | ✅ Good — catches real metacognitive failure |
| **Pragmatic Inference** | Flash-Lite fails 1/2 scalar implicature; Flash-Lite inconsistent | ✅ Good — discriminates by model size |
| **1st-order ToM** | Flash-Lite fails Sally-Anne, Flash passes | ✅ Good — discriminates by model size |
| **Sarcasm Detection** | Mock AUC: perfect=1.0, random=0.60, inverted=0.0 | ✅ Good spread |
| **Error Detection** | Mock: perfect=0.53, random=0.43, always_confident=0.46 | ✅ Reasonable spread |
| **Tower of London** | Flash fails (verbose, non-optimal) | ✅ Good — genuinely hard |
| **Planning (ToL)** | Spot test: Flash fails to give concise optimal plan | ✅ Good difficulty |

---

## 4. Priority Calibration Actions

### Critical (blocks valid scoring):
1. **Fix inverted scoring** in FOK, JOL, Calibration mocks — add resolution/discrimination component
2. **Fix import errors** in vigilance, curriculum, instruction_update benchmarks
3. **Fix learning_interference** scoring — currently non-discriminating

### High (ceiling effects undermine benchmark value):
4. **CRT:** Switch to procedural-only variants, drop classic items
5. **N-back:** Increase to 50+ items, 3-back/4-back, add distractor tasks
6. **Stroop:** Redesign as semantic Stroop for text-based models

### Medium (improve discrimination):
7. **Epistemic revision:** Add partial/ambiguous revision items
8. **Epistemic humility:** Add near-miss and obscure-but-real items  
9. **WCST:** Implement full 128-card protocol with perseveration scoring
10. **ToM:** Add 3rd/4th-order nested belief scenarios

---

## 5. Stratified Calibration Analysis

From `stratified_calibration.json`:
- Easy ECE: 0.260, Medium ECE: 0.194, Hard ECE: 0.300
- Overall ECE: 0.144
- `degrades_with_difficulty: false` — difficulty doesn't monotonically increase ECE

This suggests the difficulty stratification (easy/medium/hard) categories don't align with actual calibration difficulty. The medium tier is actually easiest. **Recommendation:** Re-examine difficulty tier assignments; consider empirical difficulty based on model accuracy rather than a priori categorization.

---

## 6. Cross-Model Discrimination Summary

From spot tests, benchmarks that successfully discriminate between Flash and Flash-Lite:

| Benchmark | Flash | Flash-Lite | Discriminates? |
|-----------|-------|------------|:-:|
| 1st-order ToM | ✓ | ✗ | ✅ Yes |
| Scalar implicature | ✓ | ✗ (1/2) | ✅ Yes |
| Tower of London | ✗ (verbose) | — | — |
| Calibration (pi) | ✗ (overconfident) | — | — |

Benchmarks that fail to discriminate (both models ceiling):
- CRT classic items (both 100%)
- Epistemic humility fabricated items (both pass)
- 2nd-order ToM (both pass)
- Epistemic revision (both pass)

**Conclusion:** Approximately half of tested benchmarks show ceiling effects for the weakest tested model (Flash-Lite). The metacognition track's most valuable benchmarks are those measuring calibration and monitoring (where models genuinely fail), not those measuring knowledge of uncertainty about fabricated items (where "I don't know" is too easy to trigger).
