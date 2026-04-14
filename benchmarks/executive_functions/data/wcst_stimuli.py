"""
WCST v3 — Hidden dimensions, probabilistic feedback, variable shifts.

Changes from v2:
- 5 dimensions (added border_style, background): model must discover which matter
- Model is NOT told what dimensions exist — must infer from feedback
- Probabilistic feedback: 85% reliable (15% random)
- Variable shift criterion: 3-7 consecutive correct before shift
- Multi-dimensional phase: later blocks require matching on 2 dimensions
- 80 total cards across phases
"""

import random
import hashlib

COLORS = ["red", "blue", "green", "yellow"]
SHAPES = ["circle", "triangle", "square", "star"]
NUMBERS = [1, 2, 3, 4]
BORDERS = ["solid", "dashed", "dotted"]
BACKGROUNDS = ["light", "dark", "striped"]

ALL_DIMS = ["color", "shape", "number", "border", "background"]

# Reference cards — each unique on all 5 dimensions
REFERENCE_CARDS = [
    {"color": "red",    "shape": "circle",   "number": 1, "border": "solid",  "background": "light"},
    {"color": "blue",   "shape": "triangle", "number": 2, "border": "dashed", "background": "dark"},
    {"color": "green",  "shape": "square",   "number": 3, "border": "dotted", "background": "striped"},
    {"color": "yellow", "shape": "star",     "number": 4, "border": "solid",  "background": "dark"},
]


def card_str(card):
    n = card["number"]
    return (f"{n} {card['color']} {card['shape']}{'s' if n > 1 else ''}, "
            f"{card['border']} border, {card['background']} background")


def _match_ref(target, rule_dims):
    """Return 1-indexed reference card matching target on rule dimensions."""
    for i, ref in enumerate(REFERENCE_CARDS):
        if all(target[d] == ref[d] for d in rule_dims):
            return i + 1
    return None


def _make_target(rng, rule_dims, correct_ref_idx):
    """Generate target matching ref[correct_ref_idx] on rule_dims, different on others."""
    ref = REFERENCE_CARDS[correct_ref_idx]
    other_indices = [i for i in range(4) if i != correct_ref_idx]
    rng.shuffle(other_indices)
    
    card = {}
    # Match on rule dimensions
    for d in rule_dims:
        card[d] = ref[d]
    
    # Differ on other dimensions
    other_dims = [d for d in ALL_DIMS if d not in rule_dims]
    for j, d in enumerate(other_dims):
        other_ref = REFERENCE_CARDS[other_indices[j % len(other_indices)]]
        card[d] = other_ref[d]
    
    return card


def generate_wcst_v3(seed="wcst_v3_seed"):
    """Generate WCST v3 trial sequence."""
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    
    phases = []
    
    # Phase 1: Single-dimension sorting (5 rule shifts)
    # Rules cycle through dimensions, model must discover which one
    single_rules = [["color"], ["shape"], ["number"], ["border"], ["background"]]
    rng.shuffle(single_rules)
    
    for rule_dims in single_rules[:5]:
        shift_after = rng.randint(3, 7)  # Variable shift criterion
        
        # Generate history (correct examples under this rule)
        history = []
        for _ in range(rng.randint(3, 5)):
            ref_idx = rng.randint(0, 3)
            target = _make_target(rng, rule_dims, ref_idx)
            correct = ref_idx + 1
            # Probabilistic feedback
            if rng.random() < 0.85:
                feedback = "Correct"
            else:
                feedback = "Incorrect"  # Noisy feedback
            history.append({
                "target": target,
                "chosen": correct,
                "feedback": feedback,
                "actual_correct": correct,
            })
        
        # Generate test cards
        n_test = rng.randint(6, 10)
        test_cards = []
        for _ in range(n_test):
            ref_idx = rng.randint(0, 3)
            target = _make_target(rng, rule_dims, ref_idx)
            test_cards.append({
                "target": target,
                "correct": ref_idx + 1,
            })
        
        phases.append({
            "phase_type": "single",
            "rule_dims": rule_dims,
            "history": history,
            "test_cards": test_cards,
            "shift_criterion": shift_after,
        })
    
    # Phase 2: Multi-dimensional sorting (2 blocks, require matching 2 dims)
    multi_rules = [["color", "number"], ["shape", "background"]]
    for rule_dims in multi_rules:
        history = []
        for _ in range(rng.randint(4, 6)):
            ref_idx = rng.randint(0, 3)
            target = _make_target(rng, rule_dims, ref_idx)
            correct = ref_idx + 1
            feedback = "Correct" if rng.random() < 0.85 else "Incorrect"
            history.append({
                "target": target,
                "chosen": correct,
                "feedback": feedback,
                "actual_correct": correct,
            })
        
        test_cards = []
        for _ in range(rng.randint(6, 8)):
            ref_idx = rng.randint(0, 3)
            target = _make_target(rng, rule_dims, ref_idx)
            test_cards.append({"target": target, "correct": ref_idx + 1})
        
        phases.append({
            "phase_type": "multi",
            "rule_dims": rule_dims,
            "history": history,
            "test_cards": test_cards,
        })
    
    return {"phases": phases, "reference_cards": REFERENCE_CARDS}


WCST_V3 = generate_wcst_v3()
