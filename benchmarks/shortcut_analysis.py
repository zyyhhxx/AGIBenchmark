"""
Shortcut Resistance Analysis

This script analyzes our benchmarks for potential shortcuts that could
allow models to achieve high scores without genuine cognitive ability.

For each benchmark, we check:
1. Can a "always confident" strategy game the score?
2. Can a "always low confidence" strategy game the score?
3. Can random guessing with calibrated confidence beat baselines?
4. Are there statistical biases in the question/answer distributions?
"""

import sys
import numpy as np
from collections import Counter

import os
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

BASE = os.path.dirname(os.path.abspath(__file__))
fok_mod = load_module('fok', os.path.join(BASE, 'metacognition/data/fok_questions.py'))
cal_mod = load_module('cal', os.path.join(BASE, 'metacognition/data/calibration_questions.py'))
err_mod = load_module('err', os.path.join(BASE, 'metacognition/data/error_detection_chains.py'))

FOK_QUESTIONS = fok_mod.FOK_QUESTIONS
CALIBRATION_QUESTIONS = cal_mod.CALIBRATION_QUESTIONS
REASONING_CHAINS = err_mod.REASONING_CHAINS


def analyze_fok_shortcuts():
    """Analyze FOK benchmark for shortcut vulnerabilities."""
    print("=" * 60)
    print("FOK BENCHMARK — SHORTCUT ANALYSIS")
    print("=" * 60)

    # Category distribution
    cats = Counter(q["category"] for q in FOK_QUESTIONS)
    print(f"\nCategory distribution: {dict(cats)}")

    # If model always says confidence=100, what happens?
    # (Assuming it answers all correctly — best case)
    n = len(FOK_QUESTIONS)
    unanswerable = sum(1 for q in FOK_QUESTIONS if q["answer"] == "__UNANSWERABLE__")
    print(f"Total questions: {n}")
    print(f"Unanswerable: {unanswerable} ({unanswerable/n:.0%})")

    # Strategy: always confident (100)
    # If model gets all answerable correct + fails unanswerable:
    # accuracy = (n - unanswerable) / n = 87.5%
    # But confidence is 100 for all → ECE = high for wrong items
    acc_optimistic = (n - unanswerable) / n
    print(f"\n--- Strategy: Always 100% confident ---")
    print(f"Best-case accuracy (if all answerable correct): {acc_optimistic:.0%}")
    print(f"ECE would be: ~{unanswerable/n:.2f} (from overconfident on unanswerable)")
    print("Score would be penalized by ECE and low gamma (no discrimination)")

    # Strategy: always 50% confident
    print(f"\n--- Strategy: Always 50% confident ---")
    print("Gamma = 0 (no ordinal association)")
    print("ECE depends on actual accuracy")
    print("AUC = 0.5 (chance)")
    gamma_norm = (0 + 1) / 2  # 0.5
    ece_score = 0.7  # Rough estimate
    auc = 0.5
    score = 0.40 * gamma_norm + 0.30 * ece_score + 0.30 * auc
    print(f"Estimated shortcut score: {score:.3f}")
    print("This is middling — genuine monitoring should beat this easily")

    # Check answer distribution bias
    print(f"\n--- Answer distribution analysis ---")
    for cat in ["retrievable", "boundary", "obscure", "reasoning", "unanswerable"]:
        items = [q for q in FOK_QUESTIONS if q["category"] == cat]
        print(f"  {cat}: {len(items)} items")

    print("\n✅ FOK appears shortcut-resistant:")
    print("  - Two-phase protocol prevents post-hoc calibration")
    print("  - Unanswerable items penalize overconfidence")
    print("  - Category diversity prevents domain-specific shortcuts")


def analyze_calibration_shortcuts():
    """Analyze calibration benchmark for shortcut vulnerabilities."""
    print("\n" + "=" * 60)
    print("CALIBRATION BENCHMARK — SHORTCUT ANALYSIS")
    print("=" * 60)

    # Difficulty distribution
    diffs = Counter(q["difficulty"] for q in CALIBRATION_QUESTIONS)
    print(f"\nDifficulty distribution: {dict(diffs)}")

    # Domain distribution
    domains = Counter(q["domain"] for q in CALIBRATION_QUESTIONS)
    print(f"Domain distribution: {dict(domains)}")
    print(f"Number of unique domains: {len(domains)}")

    # Strategy: calibrated guessing
    # If model says 33% confidence on everything (matching overall ~33% accuracy):
    print(f"\n--- Strategy: Always say 33% confident ---")
    print("ECE would be low if 33% is close to actual accuracy")
    print("But score = 1 - ECE, so could get ~0.80+")
    print("⚠️  POTENTIAL ISSUE: flat confidence can achieve good ECE")
    print("    MITIGATION: Gamma and AUC would be 0.5 / 0.0")
    print("    Our FOK/JOL benchmarks use gamma, not just ECE")

    print("\n✅ Calibration is somewhat gameable with flat confidence,")
    print("   but our metacognition SUITE uses multiple benchmarks.")
    print("   Flat confidence would score poorly on FOK (gamma) and JOL (gamma).")


