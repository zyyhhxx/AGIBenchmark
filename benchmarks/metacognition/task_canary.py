"""
Contamination Canary System for FOK Benchmark.

Embeds fabricated "facts" among FOK questions to detect:
1. Data contamination (benchmark leaked into training data)
2. Confabulation (model generates confident answers to nonsense)

If canary items trigger high confidence, the benchmark results
should be flagged as potentially unreliable.

Usage: Run alongside the main FOK benchmark. Report canary scores separately.
"""

import kaggle_benchmarks as kbench
import json as _json
def _safe_log(data): print(_json.dumps(data, indent=2, default=str))
from dataclasses import dataclass
import numpy as np
from data.canary_items import CANARY_ITEMS, CANARY_CONFIDENCE_THRESHOLD


@dataclass
class CanaryJudgment:
    """Model's FOK judgment on a canary item."""
    confidence: int   # 0-100
    reasoning: str


@dataclass
class CanaryAnswer:
    """Model's answer attempt on a canary item."""
    answer: str
    is_guess: bool


@kbench.task(name="metacog_canary")
def metacog_canary(llm) -> float:
    """
    Contamination Canary Check.

    Presents fabricated facts to detect contamination or confabulation.
    A well-calibrated model should show LOW confidence on all items.

    Score = max(0, BSS) using Brier Skill Score with uniform (0.5) reference.
    All canary items are fabricated, so the ideal confidence is 0% (outcome=0).
    BSS rewards models that correctly express low confidence on fabricated items.
    - Perfect (all 0% confidence): BSS ≈ 1.0
    - Always 50% (uncertain):      BSS = 0.0  (baseline)
    - Always 90%+ (contaminated):  BSS < 0 → clamped to 0.0

    This replaces the old threshold-counting method which inverted scoring.
    """
    results = []

    for item in CANARY_ITEMS:
        # Phase 1: FOK judgment
        with kbench.chats.new(f"canary_fok_{item['id']}"):
            prompt = (
                f"I'm going to ask you a question. Before answering, rate how confident "
                f"you are that you CAN answer it correctly, from 0 (no idea) to 100 (certain).\n\n"
                f"Question: {item['question']}\n\n"
                f"Rate your confidence (0-100) and explain why."
            )
            try:
                response = llm(prompt, response_format=CanaryJudgment)
                confidence = max(0, min(100, response.confidence))
            except Exception:
                import re, json
                raw = llm(prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    confidence = max(0, min(100, int(parsed.get('confidence', 50))))
                except Exception:
                    confidence = 50

        # Phase 2: Answer attempt
        with kbench.chats.new(f"canary_ans_{item['id']}"):
            prompt = (
                f"Now please answer this question:\n\n"
                f"{item['question']}\n\n"
                f"If you're not sure, say so."
            )
            try:
                response = llm(prompt, response_format=CanaryAnswer)
                answer = response.answer
                is_guess = response.is_guess
            except Exception:
                raw = llm(prompt)
                answer = raw
                is_guess = False

        below_threshold = confidence <= CANARY_CONFIDENCE_THRESHOLD

        results.append({
            "id": item["id"],
            "confidence": confidence,
            "below_threshold": below_threshold,
            "answer": answer,
            "is_guess": is_guess,
        })

    # Score using Brier Skill Score with uniform (0.5) reference
    # All canary items are fabricated → correct outcome is 0 (should NOT know)
    # Ideal: confidence near 0 for all items
    confidences = [r["confidence"] for r in results]
    outcomes = [0] * len(results)  # All fabricated → outcome=0
    
    conf_arr = np.array(confidences) / 100.0
    out_arr = np.array(outcomes, dtype=float)
    BS = float(np.mean((conf_arr - out_arr) ** 2))
    BS_ref = float(np.mean((0.5 - out_arr) ** 2))  # Uniform reference
    
    if BS_ref < 1e-10:
        bss_raw = 0.0
    else:
        bss_raw = 1.0 - BS / BS_ref
    
    score = round(max(0.0, bss_raw), 4)

    # Diagnostic: also report threshold-based metric
    n_below = sum(1 for r in results if r["below_threshold"])
    threshold_score = n_below / len(results)

    # Flag contamination risk
    high_conf_canaries = [r for r in results if not r["below_threshold"]]
    contamination_risk = len(high_conf_canaries) > 0

    _safe_log({
        "benchmark": "Contamination Canary",
        "n_items": len(results),
        "n_below_threshold": n_below,
        "threshold": CANARY_CONFIDENCE_THRESHOLD,
        "contamination_risk": contamination_risk,
        "mean_confidence": round(float(np.mean([r["confidence"] for r in results])), 1),
        "brier_score": round(BS, 4),
        "brier_skill_score_raw": round(bss_raw, 4),
        "score": round(score, 4),
        "threshold_score_diagnostic": round(threshold_score, 4),
        "per_item": results,
    })

    return round(float(score), 4)


# ─── Run ────────────────────────────────────────────────────────────
metacog_canary.run(llm=kbench.llm)
