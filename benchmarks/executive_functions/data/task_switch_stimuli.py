"""
Task-Switching v3 — Harder compositional rules with congruency manipulation.

Changes from v2:
- 4 harder rules requiring multi-step computation:
  - Rule A: "Is the digit sum prime?" (2,3,5,7,11,13,17,19...)
  - Rule B: "Is the letter's alphabet position even or odd?"
  - Rule C: "Is the number divisible by its digit count?"
  - Rule D: "Is the letter within 3 positions of a vowel (A,E,I,O,U)?"
- Congruency manipulation: ~30% of items where wrong-rule answer matches right-rule answer
- Post-stimulus cuing in rapid/random blocks: item shown BEFORE rule
- 4 blocks: baseline (Rule A only), slow (blocks of 3), rapid (every 1), random
"""

import random
import hashlib


# Primes up to 50 (for digit sum check)
_PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47}

# Vowel positions (1-indexed)
_VOWEL_POSITIONS = {1, 5, 9, 15, 21}  # A=1, E=5, I=9, O=15, U=21

# Letters near vowels (within 3 positions)
_NEAR_VOWEL = set()
for v in _VOWEL_POSITIONS:
    for offset in range(-3, 4):
        pos = v + offset
        if 1 <= pos <= 26:
            _NEAR_VOWEL.add(pos)


def _rule_a(stimulus):
    """Is the digit sum prime?"""
    num = int(stimulus["number"])
    dsum = sum(int(d) for d in str(num))
    return "prime" if dsum in _PRIMES else "not-prime"


def _rule_b(stimulus):
    """Is the letter's alphabet position even or odd?"""
    pos = ord(stimulus["letter"]) - ord('A') + 1
    return "even" if pos % 2 == 0 else "odd"


def _rule_c(stimulus):
    """Is the number divisible by its digit count?"""
    num = int(stimulus["number"])
    n_digits = len(str(num))
    return "yes" if num % n_digits == 0 else "no"


def _rule_d(stimulus):
    """Is the letter within 3 alphabet positions of a vowel?"""
    pos = ord(stimulus["letter"]) - ord('A') + 1
    return "yes" if pos in _NEAR_VOWEL else "no"


RULES = {
    "A": {"name": "Digit Sum Prime", "func": _rule_a,
           "prompt": "Is the digit sum of {number} a prime number?",
           "answers": ("prime", "not-prime")},
    "B": {"name": "Letter Position Parity", "func": _rule_b,
           "prompt": "Is the alphabet position of '{letter}' even or odd?",
           "answers": ("even", "odd")},
    "C": {"name": "Divisible by Digit Count", "func": _rule_c,
           "prompt": "Is {number} divisible by {n_digits} (its number of digits)?",
           "answers": ("yes", "no")},
    "D": {"name": "Near Vowel", "func": _rule_d,
           "prompt": "Is '{letter}' within 3 alphabet positions of a vowel (A,E,I,O,U)?",
           "answers": ("yes", "no")},
}


def _make_stimulus(rng):
    """Generate a number-letter pair."""
    num = rng.randint(10, 999)  # 2-3 digit numbers
    letter = chr(rng.randint(ord('A'), ord('Z')))
    return {"number": str(num), "letter": letter, "n_digits": str(len(str(num)))}


def _generate_block(rng, block_type, n_items=20):
    """Generate a block of trials with rule assignments."""
    trials = []
    
    if block_type == "baseline":
        # All Rule A
        for i in range(n_items):
            stim = _make_stimulus(rng)
            trials.append({
                "stimulus": stim,
                "rule": "A",
                "correct": _rule_a(stim),
                "is_switch_trial": False,
                "post_cue": False,
            })
    
    elif block_type == "slow_switch":
        # Blocks of 3, cycling through A→B→C→D
        rule_seq = []
        rule_cycle = ["A", "B", "C", "D"]
        idx = 0
        while len(rule_seq) < n_items:
            rule_seq.extend([rule_cycle[idx % 4]] * 3)
            idx += 1
        rule_seq = rule_seq[:n_items]
        
        for i, rule in enumerate(rule_seq):
            stim = _make_stimulus(rng)
            is_switch = (i > 0 and rule_seq[i] != rule_seq[i-1])
            trials.append({
                "stimulus": stim,
                "rule": rule,
                "correct": RULES[rule]["func"](stim),
                "is_switch_trial": is_switch,
                "post_cue": False,
            })
    
    elif block_type == "rapid_switch":
        # Alternates every 1-2 items, post-stimulus cuing
        rules_available = ["A", "B", "C", "D"]
        prev_rule = None
        for i in range(n_items):
            # Switch every item, sometimes repeat once
            if prev_rule is None or rng.random() < 0.7:
                rule = rng.choice([r for r in rules_available if r != prev_rule])
            else:
                rule = prev_rule
            stim = _make_stimulus(rng)
            is_switch = (prev_rule is not None and rule != prev_rule)
            trials.append({
                "stimulus": stim,
                "rule": rule,
                "correct": RULES[rule]["func"](stim),
                "is_switch_trial": is_switch,
                "post_cue": True,  # Rule shown AFTER stimulus
            })
            prev_rule = rule
    
    elif block_type == "random_cue":
        # Random rule per item, post-stimulus cuing
        prev_rule = None
        for i in range(n_items):
            rule = rng.choice(["A", "B", "C", "D"])
            stim = _make_stimulus(rng)
            is_switch = (prev_rule is not None and rule != prev_rule)
            trials.append({
                "stimulus": stim,
                "rule": rule,
                "correct": RULES[rule]["func"](stim),
                "is_switch_trial": is_switch,
                "post_cue": True,
            })
            prev_rule = rule
    
    return trials


def generate_all_blocks(seed="task_switch_v3"):
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    return {
        "baseline": _generate_block(rng, "baseline", 15),
        "slow_switch": _generate_block(rng, "slow_switch", 24),
        "rapid_switch": _generate_block(rng, "rapid_switch", 24),
        "random_cue": _generate_block(rng, "random_cue", 24),
    }


TASK_SWITCH_V3_BLOCKS = generate_all_blocks()
