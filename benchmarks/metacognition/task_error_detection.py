"""
MetaCog Benchmark 4: Error Detection (Metacognitive Monitoring of Reasoning)

Tests the model's ability to detect errors in step-by-step reasoning chains.
This measures metacognitive monitoring during/after processing — a critical
component of self-correction capability.

Protocol:
1. Present a problem with a worked step-by-step solution
2. Ask model to review the solution and:
   a. Determine if there's an error (binary)
   b. If yes, identify which step contains the error
   c. Rate confidence in the judgment (0-100)
3. Score based on detection accuracy, localization, and confidence calibration

Cognitive Science Basis:
- Yeung & Summerfield (2012): Error monitoring and metacognition
- Nelson & Narens (1990): Monitoring of ongoing cognitive processes
- Related to "debugging" in education research

Metrics:
- Error detection F1 (binary: error present or not)
- Error localization accuracy (correct step identified)
- Confidence calibration (ECE of error detection confidence)
- Signal detection: d' and meta-d' for error detection

Shortcut Resistance:
- Mix of correct and incorrect chains prevents bias
- Errors vary in subtlety (arithmetic, logic, conceptual)
- Some "errors" are actually correct (tests false alarm rate)
- Confidence calibration penalizes overconfident wrong judgments
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.error_detection_chains import REASONING_CHAINS


@dataclass
class ErrorReview:
    """Model's review of a reasoning chain."""
    has_error: bool       # Does this chain contain an error?
    error_step: int       # Which step (1-indexed), or 0 if no error
    explanation: str      # Explanation of the error (or why it's correct)
    confidence: int       # 0-100 confidence in the judgment


# ─── Helpers ─────────────────────────────────────────────────────

# ─── Helpers ───────────────────────────────────────────────────────

