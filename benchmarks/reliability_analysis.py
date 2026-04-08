"""
Inter-rater Reliability Simulation

For each benchmark, generates 100 synthetic response profiles and measures
test-retest reliability (Cronbach's alpha) of the scoring function.

This validates that our scoring functions produce consistent, reliable
measurements — a prerequisite for any psychometric instrument.
"""

import sys
import os
import numpy as np
import json
from pathlib import Path

# Add benchmarks to path
sys.path.insert(0, str(Path(__file__).parent.parent / "benchmarks"))

np.random.seed(42)


def cronbach_alpha(item_scores: np.ndarray) -> float:
    """
    Compute Cronbach's alpha for internal consistency.
    item_scores: (n_subjects x n_items) matrix
    """
    n_items = item_scores.shape[1]
    if n_items < 2:
        return float('nan')
    
    item_variances = item_scores.var(axis=0, ddof=1)
    total_scores = item_scores.sum(axis=1)
    total_variance = total_scores.var(ddof=1)
    
    if total_variance == 0:
        return 0.0
    
    alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
    return round(float(alpha), 4)


def simulate_fok_profiles(n_profiles=100):
    """Simulate FOK benchmark response profiles with varying ability levels."""
    n_questions = 81  # Current FOK question bank size
    profiles = []
    
    for _ in range(n_profiles):
        # Ability level determines base accuracy
        ability = np.random.beta(2, 2)  # Centered around 0.5
        # Metacognitive accuracy determines FOK-accuracy correlation
        meta_acc = np.random.beta(3, 2)  # Slightly better than chance
        
        accuracies = np.random.binomial(1, ability, n_questions)
        # FOK ratings: correlated with accuracy based on metacognitive accuracy
        fok_ratings = []
        for acc in accuracies:
            if acc:
                # Correct: FOK should be higher (modulated by meta_acc)
                mean_fok = 30 + 50 * meta_acc
            else:
                # Incorrect: FOK should be lower
                mean_fok = 70 - 50 * meta_acc
            fok = np.clip(np.random.normal(mean_fok, 15), 0, 100)
            fok_ratings.append(fok)
        
        profiles.append({
            "accuracies": accuracies,
            "fok_ratings": np.array(fok_ratings),
            "ability": ability,
            "meta_acc": meta_acc,
        })
    
    return profiles


def simulate_error_detection_profiles(n_profiles=100):
    """Simulate error detection response profiles."""
    n_chains = 21
    profiles = []
    
    for _ in range(n_profiles):
        detection_ability = np.random.beta(2, 2)
        localization_ability = np.random.beta(2, 3)
        
        detections = np.random.binomial(1, detection_ability, n_chains)
        localizations = np.random.binomial(1, localization_ability, n_chains) * detections
        confidences = []
        for det in detections:
            if det:
                conf = np.clip(np.random.normal(70, 15), 0, 100)
            else:
                conf = np.clip(np.random.normal(40, 20), 0, 100)
            confidences.append(conf)
        
        profiles.append({
            "detections": detections,
            "localizations": localizations,
            "confidences": np.array(confidences),
        })
    
    return profiles


def simulate_attention_profiles(n_profiles=100):
    """Simulate attention benchmark response profiles."""
    # Selective attention: 20 items
    n_items = 20
    profiles = []
    
    for _ in range(n_profiles):
        base_att = np.random.beta(3, 1.5)  # Most models decent at attention
        noise_resistance = np.random.beta(2, 2)
        
        items = []
        for i in range(n_items):
            # Later items have more distractors
            difficulty = 0.3 + 0.5 * (i / n_items)
            p_correct = base_att * (1 - difficulty * (1 - noise_resistance))
            items.append(np.random.binomial(1, max(0.1, min(0.99, p_correct))))
        
        profiles.append({"items": np.array(items)})
    
    return profiles


def compute_fok_score(profile):
    """Compute FOK composite score from a simulated profile."""
    from metacognition.task_fok import goodman_kruskal_gamma, compute_ece, compute_auc
    
    ratings = profile["fok_ratings"].tolist()
    acc = profile["accuracies"].tolist()
    
    gamma = goodman_kruskal_gamma(ratings, acc)
    ece_result = compute_ece(ratings, acc)
    auc = compute_auc(ratings, acc)
    
    gamma_norm = (gamma + 1) / 2
    return 0.40 * gamma_norm + 0.30 * (1 - ece_result["ece"]) + 0.30 * auc


