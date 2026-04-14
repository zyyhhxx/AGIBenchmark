"""
Executive Functions Benchmark 3: Task-Switching (v2)

Tests cognitive flexibility through alternating task rules presented
in BATCH format — the model classifies a sequence of items in one response,
applying the correct rule to each position.

v2 redesign (2026-04-11): Original had zero discrimination because each trial
was independent. Now uses batch presentation with harder rules:
- Rule A: "Digit Sum" — is the sum of digits odd or even?
- Rule B: "Letter Position" — does the letter come before or after M?

These rules require different cognitive operations, creating genuine switch cost.

Cognitive Science Basis:
- Rogers & Monsell (1995): Alternating-runs paradigm
- Monsell (2003): Switch cost = executive control reconfiguration
- Miyake et al. (2000): Shifting as core executive function
- Allport, Styles & Hsieh (1994): Task-set inertia and interference

Score = 0.15*baseline + 0.25*slow + 0.35*rapid + 0.25*switch_cost_metric
"""

import kaggle_benchmarks as kbench
import json as _json
def _safe_log(data): print(_json.dumps(data, indent=2, default=str))
import numpy as np
import re
from data.task_switch_stimuli import TASK_SWITCH_BLOCKS


def normalize_answer(answer: str, rule: str) -> str:
    """Normalize model's answer to standard form."""
    answer = answer.lower().strip()
    if rule == "digit_sum":
        if "odd" in answer:
            return "odd"
        if "even" in answer:
            return "even"
    else:  # letter_pos
        if "before" in answer:
            return "before"
        if "after" in answer:
            return "after"
    return answer



