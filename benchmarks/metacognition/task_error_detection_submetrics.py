"""
Error Detection Sub-metric Tasks: Individual leaderboard entries.

Splits the composite error detection benchmark into:
- error_detection_f1: Detection F1 score
- error_detection_localization: Localization accuracy (among detected errors)
- error_detection_ece: Confidence calibration (1 - ECE)
- error_detection_gamma: Confidence-accuracy gamma correlation
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.error_detection_chains import REASONING_CHAINS


@dataclass
class ErrorReview:
    has_error: bool
    error_step: int
    explanation: str
    confidence: int


def goodman_kruskal_gamma(x, y):
    n = len(x)
    concordant = discordant = 0
    for i in range(n):
        for j in range(i+1, n):
            product = (x[i]-x[j]) * (y[i]-y[j])
            if product > 0: concordant += 1
            elif product < 0: discordant += 1
    denom = concordant + discordant
    return (concordant - discordant) / denom if denom else 0.0

def compute_ece(confidences, accuracies, n_bins=5):
    conf = np.array(confidences) / 100.0
    acc = np.array(accuracies, dtype=float)
    boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total = len(conf)
    for i in range(n_bins):
        lo, hi = boundaries[i], boundaries[i+1]
        mask = (conf >= lo) & (conf <= hi) if i == 0 else (conf > lo) & (conf <= hi)
        if mask.sum() == 0: continue
        ece += (mask.sum() / total) * abs(acc[mask].mean() - conf[mask].mean())
    return round(float(ece), 4)

def compute_f1(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    if precision + recall == 0: return 0.0
    return 2 * precision * recall / (precision + recall)


def _collect_error_detection_data(llm):
    """Run the error detection protocol. Returns list of result dicts."""
    results = []
    for chain in REASONING_CHAINS:
        steps_text = "\n".join(chain["steps"])
        prompt = (
            f"Review the following step-by-step solution for errors.\n\n"
            f"**Problem:** {chain['problem']}\n\n"
            f"**Solution:**\n{steps_text}\n\n"
            f"**Final answer:** {chain['final_answer']}\n\n"
            f"Carefully check each step. Does this solution contain an error?\n\n"
            f'Respond with ONLY a JSON object:\n'
            f'{{"has_error": true/false, "error_step": <step number or 0>, '
            f'"explanation": "<explain>", "confidence": <0-100>}}'
        )
        with kbench.chats.new(f"errsub_{chain['id']}"):
            try:
                review = llm.prompt(prompt, schema=ErrorReview)
                pred_has_error = review.has_error
                pred_step = review.error_step
                confidence = max(0, min(100, review.confidence))
            except Exception:
                raw = llm.prompt(prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    pred_has_error = bool(parsed.get("has_error", False))
                    pred_step = int(parsed.get("error_step", 0))
                    confidence = max(0, min(100, int(parsed.get("confidence", 50))))
                except Exception:
                    raw_lower = raw.lower()
                    pred_has_error = any(w in raw_lower for w in ["error","mistake","incorrect","wrong"])
                    pred_step = 0
                    confidence = 50

        actual_has_error = chain["has_error"]
        actual_step = chain["error_step"]
        detection_correct = pred_has_error == actual_has_error
        localization_correct = (actual_has_error and pred_has_error and
                                actual_step is not None and pred_step == actual_step)

        results.append({
            "actual_has_error": actual_has_error,
            "pred_has_error": pred_has_error,
            "actual_step": actual_step,
            "pred_step": pred_step,
            "detection_correct": detection_correct,
            "localization_correct": localization_correct,
            "confidence": confidence,
        })
    return results


@kbench.task(name="metacog_error_detection_f1")
def metacog_error_detection_f1(llm) -> float:
    """Error Detection F1 — precision-recall balance for detecting reasoning errors."""
    results = _collect_error_detection_data(llm)
    tp = sum(1 for r in results if r["actual_has_error"] and r["pred_has_error"])
    fp = sum(1 for r in results if not r["actual_has_error"] and r["pred_has_error"])
    fn = sum(1 for r in results if r["actual_has_error"] and not r["pred_has_error"])
    return round(compute_f1(tp, fp, fn), 4)

@kbench.task(name="metacog_error_detection_localization")
def metacog_error_detection_localization(llm) -> float:
    """Error Localization — accuracy of identifying the specific erroneous step."""
    results = _collect_error_detection_data(llm)
    detected = [r for r in results if r["actual_has_error"] and r["pred_has_error"]]
    if not detected: return 0.0
    return round(sum(1 for r in detected if r["localization_correct"]) / len(detected), 4)

@kbench.task(name="metacog_error_detection_ece")
def metacog_error_detection_ece(llm) -> float:
    """Error Detection Calibration (1 - ECE) — confidence matches detection accuracy."""
    results = _collect_error_detection_data(llm)
    ece = compute_ece([r["confidence"] for r in results], [r["detection_correct"] for r in results])
    return round(1 - ece, 4)

@kbench.task(name="metacog_error_detection_gamma")
def metacog_error_detection_gamma(llm) -> float:
    """Error Detection Gamma — ordinal association between confidence and correctness. Normalized to [0,1]."""
    results = _collect_error_detection_data(llm)
    gamma = goodman_kruskal_gamma(
        [r["confidence"] for r in results],
        [int(r["detection_correct"]) for r in results]
    )
    return round((gamma + 1) / 2, 4)

metacog_error_detection_f1.run(llm=kbench.llm)
metacog_error_detection_localization.run(llm=kbench.llm)
metacog_error_detection_ece.run(llm=kbench.llm)
metacog_error_detection_gamma.run(llm=kbench.llm)
