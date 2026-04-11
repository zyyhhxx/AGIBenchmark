"""
Stimuli generator for Wisconsin Card Sort Test (WCST) analogue — Batch version v2.

Generates card stimuli with 3 sorting dimensions:
- Color: red, blue, green, yellow
- Shape: circle, triangle, square, star
- Number: 1, 2, 3, 4

Key design: Each block presents a rule shift scenario where the model sees:
1. History of correct sorts under Rule A
2. A few trials where old-rule answers get "Incorrect" feedback (signaling shift)
3. A few trials where new-rule answers get "Correct" feedback (hinting new rule)
4. Test trials where the model must sort under the new rule

Strong models detect the new rule quickly; weak models perseverate on old rule.
"""

import random

COLORS = ["red", "blue", "green", "yellow"]
SHAPES = ["circle", "triangle", "square", "star"]
NUMBERS = [1, 2, 3, 4]


def card_str(card: dict) -> str:
    """Human-readable card description."""
    n = card["number"]
    return f"{n} {card['color']} {card['shape']}{'s' if n > 1 else ''}"


# Fixed reference cards — Latin square so each card is unique on all dims
REFERENCE_CARDS = [
    {"color": "red",    "shape": "circle",   "number": 1},
    {"color": "blue",   "shape": "triangle", "number": 2},
    {"color": "green",  "shape": "square",   "number": 3},
    {"color": "yellow", "shape": "star",     "number": 4},
]

RULES = ["color", "shape", "number"]
DIM_TO_IDX = {
    "color":  {v: i for i, v in enumerate(COLORS)},
    "shape":  {v: i for i, v in enumerate(SHAPES)},
    "number": {v: i for i, v in enumerate(NUMBERS)},
}


def _correct_ref(target: dict, rule: str) -> int:
    """Return 1-indexed reference card that matches target on the given rule."""
    val = target[rule]
    return DIM_TO_IDX[rule][val] + 1


def _make_target(active_rule: str, correct_ref_idx: int, rng: random.Random) -> dict:
    """
    Generate a target card that matches ref[correct_ref_idx] on active_rule,
    but matches DIFFERENT refs on the other two dimensions.
    """
    refs = REFERENCE_CARDS
    other_indices = [i for i in range(4) if i != correct_ref_idx]
    rng.shuffle(other_indices)

    target = {}
    dim_order = [active_rule] + [d for d in RULES if d != active_rule]

    for i, dim in enumerate(dim_order):
        if dim == active_rule:
            target[dim] = refs[correct_ref_idx][dim]
        else:
            pick_idx = other_indices[i - 1] if i - 1 < len(other_indices) else other_indices[0]
            target[dim] = refs[pick_idx][dim]

    return target


def _make_trial(rule: str, rng: random.Random) -> dict:
    """Generate one trial under a given rule."""
    correct_ref_idx = rng.randint(0, 3)
    target = _make_target(rule, correct_ref_idx, rng)
    return {
        "target": target,
        "active_rule": rule,
        "correct_answer": correct_ref_idx + 1,
    }