def _strip_think(text: str) -> str:
    """Remove <think>...</think> tags that some models wrap around output."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def goodman_kruskal_gamma(x: list, y: list) -> float:
    n = len(x)
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            x_diff = x[i] - x[j]
            y_diff = y[i] - y[j]
            product = x_diff * y_diff
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1
    denom = concordant + discordant
    return (concordant - discordant) / denom if denom > 0 else 0.0


def compute_ece(confidences: list, accuracies: list, n_bins: int = 5) -> float:
    conf = np.array(confidences) / 100.0
    acc = np.array(accuracies, dtype=float)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total = len(conf)
    for i in range(n_bins):
        lo, hi = bin_boundaries[i], bin_boundaries[i + 1]
        if i == 0:
            mask = (conf >= lo) & (conf <= hi)
        else:
            mask = (conf > lo) & (conf <= hi)
        if mask.sum() == 0:
            continue
        ece += (mask.sum() / total) * abs(acc[mask].mean() - conf[mask].mean())
    return round(float(ece), 4)


def compute_f1(tp: int, fp: int, fn: int) -> float:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def compute_dprime(hit_rate: float, false_alarm_rate: float) -> float:
    """Compute d' (signal detection sensitivity) without scipy."""
    # Approximate inverse normal CDF using rational approximation
    # (Abramowitz & Stegun, 1964)
    def norminv(p):
        if p <= 0:
            return -4.0
        if p >= 1:
            return 4.0
        # Rational approximation for central region
        if p < 0.5:
            t = np.sqrt(-2 * np.log(p))
            c0, c1, c2 = 2.515517, 0.802853, 0.010328
            d1, d2, d3 = 1.432788, 0.189269, 0.001308
            return -(t - (c0 + c1 * t + c2 * t**2) / (1 + d1 * t + d2 * t**2 + d3 * t**3))
        else:
            t = np.sqrt(-2 * np.log(1 - p))
            c0, c1, c2 = 2.515517, 0.802853, 0.010328
            d1, d2, d3 = 1.432788, 0.189269, 0.001308
            return t - (c0 + c1 * t + c2 * t**2) / (1 + d1 * t + d2 * t**2 + d3 * t**3)

    hr = min(max(hit_rate, 0.01), 0.99)
    far = min(max(false_alarm_rate, 0.01), 0.99)
    return float(norminv(hr) - norminv(far))


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="Error Detection")
def metacog_error_detection(llm) -> float:
    """Error Detection Benchmark.

    Model reviews step-by-step reasoning chains and must:
    1. Detect whether an error exists
    2. Localize the error (which step)
    3. Rate confidence

    Score = 0.30 * weighted_detection + 0.10 * F1 + 0.25 * localization + 0.20 * (1 - ECE) + 0.15 * gamma
    """
    results = []

    for chain in REASONING_CHAINS:
        # Format the chain for review
        steps_text = "\n".join(chain["steps"])
        prompt = (
            f"Review the following step-by-step solution for errors.\n\n"
            f"**Problem:** {chain['problem']}\n\n"
            f"**Solution:**\n{steps_text}\n\n"
            f"**Final answer:** {chain['final_answer']}\n\n"
            f"Carefully check each step. Does this solution contain an error?\n\n"
            f"Respond with ONLY a JSON object:\n"
            f'{{"has_error": true/false, "error_step": <step number or 0>, '
            f'"explanation": "<explain the error or why correct>", '
            f'"confidence": <0-100>}}'
        )

        with kbench.chats.new(f"review_{chain['id']}"):
            raw = llm.prompt(prompt)
            cleaned = _strip_think(raw)
            cleaned = re.sub(r'//.*', '', cleaned)
            try:
                parsed = json.loads(re.search(r'\{.*\}', cleaned, re.DOTALL).group())
                pred_has_error = bool(parsed.get("has_error", False))
                pred_step = int(parsed.get("error_step", 0))
                confidence = max(0, min(100, int(parsed.get("confidence", 50))))
                explanation = str(parsed.get("explanation", ""))
            except Exception:
                # Crude fallback: look for keywords
                raw_lower = cleaned.lower()
                pred_has_error = any(w in raw_lower for w in ["error", "mistake", "incorrect", "wrong"])
                pred_step = 0
                confidence = 50
                explanation = cleaned[:200]

        # Score this chain
        actual_has_error = chain["has_error"]
        actual_step = chain["error_step"]

        # Detection correctness
        detection_correct = pred_has_error == actual_has_error

        # Localization correctness (only relevant when error exists and was detected)
        localization_correct = False
        if actual_has_error and pred_has_error and actual_step is not None:
            localization_correct = pred_step == actual_step

        results.append({
            "id": chain["id"],
            "problem": chain["problem"][:60],
            "actual_has_error": actual_has_error,
            "pred_has_error": pred_has_error,
            "actual_step": actual_step,
            "pred_step": pred_step,
            "detection_correct": detection_correct,
            "localization_correct": localization_correct,
            "confidence": confidence,
            "explanation": explanation[:100],
            "difficulty": chain["difficulty"],
        })

    # ── Compute Metrics (difficulty-weighted) ──
    # Difficulty weights: d=1 → 1.0, d=2 → 2.0, d=3 → 3.0
    diff_map = {1: 1.0, 2: 2.0, 3: 3.0}

    # Detection F1 (unweighted for standard metric)
    tp = sum(1 for r in results if r["actual_has_error"] and r["pred_has_error"])
    fp = sum(1 for r in results if not r["actual_has_error"] and r["pred_has_error"])
    fn = sum(1 for r in results if r["actual_has_error"] and not r["pred_has_error"])
    tn = sum(1 for r in results if not r["actual_has_error"] and not r["pred_has_error"])

    # Difficulty-weighted detection accuracy
    weighted_correct = sum(diff_map.get(r["difficulty"], 1.0) for r in results if r["detection_correct"])
    weighted_total = sum(diff_map.get(r["difficulty"], 1.0) for r in results)
    weighted_detection = weighted_correct / weighted_total if weighted_total > 0 else 0

    f1 = compute_f1(tp, fp, fn)

    # Localization accuracy (among correctly detected errors)
    error_chains = [r for r in results if r["actual_has_error"] and r["pred_has_error"]]
    # Difficulty-weighted localization accuracy
    if error_chains:
        loc_weighted = sum(diff_map.get(r["difficulty"], 1.0) for r in error_chains if r["localization_correct"])
        loc_total = sum(diff_map.get(r["difficulty"], 1.0) for r in error_chains)
        localization_acc = loc_weighted / loc_total if loc_total > 0 else 0
    else:
        localization_acc = 0.0

    # Confidence calibration
    confidences = [r["confidence"] for r in results]
    detection_accuracies = [r["detection_correct"] for r in results]
    ece = compute_ece(confidences, detection_accuracies)

    # Confidence-accuracy gamma
    gamma = goodman_kruskal_gamma(confidences, [int(a) for a in detection_accuracies])
    gamma_norm = (gamma + 1) / 2

    # Signal detection (d')
    n_signal = sum(1 for r in results if r["actual_has_error"])
    n_noise = sum(1 for r in results if not r["actual_has_error"])
    hit_rate = tp / n_signal if n_signal > 0 else 0
    false_alarm_rate = fp / n_noise if n_noise > 0 else 0

    try:
        dprime = compute_dprime(hit_rate, false_alarm_rate)
    except Exception:
        dprime = 0.0

    # Composite score — uses weighted detection instead of raw F1 for better discrimination
    score = round(
        0.30 * weighted_detection + 0.10 * f1 + 0.25 * localization_acc + 0.20 * (1 - ece) + 0.15 * gamma_norm,
        4
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"ERROR DETECTION BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Chains reviewed: {len(REASONING_CHAINS)}")
    print(f"  With errors: {n_signal}")
    print(f"  Without errors: {n_noise}")
    print(f"\n--- Detection Performance ---")
    print(f"True Positives:  {tp}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"True Negatives:  {tn}")
    print(f"Detection F1:    {f1:.4f}")
    print(f"Hit rate:        {hit_rate:.2%}")
    print(f"False alarm:     {false_alarm_rate:.2%}")
    print(f"d' (sensitivity):{dprime:+.3f}")

    print(f"\n--- Localization ---")
    print(f"Correctly localized: {sum(1 for r in error_chains if r['localization_correct'])}/{len(error_chains)}")
    print(f"Localization acc:    {localization_acc:.2%}")

    print(f"\n--- Metacognitive Metrics ---")
    print(f"ECE:             {ece:.4f}")
    print(f"Gamma:           {gamma:+.4f}")
    print(f"Mean confidence: {np.mean(confidences):.1f}%")
    print(f"Composite score: {score:.4f}")

    print(f"\n--- Per-Chain Results ---")
    for r in results:
        det = "✓" if r["detection_correct"] else "✗"
        loc = ""
        if r["actual_has_error"] and r["pred_has_error"]:
            loc = " LOC:✓" if r["localization_correct"] else f" LOC:✗(pred={r['pred_step']},actual={r['actual_step']})"
        err_label = "ERR" if r["actual_has_error"] else "OK "
        print(f"  {det} [{r['confidence']:3d}%] [{err_label}] {r['problem'][:45]}...{loc}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
metacog_error_detection.run(llm=kbench.llm)
