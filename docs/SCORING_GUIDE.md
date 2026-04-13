# Scoring Guide — AGI Benchmark Suite

## Overview
All benchmarks return a single float in [0, 1]. This document explains what each score means cognitively.

---

## Metacognition Track

### metacog_fok (Feeling-of-Knowing)
**Score = composite(gamma, 1-ECE, AUC)**
- **1.0** = Perfect metacognitive resolution — model knows exactly which items it will get right
- **0.5** = Moderate resolution, comparable to average human performance (γ ≈ 0.3–0.5)
- **0.0** = No metacognitive awareness — confidence is random w.r.t. accuracy
- **Human baseline**: γ = 0.3–0.5 (Hart, 1965; Nelson & Narens, 1990)

### metacog_jol (Judgment-of-Learning)
**Score = composite(gamma, recall_accuracy, 1-ECE)**
- Measures ability to predict what has been learned from in-context examples
- **1.0** = Perfect prediction of own learning
- **Human baseline**: γ ≈ 0.4 for JOL (Dunlosky & Metcalfe, 2009)

### metacog_calibration (Retrospective Confidence)
**Score = (1 - ECE) * accuracy_weight**
- **1.0** = Perfectly calibrated — stated confidence matches accuracy
- **0.5** = Moderate miscalibration (typical for humans on hard items)
- **0.0** = Extreme miscalibration — always says 100% but gets many wrong
- **Human baseline**: ECE ≈ 0.15–0.25 (Fischhoff et al., 1977)

### metacog_error_detection
**Score = composite(F1, localization, 1-ECE, gamma)**
- Measures ability to detect errors in reasoning chains
- **1.0** = Catches all errors, localizes them precisely, well-calibrated confidence
- **Human baseline**: F1 ≈ 0.70 for logical reasoning errors

### metacog_learning_monitoring
**Score = confidence_tracking_accuracy**
- Measures whether confidence tracks actual learning during in-context examples
- **1.0** = Confidence increases exactly as knowledge grows

### metacog_control (Metacognitive Control)
**Score = relevance × strategy_gain**
- Tests strategic re-reading under a budget constraint
- **1.0** = Perfectly selects most relevant sections to re-read
- **0.0** = Random or no strategic selection

### metacog_epistemic_revision
**Score = revision_accuracy on transfer questions**
- Tests belief updating after contradictory evidence
- **1.0** = Correctly revises all beliefs including downstream inferences
- **0.0** = Stubbornly maintains original beliefs despite contradiction

### metacog_epistemic_humility
**Score = 1 - confabulation_rate**
- Tests honesty on unanswerable questions
- **1.0** = Always says "I don't know" for genuinely unanswerable questions
- **0.0** = Confabulates plausible-sounding answers for every question
- **Key insight**: Models with RLHF honesty training should score higher

### metacog_canary (Contamination Canary)
**Score = 1 - canary_confidence_rate**
- **1.0** = Correctly expresses low confidence on all fabricated items
- **0.0** = High confidence on fabricated items (contamination signal)
- This is a meta-benchmark — it validates the test suite itself

---

## Learning Track

### learning_curves
**Score = power_law_fit_quality × learning_rate**
- Measures in-context learning dynamics over 5 exposure levels (0, 2, 4, 8, 12 examples)
- **1.0** = Perfect power-law learning curve with high asymptote
- **Human baseline**: Power-law exponent 0.3–0.5

### learning_transfer
**Score = weighted(near_transfer, far_transfer)**
- Near transfer (same structure, new surface) vs. far transfer (new structure)
- **1.0** = Perfect transfer of learned rules to novel problems
- **0.0** = Cannot apply learned rules beyond training examples

### learning_interference
**Score = 1 - interference_magnitude**
- Proactive: old learning interferes with new. Retroactive: new learning disrupts old.
- **1.0** = No interference — perfect memory compartmentalization
- **0.5** = Moderate interference (typical for humans)
- **0.0** = Complete catastrophic interference