def generate_wcst_blocks(seed: int = 42):
    """
    Generate WCST blocks for batch-prompt evaluation.
    
    Block types:
    1. Learning block: establish a rule from scratch (no prior history)
    2. Shift blocks: show old rule → shift signal → test new rule inference
    3. Ambiguous shift: minimal signal, harder to infer new rule
    
    For shift blocks, the history structure is:
    - Phase A: 5 trials correct under old rule (model sees: "sorted by X → Correct")
    - Phase B: 2-3 trials where someone sorts by old rule → "Incorrect" 
    - Phase C: 2-3 trials where someone sorts by new rule → "Correct"
    - Test: 5-6 trials model must sort (new rule is active)
    
    This gives the model the SAME information a human gets in real WCST:
    the old rule stops working, and they must figure out the new one from feedback.
    """
    rng = random.Random(seed)
    
    rule_transitions = [
        ("color", "shape"),
        ("shape", "number"),
        ("number", "color"),
        ("color", "number"),   # non-adjacent shift
        ("number", "shape"),   # non-adjacent shift
    ]
    
    blocks = []
    
    # Block 1: Pure learning — infer rule from examples (easy warmup)
    init_rule = "color"
    history_trials = []
    for _ in range(6):
        t = _make_trial(init_rule, rng)
        history_trials.append({
            **t,
            "response": t["correct_answer"],  # correct response shown
            "feedback": "Correct",
        })
    test_trials = []
    for _ in range(5):
        t = _make_trial(init_rule, rng)
        test_trials.append({**t, "is_post_shift": False, "prev_rule": None})
    
    blocks.append({
        "block_id": 1,
        "description": "Initial rule learning (color)",
        "old_rule": None,
        "new_rule": init_rule,
        "history": history_trials,
        "test_trials": test_trials,
    })
    
    # Blocks 2-6: Shift blocks with varying difficulty
    for i, (old_rule, new_rule) in enumerate(rule_transitions):
        history = []
        
        # Phase A: 5 correct under old rule
        for _ in range(5):
            t = _make_trial(old_rule, rng)
            history.append({
                **t,
                "response": t["correct_answer"],
                "feedback": "Correct",
            })
        
        # Phase B: 2-3 trials where old-rule response → Incorrect
        n_incorrect = 2 if i < 2 else 3  # harder blocks show more signal
        for _ in range(n_incorrect):
            t = _make_trial(new_rule, rng)  # trial under new rule
            old_rule_answer = _correct_ref(t["target"], old_rule)
            history.append({
                **t,
                "response": old_rule_answer,  # someone tried old rule
                "feedback": "Incorrect",
            })
        
        # Phase C: 2-3 trials where new-rule response → Correct
        # More signal for easy blocks, less for hard blocks
        n_correct_hints = 3 if i < 2 else 2 if i < 4 else 1
        for _ in range(n_correct_hints):
            t = _make_trial(new_rule, rng)
            history.append({
                **t,
                "response": t["correct_answer"],
                "feedback": "Correct",
            })
        
        # Test trials: model must sort under new rule
        n_test = 6
        test_trials = []
        for _ in range(n_test):
            t = _make_trial(new_rule, rng)
            test_trials.append({
                **t,
                "is_post_shift": True,
                "prev_rule": old_rule,
            })
        
        blocks.append({
            "block_id": i + 2,
            "description": f"Rule shift: {old_rule} → {new_rule} (signal: {n_incorrect}I/{n_correct_hints}C)",
            "old_rule": old_rule,
            "new_rule": new_rule,
            "history": history,
            "test_trials": test_trials,
        })
    
    total_test = sum(len(b["test_trials"]) for b in blocks)
    
    return {
        "reference_cards": REFERENCE_CARDS,
        "blocks": blocks,
        "total_test_trials": total_test,
    }


# Also keep backward-compat exports
WCST_BLOCKS = generate_wcst_blocks(seed=42)
# Legacy export for any code that imports WCST_STIMULI
WCST_STIMULI = WCST_BLOCKS


if __name__ == "__main__":
    stim = WCST_BLOCKS
    print(f"Reference cards:")
    for i, r in enumerate(stim["reference_cards"], 1):
        print(f"  Card {i}: {card_str(r)}")
    print(f"\nTotal blocks: {len(stim['blocks'])}")
    print(f"Total test trials: {stim['total_test_trials']}")
    for b in stim["blocks"]:
        n_post = sum(1 for t in b["test_trials"] if t["is_post_shift"])
        print(f"\n  Block {b['block_id']}: {b['description']}")
        print(f"    History trials: {len(b['history'])}, Test trials: {len(b['test_trials'])} ({n_post} post-shift)")
        
        # Show what rule history implies
        if b["history"]:
            correct_in_hist = sum(1 for h in b["history"] if h["feedback"] == "Correct")
            incorrect_in_hist = sum(1 for h in b["history"] if h["feedback"] == "Incorrect")
            print(f"    History feedback: {correct_in_hist} Correct, {incorrect_in_hist} Incorrect")
