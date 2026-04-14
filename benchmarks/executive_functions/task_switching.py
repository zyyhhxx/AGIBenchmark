"""
Task-Switching v3 — Harder compositional rules with congruency.

Changes from v2:
- 4 rules requiring multi-step computation (prime check, position parity, divisibility, vowel proximity)
- Post-stimulus cuing in rapid/random blocks (item shown before rule)
- Congruency-aware item generation
- Score: 0.10*baseline + 0.25*slow + 0.35*rapid + 0.30*switch_cost_metric

Cognitive Basis:
- Rogers & Monsell (1995): Task-switching paradigm
- Meiran (1996): Post-stimulus cuing increases switch cost
- Allport et al. (1994): Task-set inertia
"""

import kaggle_benchmarks as kbench
import re
import json as _json
import numpy as np
from benchmarks.executive_functions.data.task_switch_stimuli import (
    TASK_SWITCH_V3_BLOCKS, RULES
)


def _safe_log(data): print(_json.dumps(data, indent=2, default=str))


def _strip_think(text: str) -> str:
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def normalize_answer(answer: str, rule: str) -> str:
    """Normalize model answer to expected format."""
    answer = answer.lower().strip().rstrip('.,;')
    rule_answers = RULES[rule]["answers"]
    # Direct match
    for a in rule_answers:
        if a in answer:
            return a
    # Partial matches
    if rule == "A":
        if "not" in answer or "no" in answer or "composite" in answer:
            return "not-prime"
        if "prime" in answer or "yes" in answer:
            return "prime"
    elif rule == "B":
        if "even" in answer: return "even"
        if "odd" in answer: return "odd"
    elif rule in ("C", "D"):
        if "yes" in answer: return "yes"
        if "no" in answer: return "no"
    return answer


def parse_batch_response(response_text: str, trials: list) -> list:
    """Parse numbered responses from batch output."""
    response_text = _strip_think(response_text)
    response_text = re.sub(r'//.*', '', response_text)
    lines = response_text.strip().split('\n')
    answers = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^\d+[\.\):\s]+(.+)', line)
        if m:
            ans = m.group(1).strip().rstrip('.,;')
            answers.append(ans)
    
    # Fallback: split by commas or semicolons
    if len(answers) < len(trials):
        parts = re.split(r'[,;\n]+', response_text)
        answers = []
        for part in parts:
            part = part.strip().rstrip('.,;')
            if part and not part[0].isdigit():
                answers.append(part)
            elif part:
                m = re.match(r'\d+[\.\):\s]+(.+)', part)
                if m:
                    answers.append(m.group(1).strip())
    
    return answers[:len(trials)]


def run_block(llm, block_name: str, trials: list) -> dict:
    """Run a block of task-switching trials."""
    
    # Build prompt
    rule_descriptions = []
    for rkey in ["A", "B", "C", "D"]:
        r = RULES[rkey]
        rule_descriptions.append(
            f"- Rule {rkey} ({r['name']}): Answer '{r['answers'][0]}' or '{r['answers'][1]}'"
        )
    
    if block_name == "baseline":
        header = "For each item, apply Rule A (Digit Sum Prime): Is the digit sum a prime number?\nAnswer 'prime' or 'not-prime'."
    else:
        header = (
            "Classify each item according to its stated rule.\n"
            "Rules vary between items — pay close attention!\n\n"
            + "\n".join(rule_descriptions)
        )
    
    items_text = []
    for i, trial in enumerate(trials):
        stim = trial["stimulus"]
        rule = trial["rule"]
        r = RULES[rule]
        
        if trial.get("post_cue"):
            # Post-stimulus cuing: show item first, then rule
            item_line = f"{i+1}. Item: {stim['number']}{stim['letter']}. Now apply Rule {rule}: "
            item_line += r["prompt"].format(**stim)
        else:
            # Pre-stimulus cuing
            item_line = f"{i+1}. " + r["prompt"].format(**stim) + f" [Rule {rule}]"
        
        items_text.append(item_line)
    
    prompt = (
        header + "\n\n"
        "For each item, answer with exactly ONE word/phrase on a separate line.\n\n"
        "Items:\n" + "\n".join(items_text) + "\n\n"
        f"Provide your {len(trials)} answers, one per line, numbered to match."
    )
    
    with kbench.chats.new(f"switch_{block_name}"):
        raw = llm.prompt(prompt)
    
    answers = parse_batch_response(raw, trials)
    
    # Score
    results = []
    for i, trial in enumerate(trials):
        if i < len(answers):
            norm = normalize_answer(answers[i], trial["rule"])
            correct = (norm == trial["correct"])
        else:
            norm = ""
            correct = False
        
        results.append({
            "item": i + 1,
            "rule": trial["rule"],
            "correct_answer": trial["correct"],
            "model_answer": norm,
            "correct": correct,
            "is_switch": trial["is_switch_trial"],
        })
    
    switch_trials = [r for r in results if r["is_switch"]]
    repeat_trials = [r for r in results if not r["is_switch"]]
    
    switch_acc = sum(1 for r in switch_trials if r["correct"]) / max(len(switch_trials), 1)
    repeat_acc = sum(1 for r in repeat_trials if r["correct"]) / max(len(repeat_trials), 1)
    accuracy = sum(1 for r in results if r["correct"]) / max(len(results), 1)
    
    return {
        "accuracy": accuracy,
        "switch_accuracy": switch_acc,
        "repeat_accuracy": repeat_acc,
        "switch_cost": repeat_acc - switch_acc,
        "results": results,
        "n_correct": sum(1 for r in results if r["correct"]),
        "n_trials": len(trials),
        "n_parsed": len(answers),
        "n_switch": len(switch_trials),
    }


