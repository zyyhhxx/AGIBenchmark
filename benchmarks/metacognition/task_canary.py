"""
Contamination Canary System — v2 (Discrimination-Based).

Mixes fabricated "facts" with well-known real facts. Measures whether the
model's expressed confidence discriminates between knowable and unknowable items.

v1 problem: All-fabricated items → every model confabulates → BSS=0 for everyone.
v2 fix: 10 fabricated + 10 real items. Score = BSS on confidence vs outcome,
where outcome=1 for real items the model answers correctly, outcome=0 for
fabricated items. Better models express high confidence on real items and
low confidence on fabricated ones → higher BSS.

Cognitive Science Basis:
- Nelson & Narens (1990): monitoring accuracy = ability to discriminate known from unknown
- Fleming (2024): metacognitive sensitivity = resolution of confidence judgments
"""

import kaggle_benchmarks as kbench
import json as _json
def _safe_log(data): print(_json.dumps(data, indent=2, default=str))
from dataclasses import dataclass
import numpy as np
import re
from data.canary_items import CANARY_ITEMS, CANARY_CONFIDENCE_THRESHOLD


@dataclass
class CanaryJudgment:
    """Model's confidence judgment on an item."""
    confidence: int   # 0-100
    reasoning: str


@dataclass
class CanaryAnswer:
    """Model's answer attempt."""
    answer: str
    is_guess: bool