def _strip_think(text: str) -> str:
    """Remove <think>...</think> blocks from model output."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def parse_batch_response(response_text: str, trials: list) -> list:
    """Parse batch response — one answer per line, numbered."""
    lines = response_text.strip().split('\n')
    answers = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Match numbered answers: "1. odd", "1: before", etc.
        m = re.match(r'^(?:#?\d+[\.\):\-\s]+)\s*(.+)$', line)
        if m:
            ans = m.group(1).strip().rstrip('.,;')
            if len(ans) < 60:
                answers.append(ans)
        elif len(line) < 20 and any(w in line.lower() for w in ['odd', 'even', 'before', 'after']):
            answers.append(line)
    
    # Fallback: comma-separated
    if len(answers) < len(trials) // 2:
        answers = []
        parts = response_text.replace('\n', ' ').split(',')
        for part in parts:
            part = part.strip().rstrip('.,;')
            m = re.match(r'^(?:#?\d+[\.\):\-\s]+)?\s*(.+)$', part)
            if m:
                ans = m.group(1).strip()
                if len(ans) < 30:
                    answers.append(ans)
    
    return answers


def run_block(llm, block_name: str, trials: list) -> dict:
    """Run one block in batch mode."""
    lines = []
    for i, trial in enumerate(trials):
        lines.append(f"{i+1}. {trial['instruction']}  [Rule: {trial['rule_label']}]")
    
    items_text = "\n".join(lines)
    
    if block_name == "baseline":
        intro = (
            "For each item below, determine if the sum of the number's digits is odd or even.\n"
            "Answer with exactly ONE word per item: 'odd' or 'even'.\n"
        )
    else:
        intro = (
            "Classify each item below according to its stated rule.\n"
            "Rules vary between items — pay close attention!\n\n"
            "- 'Digit Sum Odd/Even': Is the sum of the number's digits odd or even? Answer 'odd' or 'even'\n"
            "- 'Letter Before/After M': Does the letter come before or after M in the alphabet? Answer 'before' or 'after'\n\n"
            "For each item, answer with exactly ONE word on a separate line.\n"
        )
    
    prompt = (
        f"{intro}\n"
        f"Items:\n{items_text}\n\n"
        f"Provide your {len(trials)} answers, one per line, numbered to match."
    )
    
    with kbench.chats.new(f"switch_{block_name}"):
        raw = llm.prompt(prompt)
    
    answers = parse_batch_response(_strip_think(raw), trials)
    
    results = []
    for i, trial in enumerate(trials):
        if i < len(answers):
            model_answer = normalize_answer(answers[i], trial["rule"])
        else:
            model_answer = ""
        
        correct = (model_answer == trial["correct_answer"])
        results.append({
            "trial_idx": i,
            "stimulus": trial["stimulus"],
            "rule": trial["rule"],
            "correct_answer": trial["correct_answer"],
            "model_answer": model_answer,
            "correct": correct,
            "is_switch": trial["is_switch_trial"],
        })
    
    total = len(results)
    n_correct = sum(1 for r in results if r["correct"])
    accuracy = n_correct / total if total > 0 else 0
    
    switch_trials = [r for r in results if r["is_switch"]]
    repeat_trials = [r for r in results if not r["is_switch"]]
    
    switch_acc = sum(1 for r in switch_trials if r["correct"]) / max(len(switch_trials), 1)
    repeat_acc = sum(1 for r in repeat_trials if r["correct"]) / max(len(repeat_trials), 1)
    switch_cost = repeat_acc - switch_acc
    
    return {
        "block": block_name,
        "accuracy": accuracy,
        "switch_accuracy": switch_acc,
        "repeat_accuracy": repeat_acc,
        "switch_cost": switch_cost,
        "n_trials": total,
        "n_correct": n_correct,
        "n_switch": len(switch_trials),
        "n_parsed": len(answers),
        "results": results,
    }


@kbench.task(name="Task Switching")
def exec_func_task_switch(llm) -> float:
    """
    Task-Switching Benchmark (v2 — batch presentation, harder rules).

    Tests cognitive flexibility via alternating classification rules:
    - Digit Sum: is the sum of digits odd or even?
    - Letter Position: does the letter come before or after M?

    Score = 0.15*baseline + 0.25*slow + 0.35*rapid + 0.25*switch_cost_metric

    Cognitive Science: Rogers & Monsell (1995), Monsell (2003), Miyake et al. (2000).
    """
    blocks = TASK_SWITCH_BLOCKS
    block_results = {}
    
    for block_name in ["baseline", "slow_switch", "rapid_switch", "random_cue"]:
        block_results[block_name] = run_block(llm, block_name, blocks[block_name])
    
    baseline_acc = block_results["baseline"]["accuracy"]
    slow_acc = block_results["slow_switch"]["accuracy"]
    rapid_acc = block_results["rapid_switch"]["accuracy"]
    
    # Aggregate switch/repeat accuracy across blocks 2-4
    all_switch_correct = 0
    all_switch_total = 0
    all_repeat_correct = 0
    all_repeat_total = 0
    for bname in ["slow_switch", "rapid_switch", "random_cue"]:
        for r in block_results[bname]["results"]:
            if r["is_switch"]:
                all_switch_total += 1
                if r["correct"]:
                    all_switch_correct += 1
            else:
                all_repeat_total += 1
                if r["correct"]:
                    all_repeat_correct += 1
    
    agg_switch_acc = all_switch_correct / max(all_switch_total, 1)
    agg_repeat_acc = all_repeat_correct / max(all_repeat_total, 1)
    agg_switch_cost = agg_repeat_acc - agg_switch_acc
    
    # Penalize high switch cost: 0 cost = 1.0; 0.5 cost = 0.0
    switch_cost_metric = max(0.0, 1.0 - 2.0 * max(0, agg_switch_cost))
    
    score = (
        0.15 * baseline_acc +
        0.25 * slow_acc +
        0.35 * rapid_acc +
        0.25 * switch_cost_metric
    )
    score = round(float(np.clip(score, 0, 1)), 4)
    
    log_data = {
        "benchmark": "Task Switching v2",
        "composite_score": score,
        "baseline_accuracy": round(baseline_acc, 4),
        "slow_switch_accuracy": round(slow_acc, 4),
        "rapid_switch_accuracy": round(rapid_acc, 4),
        "aggregate_switch_accuracy": round(agg_switch_acc, 4),
        "aggregate_repeat_accuracy": round(agg_repeat_acc, 4),
        "aggregate_switch_cost": round(agg_switch_cost, 4),
        "switch_cost_metric": round(switch_cost_metric, 4),
        "blocks": {},
    }
    for bname, br in block_results.items():
        log_data["blocks"][bname] = {
            "accuracy": round(br["accuracy"], 4),
            "switch_acc": round(br["switch_accuracy"], 4),
            "repeat_acc": round(br["repeat_accuracy"], 4),
            "switch_cost": round(br["switch_cost"], 4),
            "n_parsed": br["n_parsed"],
            "n_trials": br["n_trials"],
        }
    _safe_log(log_data)
    
    print(f"\n{'='*60}")
    print(f"TASK SWITCHING RESULTS (v2 — harder rules)")
    print(f"{'='*60}")
    for bname in ["baseline", "slow_switch", "rapid_switch", "random_cue"]:
        br = block_results[bname]
        print(f"\n  Block: {bname}")
        print(f"    Accuracy: {br['accuracy']:.2%} ({br['n_correct']}/{br['n_trials']})")
        print(f"    Switch trials acc: {br['switch_accuracy']:.2%} (n={br['n_switch']})")
        print(f"    Repeat trials acc: {br['repeat_accuracy']:.2%}")
        print(f"    Answers parsed: {br['n_parsed']}/{br['n_trials']}")
    
    print(f"\n--- Aggregate ---")
    print(f"  Switch accuracy: {agg_switch_acc:.2%}")
    print(f"  Repeat accuracy: {agg_repeat_acc:.2%}")
    print(f"  Switch cost: {agg_switch_cost:.4f}")
    print(f"  Composite score: {score:.4f}")
    
    return score


exec_func_task_switch.run(llm=kbench.llm)
