"""
FOK Sub-metric Tasks: Individual leaderboard entries for each FOK metric.

Splits the composite FOK benchmark into separate tasks for:
- fok_gamma: Goodman-Kruskal gamma correlation
- fok_ece: Expected Calibration Error (inverted: 1 - ECE)  
- fok_auc: Discrimination AUC

Each runs the same two-phase protocol but returns a single metric.
These are self-contained — they don't import from task_fok.py (which
has module-level .run() calls that fail outside Kaggle).
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json

from data.fok_questions import FOK_QUESTIONS


# ─── Schemas ─────────────────────────────────────────────────────────

@dataclass
class FOKJudgment:
    confidence: int
    reasoning: str

@dataclass
class FOKAnswer:
    answer: str
    is_guess: bool


# ─── Metric Functions (self-contained) ──────────────────────────────

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'\b(the|a|an)\b', '', text)
    text = re.sub(r'[^\w\s\.\+\-/]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def check_answer(model_answer: str, question: dict) -> bool:
    if question["answer"] == "__UNANSWERABLE__":
        lower = model_answer.lower()
        markers = ["unanswerable", "cannot be answered", "no correct answer",
                    "impossible to", "cannot determine", "don't know",
                    "subjective", "no definitive", "not possible", "undefined"]
        return any(m in lower for m in markers)
    model_norm = normalize(model_answer)
    for pattern in question.get("accept_patterns", []):
        if pattern.lower() in model_norm:
            return True
    tol = question.get("numeric_tolerance", 0.05)
    try:
        model_num = float(re.search(r'[\-\+]?[\d\.]+', model_norm).group())
        correct_num = float(re.search(r'[\-\+]?[\d\.]+', question["answer"]).group())
        if correct_num == 0:
            return abs(model_num) < 0.01
        return abs(model_num - correct_num) / abs(correct_num) < tol
    except (ValueError, AttributeError, ZeroDivisionError):
        pass
    return False

def goodman_kruskal_gamma(x, y):
    n = len(x)
    concordant = discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            product = (x[i] - x[j]) * (y[i] - y[j])
            if product > 0: concordant += 1
            elif product < 0: discordant += 1
    denom = concordant + discordant
    return (concordant - discordant) / denom if denom else 0.0

def compute_ece(confidences, accuracies, n_bins=10):
    conf = np.array(confidences) / 100.0
    acc = np.array(accuracies, dtype=float)
    boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total = len(conf)
    for i in range(n_bins):
        lo, hi = boundaries[i], boundaries[i + 1]
        mask = (conf >= lo) & (conf <= hi) if i == 0 else (conf > lo) & (conf <= hi)
        n = mask.sum()
        if n == 0: continue
        ece += (n / total) * abs(acc[mask].mean() - conf[mask].mean())
    return round(float(ece), 4)

def compute_auc(confidences, accuracies):
    conf = np.array(confidences, dtype=float)
    acc = np.array(accuracies, dtype=float)
    if acc.sum() == 0 or acc.sum() == len(acc): return 0.5
    idx = np.argsort(-conf)
    sorted_acc = acc[idx]
    tpr, fpr = [0.0], [0.0]
    tp = fp = 0
    pos, neg = acc.sum(), len(acc) - acc.sum()
    for a in sorted_acc:
        if a == 1: tp += 1
        else: fp += 1
        tpr.append(tp / pos)
        fpr.append(fp / neg)
    auc = sum((fpr[i] - fpr[i-1]) * (tpr[i] + tpr[i-1]) / 2 for i in range(1, len(tpr)))
    return round(float(auc), 4)


# ─── Data Collection ────────────────────────────────────────────────

def _collect_fok_data(llm):
    """Run the FOK two-phase protocol. Returns (fok_ratings, accuracies)."""
    fok_ratings = []
    accuracies = []

    for i, q in enumerate(FOK_QUESTIONS):
        with kbench.chats.new(f"foksub_p1_{i}"):
            p1 = (
                f"Rate how confident you are (0-100) that you CAN correctly answer "
                f"this question. DO NOT answer it yet.\n\n"
                f"Question: {q['question']}\n\n"
                f'Respond: {{"confidence": <0-100>, "reasoning": "<brief>"}}'
            )
            try:
                r = llm.prompt(p1, schema=FOKJudgment)
                conf = max(0, min(100, r.confidence))
            except Exception:
                conf = 50

        with kbench.chats.new(f"foksub_p2_{i}"):
            p2 = (
                f"Answer this question accurately. If unanswerable, say so.\n\n"
                f"Question: {q['question']}\n\n"
                f'Respond: {{"answer": "<answer>", "is_guess": <true/false>}}'
            )
            try:
                r = llm.prompt(p2, schema=FOKAnswer)
                answer = r.answer
            except Exception:
                raw = llm.prompt(p2)
                answer = raw

        fok_ratings.append(conf)
        accuracies.append(check_answer(answer, q))

    return fok_ratings, accuracies


# ─── Sub-metric Tasks ───────────────────────────────────────────────

@kbench.task(name="metacog_fok_gamma")
def metacog_fok_gamma(llm) -> float:
    """
    FOK Gamma Correlation — ordinal association between confidence and accuracy.
    Normalized to [0,1]: score = (gamma + 1) / 2.
    Human range: gamma 0.25–0.55 → score 0.625–0.775.
    """
    ratings, acc = _collect_fok_data(llm)
    gamma = goodman_kruskal_gamma(ratings, [int(a) for a in acc])
    return round((gamma + 1) / 2, 4)


@kbench.task(name="metacog_fok_ece")
def metacog_fok_ece(llm) -> float:
    """
    FOK Calibration (1 - ECE) — how well confidence matches accuracy.
    Human range: ECE 0.10–0.20 → score 0.80–0.90.
    """
    ratings, acc = _collect_fok_data(llm)
    ece = compute_ece(ratings, acc)
    return round(1 - ece, 4)


@kbench.task(name="metacog_fok_auc")
def metacog_fok_auc(llm) -> float:
    """
    FOK Discrimination AUC — does higher confidence predict correctness?
    Random baseline = 0.5.
    """
    ratings, acc = _collect_fok_data(llm)
    return compute_auc(ratings, acc)
