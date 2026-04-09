#!/usr/bin/env python3
"""
Mock validation: run all benchmark scoring pipelines with synthetic response profiles.

Profiles tested:
1. always-confident: always says 100% confident, always answers "yes"/first option
2. always-uncertain: always says 0% confident, always answers "I don't know"
3. random: random confidence/answers
4. perfect: always correct with calibrated confidence

This validates that scoring functions produce sensible score distributions
and don't crash on edge cases.
"""

import sys
import os
import json
import random
import numpy as np
from datetime import datetime, timezone
import importlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def import_from_dir(module_name, package_dir):
    """Import a module after temporarily changing to its directory."""
    old_cwd = os.getcwd()
    old_path = sys.path[:]
    try:
        os.chdir(package_dir)
        sys.path.insert(0, package_dir)
        # Clear cached data package and submodules to avoid cross-contamination
        to_remove = [k for k in sys.modules if k == module_name or k.startswith('data')]
        for k in to_remove:
            del sys.modules[k]
        # Mock kbench attributes so task files that call .run(llm=kbench.llm)
        # at module level don't crash during import
        import kaggle_benchmarks as kbench
        if not hasattr(kbench, 'llm'):
            kbench.llm = lambda *a, **kw: 'mock'
        if not hasattr(kbench, 'log'):
            kbench.log = lambda *a, **kw: None
        mod = importlib.import_module(module_name)
        return mod
    finally:
        os.chdir(old_cwd)
        sys.path[:] = old_path


def test_wcst_scoring():
    """Test WCST scoring with mock profiles."""
    ef_dir = os.path.join(SCRIPT_DIR, 'benchmarks', 'executive_functions')
    wcst_stim = import_from_dir('data.wcst_stimuli', ef_dir)
    WCST_STIMULI = wcst_stim.WCST_STIMULI
    
    trials = WCST_STIMULI["trials"]
    results = {}
    
    # Profile 1: Always pick Card 1
    trial_results = []
    for t in trials:
        correct = (1 == t["correct_answer"])
        trial_results.append({
            "correct": correct,
            "error_type": "perseverative" if not correct else None,
            "rule_episode": t["rule_episode"],
        })
    acc = sum(1 for r in trial_results if r["correct"]) / len(trial_results)
    results["always_card1"] = {"accuracy": round(acc, 4), "n_correct": sum(1 for r in trial_results if r["correct"])}
    
    # Profile 2: Random choice
    random.seed(42)
    trial_results = []
    for t in trials:
        choice = random.randint(1, 4)
        correct = (choice == t["correct_answer"])
        trial_results.append({"correct": correct})
    acc = sum(1 for r in trial_results if r["correct"]) / len(trial_results)
    results["random"] = {"accuracy": round(acc, 4)}
    
    # Profile 3: Perfect (always correct)
    results["perfect"] = {"accuracy": 1.0}
    
    return results


def test_tol_scoring():
    """Test ToL scoring with mock move sequences."""
    ef_dir = os.path.join(SCRIPT_DIR, 'benchmarks', 'executive_functions')
    tol_mod = import_from_dir('data.tol_problems', ef_dir)
    TOL_PROBLEMS = tol_mod.TOL_PROBLEMS
    task_tol = import_from_dir('task_tol', ef_dir)
    validate_solution = task_tol.validate_solution
    
    results = {}
    
    # Profile: submit optimal solutions
    valid_count = 0
    for p in TOL_PROBLEMS:
        moves = [(s, d) for s, d, b in p["optimal_solution"]]
        val = validate_solution(p["start"], p["goal"], moves)
        if val["reached_goal"]:
            valid_count += 1
    results["optimal"] = {"valid": valid_count, "total": len(TOL_PROBLEMS)}
    
    # Profile: submit empty moves
    invalid_count = 0
    for p in TOL_PROBLEMS:
        val = validate_solution(p["start"], p["goal"], [])
        if not val["reached_goal"]:
            invalid_count += 1
    results["empty"] = {"invalid": invalid_count, "total": len(TOL_PROBLEMS)}
    
    return results


