"""
MetaCog Benchmark 1: Retrospective Confidence Calibration

Tests whether a model's stated confidence in its answers correlates
with its actual accuracy. Well-calibrated models should be right ~80%
of the time when they say they're 80% confident.

Cognitive Science Basis:
- Based on the metacognitive monitoring framework (Nelson & Narens, 1990)
- Measures "retrospective confidence" — post-answer confidence ratings
- Uses Expected Calibration Error (ECE) as the primary metric
- Human baseline ECE is typically 0.10–0.20

Methodology:
1. Present diverse questions across domains and difficulty levels
2. Ask model to answer AND rate confidence (0–100)
3. Bin answers by confidence level
4. Compare stated confidence to actual accuracy per bin
5. Compute ECE = weighted average of |accuracy_bin - confidence_bin|

Score: 1 - ECE (higher = better calibrated, range 0–1)

Shortcut Resistance:
- Questions span many domains (no single-domain memorisation helps)
- Mix of difficulty levels forces genuine uncertainty
- Confidence must be stated alongside the answer (no post-hoc adjustment)
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import pandas as pd
import re
import json


# ─── Question Dataset ───────────────────────────────────────────────
# Inline the questions so the notebook is self-contained on Kaggle

CALIBRATION_QUESTIONS = [
    # TIER 1: Easy
    {"question": "What is the chemical symbol for gold?", "answer": "Au", "domain": "chemistry", "difficulty": 1},
    {"question": "How many sides does a hexagon have?", "answer": "6", "domain": "math", "difficulty": 1},
    {"question": "What planet is known as the Red Planet?", "answer": "Mars", "domain": "astronomy", "difficulty": 1},
    {"question": "What is the largest organ in the human body?", "answer": "skin", "domain": "biology", "difficulty": 1},
    {"question": "In which year did World War II end?", "answer": "1945", "domain": "history", "difficulty": 1},
    {"question": "What is the boiling point of water in degrees Celsius at standard atmospheric pressure?", "answer": "100", "domain": "physics", "difficulty": 1},
    {"question": "Who wrote the play 'Romeo and Juliet'?", "answer": "Shakespeare", "domain": "literature", "difficulty": 1},
    {"question": "What is the capital of Japan?", "answer": "Tokyo", "domain": "geography", "difficulty": 1},
    {"question": "What does DNA stand for?", "answer": "deoxyribonucleic acid", "domain": "biology", "difficulty": 1},
    {"question": "What is the speed of light in a vacuum, approximately in km/s?", "answer": "300000", "domain": "physics", "difficulty": 1},
    # TIER 2: Medium
    {"question": "What is the smallest prime number greater than 50?", "answer": "53", "domain": "math", "difficulty": 2},
    {"question": "Which enzyme is primarily responsible for unwinding the DNA double helix during replication?", "answer": "helicase", "domain": "biology", "difficulty": 2},
    {"question": "In what year was the Treaty of Westphalia signed, ending the Thirty Years' War?", "answer": "1648", "domain": "history", "difficulty": 2},
    {"question": "What is the derivative of ln(x) with respect to x?", "answer": "1/x", "domain": "math", "difficulty": 2},
    {"question": "Which country has the longest coastline in the world?", "answer": "Canada", "domain": "geography", "difficulty": 2},
    {"question": "What is the half-life of Carbon-14, approximately in years?", "answer": "5730", "domain": "physics", "difficulty": 2},
    {"question": "Who composed 'The Four Seasons'?", "answer": "Vivaldi", "domain": "music", "difficulty": 2},
    {"question": "What is the Mohs hardness of quartz?", "answer": "7", "domain": "geology", "difficulty": 2},
    {"question": "In computing, what does the acronym RISC stand for?", "answer": "reduced instruction set computer", "domain": "computing", "difficulty": 2},
    {"question": "What neurotransmitter is most directly associated with the reward system in the brain?", "answer": "dopamine", "domain": "neuroscience", "difficulty": 2},
    {"question": "What is the approximate distance from Earth to the Moon in kilometers?", "answer": "384400", "domain": "astronomy", "difficulty": 2},
    {"question": "Which philosopher wrote 'Critique of Pure Reason'?", "answer": "Kant", "domain": "philosophy", "difficulty": 2},
    {"question": "What is the oxidation state of iron in rust (Fe2O3)?", "answer": "+3", "domain": "chemistry", "difficulty": 2},
    {"question": "In what year did the Berlin Wall fall?", "answer": "1989", "domain": "history", "difficulty": 2},
    {"question": "What is the name of the longest river in Africa?", "answer": "Nile", "domain": "geography", "difficulty": 2},
    # TIER 3: Hard
    {"question": "What is the sum of the first 20 prime numbers?", "answer": "639", "domain": "math", "difficulty": 3},
    {"question": "In which specific year did the Tunguska event occur?", "answer": "1908", "domain": "history", "difficulty": 3},
    {"question": "What is the atomic number of Promethium?", "answer": "61", "domain": "chemistry", "difficulty": 3},
    {"question": "How many bones are in the adult human wrist (carpal bones only)?", "answer": "8", "domain": "anatomy", "difficulty": 3},
    {"question": "What is the escape velocity from the surface of Mars in km/s, approximately?", "answer": "5.0", "domain": "physics", "difficulty": 3},
    {"question": "Who proved the incompleteness theorems in 1931?", "answer": "Gödel", "domain": "math", "difficulty": 3},
    {"question": "What is the name of the deepest known point in the Earth's oceans?", "answer": "Challenger Deep", "domain": "geography", "difficulty": 3},
    {"question": "In which year was the Rosetta Stone discovered?", "answer": "1799", "domain": "history", "difficulty": 3},
    {"question": "What is the second most abundant element in the Earth's crust by mass?", "answer": "silicon", "domain": "geology", "difficulty": 3},
    {"question": "What is the value of the golden ratio (phi) to 3 decimal places?", "answer": "1.618", "domain": "math", "difficulty": 3},
    {"question": "Which organelle is known as the 'powerhouse of the cell' and uses oxidative phosphorylation?", "answer": "mitochondria", "domain": "biology", "difficulty": 3},
    {"question": "What is the coefficient of restitution for a perfectly elastic collision?", "answer": "1", "domain": "physics", "difficulty": 3},
    {"question": "Who formulated the Church-Turing thesis alongside Turing?", "answer": "Church", "domain": "computing", "difficulty": 3},
    {"question": "In what year was the Universal Declaration of Human Rights adopted?", "answer": "1948", "domain": "history", "difficulty": 3},
    {"question": "What is the name of the largest known structure in the observable universe?", "answer": "Hercules-Corona Borealis Great Wall", "domain": "astronomy", "difficulty": 3},
]


# ─── Structured Output Schema ──────────────────────────────────────

@dataclass
class ConfidentAnswer:
    """Model's answer with a confidence rating."""
    answer: str           # The actual answer to the question
    confidence: int       # 0-100 confidence rating


