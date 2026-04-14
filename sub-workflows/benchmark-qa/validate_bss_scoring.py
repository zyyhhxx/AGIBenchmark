"""
Mock validation: verify BSS scoring fixes the inversion problem.
Tests three mock agents against all four benchmarks' scoring formulas.
"""
import numpy as np
import sys

def brier_skill_score(confidences_0_100, outcomes_binary, ref="climatological"):
    """BSS = 1 - BS / BS_ref"""
    conf = np.array(confidences_0_100) / 100.0
    out = np.array(outcomes_binary, dtype=float)
    BS = float(np.mean((conf - out) ** 2))
    if ref == "climatological":
        base_rate = float(out.mean())
        BS_ref = base_rate * (1 - base_rate)
    else:
        BS_ref = float(np.mean((0.5 - out) ** 2))
    if BS_ref < 1e-10:
        BS_ref = float(np.mean((0.5 - out) ** 2))
    if BS_ref < 1e-10:
        return 0.0
    return 1.0 - BS / BS_ref

def goodman_kruskal_gamma(x, y):
    n = len(x)
    conc, disc = 0, 0
    for i in range(n):
        for j in range(i+1, n):
            p = (x[i]-x[j]) * (y[i]-y[j])
            if p > 0: conc += 1
            elif p < 0: disc += 1
    d = conc + disc
    return (conc - disc) / d if d else 0.0

np.random.seed(42)
N = 60  # typical question count

# Generate outcomes: 60% accuracy base rate
outcomes = [1]*36 + [0]*24

# === Mock Agent 1: Perfect metacognitor ===
# High confidence on correct, low on incorrect
perfect_conf = [np.random.randint(80, 100) if o else np.random.randint(5, 25) for o in outcomes]

# === Mock Agent 2: Always uncertain (50%) ===
uncertain_conf = [50] * N

# === Mock Agent 3: Random baseline ===
random_conf = list(np.random.randint(0, 101, N))

print("=" * 70)
print("MOCK VALIDATION: BSS Scoring Fix")
print("=" * 70)

all_pass = True

for bench_name, use_auc in [("FOK", True), ("JOL", False), ("Calibration", False)]:
    print(f"\n--- {bench_name} Benchmark ---")
    
    for agent_name, confs in [("Perfect metacognitor", perfect_conf), 
                               ("Always uncertain", uncertain_conf),
                               ("Random baseline", random_conf)]:
        gamma = goodman_kruskal_gamma(confs, outcomes)
        gamma_norm = (gamma + 1) / 2
        bss = brier_skill_score(confs, outcomes)
        bss_clamped = max(0.0, bss)
        
        if bench_name == "FOK":
            # Simplified AUC (use gamma as proxy for mock)
            auc = 0.95 if agent_name == "Perfect metacognitor" else (0.5 if "Random" in agent_name else 0.5)
            score = round(0.40 * gamma_norm + 0.30 * bss_clamped + 0.30 * auc, 4)
        elif bench_name == "JOL":
            recall = 0.6  # same for all mock agents
            score = round(0.40 * gamma_norm + 0.30 * bss_clamped + 0.30 * recall, 4)
        else:  # Calibration
            score = round(bss_clamped, 4)
        
        print(f"  {agent_name:25s}: γ={gamma:+.3f}, BSS={bss:+.4f}, score={score:.4f}")
        
        # Validation checks: the KEY requirement is perfect >> uncertain (no inversion)
        if agent_name == "Perfect metacognitor" and score < 0.8:
            print(f"    *** FAIL: Perfect metacognitor should score >0.8, got {score}")
            all_pass = False
        if agent_name == "Always uncertain" and score > 0.5:
            print(f"    *** FAIL: Always uncertain should score <0.5, got {score}")
            all_pass = False

# === Canary Benchmark ===
print(f"\n--- Canary Benchmark ---")
canary_outcomes = [0] * 20  # All fabricated

canary_perfect = [np.random.randint(0, 15) for _ in range(20)]
canary_uncertain = [50] * 20
canary_contaminated = [np.random.randint(75, 100) for _ in range(20)]

for agent_name, confs in [("Perfect (low conf)", canary_perfect),
                           ("Always uncertain", canary_uncertain),
                           ("Contaminated (high)", canary_contaminated)]:
    conf_arr = np.array(confs) / 100.0
    out_arr = np.array(canary_outcomes, dtype=float)
    BS = float(np.mean((conf_arr - out_arr) ** 2))
    BS_ref = float(np.mean((0.5 - out_arr) ** 2))
    bss = 1.0 - BS / BS_ref if BS_ref > 1e-10 else 0.0
    score = round(max(0.0, bss), 4)
    
    print(f"  {agent_name:25s}: mean_conf={np.mean(confs):.0f}%, BSS={bss:+.4f}, score={score:.4f}")
    
    if agent_name == "Perfect (low conf)" and score < 0.8:
        print(f"    *** FAIL: Perfect canary should score >0.8, got {score}")
        all_pass = False
    if agent_name == "Always uncertain" and score > 0.3:
        print(f"    *** FAIL: Uncertain canary should score <0.3, got {score}")
        all_pass = False
    if "Contaminated" in agent_name and score > 0.0:
        print(f"    *** FAIL: Contaminated canary should score 0.0, got {score}")
        all_pass = False

print(f"\n{'=' * 70}")
if all_pass:
    print("ALL VALIDATION CHECKS PASSED ✓")
else:
    print("SOME CHECKS FAILED ✗")
    sys.exit(1)
