"""
Executive Functions Benchmark 3: Task-Switching

Tests cognitive flexibility through alternating task rules.
Model classifies numbers using alternating rules:
- Rule A: Classify as Odd or Even
- Rule B: Classify as Greater or Less than 5

Rules alternate every 4 trials. The key metric is "switch cost" —
the accuracy drop on switch trials vs. repeat trials.

Cognitive Science Basis:
- Task-switching paradigm (Jersild, 1927; Rogers & Monsell, 1995)
- Switch cost reflects executive control needed to reconfigure task set
- Miyake et al. (2000): shifting as a core executive function
- Healthy adults show ~5-10% accuracy drop and ~200ms RT increase on switch trials

Metrics:
- Overall accuracy
- Switch cost: accuracy_repeat - accuracy_switch (positive = normal switch cost)
- Accuracy on switch trials vs. repeat trials
- Congruency effect: performance on trials where both rules give same answer

Score = 0.40 * overall_accuracy + 0.30 * switch_trial_accuracy + 0.30 * consistency

Shortcut Resistance:
- Rules are explicitly stated each trial — tests execution, not memory
- Switch cost measures cognitive flexibility, not just knowledge
- Numbers are random, preventing memorization
"""

import kaggle_benchmarks as kbench
import json as _json
def _safe_log(data): print(_json.dumps(data, indent=2, default=str))
from dataclasses import dataclass
import numpy as np
import re
from data.task_switch_stimuli import TASK_SWITCH_TRIALS


@dataclass
class TaskSwitchResponse:
    """Model's classification response."""
    answer: str       # The classification (odd/even/greater/less)
    reasoning: str    # Brief explanation


def normalize_answer(answer: str, rule: str) -> str:
    """Normalize model's answer to standard form."""
    answer = answer.lower().strip()
    
    if rule == "odd_even":
        if "odd" in answer:
            return "odd"
        if "even" in answer:
            return "even"
    else:  # greater_less
        if "greater" in answer or "more" in answer or "above" in answer or "higher" in answer:
            return "greater"
        if "less" in answer or "fewer" in answer or "below" in answer or "lower" in answer or "smaller" in answer:
            return "less"
    
    return answer


@kbench.task(name="exec_func_task_switch")
def exec_func_task_switch(llm) -> float:
    """
    Task-Switching Benchmark.

    Tests cognitive flexibility via alternating classification rules.
    Key metric: switch cost (accuracy difference between switch and repeat trials).

    Score = 0.40 * accuracy + 0.30 * switch_accuracy + 0.30 * consistency

    Cognitive Science Basis: Rogers & Monsell (1995), Miyake et al. (2000).
    Human switch cost: ~5-10% accuracy drop on switch trials.
    """
    trials = TASK_SWITCH_TRIALS
    results = []
    
    for trial in trials:
        rule_instruction = (
            f"Classify the number {trial['number']}.\n"
            f"Current rule: **{trial['rule_label']}**\n\n"
        )
        
        if trial["rule"] == "odd_even":
            rule_instruction += (
                f"Is {trial['number']} ODD or EVEN?\n"
                f"Answer with exactly one word: 'odd' or 'even'"
            )
        else:
            rule_instruction += (
                f"Is {trial['number']} GREATER than 5 or LESS than 5?\n"
                f"Answer with exactly one word: 'greater' or 'less'"
            )
        
        with kbench.chats.new(f"switch_{trial['trial_num']}"):
            try:
                response = llm.prompt(rule_instruction, schema=TaskSwitchResponse)
                raw_answer = response.answer
            except Exception:
                raw_answer = llm.prompt(rule_instruction)
        
        model_answer = normalize_answer(raw_answer, trial["rule"])
        correct = (model_answer == trial["correct_answer"])
        
        results.append({
            "trial_num": trial["trial_num"],
            "number": trial["number"],
            "rule": trial["rule"],
            "correct_answer": trial["correct_answer"],
            "model_answer": model_answer,
            "correct": correct,
            "is_switch": trial["is_switch_trial"],
        })
    
    # ── Compute Metrics ──
    
    n_correct = sum(1 for r in results if r["correct"])
    accuracy = n_correct / len(results)
    
    switch_trials = [r for r in results if r["is_switch"]]
    repeat_trials = [r for r in results if not r["is_switch"]]
    
    switch_acc = sum(1 for r in switch_trials if r["correct"]) / max(len(switch_trials), 1)
    repeat_acc = sum(1 for r in repeat_trials if r["correct"]) / max(len(repeat_trials), 1)
    switch_cost = repeat_acc - switch_acc  # positive = expected
    
    # Consistency: low variance in performance across trial blocks
    block_size = 4
    block_accs = []
    for i in range(0, len(results), block_size):
        block = results[i:i+block_size]
        if block:
            block_accs.append(sum(1 for r in block if r["correct"]) / len(block))
    consistency = 1.0 - min(np.std(block_accs), 0.5) / 0.5 if block_accs else 0.5
    
    # ── Composite Score ──
    score = (
        0.40 * accuracy +
        0.30 * switch_acc +
        0.30 * float(consistency)
    )
    score = round(float(np.clip(score, 0, 1)), 4)
    
    _safe_log({
        "benchmark": "Task Switching",
        "n_trials": len(results),
        "overall_accuracy": round(accuracy, 4),
        "switch_trial_accuracy": round(switch_acc, 4),
        "repeat_trial_accuracy": round(repeat_acc, 4),
        "switch_cost": round(switch_cost, 4),
        "consistency": round(float(consistency), 4),
        "composite_score": score,
        "per_rule": {
            "odd_even": round(sum(1 for r in results if r["rule"] == "odd_even" and r["correct"]) / 
                        max(sum(1 for r in results if r["rule"] == "odd_even"), 1), 4),
            "greater_less": round(sum(1 for r in results if r["rule"] == "greater_less" and r["correct"]) / 
                           max(sum(1 for r in results if r["rule"] == "greater_less"), 1), 4),
        },
    })
    
    return score

exec_func_task_switch.run(llm=kbench.llm)