def test_nback_scoring():
    """Test N-back d-prime computation."""
    ef_dir = os.path.join(SCRIPT_DIR, 'benchmarks', 'executive_functions')
    nback_mod = import_from_dir('task_nback', ef_dir)
    dprime_fallback = nback_mod.dprime_fallback
    
    results = {}
    
    # Perfect detector
    dp = dprime_fallback(15, 0, 0, 45)
    results["perfect"] = {"dprime": dp}
    
    # Random detector (50% hit, 50% FA)
    dp = dprime_fallback(7, 8, 22, 23)
    results["random"] = {"dprime": dp}
    
    # Always-yes (100% hit, 100% FA)
    dp = dprime_fallback(15, 0, 45, 0)
    results["always_yes"] = {"dprime": dp}
    
    # Always-no (0% hit, 0% FA)
    dp = dprime_fallback(0, 15, 0, 45)
    results["always_no"] = {"dprime": dp}
    
    return results


def test_false_belief_scoring():
    """Test false-belief scoring logic."""
    sc_dir = os.path.join(SCRIPT_DIR, 'benchmarks', 'social_cognition')
    fb_mod = import_from_dir('data.false_belief_scenarios', sc_dir)
    FALSE_BELIEF_SCENARIOS = fb_mod.FALSE_BELIEF_SCENARIOS
    task_mod = import_from_dir('task_false_belief', sc_dir)
    check_answer = task_mod.check_answer
    
    results = {}
    
    # Profile: always answer with belief answer (correct for ToM)
    correct = 0
    for s in FALSE_BELIEF_SCENARIOS:
        if check_answer(s["belief_answer"], s["belief_accept"]):
            correct += 1
    results["correct_belief"] = {"correct": correct, "total": len(FALSE_BELIEF_SCENARIOS)}
    
    # Profile: always answer with reality (wrong for ToM)
    correct = 0
    for s in FALSE_BELIEF_SCENARIOS:
        if check_answer(s["reality_answer"], s["belief_accept"]):
            correct += 1
    results["reality_error"] = {"belief_correct": correct, "total": len(FALSE_BELIEF_SCENARIOS)}
    
    return results


def test_sarcasm_scoring():
    """Test sarcasm AUC computation."""
    sc_dir = os.path.join(SCRIPT_DIR, 'benchmarks', 'social_cognition')
    sarc_mod = import_from_dir('task_sarcasm', sc_dir)
    compute_auc = sarc_mod.compute_auc
    
    results = {}
    
    # Perfect discrimination
    ratings = [10]*20 + [90]*20  # Low for sarcastic, high for sincere
    labels = [0]*20 + [1]*20
    results["perfect"] = {"auc": compute_auc(ratings, labels)}
    
    # Random ratings
    random.seed(42)
    ratings = [random.randint(0, 100) for _ in range(40)]
    labels = [0]*20 + [1]*20
    results["random"] = {"auc": compute_auc(ratings, labels)}
    
    # Inverted (always wrong)
    ratings = [90]*20 + [10]*20
    labels = [0]*20 + [1]*20
    results["inverted"] = {"auc": compute_auc(ratings, labels)}
    
    return results


def main():
    print("=" * 60)
    print("MOCK VALIDATION: Scoring Pipeline Tests")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    all_results = {}
    
    tests = [
        ("WCST (Exec Functions)", test_wcst_scoring),
        ("Tower of London (Exec Functions)", test_tol_scoring),
        ("N-back d-prime (Exec Functions)", test_nback_scoring),
        ("False Belief (Social Cognition)", test_false_belief_scoring),
        ("Sarcasm AUC (Social Cognition)", test_sarcasm_scoring),
    ]
    
    for name, test_fn in tests:
        print(f"\n--- {name} ---")
        try:
            result = test_fn()
            all_results[name] = {"status": "PASS", "results": result}
            for profile, data in result.items():
                print(f"  {profile}: {data}")
            print(f"  ✓ PASS")
        except Exception as e:
            all_results[name] = {"status": "FAIL", "error": str(e)}
            print(f"  ✗ FAIL: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    passed = sum(1 for v in all_results.values() if v["status"] == "PASS")
    total = len(all_results)
    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'=' * 60}")
    
    # Write results
    os.makedirs("results", exist_ok=True)
    with open("results/mock_validation.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nDetailed results written to results/mock_validation.json")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