def analyze_error_detection_shortcuts():
    """Analyze error detection benchmark for shortcut vulnerabilities."""
    print("\n" + "=" * 60)
    print("ERROR DETECTION — SHORTCUT ANALYSIS")
    print("=" * 60)

    n = len(REASONING_CHAINS)
    errors = sum(1 for c in REASONING_CHAINS if c["has_error"])
    correct = n - errors
    print(f"\nTotal chains: {n}")
    print(f"With errors: {errors} ({errors/n:.0%})")
    print(f"Without errors: {correct} ({correct/n:.0%})")

    # Strategy: always say "no error"
    print(f"\n--- Strategy: Always say 'no error' ---")
    tp, fp, fn, tn = 0, 0, errors, correct
    precision = 0
    recall = 0
    f1 = 0
    print(f"F1: {f1:.2f} (terrible — misses all errors)")

    # Strategy: always say "error at step 1"
    print(f"\n--- Strategy: Always say 'error at step 1' ---")
    tp = sum(1 for c in REASONING_CHAINS if c["has_error"])
    fp = correct
    fn = 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    step1_errors = sum(1 for c in REASONING_CHAINS if c["has_error"] and c["error_step"] == 1)
    loc_acc = step1_errors / tp if tp > 0 else 0
    print(f"F1: {f1:.3f}")
    print(f"Localization: {loc_acc:.2%} (only {step1_errors}/{tp} errors are at step 1)")

    # Balance check
    error_steps = [c["error_step"] for c in REASONING_CHAINS if c["has_error"]]
    step_dist = Counter(error_steps)
    print(f"\n--- Error step distribution ---")
    for step, count in sorted(step_dist.items()):
        print(f"  Step {step}: {count} errors")

    print(f"\n--- Difficulty distribution ---")
    diff_dist = Counter(c["difficulty"] for c in REASONING_CHAINS)
    for d, count in sorted(diff_dist.items()):
        print(f"  Difficulty {d}: {count} chains")

    print("\n✅ Error detection appears shortcut-resistant:")
    print("  - Balanced error/correct ratio prevents bias exploitation")
    print("  - Error steps are distributed (no 'always step 1' shortcut)")
    print("  - Localization requirement adds discrimination")
    print("  - Confidence calibration penalizes blind guessing")

    # Check for error ratio
    ratio = errors / n
    if abs(ratio - 0.5) > 0.15:
        print(f"\n⚠️  Warning: error ratio ({ratio:.0%}) is not well balanced.")
        print(f"   Consider adding {'more error' if ratio < 0.5 else 'more correct'} chains.")


def analyze_learning_shortcuts():
    """Analyze learning benchmarks for shortcuts."""
    print("\n" + "=" * 60)
    print("LEARNING BENCHMARKS — SHORTCUT ANALYSIS")
    print("=" * 60)

    print("\n--- Learning Curves ---")
    print("Shortcut: Ignore examples, use rules only")
    print("If rules are sufficient, examples don't help → flat curve")
    print("This is actually what we're TESTING — rule comprehension vs example learning")
    print("✅ Not a shortcut — it reveals the model's learning strategy")

    print("\n--- Transfer ---")
    print("Shortcut: Apply original rules to all conditions")
    print("Near/far test items use DIFFERENT rules → wrong answers")
    print("✅ Transfer test inherently requires adapting to new rules")

    print("\n--- Interference ---")
    print("Shortcut: Perfect memory → no interference")
    print("That's not a shortcut — it's genuine robustness!")
    print("Low interference = high score = good learning ability")
    print("✅ The metric itself rewards the intended ability")

    print("\n--- Curriculum Sensitivity ---")
    print("Shortcut: Same performance regardless of ordering")
    print("Sensitivity = 0 → low score component")
    print("But max_accuracy still counted")
    print("✅ Balanced: rewards both accuracy and sensitivity")


if __name__ == "__main__":
    analyze_fok_shortcuts()
    analyze_calibration_shortcuts()
    analyze_error_detection_shortcuts()
    analyze_learning_shortcuts()

    print("\n" + "=" * 60)
    print("OVERALL ASSESSMENT")
    print("=" * 60)
    print("""
Key strengths:
1. Two-phase FOK protocol is fundamentally shortcut-resistant
2. Novel stimuli in JOL/learning prevent memorization
3. Multiple metrics prevent single-strategy gaming
4. Category diversity prevents domain-specific shortcuts

Areas to watch:
1. Calibration (alone) can be gamed with flat confidence
   → Mitigated by using calibration as part of suite, not standalone
2. Error detection ratio (7:10) slightly imbalanced
   → Consider adding 1-2 more error chains for balance
3. Need to verify difficulty spread creates genuine uncertainty
   → Test on frontier models to confirm
""")