### learning_curriculum
**Score = curriculum_sensitivity_index**
- Does the order of examples matter?
- **1.0** = Strong curriculum effect — learns much better with good ordering
- **0.0** = Order-insensitive (either always good or always bad)

---

## Attention Track

### attention_selective (Stroop-like)
**Score = 1 - stroop_interference**
- **1.0** = Perfect selective attention — ignores distractors completely
- **0.5** = Moderate interference from distractors
- **Human baseline**: 50-100ms Stroop effect (translated to accuracy penalty)

### attention_vigilance (Sustained Attention)
**Score = d'_signal_detection over long sequence**
- **1.0** = Perfect signal detection across entire sequence
- **Decrement pattern**: Performance should degrade over time (vigilance decrement)
- **Human baseline**: d' decreases ~0.5 SD over 30-min watch

### attention_divided
**Score = 1 - dual_task_cost**
- **1.0** = No dual-task cost — handles multiple streams perfectly
- **0.0** = Complete failure under dual-task conditions
- **Human baseline**: 10-30% cost for concurrent tasks

### attention_instruction_update
**Score = switch_accuracy × catch_trial_accuracy**
- **1.0** = Perfect adaptation to mid-stream instruction changes
- Catch trials ensure model isn't just following the latest instruction blindly

---

## Executive Functions Track

### exec_func_wcst (Wisconsin Card Sorting)
**Score = 1 - perseverative_error_rate**
- **1.0** = No perseveration — adapts immediately to rule changes
- **0.0** = Perseverates on old rule despite negative feedback
- **Human baseline**: 5-15% perseverative errors in healthy adults

### exec_func_tol (Tower of London)
**Score = move_efficiency (optimal/actual)**
- **1.0** = Solves all problems in minimum moves
- **Human baseline**: ~60-70% optimal move efficiency

### exec_func_task_switch
**Score = 1 - switch_cost**
- **1.0** = No switch cost — equal performance on switch and stay trials
- **Human baseline**: 200-500ms switch cost (translated to accuracy)

### exec_func_nback (Working Memory)
**Score = d'_normalized across N=1,2,3**
- **1.0** = Perfect working memory updating
- **Performance should decrease** with N: 1-back > 2-back > 3-back
- **Human baseline**: d' ≈ 3.0 (1-back), 2.0 (2-back), 1.0 (3-back)

### exec_func_crt (Cognitive Reflection Test)
**Score = proportion correct on CRT items**
- **1.0** = Resists all intuitive traps — pure System 2 thinking
- **0.0** = Falls for every trap — pure System 1 responding
- **Human baseline**: 30-48% accuracy (Frederick, 2005)
- **Key**: Uses procedurally generated variants, not the famous 3 items

---

## Social Cognition Track

### social_cog_false_belief (Theory of Mind)
**Score = belief_accuracy - max(0, belief_acc - control_acc)**
- Subtracts control accuracy to isolate genuine ToM from comprehension
- **1.0** = Perfect belief attribution (both 1st and 2nd order)
- **Human baseline**: ~85% by age 5 (1st order), ~60% by age 7 (2nd order)

### social_cog_pragmatic (Pragmatic Inference)
**Score = intended_accuracy - 0.1 × literal_trap_rate**
- **1.0** = Always identifies speaker's true intent over literal meaning
- **0.0** = Always gives literal interpretation (pragmatic blindness)
- **Human baseline**: 90-95% for adults
- **Known finding**: Gemini 2.5 Flash shows literal bias on scalar implicature

### social_cog_sarcasm
**Score = detection_accuracy × calibration_weight**
- **1.0** = Perfect sarcasm detection with appropriate confidence
- Distinguishes genuine sarcasm detection from "always says yes"

### social_cog_emotional_prosody
**Score = tone_shift_detection_accuracy**
- Detects emotional tone changes in dialogue
- **1.0** = Perfect identification of emotional shifts
- Tests affective understanding in text without audio cues
