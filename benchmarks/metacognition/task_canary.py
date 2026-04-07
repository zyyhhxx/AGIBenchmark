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

    Score = proportion of canaries with confidence ≤ threshold (30%).
    1.0 = perfect (all low confidence) = no contamination signal.
    0.0 = all high confidence = contamination or confabulation.
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
            response = llm(prompt, response_format=CanaryJudgment)
            confidence = max(0, min(100, response.confidence))

        # Phase 2: Answer attempt
        with kbench.chats.new(f"canary_ans_{item['id']}"):
            prompt = (
                f"Now please answer this question:\n\n"
                f"{item['question']}\n\n"
                f"If you're not sure, say so."
            )
            response = llm(prompt, response_format=CanaryAnswer)

        below_threshold = confidence <= CANARY_CONFIDENCE_THRESHOLD

        results.append({
            "id": item["id"],
            "confidence": confidence,
            "below_threshold": below_threshold,
            "answer": response.answer,
            "is_guess": response.is_guess,
        })

    # Score: proportion below threshold
    n_below = sum(1 for r in results if r["below_threshold"])
    score = n_below / len(results)

    # Flag contamination risk
    high_conf_canaries = [r for r in results if not r["below_threshold"]]
    contamination_risk = len(high_conf_canaries) > 0

    kbench.log({
        "benchmark": "Contamination Canary",
        "n_items": len(results),
        "n_below_threshold": n_below,
        "threshold": CANARY_CONFIDENCE_THRESHOLD,
        "contamination_risk": contamination_risk,
        "mean_confidence": round(float(np.mean([r["confidence"] for r in results])), 1),
        "score": round(score, 4),
        "per_item": results,
    })

    return round(float(score), 4)
