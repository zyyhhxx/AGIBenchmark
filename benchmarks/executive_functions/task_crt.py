"""
Executive Functions Benchmark 5: Cognitive Reflection Test (CRT)

Tests the ability to override intuitive-but-wrong responses (System 1)
with deliberate reasoning (System 2). This measures response inhibition,
a core component of executive function.

Cognitive Science Basis:
- Frederick (2005): The Cognitive Reflection Test
- Kahneman (2011): System 1 (fast, intuitive) vs System 2 (slow, deliberate)
- Miyake et al. (2000): Inhibition as a core executive function
- Toplak et al. (2011): CRT correlates with rational thinking ability

Protocol:
1. Present 12 novel CRT-style questions (not from published tests)
2. Each has a compelling intuitive-but-wrong answer
3. Model provides numerical/short answer + confidence (0-100)
4. Score: correct answers that resist the intuitive trap

Metrics:
- Accuracy: proportion of correct (System 2) answers
- Intuitive trap rate: proportion of intuitive-wrong answers
- Deliberation score: accuracy weighted by difficulty
- Confidence calibration: are correct answers higher-confidence?

Score = 0.40 * accuracy + 0.30 * (1 - trap_rate) + 0.20 * difficulty_bonus + 0.10 * calibration

Shortcut Resistance:
- Novel items (not from Frederick 2005 or published CRTs)
- Each item has a SPECIFIC intuitive wrong answer — we check if the model
  falls for it vs. gets a different wrong answer vs. gets it right
- Difficulty stratification reveals genuine reasoning vs. memorization
"""

import kaggle_benchmarks as kbench
import json as _json
def _safe_log(data): print(_json.dumps(data, indent=2, default=str))
from dataclasses import dataclass
import numpy as np
import re
import json

from data.crt_items import CRT_ITEMS


# ─── Structured Output Schema ──────────────────────────────────────

@dataclass
class CRTResponse:
    """Model's answer to a CRT question."""
    answer: str        # The answer (number or short text)
    confidence: int    # 0-100 confidence
    reasoning: str     # Explanation of thought process


# ─── Answer Checking ────────────────────────────────────────────────

def normalize_answer(answer: str) -> str:
    """Normalize an answer for comparison."""
    answer = answer.strip().lower()
    # Remove common prefixes
    for prefix in ['$', '£', '€']:
        answer = answer.replace(prefix, '')
    # Remove trailing units
    answer = re.sub(r'\s*(dollars?|cents?|minutes?|days?|sheep|position|percent|%|leaves?|times?|name).*$', '', answer, flags=re.IGNORECASE)
    answer = answer.strip().rstrip('.')
    return answer