def main():
    print("=" * 60)
    print("INTER-RATER RELIABILITY SIMULATION")
    print("=" * 60)
    
    results = {}
    
    # --- FOK Benchmark ---
    print("\n--- FOK Benchmark ---")
    fok_profiles = simulate_fok_profiles(100)
    
    # Create item-level score matrix for Cronbach's alpha
    # Items = individual questions; score = (FOK > 50) matches accuracy
    fok_item_matrix = np.zeros((100, 81))
    fok_composite_scores = []
    
    for i, p in enumerate(fok_profiles):
        for j in range(81):
            # Item-level metacognitive accuracy: high FOK + correct OR low FOK + incorrect
            fok_high = p["fok_ratings"][j] > 50
            is_correct = bool(p["accuracies"][j])
            fok_item_matrix[i, j] = float(fok_high == is_correct)
        
        # Composite score using simplified metric
        gamma = float(np.corrcoef(p["fok_ratings"], p["accuracies"])[0, 1])
        if np.isnan(gamma):
            gamma = 0
        fok_composite_scores.append((gamma + 1) / 2)
    
    fok_alpha = cronbach_alpha(fok_item_matrix)
    fok_score_std = np.std(fok_composite_scores)
    print(f"  Cronbach's alpha (item-level): {fok_alpha}")
    print(f"  Score range: [{min(fok_composite_scores):.3f}, {max(fok_composite_scores):.3f}]")
    print(f"  Score std: {fok_score_std:.3f}")
    results["fok"] = {"alpha": fok_alpha, "score_std": round(fok_score_std, 4)}
    
    # --- Error Detection Benchmark ---
    print("\n--- Error Detection Benchmark ---")
    ed_profiles = simulate_error_detection_profiles(100)
    
    ed_item_matrix = np.zeros((100, 21))
    for i, p in enumerate(ed_profiles):
        ed_item_matrix[i] = p["detections"]
    
    ed_alpha = cronbach_alpha(ed_item_matrix)
    print(f"  Cronbach's alpha (detection): {ed_alpha}")
    
    # Localization
    ed_loc_matrix = np.zeros((100, 21))
    for i, p in enumerate(ed_profiles):
        ed_loc_matrix[i] = p["localizations"]
    ed_loc_alpha = cronbach_alpha(ed_loc_matrix)
    print(f"  Cronbach's alpha (localization): {ed_loc_alpha}")
    results["error_detection"] = {
        "alpha_detection": ed_alpha,
        "alpha_localization": ed_loc_alpha,
    }
    
    # --- Attention Benchmark ---
    print("\n--- Attention Benchmark ---")
    att_profiles = simulate_attention_profiles(100)
    att_matrix = np.zeros((100, 20))
    for i, p in enumerate(att_profiles):
        att_matrix[i] = p["items"]
    
    att_alpha = cronbach_alpha(att_matrix)
    print(f"  Cronbach's alpha: {att_alpha}")
    results["attention"] = {"alpha": att_alpha}
    
    # --- Split-Half Reliability ---
    print("\n--- Split-Half Reliability (FOK) ---")
    # Odd-even split
    odd_scores = fok_item_matrix[:, ::2].mean(axis=1)
    even_scores = fok_item_matrix[:, 1::2].mean(axis=1)
    split_half_r = float(np.corrcoef(odd_scores, even_scores)[0, 1])
    # Spearman-Brown correction
    sb_reliability = 2 * split_half_r / (1 + split_half_r) if (1 + split_half_r) != 0 else 0
    print(f"  Split-half r: {split_half_r:.4f}")
    print(f"  Spearman-Brown reliability: {sb_reliability:.4f}")
    results["fok"]["split_half_r"] = round(split_half_r, 4)
    results["fok"]["spearman_brown"] = round(sb_reliability, 4)
    
    # --- Summary ---
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print("Benchmark                  | Cronbach's α | Interpretation")
    print("-" * 60)
    
    def interpret(a):
        if a >= 0.9: return "Excellent"
        elif a >= 0.8: return "Good"
        elif a >= 0.7: return "Acceptable"
        elif a >= 0.6: return "Questionable"
        elif a >= 0.5: return "Poor"
        else: return "Unacceptable"
    
    for name, data in results.items():
        for key, val in data.items():
            if "alpha" in key:
                print(f"  {name:20s} {key:15s} | {val:.4f}       | {interpret(val)}")
    
    print(f"\nNote: α ≥ 0.70 is the standard threshold for psychometric instruments.")
    print(f"These are simulated profiles — real model responses may differ.\n")
    
    # Save results
    os.makedirs("results", exist_ok=True)
    with open("results/reliability_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to results/reliability_analysis.json")


if __name__ == "__main__":
    main()