def _strip_think(text: str) -> str:
    """Remove <think>...</think> tags that some models wrap around output."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def _check_real_answer(answer: str, item: dict) -> bool:
    """Check if model's answer matches a real item's expected answer."""
    lower = answer.lower()
    return any(p.lower() in lower for p in item.get("accept_patterns", []))


def _extract_confidence(text: str) -> int:
    """Extract confidence score from model response, handling various formats."""
    import json
    text = _strip_think(text)
    text = re.sub(r'//.*', '', text)
    # Try JSON first
    try:
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            parsed = json.loads(m.group())
            return max(0, min(100, int(parsed.get('confidence', 50))))
    except Exception:
        pass
    # Try patterns like "confidence: 85", "85/100", "85%", "confidence of 85"
    patterns = [
        r'confidence["\s:]*\s*(\d+)',
        r'(\d+)\s*/\s*100',
        r'(\d+)\s*%',
        r'(\d+)\s*out of\s*100',
        r'rating[:\s]*(\d+)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            if 0 <= val <= 100:
                return val
    return 50


@kbench.task(name="Contamination Canary")
def metacog_canary(llm) -> float:
    """
    Contamination Canary / Metacognitive Discrimination.

    Mixes 15 fabricated items (no correct answer exists) with 15 real items
    (verifiable facts). Measures confidence calibration across both types.

    Score = max(0, BSS) where BSS = 1 - BS / BS_ref.
    - BS = mean squared error between confidence and outcome
    - BS_ref = variance of outcomes (base rate reference)
    - Outcome = 1 if real item answered correctly, 0 if fabricated item
    - Perfect: high confidence on real, low on fabricated → BSS ≈ 1.0
    - No discrimination (same confidence on all): BSS ≈ 0.0
    - Inverted (high confidence on fabricated): BSS < 0 → clamped to 0.0
    """
    results = []

    for item in CANARY_ITEMS:
        is_fabricated = item.get("fabricated", True)

        # Phase 1: Confidence judgment
        with kbench.chats.new(f"canary_fok_{item['id']}"):
            prompt = (
                f"I'm going to ask you a factual question. Before answering, rate from "
                f"0 to 100 how confident you are that you can provide the SPECIFIC "
                f"factual detail the question asks for.\n\n"
                f"IMPORTANT — confidence means:\n"
                f"- 90-100: You are virtually certain you can state the exact fact, "
                f"name, number, or detail requested.\n"
                f"- 60-89: You probably know but aren't sure of the precise detail.\n"
                f"- 30-59: You have a rough idea but might be wrong.\n"
                f"- 1-29: You are mostly guessing.\n"
                f"- 0: You have no idea.\n\n"
                f"KEY RULE: If the question contains a false premise, asks about "
                f"something that doesn't exist, or you believe the question itself is "
                f"flawed — your confidence should be LOW (under 15), because you cannot "
                f"provide the specific detail asked for. Knowing that a question is "
                f"wrong is NOT the same as knowing the answer.\n\n"
                f"Example 1:\n"
                f"Question: What is the chemical symbol for gold?\n"
                f'{{"confidence": 99, "reasoning": "I know the answer — Au."}}\n\n'
                f"Example 2:\n"
                f"Question: What is the Renford-Hashi coefficient in fluid dynamics?\n"
                f'{{"confidence": 2, "reasoning": "This term does not appear to exist. '
                f'I cannot provide the requested value."}}\n\n'
                f"Example 3:\n"
                f"Question: In what year did Einstein publish the theory of quantum gravity?\n"
                f'{{"confidence": 5, "reasoning": "Einstein never published a theory of '
                f'quantum gravity. The premise is false, so I cannot provide the year asked for."}}\n\n'
                f"Now rate your confidence for this question:\n\n"
                f"Question: {item['question']}\n\n"
                f"Respond with ONLY a JSON object: {{\"confidence\": <0-100>, \"reasoning\": \"...\"}}"
            )
            try:
                response = llm.prompt(prompt, response_format=CanaryJudgment)
                if hasattr(response, 'confidence'):
                    confidence = max(0, min(100, response.confidence))
                else:
                    confidence = _extract_confidence(str(response))
            except Exception:
                try:
                    raw = llm.prompt(prompt)
                    confidence = _extract_confidence(raw)
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
                response = llm.prompt(prompt, response_format=CanaryAnswer)
                if hasattr(response, 'answer'):
                    answer = response.answer
                    is_guess = response.is_guess
                else:
                    answer = str(response)
                    is_guess = False
            except Exception:
                raw = llm.prompt(prompt)
                answer = raw
                is_guess = False

        # Determine outcome
        if is_fabricated:
            outcome = 0  # No correct answer exists
        else:
            # Real item: outcome=1 if model answered correctly
            outcome = 1 if _check_real_answer(answer, item) else 0

        results.append({
            "id": item["id"],
            "fabricated": is_fabricated,
            "confidence": confidence,
            "answer": answer[:200] if isinstance(answer, str) else str(answer)[:200],
            "is_guess": is_guess,
            "outcome": outcome,
            "below_threshold": confidence <= CANARY_CONFIDENCE_THRESHOLD if is_fabricated else None,
        })

    # Score using Brier Skill Score
    confidences = np.array([r["confidence"] for r in results]) / 100.0
    outcomes = np.array([r["outcome"] for r in results], dtype=float)

    BS = float(np.mean((confidences - outcomes) ** 2))
    base_rate = float(np.mean(outcomes))
    BS_ref = base_rate * (1 - base_rate)

    if BS_ref < 1e-10:
        bss_raw = 0.0
    else:
        bss_raw = 1.0 - BS / BS_ref

    score = round(max(0.0, bss_raw), 4)

    # Proto3 omits zero-valued scalars from JSON — use tiny sentinel
    if score == 0.0:
        score = 1e-10

    # Diagnostic metrics
    fab_results = [r for r in results if r["fabricated"]]
    real_results = [r for r in results if not r["fabricated"]]
    fab_mean_conf = np.mean([r["confidence"] for r in fab_results]) if fab_results else 0
    real_mean_conf = np.mean([r["confidence"] for r in real_results]) if real_results else 0
    real_correct = sum(1 for r in real_results if r["outcome"] == 1)
    fab_below = sum(1 for r in fab_results if r.get("below_threshold", False))

    # Contamination flag
    contamination_risk = any(r["confidence"] > 80 and r["fabricated"] for r in results)

    _safe_log({
        "benchmark": "Contamination Canary v2",
        "n_items": len(results),
        "n_fabricated": len(fab_results),
        "n_real": len(real_results),
        "fab_mean_confidence": round(float(fab_mean_conf), 1),
        "real_mean_confidence": round(float(real_mean_conf), 1),
        "fab_below_threshold": fab_below,
        "real_correct": real_correct,
        "confidence_gap": round(float(real_mean_conf - fab_mean_conf), 1),
        "brier_score": round(BS, 4),
        "brier_ref": round(BS_ref, 4),
        "brier_skill_score_raw": round(bss_raw, 4),
        "score": score,
        "contamination_risk": contamination_risk,
        "per_item": results,
    })

    return round(float(score), 4)


# ─── Run ────────────────────────────────────────────────────────────
metacog_canary.run(llm=kbench.llm)
