"""
MetaCog Benchmark 2: Feeling-of-Knowing (FOK)

Two-phase prospective metacognitive monitoring benchmark.
Phase 1: Model rates confidence it CAN answer (0-100) WITHOUT seeing/giving the answer.
Phase 2: Model attempts to answer the question.

This separation is critical — it prevents post-hoc rationalization and tests
genuine metacognitive monitoring (Nelson & Narens, 1990).

Cognitive Science Basis:
- Feeling-of-Knowing (Hart, 1965; Nelson & Narens, 1990)
- After failing to immediately recall, humans can predict recognition success
- FOK monitors "recallable aspects related to that item" (non-magic hypothesis)
- Human FOK gamma: 0.25–0.55 (Goodman-Kruskal correlation)

Metrics:
- Gamma correlation: ordinal association between FOK ratings and accuracy
- ECE: Expected Calibration Error (binned confidence vs accuracy)
- Resolution/AUC: discrimination between known and unknown items
- Category breakdown: calibration by question type

Score: Composite of gamma, 1-ECE, and AUC (weighted).

Shortcut Resistance:
- Two-phase protocol prevents confidence being conditioned on answer quality
- Mix of retrievable, boundary, obscure, reasoning, and unanswerable questions
- Unanswerable items test epistemic humility (ideal: low FOK + refusal to answer)
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.fok_questions import FOK_QUESTIONS


# ─── Structured Output Schemas ──────────────────────────────────────

@dataclass
class FOKJudgment:
    """Phase 1: Feeling-of-knowing judgment (before answering)."""
    confidence: int  # 0-100: How confident are you that you CAN answer this correctly?
    reasoning: str   # Brief explanation of why you feel you do/don't know this


@dataclass
class FOKAnswer:
    """Phase 2: The actual answer attempt."""
    answer: str       # The answer (or "I don't know" / "unanswerable")
    is_guess: bool    # Whether this is a guess vs a confident answer


# ─── Answer Verification ────────────────────────────────────────────

def normalize(text: str) -> str:
    """Normalize text for fuzzy matching."""
    text = text.lower().strip()
    text = re.sub(r'\b(the|a|an)\b', '', text)
    text = re.sub(r'[^\w\s\.\+\-/]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def check_answer(model_answer: str, question: dict) -> bool:
    """Check if model's answer matches the correct answer."""
    if question["answer"] == "__UNANSWERABLE__":
        # For unanswerable questions, the model should express uncertainty
        lower = model_answer.lower()
        uncertainty_markers = [
            "unanswerable", "cannot be answered", "no correct answer",
            "impossible to", "cannot determine", "no way to know",
            "subjective", "don't know", "doesn't have", "no definitive",
            "can't be determined", "not possible", "no single",
            "matter of opinion", "no objective", "undefined",
        ]
        return any(marker in lower for marker in uncertainty_markers)

    model_norm = normalize(model_answer)

    # Check against accept patterns
    for pattern in question.get("accept_patterns", []):
        if pattern.lower() in model_norm:
            return True

    # Numeric tolerance check
    tolerance = question.get("numeric_tolerance", 0.05)
    try:
        model_num = float(re.search(r'[\-\+]?[\d\.]+', model_norm).group())
        correct_num = float(re.search(r'[\-\+]?[\d\.]+', question["answer"]).group())
        if correct_num == 0:
            return abs(model_num) < 0.01
        return abs(model_num - correct_num) / abs(correct_num) < tolerance
    except (ValueError, AttributeError, ZeroDivisionError):
        pass

    return False


# ─── Statistical Metrics ────────────────────────────────────────────

def goodman_kruskal_gamma(x: list, y: list) -> float:
    """
    Compute Goodman-Kruskal gamma correlation.
    Standard metric in metamemory research for ordinal association.

    gamma = (concordant - discordant) / (concordant + discordant)
    Range: -1 to +1
    """
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
            # ties (product == 0) are excluded

    denom = concordant + discordant
    if denom == 0:
        return 0.0
    return concordant / denom - discordant / denom


