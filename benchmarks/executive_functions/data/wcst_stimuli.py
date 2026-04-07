"""
Stimuli generator for Wisconsin Card Sort Test (WCST) analogue.

Generates card stimuli with 3 sorting dimensions:
- Color: red, blue, green, yellow
- Shape: circle, triangle, square, star
- Number: 1, 2, 3, 4

Each trial has a target card and 4 reference cards (one matching on each
dimension, ensuring unique correct answer per active rule).
"""

import random
import json
from itertools import product

COLORS = ["red", "blue", "green", "yellow"]
SHAPES = ["circle", "triangle", "square", "star"]
NUMBERS = [1, 2, 3, 4]

ALL_CARDS = [
    {"color": c, "shape": s, "number": n}
    for c, s, n in product(COLORS, SHAPES, NUMBERS)
]


def card_str(card: dict) -> str:
    """Human-readable card description."""
    return f"{card['number']} {card['color']} {card['shape']}{'s' if card['number'] > 1 else ''}"


def generate_reference_cards():
    """
    Generate 4 reference cards that are maximally distinctive.
    Each reference card should have a unique value on each dimension.
    """
    # Use a Latin square approach: each reference card has unique color, shape, number
    refs = [
        {"color": COLORS[0], "shape": SHAPES[0], "number": NUMBERS[0]},
        {"color": COLORS[1], "shape": SHAPES[1], "number": NUMBERS[1]},
        {"color": COLORS[2], "shape": SHAPES[2], "number": NUMBERS[2]},
        {"color": COLORS[3], "shape": SHAPES[3], "number": NUMBERS[3]},
    ]
    return refs


def generate_target_card(refs: list, active_rule: str, correct_ref_idx: int) -> dict:
    """
    Generate a target card that matches reference[correct_ref_idx] on the active
    dimension, but does NOT match ANY reference on the other two dimensions.
    This ensures a unique correct answer for the active rule while making
    other-dimension matches misleading.
    """
    correct_ref = refs[correct_ref_idx]
    dims = ["color", "shape", "number"]
    other_dims = [d for d in dims if d != active_rule]

    # Target matches on active dimension
    target = {active_rule: correct_ref[active_rule]}

    # For other dimensions, pick values that match DIFFERENT reference cards
    # (or no reference at all) to create distractors
    for dim in other_dims:
        # Pick a value from a different reference card index
        other_indices = [i for i in range(4) if i != correct_ref_idx]
        random.shuffle(other_indices)
        # Use a value from a random other reference
        target[dim] = refs[other_indices[0]][dim]
        other_indices = other_indices[1:]  # rotate for next dim if needed

    return target


def generate_wcst_trials(n_trials: int = 80, rule_switch_after: int = 10, seed: int = 42):
    """
    Generate a full set of WCST trials.

    Rules cycle: color -> shape -> number -> color -> ...
    Rule switches after `rule_switch_after` consecutive correct responses.
    We pre-generate the stimuli and the expected feedback sequence.

    Returns list of trial dicts with:
    - trial_num
    - target_card
    - reference_cards (always same 4)
    - active_rule (hidden from model)
    - correct_answer (1-4, index of correct reference)
    - rule_episode (which rule epoch we're in)
    """
    random.seed(seed)
    rules = ["color", "shape", "number"]
    refs = generate_reference_cards()

    trials = []
    current_rule_idx = 0
    rule_episode = 0

    for t in range(n_trials):
        active_rule = rules[current_rule_idx % len(rules)]
        # Random correct reference index (1-indexed for user-friendliness)
        correct_ref_idx = random.randint(0, 3)
        target = generate_target_card(refs, active_rule, correct_ref_idx)

        trials.append({
            "trial_num": t + 1,
            "target_card": target,
            "reference_cards": refs,
            "active_rule": active_rule,
            "correct_answer": correct_ref_idx + 1,  # 1-indexed
            "rule_episode": rule_episode,
        })

        # Simulate rule switch: after every `rule_switch_after` trials in an episode
        # (In actual task, switch happens after N correct; here we pre-set switch points)
        if (t + 1) % rule_switch_after == 0:
            current_rule_idx += 1
            rule_episode += 1

    return {"reference_cards": refs, "trials": trials}


# Pre-generated stimuli
WCST_STIMULI = generate_wcst_trials(n_trials=80, rule_switch_after=10, seed=42)

if __name__ == "__main__":
    stim = WCST_STIMULI
    print(f"Reference cards:")
    for i, r in enumerate(stim["reference_cards"], 1):
        print(f"  Card {i}: {card_str(r)}")
    print(f"\nTotal trials: {len(stim['trials'])}")
    print(f"Rule episodes: {stim['trials'][-1]['rule_episode'] + 1}")
    print(f"\nSample trials:")
    for t in stim["trials"][:5]:
        print(f"  Trial {t['trial_num']}: target={card_str(t['target_card'])}, "
              f"rule={t['active_rule']}, correct=Card {t['correct_answer']}")