@kbench.task(name="Task Switching")
def exec_func_task_switch(llm) -> float:
    """
    Task-Switching v3 with compositional rules and post-stimulus cuing.
    
    Score = 0.10*baseline + 0.25*slow + 0.35*rapid + 0.30*switch_cost_metric
    """
    blocks = TASK_SWITCH_V3_BLOCKS
    block_results = {}
    
    for block_name in ["baseline", "slow_switch", "rapid_switch", "random_cue"]:
        block_results[block_name] = run_block(llm, block_name, blocks[block_name])
    
    baseline_acc = block_results["baseline"]["accuracy"]
    slow_acc = block_results["slow_switch"]["accuracy"]
    rapid_acc = block_results["rapid_switch"]["accuracy"]
    
    # Aggregate switch cost across blocks 2-4
    all_switch_correct = all_switch_total = 0
    all_repeat_correct = all_repeat_total = 0
    for bname in ["slow_switch", "rapid_switch", "random_cue"]:
        for r in block_results[bname]["results"]:
            if r["is_switch"]:
                all_switch_total += 1
                if r["correct"]: all_switch_correct += 1
            else:
                all_repeat_total += 1
                if r["correct"]: all_repeat_correct += 1
    
    agg_switch_acc = all_switch_correct / max(all_switch_total, 1)
    agg_repeat_acc = all_repeat_correct / max(all_repeat_total, 1)
    agg_switch_cost = agg_repeat_acc - agg_switch_acc
    
    switch_cost_metric = max(0.0, 1.0 - 2.0 * max(0, agg_switch_cost))
    
    score = 0.10 * baseline_acc + 0.25 * slow_acc + 0.35 * rapid_acc + 0.30 * switch_cost_metric
    score = round(float(np.clip(score, 0, 1)), 4)
    
    print(f"\n{'='*60}")
    print(f"TASK SWITCHING v3 RESULTS")
    print(f"{'='*60}")
    for bname in ["baseline", "slow_switch", "rapid_switch", "random_cue"]:
        br = block_results[bname]
        print(f"\n  {bname}: acc={br['accuracy']:.2%} switch_acc={br['switch_accuracy']:.2%} "
              f"repeat_acc={br['repeat_accuracy']:.2%} parsed={br['n_parsed']}/{br['n_trials']}")
    print(f"\n  Aggregate switch cost: {agg_switch_cost:.4f}")
    print(f"  Composite score: {score:.4f}")
    
    _safe_log({
        "benchmark": "Task Switching v3",
        "composite_score": score,
        "blocks": {b: {"accuracy": block_results[b]["accuracy"],
                       "switch_acc": block_results[b]["switch_accuracy"],
                       "switch_cost": block_results[b]["switch_cost"]}
                  for b in block_results},
    })
    
    return score