# ─── Answer Verification ────────────────────────────────────────────

def normalize(text: str) -> str:
    """Normalize text for fuzzy matching."""
    text = text.lower().strip()
    # Remove articles, punctuation
    text = re.sub(r'\b(the|a|an)\b', '', text)
    text = re.sub(r'[^\w\s\.\+\-/]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def check_answer(model_answer: str, correct_answer: str) -> bool:
    """Check if model's answer matches the correct answer (fuzzy)."""
    model_norm = normalize(model_answer)
    correct_norm = normalize(correct_answer)

    # Direct containment (either direction)
    if correct_norm in model_norm or model_norm in correct_norm:
        return True

    # For numeric answers, try numeric comparison
    try:
        model_num = float(re.search(r'[\-\+]?[\d\.]+', model_norm).group())
        correct_num = float(re.search(r'[\-\+]?[\d\.]+', correct_norm).group())
        # Allow 5% tolerance for approximate numeric answers
        if correct_num == 0:
            return abs(model_num) < 0.01
        return abs(model_num - correct_num) / abs(correct_num) < 0.05
    except (ValueError, AttributeError, ZeroDivisionError):
        pass

    return False


# ─── ECE Computation ────────────────────────────────────────────────

def compute_ece(confidences: list[float], accuracies: list[bool], n_bins: int = 10) -> dict:
    """
    Compute Expected Calibration Error.

    Returns dict with:
    - ece: float (0-1, lower = better calibrated)
    - bin_data: list of dicts with bin details
    - n_samples: int
    """
    confidences = np.array(confidences) / 100.0  # Normalize to 0-1
    accuracies = np.array(accuracies, dtype=float)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_data = []

    ece = 0.0
    total = len(confidences)

    for i in range(n_bins):
        lo, hi = bin_boundaries[i], bin_boundaries[i + 1]
        mask = (confidences > lo) & (confidences <= hi) if i > 0 else (confidences >= lo) & (confidences <= hi)
        bin_count = mask.sum()

        if bin_count == 0:
            bin_data.append({
                "bin": f"{lo:.1f}-{hi:.1f}",
                "count": 0,
                "avg_confidence": None,
                "avg_accuracy": None,
                "gap": None,
            })
            continue

        avg_conf = confidences[mask].mean()
        avg_acc = accuracies[mask].mean()
        gap = abs(avg_acc - avg_conf)
        ece += (bin_count / total) * gap

        bin_data.append({
            "bin": f"{lo:.1f}-{hi:.1f}",
            "count": int(bin_count),
            "avg_confidence": round(float(avg_conf), 3),
            "avg_accuracy": round(float(avg_acc), 3),
            "gap": round(float(gap), 3),
        })

    return {
        "ece": round(float(ece), 4),
        "bin_data": bin_data,
        "n_samples": total,
    }


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="metacog_calibration")
def metacog_calibration(llm) -> float:
    """
    Metacognitive Calibration Benchmark.

    Measures how well a model's stated confidence matches its actual accuracy.
    Score = 1 - ECE (higher = better calibrated).

    Cognitive Science Basis: Nelson & Narens (1990) metamemory monitoring framework.
    Human baseline ECE: 0.10-0.20, so human score ≈ 0.80-0.90.
    """
    confidences = []
    accuracies = []
    results_log = []

    for i, q in enumerate(CALIBRATION_QUESTIONS):
        with kbench.chats.new(f"q_{i}"):
            prompt = (
                f"Answer the following question. After your answer, rate your confidence "
                f"from 0 to 100 (where 0 = pure guess, 100 = absolutely certain).\n\n"
                f"Question: {q['question']}\n\n"
                f"Respond with ONLY a JSON object in this exact format:\n"
                f'{{"answer": "<your answer>", "confidence": <0-100>}}'
            )

            try:
                result = llm.prompt(prompt, schema=ConfidentAnswer)
                answer = result.answer
                confidence = max(0, min(100, result.confidence))
            except Exception:
                # Fallback: try to parse raw text
                raw = llm.prompt(prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    answer = str(parsed.get("answer", ""))
                    confidence = int(parsed.get("confidence", 50))
                    confidence = max(0, min(100, confidence))
                except Exception:
                    answer = raw
                    confidence = 50  # Default if parsing fails

            is_correct = check_answer(answer, q["answer"])
            confidences.append(confidence)
            accuracies.append(is_correct)

            results_log.append({
                "question": q["question"],
                "correct_answer": q["answer"],
                "model_answer": answer,
                "confidence": confidence,
                "is_correct": is_correct,
                "domain": q["domain"],
                "difficulty": q["difficulty"],
            })

    # Compute calibration metrics
    metrics = compute_ece(confidences, accuracies)
    score = round(1.0 - metrics["ece"], 4)

    # Log detailed results for analysis
    print(f"\n{'='*60}")
    print(f"METACOGNITIVE CALIBRATION RESULTS")
    print(f"{'='*60}")
    print(f"Questions answered: {metrics['n_samples']}")
    print(f"Overall accuracy: {sum(accuracies)/len(accuracies):.2%}")
    print(f"Mean confidence: {sum(confidences)/len(confidences):.1f}%")
    print(f"ECE: {metrics['ece']:.4f}")
    print(f"Score (1-ECE): {score:.4f}")
    print(f"\nCalibration by bin:")
    for b in metrics["bin_data"]:
        if b["count"] > 0:
            print(f"  {b['bin']}: n={b['count']}, "
                  f"conf={b['avg_confidence']:.2f}, "
                  f"acc={b['avg_accuracy']:.2f}, "
                  f"gap={b['gap']:.3f}")

    # Log per-question details
    print(f"\nPer-question results:")
    for r in results_log:
        status = "✓" if r["is_correct"] else "✗"
        print(f"  {status} [{r['confidence']:3d}%] {r['question'][:50]}... "
              f"→ {r['model_answer'][:30]}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
# On Kaggle: use kbench.llm
# Locally: this will error without the Kaggle proxy, but the code is testable

metacog_calibration.run(llm=kbench.llm)

# ─── Choose this task for leaderboard ──────────────────────────────
# In the final cell of the Kaggle notebook:
# %choose metacog_calibration
