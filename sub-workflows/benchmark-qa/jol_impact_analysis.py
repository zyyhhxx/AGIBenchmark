"""
Step 5: Retroactive JOL score recalculation — impact analysis.

We don't have raw per-item transcripts, only final scores. This script
simulates the impact of the gamma variation penalty by:
1. Computing what gamma_norm would be for constant-confidence models (std < 1.0)
2. Showing before/after scores for typical constant vs varying confidence patterns
3. Identifying which models likely had constant confidence (score near 0.50 gamma_norm baseline)
"""
import numpy as np

def goodman_kruskal_gamma(x, y):
    n = len(x)
    concordant = discordant = 0
    for i in range(n):
        for j in range(i+1, n):
            product = (x[i]-x[j]) * (y[i]-y[j])
            if product > 0: concordant += 1
            elif product < 0: discordant += 1
    denom = concordant + discordant
    return (concordant - discordant) / denom if denom else 0.0

def brier_skill_score(conf_0_100, outcomes):
    conf = np.array(conf_0_100) / 100.0
    out = np.array(outcomes, dtype=float)
    BS = float(np.mean((conf - out)**2))
    base_rate = float(out.mean())
    BS_ref = base_rate * (1 - base_rate)
    if BS_ref < 1e-10:
        BS_ref = float(np.mean((0.5 - out)**2))
    if BS_ref < 1e-10:
        return 0.0
    return 1.0 - BS / BS_ref

def compute_score_old(jol_ratings, accuracies):
    gamma = goodman_kruskal_gamma(jol_ratings, [int(a) for a in accuracies])
    bss = brier_skill_score(jol_ratings, [int(a) for a in accuracies])
    recall_rate = sum(accuracies) / len(accuracies)
    gamma_norm = (gamma + 1) / 2
    return round(0.40 * gamma_norm + 0.30 * max(0.0, bss) + 0.30 * recall_rate, 4)

def compute_score_new(jol_ratings, accuracies):
    gamma = goodman_kruskal_gamma(jol_ratings, [int(a) for a in accuracies])
    bss = brier_skill_score(jol_ratings, [int(a) for a in accuracies])
    recall_rate = sum(accuracies) / len(accuracies)
    if np.std(jol_ratings) < 1.0:
        gamma_norm = 0.0
    else:
        gamma_norm = (gamma + 1) / 2
    return round(0.40 * gamma_norm + 0.30 * max(0.0, bss) + 0.30 * recall_rate, 4)

print("="*70)
print("JOL GAMMA VARIATION PENALTY — IMPACT ANALYSIS")
print("="*70)
print()

# Known model scores from results
model_scores = {
    "Nova Pro":        0.4019,
    "Claude Opus":     0.4643,
    "Claude Sonnet":   0.4631,
    "DeepSeek R1":     0.2759,
    "Llama 3.3 70B":   0.4647,
    "Llama 4 Maverick":0.4647,
    "Ministral 3B":    0.4315,
    "GPT-OSS 120B":    0.2000,
    "Qwen3 80B":       0.3627,
    "GLM 4.7":         0.4010,
}

print("--- Known Model Scores (from Kaggle runs, old formula) ---")
for model, score in sorted(model_scores.items(), key=lambda x: -x[1]):
    print(f"  {model:20s}: {score:.4f}")

print()
print("--- Simulated Impact of Gamma Variation Penalty ---")
print("(Using synthetic confidence patterns to illustrate the fix)")
print()

# Simulate scenarios
n_items = 15  # typical JOL item count (10 words + 5 rules)
np.random.seed(42)

scenarios = [
    ("Constant conf=85, recall=70%", [85]*n_items, [1]*10+[0]*5),
    ("Constant conf=90, recall=80%", [90]*n_items, [1]*12+[0]*3),
    ("Constant conf=50, recall=50%", [50]*n_items, [1]*8+[0]*7),
    ("Varying conf (good metacog)",  [90,85,80,75,70,65,60,55,50,45,40,35,30,25,20], [1,1,1,1,1,1,1,0,0,0,0,0,0,0,0]),
    ("Varying conf (poor metacog)",  [20,25,30,35,40,45,50,55,60,65,70,75,80,85,90], [1,1,1,1,1,1,1,0,0,0,0,0,0,0,0]),
]

print(f"{'Scenario':40s} {'Old':>8s} {'New':>8s} {'Delta':>8s} {'std(conf)':>10s}")
print("-"*76)
for name, confs, accs in scenarios:
    old = compute_score_old(confs, accs)
    new = compute_score_new(confs, accs)
    std = np.std(confs)
    delta = new - old
    flag = " ← PENALIZED" if std < 1.0 else ""
    print(f"  {name:38s} {old:8.4f} {new:8.4f} {delta:+8.4f}   {std:7.1f}{flag}")

print()
print("--- Key Insight ---")
print("Models reporting constant confidence (std < 1.0) get a FREE 0.50 gamma_norm")
print("because gamma=0.0 when all pairs are tied, yielding (0+1)/2 = 0.50.")
print("The fix sets gamma_norm=0.0 for these models, removing the unearned 0.20 score boost.")
print()
print("Models with Llama 3.3 70B and Llama 4 Maverick have identical scores (0.4647),")
print("suggesting they may report constant confidence. After the fix, their scores would drop.")
print()

# Estimate which models are likely affected
print("--- Estimated Before/After for Constant-Confidence Models ---")
print("(Assuming constant confidence → gamma_norm drops from 0.50 to 0.00)")
print(f"{'Model':20s} {'Before':>8s} {'After (est)':>12s} {'Delta':>8s}")
print("-"*52)
for model, score in sorted(model_scores.items(), key=lambda x: -x[1]):
    # If a model had constant confidence, its score includes 0.40*0.50 = 0.20 from gamma
    # New score would be score - 0.20
    estimated_new = score - 0.20
    # Only flag models where this is plausible (score pattern suggests constant conf)
    print(f"  {model:18s} {score:8.4f} {estimated_new:12.4f} {-0.20:+8.4f}  (if constant)")