def check_answer(model_answer: str, correct: str, intuitive_wrong: str):
    """
    Check if answer is correct, intuitively wrong, or other wrong.
    Returns: 'correct', 'intuitive_trap', or 'other_wrong'
    """
    norm_model = normalize_answer(str(model_answer))
    norm_correct = normalize_answer(str(correct))
    norm_intuitive = normalize_answer(str(intuitive_wrong))

    # Check for correct
    if norm_model == norm_correct:
        return 'correct'
    # Try numeric comparison
    try:
        if abs(float(norm_model) - float(norm_correct)) < 0.01:
            return 'correct'
    except (ValueError, TypeError):
        pass
    # Check for special cases
    if norm_correct == 'emily' and 'emily' in norm_model:
        return 'correct'

    # Check for intuitive trap
    if norm_model == norm_intuitive:
        return 'intuitive_trap'
    try:
        if abs(float(norm_model) - float(norm_intuitive)) < 0.01:
            return 'intuitive_trap'
    except (ValueError, TypeError):
        pass

    return 'other_wrong'


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="exec_func_crt")
def exec_func_crt(llm) -> float:
    """
    Cognitive Reflection Test Benchmark.

    Tests inhibition of intuitive-but-wrong answers in favor of
    deliberate reasoning. A core executive function measure.

    Score = 0.40 * accuracy + 0.30 * (1 - trap_rate) + 0.20 * difficulty_bonus + 0.10 * calibration

    Cognitive Science: Frederick (2005), Kahneman (2011).
    Human accuracy: ~30% (general public), ~50% (MIT students).
    """
    results = []
    difficulty_correct = {"easy": [], "medium": [], "hard": []}

    for item in CRT_ITEMS:
        prompt = (
            f"Please answer this question. Give ONLY the numerical answer "
            f"(or a short phrase if non-numerical), your confidence level (0-100), "
            f"and a brief explanation of your reasoning.\n\n"
            f"Question: {item['question']}\n\n"
            f"Think carefully before answering."
        )

        with kbench.chats.new(f"crt_{item['id']}"):
            try:
                response = llm(prompt, response_format=CRTResponse)
                answer = response.answer
                confidence = max(0, min(100, response.confidence))
                reasoning = response.reasoning
            except Exception:
                raw = llm(prompt)
                answer = raw.strip()
                confidence = 50
                reasoning = ""

        verdict = check_answer(answer, item['correct'], item['intuitive_wrong'])
        is_correct = verdict == 'correct'
        is_trap = verdict == 'intuitive_trap'

        result = {
            "id": item["id"],
            "difficulty": item["difficulty"],
            "model_answer": str(answer)[:100],
            "correct_answer": item["correct"],
            "intuitive_wrong": item["intuitive_wrong"],
            "verdict": verdict,
            "confidence": confidence,
            "cognitive_trap": item["cognitive_trap"],
        }
        results.append(result)
        difficulty_correct[item["difficulty"]].append(1.0 if is_correct else 0.0)

    # ── Compute Metrics ──

    n_correct = sum(1 for r in results if r["verdict"] == "correct")
    n_trap = sum(1 for r in results if r["verdict"] == "intuitive_trap")
    n_other = sum(1 for r in results if r["verdict"] == "other_wrong")

    accuracy = n_correct / len(results)
    trap_rate = n_trap / len(results)

    # Difficulty bonus: harder items worth more
    diff_weights = {"easy": 1.0, "medium": 1.5, "hard": 2.0}
    weighted_correct = 0
    weighted_total = 0
    for diff, scores in difficulty_correct.items():
        w = diff_weights[diff]
        weighted_correct += sum(s * w for s in scores)
        weighted_total += len(scores) * w
    difficulty_bonus = weighted_correct / weighted_total if weighted_total > 0 else 0

    # Calibration: are correct answers higher-confidence than wrong?
    correct_confs = [r["confidence"] for r in results if r["verdict"] == "correct"]
    wrong_confs = [r["confidence"] for r in results if r["verdict"] != "correct"]
    if correct_confs and wrong_confs:
        calibration = min(1.0, max(0.0,
            (np.mean(correct_confs) - np.mean(wrong_confs)) / 100 + 0.5
        ))
    else:
        calibration = 0.5  # No signal

    # ── Composite Score ──
    score = (
        0.40 * accuracy +
        0.30 * (1 - trap_rate) +
        0.20 * difficulty_bonus +
        0.10 * calibration
    )
    score = round(float(np.clip(score, 0, 1)), 4)

    # ── Log ──
    _safe_log({
        "benchmark": "Cognitive Reflection Test",
        "n_items": len(results),
        "accuracy": round(accuracy, 4),
        "intuitive_trap_rate": round(trap_rate, 4),
        "other_wrong_rate": round(n_other / len(results), 4),
        "difficulty_bonus": round(difficulty_bonus, 4),
        "calibration": round(calibration, 4),
        "composite_score": score,
        "difficulty_breakdown": {
            d: round(np.mean(s), 4) if s else 0
            for d, s in difficulty_correct.items()
        },
        "per_item": results,
    })

    # ── Display ──
    print(f"\n{'='*60}")
    print(f"COGNITIVE REFLECTION TEST RESULTS")
    print(f"{'='*60}")
    for r in results:
        icon = "✓" if r["verdict"] == "correct" else ("⚠" if r["verdict"] == "intuitive_trap" else "✗")
        print(f"  {icon} {r['id']} [{r['difficulty']:6s}] [{r['confidence']:3d}%] "
              f"Got: {r['model_answer'][:20]:20s} Correct: {r['correct_answer']:10s} "
              f"Trap: {r['intuitive_wrong']:5s} → {r['verdict']}")

    print(f"\n--- Summary ---")
    print(f"Accuracy:           {accuracy:.2%} ({n_correct}/{len(results)})")
    print(f"Intuitive trap rate: {trap_rate:.2%} ({n_trap}/{len(results)})")
    print(f"Other wrong:         {n_other/len(results):.2%}")
    print(f"Difficulty bonus:    {difficulty_bonus:.4f}")
    print(f"Calibration:         {calibration:.4f}")
    print(f"Composite score:     {score:.4f}")

    return score


exec_func_crt.run(llm=kbench.llm)