def compute_ece(confidences: list, accuracies: list, n_bins: int = 10) -> dict:
    """Compute Expected Calibration Error with bin details."""
    conf = np.array(confidences) / 100.0
    acc = np.array(accuracies, dtype=float)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_data = []
    ece = 0.0
    total = len(conf)

    for i in range(n_bins):
        lo, hi = bin_boundaries[i], bin_boundaries[i + 1]
        if i == 0:
            mask = (conf >= lo) & (conf <= hi)
        else:
            mask = (conf > lo) & (conf <= hi)
        bin_count = mask.sum()

        if bin_count == 0:
            bin_data.append({"bin": f"{lo:.1f}-{hi:.1f}", "count": 0})
            continue

        avg_conf = conf[mask].mean()
        avg_acc = acc[mask].mean()
        gap = abs(avg_acc - avg_conf)
        ece += (bin_count / total) * gap

        bin_data.append({
            "bin": f"{lo:.1f}-{hi:.1f}",
            "count": int(bin_count),
            "avg_confidence": round(float(avg_conf), 3),
            "avg_accuracy": round(float(avg_acc), 3),
            "gap": round(float(gap), 3),
        })

    return {"ece": round(float(ece), 4), "bin_data": bin_data, "n_samples": total}


def compute_auc(confidences: list, accuracies: list) -> float:
    """
    Compute AUC for FOK ratings predicting correctness.
    Uses the trapezoidal rule on the empirical ROC.
    """
    conf = np.array(confidences, dtype=float)
    acc = np.array(accuracies, dtype=float)

    if acc.sum() == 0 or acc.sum() == len(acc):
        return 0.5  # Degenerate case

    # Sort by descending confidence
    sorted_idx = np.argsort(-conf)
    sorted_acc = acc[sorted_idx]

    # Compute ROC
    tpr_list = [0.0]
    fpr_list = [0.0]
    tp = 0
    fp = 0
    pos = acc.sum()
    neg = len(acc) - pos

    for a in sorted_acc:
        if a == 1:
            tp += 1
        else:
            fp += 1
        tpr_list.append(tp / pos)
        fpr_list.append(fp / neg)

    # Trapezoidal AUC
    auc = 0.0
    for i in range(1, len(tpr_list)):
        auc += (fpr_list[i] - fpr_list[i - 1]) * (tpr_list[i] + tpr_list[i - 1]) / 2

    return round(float(auc), 4)


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="metacog_fok")
def metacog_fok(llm) -> float:
    """
    Feeling-of-Knowing (FOK) Benchmark.

    Two-phase protocol measuring prospective metacognitive monitoring.
    Phase 1: Rate confidence you CAN answer (without answering).
    Phase 2: Actually answer.

    Score = weighted composite:
      0.40 * normalized_gamma + 0.30 * (1 - ECE) + 0.30 * AUC

    Cognitive Science Basis: Hart (1965), Nelson & Narens (1990).
    Human FOK gamma: 0.25–0.55. Human ECE: 0.10–0.20.
    """
    fok_ratings = []
    accuracies = []
    results_log = []
    category_results = {}

    for i, q in enumerate(FOK_QUESTIONS):
        cat = q["category"]
        if cat not in category_results:
            category_results[cat] = {"fok": [], "acc": []}

        # ── Phase 1: FOK Judgment (confidence BEFORE answering) ──
        with kbench.chats.new(f"fok_phase1_{i}"):
            phase1_prompt = (
                f"I'm going to ask you a question. Before answering, I want you to rate "
                f"how confident you are that you CAN answer it correctly.\n\n"
                f"Question: {q['question']}\n\n"
                f"DO NOT answer the question yet. Only rate your confidence.\n\n"
                f"Respond with ONLY a JSON object:\n"
                f'{{"confidence": <0-100>, "reasoning": "<brief explanation>"}}'
            )

            try:
                fok = llm.prompt(phase1_prompt, schema=FOKJudgment)
                fok_confidence = max(0, min(100, fok.confidence))
                fok_reasoning = fok.reasoning
            except Exception:
                raw = llm.prompt(phase1_prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    fok_confidence = max(0, min(100, int(parsed.get("confidence", 50))))
                    fok_reasoning = str(parsed.get("reasoning", ""))
                except Exception:
                    fok_confidence = 50
                    fok_reasoning = raw[:200]

        # ── Phase 2: Answer Attempt (separate chat — no confidence leakage) ──
        with kbench.chats.new(f"fok_phase2_{i}"):
            phase2_prompt = (
                f"Answer the following question as accurately as you can. "
                f"If the question is unanswerable or has no single correct answer, say so.\n\n"
                f"Question: {q['question']}\n\n"
                f"Respond with ONLY a JSON object:\n"
                f'{{"answer": "<your answer>", "is_guess": <true/false>}}'
            )

            try:
                ans = llm.prompt(phase2_prompt, schema=FOKAnswer)
                answer = ans.answer
                is_guess = ans.is_guess
            except Exception:
                raw = llm.prompt(phase2_prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    answer = str(parsed.get("answer", raw))
                    is_guess = bool(parsed.get("is_guess", False))
                except Exception:
                    answer = raw
                    is_guess = False

        is_correct = check_answer(answer, q)
        fok_ratings.append(fok_confidence)
        accuracies.append(is_correct)
        category_results[cat]["fok"].append(fok_confidence)
        category_results[cat]["acc"].append(is_correct)

        results_log.append({
            "id": q["id"],
            "question": q["question"],
            "category": cat,
            "fok_confidence": fok_confidence,
            "fok_reasoning": fok_reasoning[:100],
            "answer": answer[:100],
            "correct_answer": q["answer"],
            "is_correct": is_correct,
            "is_guess": is_guess,
        })

    # ── Compute Metrics ──
    gamma = goodman_kruskal_gamma(fok_ratings, [int(a) for a in accuracies])
    ece_result = compute_ece(fok_ratings, accuracies)
    auc = compute_auc(fok_ratings, accuracies)

    # Normalize gamma from [-1, 1] to [0, 1]
    gamma_norm = (gamma + 1) / 2

    # Composite score
    score = round(0.40 * gamma_norm + 0.30 * (1 - ece_result["ece"]) + 0.30 * auc, 4)

    # ── Detailed Logging ──
    print(f"\n{'='*60}")
    print(f"FEELING-OF-KNOWING (FOK) BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Questions: {len(FOK_QUESTIONS)}")
    print(f"Overall accuracy: {sum(accuracies)/len(accuracies):.2%}")
    print(f"Mean FOK confidence: {sum(fok_ratings)/len(fok_ratings):.1f}%")
    print(f"\n--- Metacognitive Metrics ---")
    print(f"Gamma correlation: {gamma:+.4f}  (human range: 0.25–0.55)")
    print(f"ECE: {ece_result['ece']:.4f}  (human range: 0.10–0.20)")
    print(f"AUC (discrimination): {auc:.4f}")
    print(f"Composite score: {score:.4f}")

    # Category breakdown
    print(f"\n--- By Category ---")
    for cat, data in sorted(category_results.items()):
        n = len(data["acc"])
        acc = sum(data["acc"]) / n if n > 0 else 0
        mean_fok = sum(data["fok"]) / n if n > 0 else 0
        cat_gamma = goodman_kruskal_gamma(data["fok"], [int(a) for a in data["acc"]])
        print(f"  {cat:15s}: n={n:2d}, acc={acc:.2%}, mean_fok={mean_fok:.0f}%, γ={cat_gamma:+.3f}")

    # Calibration bins
    print(f"\n--- Calibration Bins ---")
    for b in ece_result["bin_data"]:
        if b["count"] > 0:
            print(f"  {b['bin']}: n={b['count']}, "
                  f"conf={b['avg_confidence']:.2f}, "
                  f"acc={b['avg_accuracy']:.2f}, "
                  f"gap={b['gap']:.3f}")

    # Per-question results
    print(f"\n--- Per-Question Results ---")
    for r in results_log:
        status = "✓" if r["is_correct"] else "✗"
        print(f"  {status} [{r['fok_confidence']:3d}%] [{r['category']:12s}] "
              f"{r['question'][:45]}... → {r['answer'][:30]}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
metacog_fok.run(llm=kbench.llm)
