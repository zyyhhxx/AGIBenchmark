"""
WCST v3 — Hidden dimensions, probabilistic feedback, variable shifts.

Changes from v2:
- 5 sorting dimensions (color, shape, number, border, background)
- Model NOT told which dimensions exist — must discover from feedback
- Probabilistic feedback (85% reliable)
- Variable shift criterion (3-7 correct before shift)
- Multi-dimensional phase (match on 2 dims simultaneously)

Cognitive Basis:
- Grant & Berg (1948): Original WCST
- Milner (1963): Perseveration in frontal lobe patients
- Barceló (2003): Probabilistic feedback variants
"""

import kaggle_benchmarks as kbench
import re
import json as _json
import numpy as np
from benchmarks.executive_functions.data.wcst_stimuli import (
    WCST_V3, card_str, REFERENCE_CARDS
)


def _safe_log(data): print(_json.dumps(data, indent=2, default=str))


def _strip_think(text: str) -> str:
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def _parse_responses(raw: str, n_expected: int) -> list:
    """Parse card number responses (1-4)."""
    raw = _strip_think(raw)
    raw = re.sub(r'//.*', '', raw)
    
    # Try numbered lines
    results = []
    for line in raw.strip().split('\n'):
        line = line.strip()
        m = re.search(r'\b([1-4])\b', line)
        if m:
            results.append(int(m.group(1)))
            if len(results) >= n_expected:
                break
    
    if len(results) >= n_expected:
        return results[:n_expected]
    
    # Fallback: all numbers 1-4 in order
    all_nums = re.findall(r'\b([1-4])\b', raw)
    # Take last n_expected (more likely to be final answers)
    nums = [int(x) for x in all_nums]
    if len(nums) >= n_expected:
        return nums[-n_expected:]
    
    # Pad with 1
    while len(nums) < n_expected:
        nums.append(1)
    return nums[:n_expected]


def run_phase(llm, phase: dict, phase_idx: int) -> dict:
    """Run one WCST phase (single or multi-dimensional sorting)."""
    history = phase["history"]
    test_cards = phase["test_cards"]
    rule_dims = phase["rule_dims"]
    
    # Build reference card display (show ALL 5 dimensions, don't reveal which matter)
    ref_display = "\n".join(
        f"  Card {i+1}: {card_str(ref)}"
        for i, ref in enumerate(REFERENCE_CARDS)
    )
    
    # Build history display with feedback
    history_lines = []
    for h in history:
        history_lines.append(
            f"  Target: {card_str(h['target'])} → Sorted to Card {h['chosen']} → {h['feedback']}"
        )
    
    # Build test card display
    test_lines = []
    for i, tc in enumerate(test_cards):
        test_lines.append(f"  {i+1}. {card_str(tc['target'])}")
    
    phase_label = "Multi-Dimension" if phase["phase_type"] == "multi" else "Single-Dimension"
    
    prompt = (
        f"CARD SORTING TASK — Phase {phase_idx + 1} ({phase_label})\n\n"
        f"You have 4 reference cards:\n{ref_display}\n\n"
        f"Each card has multiple properties. The sorting rule uses one or more properties "
        f"to determine which reference card a target matches.\n\n"
        f"Here is the recent sorting history with feedback:\n"
        + "\n".join(history_lines) + "\n\n"
        f"Based on the pattern in the feedback, sort each new target card.\n"
        f"For each card, respond with the reference card number (1-4).\n\n"
        f"New cards to sort:\n" + "\n".join(test_lines) + "\n\n"
        f"Respond with {len(test_cards)} numbers (1-4), one per line."
    )
    
    with kbench.chats.new(f"wcst_phase_{phase_idx}"):
        raw = llm.prompt(prompt)
    
    choices = _parse_responses(raw, len(test_cards))
    
    # Score
    correct_count = 0
    results = []
    for i, (tc, choice) in enumerate(zip(test_cards, choices)):
        is_correct = (choice == tc["correct"])
        if is_correct:
            correct_count += 1
        results.append({
            "card": i + 1,
            "correct_ref": tc["correct"],
            "model_choice": choice,
            "correct": is_correct,
        })
    
    accuracy = correct_count / max(len(test_cards), 1)
    
    return {
        "phase_type": phase["phase_type"],
        "rule_dims": rule_dims,
        "accuracy": round(accuracy, 4),
        "n_correct": correct_count,
        "n_test": len(test_cards),
        "results": results,
    }


@kbench.task(name="Wisconsin Card Sort")
def exec_func_wcst(llm) -> float:
    """
    WCST v3 — Hidden dimensions, probabilistic feedback, variable shifts.
    
    Score = 0.30 * single_phase_mean + 0.45 * multi_phase_mean + 0.25 * perseveration_resistance
    """
    data = WCST_V3
    phase_results = []
    
    for i, phase in enumerate(data["phases"]):
        result = run_phase(llm, phase, i)
        phase_results.append(result)
    
    # Separate single and multi-dim phases
    single_accs = [r["accuracy"] for r in phase_results if r["phase_type"] == "single"]
    multi_accs = [r["accuracy"] for r in phase_results if r["phase_type"] == "multi"]
    
    single_mean = sum(single_accs) / max(len(single_accs), 1)
    multi_mean = sum(multi_accs) / max(len(multi_accs), 1)
    
    # Perseveration resistance: accuracy should not drop across phases
    if len(single_accs) >= 2:
        first_half = single_accs[:len(single_accs)//2]
        second_half = single_accs[len(single_accs)//2:]
        first_mean = sum(first_half) / len(first_half)
        second_mean = sum(second_half) / len(second_half)
        # If second half is worse, perseveration penalty
        persev_resistance = min(1.0, second_mean / max(first_mean, 0.01))
    else:
        persev_resistance = single_mean
    
    score = 0.30 * single_mean + 0.45 * multi_mean + 0.25 * persev_resistance
    score = round(float(np.clip(score, 0, 1)), 4)
    
    print(f"\n{'='*60}")
    print(f"WCST v3 RESULTS")
    print(f"{'='*60}")
    for r in phase_results:
        dims = "+".join(r["rule_dims"])
        print(f"  {r['phase_type']} [{dims}]: {r['accuracy']:.2%} ({r['n_correct']}/{r['n_test']})")
    print(f"\n  Single-dim mean: {single_mean:.2%}")
    print(f"  Multi-dim mean:  {multi_mean:.2%}")
    print(f"  Perseveration resistance: {persev_resistance:.2%}")
    print(f"  Composite score: {score:.4f}")
    
    _safe_log({
        "benchmark": "WCST v3",
        "phases": [{
            "type": r["phase_type"],
            "dims": r["rule_dims"],
            "accuracy": r["accuracy"],
        } for r in phase_results],
        "composite_score": score,
    })
    
    return score
