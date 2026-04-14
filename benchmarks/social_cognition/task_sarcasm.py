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

3-Tier Difficulty:
- Tier 1 (40 items, difficulty=1): Obvious context-utterance contradiction
- Tier 2 (15 items, difficulty=2): Implicit contradiction, contextual sarcasm
- Tier 3 (15 items, difficulty=3): Subtle/ambiguous, deadpan, cultural patterns

Score = 0.05 * tier1_composite + 0.15 * tier2_composite + 0.80 * tier3_binary_acc
Tier 1-2 composite = 0.50 * AUC + 0.30 * (1 - cal_error) + 0.20 * threshold_acc
Tier 3 = binary accuracy only (AUC too forgiving for subtle sarcasm)
"""

import kaggle_benchmarks as kbench
import json as _json
import re as _re
import numpy as np
from data.sarcasm_items import SARCASM_ITEMS

def _safe_log(data): print(_json.dumps(data, indent=2, default=str))


def _strip_think(text):
    """Remove <think>...</think> blocks from model output."""
    return _re.sub(r'<think>.*?</think>', '', text, flags=_re.DOTALL).strip()


def _strip_fences(text):
    """Remove markdown code fences from model output."""
    text = _re.sub(r'```(?:json)?\s*', '', text)
    text = _re.sub(r'```\s*$', '', text)
    return text.strip()


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


def _compute_tier_composite(results_tier: list) -> dict:
    """Compute composite score for a single difficulty tier."""
    if not results_tier:
        return {"auc": 0.5, "cal_error": 0.5, "threshold_acc": 0.0, "composite": 0.0, "n": 0}

    sincerity_ratings = [r["sincerity_rating"] for r in results_tier]
    true_labels = [1 if not r["is_sarcastic"] else 0 for r in results_tier]

    # AUC
    auc = compute_auc(sincerity_ratings, true_labels)

    # Binary accuracy at threshold 50
    binary_correct = sum(1 for r in results_tier if r["binary_correct"])
    threshold_acc = binary_correct / len(results_tier)

    # Calibration error (binned)
    ratings_norm = np.array(sincerity_ratings) / 100.0
    labels = np.array(true_labels, dtype=float)
    n_bins = 5
    bin_edges = np.linspace(0, 1, n_bins + 1)
    cal_error = 0.0
    total_in_bins = 0

    for i in range(n_bins):
        if i == n_bins - 1:
            mask = (ratings_norm >= bin_edges[i]) & (ratings_norm <= bin_edges[i+1])
        else:
            mask = (ratings_norm >= bin_edges[i]) & (ratings_norm < bin_edges[i+1])
        if mask.sum() == 0:
            continue
        avg_rating = ratings_norm[mask].mean()
        avg_sincere = labels[mask].mean()
        cal_error += mask.sum() * abs(avg_rating - avg_sincere)
        total_in_bins += mask.sum()

    cal_error = cal_error / total_in_bins if total_in_bins > 0 else 0.5

    composite = 0.50 * auc + 0.30 * (1.0 - cal_error) + 0.20 * threshold_acc
    composite = round(float(np.clip(composite, 0, 1)), 4)

    return {
        "auc": auc,
        "cal_error": round(float(cal_error), 4),
        "threshold_acc": round(threshold_acc, 4),
        "composite": composite,
        "n": len(results_tier),
    }


@kbench.task(name="Sarcasm Detection")
def social_cog_sarcasm(llm) -> float:
    """
    Sarcasm Detection in Context Benchmark.

    Tests discrimination between sarcastic and sincere utterances
    using matched-pair design with shared surface forms across 3
    difficulty tiers.

    Score = 0.05 * tier1_composite + 0.15 * tier2_composite + 0.80 * tier3_binary_acc
    Tier 1-2: 0.50 * AUC + 0.30 * (1 - cal_error) + 0.20 * threshold_acc
    Tier 3: binary accuracy only (AUC too forgiving for subtle sarcasm)

    Cognitive Science: Gibbs (1986), Shamay-Tsoory et al. (2005).
    Human AUC: ~0.95 for adults with context (tier 1), ~0.80 (tier 3).
    """
    results = []

    for item in SARCASM_ITEMS:
        prompt = (
            f"Read this conversation carefully:\n\n"
            f"Context: {item['context']}\n"
            f"Utterance: \"{item['utterance']}\"\n\n"
            f"Rate the SINCERITY of this utterance on a scale from 0 to 100.\n"
            f"0 = Definitely sarcastic (the speaker means the OPPOSITE of what they say)\n"
            f"100 = Definitely sincere (the speaker genuinely means what they say)\n\n"
            f"Consider the context carefully before judging."
            f'\n\nRespond in JSON format: {{"sincerity_rating": <0-100>, "is_sarcastic": <true/false>, "reasoning": "<brief>"}}'
        )

        with kbench.chats.new(f"sarcasm_{item['id']}"):
            try:
                raw = llm.prompt(prompt)
                cleaned = _strip_think(raw)
                cleaned = _strip_fences(cleaned)
                m = _re.search(r'\{.*\}', cleaned, _re.DOTALL)
                data = _json.loads(m.group()) if m else {}
                rating = int(data.get("sincerity_rating", 50))
                rating = max(0, min(100, rating))
                model_says_sarcastic = bool(data.get("is_sarcastic", False))
            except Exception:
                # Fallback: try to extract a number
                try:
                    nums = _re.findall(r'\b(\d{1,3})\b', str(raw))
                    rating = max(0, min(100, int(nums[0]))) if nums else 50
                    model_says_sarcastic = "sarcas" in str(raw).lower()
                except Exception:
                    rating = 50
                    model_says_sarcastic = False

        is_sincere = not item["is_sarcastic"]

        results.append({
            "id": item["id"],
            "is_sarcastic": item["is_sarcastic"],
            "difficulty": item["difficulty"],
            "sincerity_rating": rating,
            "model_says_sarcastic": model_says_sarcastic,
            "binary_correct": (model_says_sarcastic == item["is_sarcastic"]),
        })

    # ── Compute per-tier metrics ──
    tier1_results = [r for r in results if r["difficulty"] == 1]
    tier2_results = [r for r in results if r["difficulty"] == 2]
    tier3_results = [r for r in results if r["difficulty"] == 3]

    tier1 = _compute_tier_composite(tier1_results)
    tier2 = _compute_tier_composite(tier2_results)
    tier3 = _compute_tier_composite(tier3_results)

    # ── Weighted composite score ──
    # Tier 3 uses binary accuracy only (AUC/calibration too forgiving for subtle items)
    tier3_score = tier3["threshold_acc"]
    score = 0.05 * tier1["composite"] + 0.15 * tier2["composite"] + 0.80 * tier3_score
    score = round(float(np.clip(score, 0, 1)), 4)

    # ── Rating distributions ──
    sarcastic_ratings = [r["sincerity_rating"] for r in results if r["is_sarcastic"]]
    sincere_ratings = [r["sincerity_rating"] for r in results if not r["is_sarcastic"]]

    _safe_log({
        "benchmark": "Sarcasm Detection",
        "n_items": len(results),
        "tier_breakdown": {
            "tier1": tier1,
            "tier2": tier2,
            "tier3": tier3,
        },
        "weighted_score": score,
        "tier_weights": {"tier1": 0.05, "tier2": 0.15, "tier3": 0.80},
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
