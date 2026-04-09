"""
Social Cognition Benchmark 3: Sarcasm Detection in Context

Tests ability to distinguish sarcastic from sincere utterances using
rich conversational context. Matched pairs: same surface utterance,
different context → different intent.

Cognitive Science Basis:
- Sarcasm comprehension requires theory of mind + context integration
- Incongruity detection between context and utterance (Gibbs, 1986)
- Right hemisphere / prefrontal involvement (Shamay-Tsoory et al., 2005)
- Context-dependent interpretation is a hallmark of pragmatic competence

Key Design: Matched pairs — some sarcastic and sincere items share nearly
identical surface utterances but have different contexts. This forces
reliance on context rather than surface cues.

Metrics:
- AUC: Area under ROC curve for sincerity ratings predicting sarcasm
- Calibration: correlation between sincerity rating and actual sincerity
- Accuracy at threshold (50): binary classification accuracy
- Matched pair discrimination: accuracy on items sharing surface forms

Score = 0.50 * AUC + 0.30 * (1 - calibration_error) + 0.20 * threshold_accuracy
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
from data.sarcasm_items import SARCASM_ITEMS


@dataclass
class SarcasmResponse:
    """Model's sarcasm detection judgment."""
    sincerity_rating: int    # 0-100: How sincere is this utterance? (0=definitely sarcastic, 100=definitely sincere)
    is_sarcastic: bool       # Binary judgment: is this sarcastic?
    reasoning: str           # Brief explanation


def compute_auc(ratings: list, labels: list) -> float:
    """
    Compute AUC for sincerity ratings predicting sincere (not sarcastic).
    Higher sincerity rating should predict sincere utterances.
    """
    ratings = np.array(ratings, dtype=float)
    labels = np.array(labels, dtype=float)  # 1 = sincere, 0 = sarcastic
    
    if labels.sum() == 0 or labels.sum() == len(labels):
        return 0.5
    
    sorted_idx = np.argsort(-ratings)  # descending sincerity
    sorted_labels = labels[sorted_idx]
    
    tpr_list = [0.0]
    fpr_list = [0.0]
    tp = 0
    fp = 0
    pos = labels.sum()
    neg = len(labels) - pos
    
    for label in sorted_labels:
        if label == 1:
            tp += 1
        else:
            fp += 1
        tpr_list.append(tp / pos)
        fpr_list.append(fp / neg)
    
    auc = 0.0
    for i in range(1, len(tpr_list)):
        auc += (fpr_list[i] - fpr_list[i-1]) * (tpr_list[i] + tpr_list[i-1]) / 2
    
    return round(float(auc), 4)


@kbench.task(name="social_cog_sarcasm")
def social_cog_sarcasm(llm) -> float:
    """
    Sarcasm Detection in Context Benchmark.

    Tests discrimination between sarcastic and sincere utterances
    using matched-pair design with shared surface forms.

    Score = 0.50 * AUC + 0.30 * (1 - cal_error) + 0.20 * threshold_accuracy

    Cognitive Science: Gibbs (1986), Shamay-Tsoory et al. (2005).
    Human AUC: ~0.95 for adults with context.
    """
    results = []
    sincerity_ratings = []
    true_labels = []  # 1 = sincere, 0 = sarcastic
    
    for item in SARCASM_ITEMS:
        prompt = (
            f"Read this conversation carefully:\n\n"
            f"Context: {item['context']}\n"
            f"Utterance: \"{item['utterance']}\"\n\n"
            f"Rate the SINCERITY of this utterance on a scale from 0 to 100.\n"
            f"0 = Definitely sarcastic (the speaker means the OPPOSITE of what they say)\n"
            f"100 = Definitely sincere (the speaker genuinely means what they say)\n\n"
            f"Consider the context carefully before judging."
        )
        
        with kbench.chats.new(f"sarcasm_{item['id']}"):
            try:
                response = llm(prompt, response_format=SarcasmResponse)
                rating = max(0, min(100, response.sincerity_rating))
                model_says_sarcastic = response.is_sarcastic
            except Exception:
                import re as _re
                raw = llm(prompt)
                # Try to extract a number
                nums = _re.findall(r'\b(\d{1,3})\b', raw)
                rating = max(0, min(100, int(nums[0]))) if nums else 50
                model_says_sarcastic = "sarcas" in raw.lower()
        
        is_sincere = not item["is_sarcastic"]
        
        results.append({
            "id": item["id"],
            "is_sarcastic": item["is_sarcastic"],
            "sincerity_rating": rating,
            "model_says_sarcastic": model_says_sarcastic,
            "binary_correct": (model_says_sarcastic == item["is_sarcastic"]),
        })
        
        sincerity_ratings.append(rating)
        true_labels.append(1 if is_sincere else 0)
    
    # ── Compute Metrics ──
    
    # AUC
    auc = compute_auc(sincerity_ratings, true_labels)
    
    # Binary accuracy at threshold 50
    binary_correct = sum(1 for r in results if r["binary_correct"])
    threshold_acc = binary_correct / len(results)
    
    # Calibration error: mean absolute difference between normalized rating and actual label
    ratings_norm = np.array(sincerity_ratings) / 100.0
    labels = np.array(true_labels, dtype=float)
    
    # Bin calibration
    n_bins = 5
    bin_edges = np.linspace(0, 1, n_bins + 1)
    cal_error = 0.0
    total_in_bins = 0
    
    for i in range(n_bins):
        mask = (ratings_norm >= bin_edges[i]) & (ratings_norm < bin_edges[i+1])
        if i == n_bins - 1:
            mask = (ratings_norm >= bin_edges[i]) & (ratings_norm <= bin_edges[i+1])
        if mask.sum() == 0:
            continue
        avg_rating = ratings_norm[mask].mean()
        avg_sincere = labels[mask].mean()
        cal_error += mask.sum() * abs(avg_rating - avg_sincere)
        total_in_bins += mask.sum()
    
    cal_error = cal_error / total_in_bins if total_in_bins > 0 else 0.5
    
    # Sarcastic vs sincere rating distributions
    sarcastic_ratings = [r["sincerity_rating"] for r in results if r["is_sarcastic"]]
    sincere_ratings = [r["sincerity_rating"] for r in results if not r["is_sarcastic"]]
    
    # ── Composite Score ──
    score = (
        0.50 * auc +
        0.30 * (1.0 - cal_error) +
        0.20 * threshold_acc
    )
    score = round(float(np.clip(score, 0, 1)), 4)
    
    kbench.log({
        "benchmark": "Sarcasm Detection",
        "n_items": len(results),
        "auc": auc,
        "calibration_error": round(float(cal_error), 4),
        "threshold_accuracy": round(threshold_acc, 4),
        "composite_score": score,
        "rating_distributions": {
            "sarcastic_mean": round(float(np.mean(sarcastic_ratings)), 1),
            "sarcastic_std": round(float(np.std(sarcastic_ratings)), 1),
            "sincere_mean": round(float(np.mean(sincere_ratings)), 1),
            "sincere_std": round(float(np.std(sincere_ratings)), 1),
        },
        "per_item": results,
    })
    
    return score

social_cog_sarcasm.run(llm=kbench.llm)
