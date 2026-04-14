#!/usr/bin/env python3
"""
Validate that the redesigned interference scoring discriminates
between 4 mock strategies with >0.1 separation on at least 3 pairs.
"""

import sys
sys.path.insert(0, "/home/ubuntu/.openclaw/workspace-agi-bench/repo/benchmarks/learning")

# Import only the scoring function (doesn't need kbench)
# We'll inline it to avoid kbench import issues
def compute_interference_score(control_A, baseline_B, post_interf_A):
    retro_raw = max(0.0, control_A - post_interf_A)
    retro_norm = retro_raw / control_A if control_A > 0 else 0.0
    proactive_raw = max(0.0, control_A - baseline_B)
    proactive_norm = proactive_raw / control_A if control_A > 0 else 0.0
    compartment = post_interf_A / control_A if control_A > 0 else 0.0
    compartment = min(1.0, compartment)
    score = round(
        0.25 * retro_norm + 0.25 * proactive_norm
        + 0.25 * compartment + 0.25 * control_A, 4
    )
    return {
        "retro_norm": retro_norm,
        "proactive_norm": proactive_norm,
        "compartmentalization": compartment,
        "control_A": control_A,
        "composite_score": max(0.0, min(1.0, score)),
    }

# 4 mock strategies simulating different model behaviors
strategies = {
    "perfect_compartmentalizer": {
        # Learns both perfectly, no interference at all
        "control_A": 1.0, "baseline_B": 1.0, "post_interf_A": 1.0,
    },
    "full_retroactive_forgetter": {
        # Learns A well, learns B well, but completely forgets A
        "control_A": 0.8, "baseline_B": 0.8, "post_interf_A": 0.0,
    },
    "proactive_blocker": {
        # Learns A well, A blocks B learning, but retains A fine
        "control_A": 0.8, "baseline_B": 0.2, "post_interf_A": 0.8,
    },
    "cant_learn_anything": {
        # Fails at everything — no signal
        "control_A": 0.0, "baseline_B": 0.0, "post_interf_A": 0.0,
    },
}

print("=" * 70)
print("MOCK STRATEGY VALIDATION — Interference Scoring v2")
print("=" * 70)

scores = {}
for name, params in strategies.items():
    m = compute_interference_score(**params)
    scores[name] = m["composite_score"]
    print(f"\n--- {name} ---")
    print(f"  control_A={params['control_A']}, baseline_B={params['baseline_B']}, "
          f"post_interf_A={params['post_interf_A']}")
    print(f"  retro_norm={m['retro_norm']:.4f}, proactive_norm={m['proactive_norm']:.4f}")
    print(f"  compartment={m['compartmentalization']:.4f}")
    print(f"  SCORE = {m['composite_score']:.4f}")

# Check discrimination
print(f"\n{'='*70}")
print("DISCRIMINATION CHECK")
print(f"{'='*70}")
names = list(scores.keys())
distinct_pairs = 0
total_pairs = 0
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        diff = abs(scores[names[i]] - scores[names[j]])
        sep = "✓" if diff > 0.1 else "✗"
        print(f"  {names[i]} vs {names[j]}: |{scores[names[i]]:.4f} - {scores[names[j]]:.4f}| = {diff:.4f} {sep}")
        total_pairs += 1
        if diff > 0.1:
            distinct_pairs += 1

print(f"\nDistinct pairs (>0.1 separation): {distinct_pairs}/{total_pairs}")
print(f"Requirement: at least 3 of 4 strategies produce distinct scores")

# Check: at least 3 strategies have unique scores separated by >0.1
sorted_scores = sorted(scores.values())
n_distinct = 1
for i in range(1, len(sorted_scores)):
    if sorted_scores[i] - sorted_scores[i-1] > 0.1:
        n_distinct += 1
print(f"Distinct score clusters (>0.1 gap): {n_distinct}")
print(f"\nPASS: {distinct_pairs >= 3 and n_distinct >= 3}")
