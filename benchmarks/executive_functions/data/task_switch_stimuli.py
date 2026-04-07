"""
Stimuli generator for Task-Switching benchmark.

Generates number stimuli with alternating rules:
- Rule A: Odd/Even classification
- Rule B: Greater/Less than 5 classification

Trials alternate rules every N trials. Switch trials (where rule changes)
vs. repeat trials (same rule as previous) allow measuring switch cost.
"""

import random

def generate_task_switch_trials(n_trials=40, switch_every=4, seed=42):
    """
    Generate task-switching stimuli.
    
    Rules alternate every `switch_every` trials.
    Numbers 1-9 (excluding 5 for rule B clarity).
    
    Returns list of trial dicts.
    """
    random.seed(seed)
    
    numbers = [1, 2, 3, 4, 6, 7, 8, 9]  # exclude 5 (boundary for rule B)
    rules = ["odd_even", "greater_less"]
    
    trials = []
    for i in range(n_trials):
        rule_idx = (i // switch_every) % 2
        rule = rules[rule_idx]
        number = random.choice(numbers)
        
        # Determine correct answer
        if rule == "odd_even":
            correct = "odd" if number % 2 == 1 else "even"
        else:  # greater_less
            correct = "greater" if number > 5 else "less"
        
        # Is this a switch trial?
        if i == 0:
            is_switch = False
        else:
            prev_rule_idx = ((i - 1) // switch_every) % 2
            is_switch = (rule_idx != prev_rule_idx)
        
        trials.append({
            "trial_num": i + 1,
            "number": number,
            "rule": rule,
            "rule_label": "Odd/Even" if rule == "odd_even" else "Greater/Less than 5",
            "correct_answer": correct,
            "is_switch_trial": is_switch,
        })
    
    return trials


TASK_SWITCH_TRIALS = generate_task_switch_trials(n_trials=40, switch_every=4, seed=42)

if __name__ == "__main__":
    trials = TASK_SWITCH_TRIALS
    print(f"Total trials: {len(trials)}")
    switches = sum(1 for t in trials if t["is_switch_trial"])
    print(f"Switch trials: {switches}, Repeat trials: {len(trials) - switches}")
    print("\nFirst 12 trials:")
    for t in trials[:12]:
        sw = " [SWITCH]" if t["is_switch_trial"] else ""
        print(f"  Trial {t['trial_num']}: number={t['number']}, rule={t['rule_label']}, "
              f"correct={t['correct_answer']}{sw}")
