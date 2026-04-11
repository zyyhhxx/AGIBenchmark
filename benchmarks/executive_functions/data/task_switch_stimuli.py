"""
Stimuli generator for Task-Switching benchmark (v2).

v2 redesign: Uses harder classification rules that create genuine interference.

Rules:
- Rule A: "Sum of digits" — classify whether the sum of digits is odd or even
- Rule B: "Letter value" — given a number-letter pair, classify whether the letter 
  comes before or after 'M' in the alphabet

These rules require different cognitive operations (arithmetic vs. ordinal comparison)
and create genuine switch cost because the stimulus format changes between rules.

Blocks:
- Baseline: 15 items, Rule A only
- Slow switch: 20 items, rule alternates every 5
- Rapid switch: 20 items, rule alternates every 1-2
- Random cue: 20 items, random rule per item
"""

import random
import string


def generate_task_switch_blocks(seed=42):
    """
    Generate 4 blocks of task-switching stimuli with harder rules.
    """
    rng = random.Random(seed)
    
    # Stimulus pool for Rule A (digit sum): 2-3 digit numbers
    # Stimulus pool for Rule B (letter comparison): number-letter pairs
    letters_before_m = list("ABCDEFGHIJKL")  # before M
    letters_after_m = list("NOPQRSTUVWXYZ")   # after M
    all_letters = letters_before_m + letters_after_m
    
    def make_stimulus_a(rng):
        """Generate a number for digit-sum classification."""
        n = rng.randint(10, 99)
        digit_sum = sum(int(d) for d in str(n))
        correct = "odd" if digit_sum % 2 == 1 else "even"
        return {"stimulus": str(n), "correct": correct, "detail": f"digits sum to {digit_sum}"}
    
    def make_stimulus_b(rng):
        """Generate a number-letter pair for letter comparison."""
        num = rng.randint(1, 50)
        letter = rng.choice(all_letters)
        correct = "before" if letter < 'M' else "after"
        return {"stimulus": f"{num}{letter}", "correct": correct, "detail": f"'{letter}' is {correct} M"}
    
    def make_trial(rng, rule, prev_rule):
        if rule == "digit_sum":
            stim = make_stimulus_a(rng)
            rule_label = "Digit Sum Odd/Even"
            instruction = f"Is the sum of digits of {stim['stimulus']} odd or even?"
        else:
            stim = make_stimulus_b(rng)
            rule_label = "Letter Before/After M"
            instruction = f"In '{stim['stimulus']}', does the letter come before or after M in the alphabet?"
        
        return {
            "stimulus": stim["stimulus"],
            "rule": rule,
            "rule_label": rule_label,
            "instruction": instruction,
            "correct_answer": stim["correct"],
            "detail": stim["detail"],
            "is_switch_trial": prev_rule is not None and prev_rule != rule,
        }
    
    blocks = {}
    rules = ["digit_sum", "letter_pos"]
    
    # Block 1: Baseline (all digit_sum)
    baseline = []
    for i in range(15):
        baseline.append(make_trial(rng, "digit_sum", "digit_sum" if i > 0 else None))
    blocks["baseline"] = baseline
    
    # Block 2: Slow switch (every 5 items)
    slow = []
    prev_rule = None
    for i in range(20):
        rule = rules[(i // 5) % 2]
        slow.append(make_trial(rng, rule, prev_rule))
        prev_rule = rule
    blocks["slow_switch"] = slow
    
    # Block 3: Rapid switch (every 1-2 items)
    rapid = []
    prev_rule = None
    current_rule = "digit_sum"
    count_in_run = 0
    run_length = rng.choice([1, 2])
    for i in range(20):
        rapid.append(make_trial(rng, current_rule, prev_rule))
        prev_rule = current_rule
        count_in_run += 1
        if count_in_run >= run_length:
            current_rule = "letter_pos" if current_rule == "digit_sum" else "digit_sum"
            count_in_run = 0
            run_length = rng.choice([1, 2])
    blocks["rapid_switch"] = rapid
    
    # Block 4: Random cue
    random_cue = []
    prev_rule = None
    for i in range(20):
        rule = rng.choice(rules)
        random_cue.append(make_trial(rng, rule, prev_rule))
        prev_rule = rule
    blocks["random_cue"] = random_cue
    
    return blocks


TASK_SWITCH_BLOCKS = generate_task_switch_blocks(seed=42)

# Legacy compat
TASK_SWITCH_TRIALS = []
for block_name in ["baseline", "slow_switch", "rapid_switch", "random_cue"]:
    for i, trial in enumerate(TASK_SWITCH_BLOCKS[block_name]):
        trial_copy = dict(trial)
        trial_copy["trial_num"] = len(TASK_SWITCH_TRIALS) + 1
        trial_copy["block"] = block_name
        TASK_SWITCH_TRIALS.append(trial_copy)


if __name__ == "__main__":
    blocks = TASK_SWITCH_BLOCKS
    for bname, trials in blocks.items():
        switches = sum(1 for t in trials if t["is_switch_trial"])
        print(f"Block '{bname}': {len(trials)} trials, {switches} switch trials")
        for i, t in enumerate(trials[:6]):
            sw = " [SWITCH]" if t["is_switch_trial"] else ""
            print(f"  {i+1}: stim={t['stimulus']:5s} rule={t['rule_label']:22s} correct={t['correct_answer']:6s} {t['detail']}{sw}")
        if len(trials) > 6:
            print(f"  ... ({len(trials) - 6} more)")
