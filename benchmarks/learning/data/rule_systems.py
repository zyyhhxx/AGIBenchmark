"""
Novel Rule System Generator for Learning Benchmarks.

Generates procedural rule systems that cannot be in training data.
Each system defines a mapping from inputs to outputs via a chain
of deterministic rules. Difficulty is controlled by:
- Number of rules
- Number of input features
- Rule interaction complexity (independent vs. chained)

Systems are seeded for reproducibility across runs.
"""

import random
import hashlib
from dataclasses import dataclass, field


@dataclass
class RuleSystem:
    """A generated rule system with examples."""
    name: str
    description: str
    rules: list[str]
    examples: list[dict]  # {"input": str, "output": str}
    test_items: list[dict]  # {"input": str, "output": str}
    difficulty: int  # 1-3
    n_rules: int
    domain: str  # "symbol", "language", "number"


def _make_rng(seed: str) -> random.Random:
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    return random.Random(h)


def generate_symbol_system(seed: str = "sym_default", difficulty: int = 1) -> RuleSystem:
    """
    Generate a symbol transformation rule system.

    Input: sequence of symbols (e.g., "△ ○ □")
    Rules: transformations (e.g., "△ followed by ○ becomes ★")
    Output: transformed sequence
    """
    rng = _make_rng(seed)

    shapes = ["△", "○", "□", "◇", "★", "⬡", "⬟", "▽"]
    colors = ["red", "blue", "green", "yellow"]

    if difficulty == 1:
        # Simple 1-to-1 substitution
        src = rng.sample(shapes[:4], 3)
        dst = rng.sample(shapes[4:], 3) + [rng.choice(shapes[4:])]
        mapping = dict(zip(src, dst[:3]))
        rules = [f"Replace {s} with {d}" for s, d in mapping.items()]
        rules.append("All other symbols stay the same")

        def apply_rules(seq):
            return [mapping.get(s, s) for s in seq]

    elif difficulty == 2:
        # Context-dependent: pairs matter
        src = rng.sample(shapes[:5], 4)
        dst = rng.sample(shapes[4:], 3) + [rng.choice(shapes)]
        mapping = dict(zip(src[:3], dst[:3]))
        pair_rule = (src[0], src[1], dst[3])  # "X followed by Y becomes Z"
        rules = [f"Replace {s} with {d}" for s, d in mapping.items()]
        rules.append(f"EXCEPTION: {pair_rule[0]} followed by {pair_rule[1]} → both become {pair_rule[2]}")
        rules.append("All other symbols stay the same")

        def apply_rules(seq):
            result = []
            i = 0
            while i < len(seq):
                if i + 1 < len(seq) and seq[i] == pair_rule[0] and seq[i + 1] == pair_rule[1]:
                    result.extend([pair_rule[2], pair_rule[2]])
                    i += 2
                else:
                    result.append(mapping.get(seq[i], seq[i]))
                    i += 1
            return result

    else:  # difficulty == 3
        # Multi-pass with conditional rules
        src = rng.sample(shapes[:6], 5)
        dst = rng.sample(shapes, 5)
        mapping1 = {src[0]: dst[0], src[1]: dst[1]}
        mapping2 = {dst[0]: dst[2]}  # Chain: src[0] → dst[0] → dst[2]
        cond = src[2]  # If this symbol is present, apply extra rule
        extra_map = {src[3]: dst[3]}

        rules = [
            f"Pass 1: Replace {s} with {d}" for s, d in mapping1.items()
        ]
        rules.append(f"Pass 2: Replace {list(mapping2.keys())[0]} with {list(mapping2.values())[0]}")
        rules.append(f"IF the sequence contains {cond}: also replace {src[3]} with {dst[3]}")
        rules.append("All other symbols stay the same throughout")

        def apply_rules(seq):
            # Pass 1
            result = [mapping1.get(s, s) for s in seq]
            # Pass 2
            result = [mapping2.get(s, s) for s in result]
            # Conditional
            if cond in seq:  # Check original sequence
                result = [extra_map.get(s, s) for s in result]
            return result

    # Generate examples
    all_items = []
    for _ in range(25):
        length = rng.randint(3, 6)
        seq = [rng.choice(shapes[:5]) for _ in range(length)]
        output = apply_rules(seq)
        all_items.append({"input": " ".join(seq), "output": " ".join(output)})

    # Deduplicate by input
    seen = set()
    unique_items = []
    for item in all_items:
        if item["input"] not in seen:
            seen.add(item["input"])
            unique_items.append(item)

    rng.shuffle(unique_items)
    n_examples = min(15, len(unique_items) - 5)
    examples = unique_items[:n_examples]
    test_items = unique_items[n_examples:n_examples + 5]

    return RuleSystem(
        name=f"SymbolTransform-{seed}",
        description="Apply symbol transformation rules to input sequences",
        rules=rules,
        examples=examples,
        test_items=test_items,
        difficulty=difficulty,
        n_rules=len(rules),
        domain="symbol",
    )


def generate_number_system(seed: str = "num_default", difficulty: int = 1) -> RuleSystem:
    """
    Generate a novel number system / arithmetic.

    Input: expression in the invented system
    Rules: how operators work
    Output: numeric result
    """
    rng = _make_rng(seed)

    op_names = ["grok", "flim", "zorp", "quex", "blix"]
    ops = rng.sample(op_names, 3)

    if difficulty == 1:
        # Two operators: basic arithmetic with twist
        a_op, b_op = ops[0], ops[1]
        a_fn = lambda x, y: x + y + 1  # "grok" = add and increment
        b_fn = lambda x, y: abs(x - y)  # "flim" = absolute difference
        rules = [
            f"'{a_op}(x, y)' means: add x and y, then add 1",
            f"'{b_op}(x, y)' means: absolute difference of x and y",
        ]
        op_map = {a_op: a_fn, b_op: b_fn}

    elif difficulty == 2:
        a_op, b_op, c_op = ops[0], ops[1], ops[2]
        a_fn = lambda x, y: x * 2 + y
        b_fn = lambda x, y: (x + y) % 10
        c_fn = lambda x, y: max(x, y) - min(x, y) + 1
        rules = [
            f"'{a_op}(x, y)' means: double x, then add y",
            f"'{b_op}(x, y)' means: add x and y, take the last digit (mod 10)",
            f"'{c_op}(x, y)' means: difference of larger and smaller, plus 1",
        ]
        op_map = {a_op: a_fn, b_op: b_fn, c_op: c_fn}

    else:  # difficulty == 3
        a_op, b_op, c_op = ops[0], ops[1], ops[2]
        # Nested operations
        a_fn = lambda x, y: x + y + 1
        b_fn = lambda x, y: x * y
        rules = [
            f"'{a_op}(x, y)' means: add x and y, then add 1",
            f"'{b_op}(x, y)' means: multiply x and y",
            f"Operations can be nested: '{a_op}({b_op}(x, y), z)' means: first compute {b_op}(x, y), then use the result as the first argument to {a_op}",
        ]
        op_map = {a_op: a_fn, b_op: b_fn}

    # Generate examples
    all_items = []
    for _ in range(20):
        if difficulty <= 2:
            op_name = rng.choice(list(op_map.keys()))
            x = rng.randint(1, 9)
            y = rng.randint(1, 9)
            result = op_map[op_name](x, y)
            expr = f"{op_name}({x}, {y})"
        else:
            # Allow nesting
            if rng.random() < 0.5:
                op_name = rng.choice(list(op_map.keys()))
                x = rng.randint(1, 9)
                y = rng.randint(1, 9)
                result = op_map[op_name](x, y)
                expr = f"{op_name}({x}, {y})"
            else:
                inner_op = rng.choice(list(op_map.keys()))
                outer_op = rng.choice(list(op_map.keys()))
                x, y, z = rng.randint(1, 5), rng.randint(1, 5), rng.randint(1, 5)
                inner_result = op_map[inner_op](x, y)
                result = op_map[outer_op](inner_result, z)
                expr = f"{outer_op}({inner_op}({x}, {y}), {z})"

        all_items.append({"input": expr, "output": str(result)})

    # Deduplicate
    seen = set()
    unique_items = []
    for item in all_items:
        if item["input"] not in seen:
            seen.add(item["input"])
            unique_items.append(item)

    rng.shuffle(unique_items)
    n_ex = min(12, len(unique_items) - 5)
    examples = unique_items[:n_ex]
    test_items = unique_items[n_ex:n_ex + 5]

    return RuleSystem(
        name=f"NumberSystem-{seed}",
        description="Evaluate expressions using novel arithmetic operators",
        rules=rules,
        examples=examples,
        test_items=test_items,
        difficulty=difficulty,
        n_rules=len(rules),
        domain="number",
    )


# Pre-generated systems for the benchmark
LEARNING_CURVE_SYSTEMS = [
    generate_symbol_system("lc_sym_easy", difficulty=1),
    generate_symbol_system("lc_sym_med", difficulty=2),
    generate_symbol_system("lc_sym_hard", difficulty=3),
    generate_number_system("lc_num_easy", difficulty=1),
    generate_number_system("lc_num_med", difficulty=2),
    generate_number_system("lc_num_hard", difficulty=3),
    generate_symbol_system("lc_sym_extreme1", difficulty=3),
    generate_number_system("lc_num_extreme2", difficulty=3),
]

# Systems for transfer testing
TRANSFER_BASE_SYSTEM = generate_symbol_system("transfer_base", difficulty=2)
TRANSFER_NEAR_SYSTEM = generate_symbol_system("transfer_near", difficulty=2)
TRANSFER_FAR_SYSTEM = generate_number_system("transfer_far", difficulty=2)

# Systems for interference testing
INTERFERENCE_A = generate_symbol_system("interf_a", difficulty=2)
INTERFERENCE_B = generate_symbol_system("interf_b_similar", difficulty=2)


# ── Positional rule system (rules depend on position) ───────────────
def generate_positional_system(seed: str = "pos_default", difficulty: int = 3) -> RuleSystem:
    """
    Generate a positional rule system where transformations depend on
    element position in the sequence, not just identity.
    """
    rng = _make_rng(seed)
    shapes = ["△", "○", "□", "◇", "★", "⬡"]

    # Rules: position-dependent transformations
    pos_rules = [
        (0, shapes[0], shapes[4]),  # At position 0: △ → ★
        (1, shapes[1], shapes[5]),  # At position 1: ○ → ⬡
    ]
    swap_pair = (shapes[2], shapes[3])  # □ ↔ ◇ at even positions

    rules = [
        f"At position 0 (first element): replace {shapes[0]} with {shapes[4]}",
        f"At position 1 (second element): replace {shapes[1]} with {shapes[5]}",
        f"At even positions (0, 2, 4, ...): swap {shapes[2]} and {shapes[3]}",
        f"At odd positions (1, 3, 5, ...): duplicate the symbol (e.g., △ → △ △)",
        "Position-specific rules override the odd-position duplication rule",
    ]

    def apply_rules(seq):
        result = []
        for i, s in enumerate(seq):
            applied = False
            for pos, src, dst in pos_rules:
                if i == pos and s == src:
                    result.append(dst)
                    applied = True
                    break
            if not applied:
                if i % 2 == 0:  # even position
                    if s == swap_pair[0]:
                        result.append(swap_pair[1])
                    elif s == swap_pair[1]:
                        result.append(swap_pair[0])
                    else:
                        result.append(s)
                else:  # odd position - duplicate
                    for pos2, src2, _ in pos_rules:
                        if i == pos2 and s == src2:
                            applied = True
                            break
                    if not applied:
                        result.extend([s, s])
                    else:
                        result.append(s)
        return result

    all_items = []
    for _ in range(25):
        length = rng.randint(3, 5)
        seq = [rng.choice(shapes[:4]) for _ in range(length)]
        output = apply_rules(seq)
        all_items.append({"input": " ".join(seq), "output": " ".join(output)})

    seen = set()
    unique = []
    for item in all_items:
        if item["input"] not in seen:
            seen.add(item["input"])
            unique.append(item)

    rng.shuffle(unique)
    n_ex = min(12, len(unique) - 5)
    return RuleSystem(
        name=f"PositionalTransform-{seed}",
        description="Apply position-dependent transformation rules to symbol sequences",
        rules=rules,
        examples=unique[:n_ex],
        test_items=unique[n_ex:n_ex + 5],
        difficulty=difficulty,
        n_rules=len(rules),
        domain="positional",
    )


# ── Stateful accumulator system ─────────────────────────────────────
def generate_stateful_system(seed: str = "state_default", difficulty: int = 3) -> RuleSystem:
    """
    Generate a stateful system where output depends on running state
    accumulated through the sequence.
    """
    rng = _make_rng(seed)
    tokens = ["A", "B", "C", "D"]

    # State machine: counter starts at 0, each token modifies it
    token_effects = {
        "A": +2,
        "B": -1,
        "C": lambda s: s * 2 if s > 0 else 1,  # double if positive, else set to 1
        "D": 0,  # reset to 0
    }

    rules = [
        "Start with counter = 0",
        "A: add 2 to counter",
        "B: subtract 1 from counter",
        "C: if counter > 0, double it; otherwise set counter to 1",
        "D: reset counter to 0",
        "Output: the final counter value after processing all tokens left to right",
    ]

    def apply_rules(seq):
        counter = 0
        for t in seq:
            if t == "A":
                counter += 2
            elif t == "B":
                counter -= 1
            elif t == "C":
                counter = counter * 2 if counter > 0 else 1
            elif t == "D":
                counter = 0
        return str(counter)

    all_items = []
    for _ in range(30):
        length = rng.randint(3, 7)
        seq = [rng.choice(tokens) for _ in range(length)]
        output = apply_rules(seq)
        all_items.append({"input": " ".join(seq), "output": output})

    seen = set()
    unique = []
    for item in all_items:
        if item["input"] not in seen:
            seen.add(item["input"])
            unique.append(item)

    rng.shuffle(unique)
    n_ex = min(12, len(unique) - 5)
    return RuleSystem(
        name=f"StatefulAccumulator-{seed}",
        description="Process token sequences through a stateful counter to compute final value",
        rules=rules,
        examples=unique[:n_ex],
        test_items=unique[n_ex:n_ex + 5],
        difficulty=difficulty,
        n_rules=len(rules),
        domain="stateful",
    )


# ── Far-transfer: genuine structural transfer ───────────────────────
def generate_structural_transfer(seed: str, base_system: RuleSystem) -> RuleSystem:
    """
    Generate a far-transfer system with genuinely different representation.

    For symbol systems: encode symbols as coordinate pairs, requiring the
    model to map coordinates → symbols → apply rules → symbols → coordinates.

    For number systems: encode as word-problem format with no operator syntax,
    requiring the model to identify which operator applies from context.
    """
    rng = _make_rng(seed)

    if base_system.domain == "symbol":
        # Map each shape to a coordinate pair
        shapes_all = ["△", "○", "□", "◇", "★", "⬡", "⬟", "▽"]
        coords = [(i, j) for i in range(1, 4) for j in range(1, 4)]  # 9 coords
        rng.shuffle(coords)
        shape_to_coord = {}
        coord_to_shape = {}
        for i, s in enumerate(shapes_all[:len(coords)]):
            c = coords[i]
            shape_to_coord[s] = c
            coord_to_shape[c] = s

        def encode_seq(text):
            tokens = text.split()
            encoded = []
            for t in tokens:
                if t in shape_to_coord:
                    c = shape_to_coord[t]
                    encoded.append(f"({c[0]},{c[1]})")
                else:
                    encoded.append(t)
            return " ".join(encoded)

        # The transfer system has NO rules listed — just the coordinate mapping
        # and 2 worked examples. Model must figure out the structure.
        coord_legend = [f"({c[0]},{c[1]}) = {s}" for s, c in shape_to_coord.items()
                        if s in " ".join(e["input"] for e in base_system.examples + base_system.test_items)]

        return RuleSystem(
            name=f"CoordinateTransfer-{seed}",
            description=(
                "Same transformation rules as the base system, but symbols are encoded "
                "as coordinate pairs. Decode coordinates, apply rules, re-encode output."
            ),
            rules=[f"Coordinate mapping: {', '.join(coord_legend[:6])}",
                   "Apply the SAME transformation rules from the base system",
                   "Output the result as coordinate pairs"],
            examples=[{"input": encode_seq(e["input"]), "output": encode_seq(e["output"])}
                      for e in base_system.examples[:2]],  # Only 2 examples!
            test_items=[{"input": encode_seq(t["input"]), "output": encode_seq(t["output"])}
                        for t in base_system.test_items],
            difficulty=base_system.difficulty + 1,
            n_rules=3,
            domain="coordinate_transfer",
        )
    else:
        # Number system → word problem format
        # Extract operators from base system
        contexts = [
            "In a factory, workers {op} {x} units from line A with {y} units from line B. How many total units?",
            "A recipe calls for {op}-processing {x} grams of ingredient X and {y} grams of ingredient Y. What is the result?",
            "In the game, player scores are combined by {op}: first score is {x}, second score is {y}. Final score?",
        ]
        rng.shuffle(contexts)

        # Use base examples but reformat as word problems
        transfer_examples = []
        transfer_tests = []

        for item in base_system.examples[:2]:
            transfer_examples.append({
                "input": f"Word problem: {item['input']} (evaluate using the learned rules)",
                "output": item["output"],
            })

        for item in base_system.test_items:
            transfer_tests.append({
                "input": f"Word problem: {item['input']} (evaluate using the learned rules)",
                "output": item["output"],
            })

        return RuleSystem(
            name=f"ContextualTransfer-{seed}",
            description="Same arithmetic rules, but expressions are embedded in word-problem context",
            rules=["Apply the SAME operator rules you learned from the base system",
                   "Extract the expression from the word problem and evaluate"],
            examples=transfer_examples,
            test_items=transfer_tests,
            difficulty=base_system.difficulty + 1,
            n_rules=2,
            domain="contextual_transfer",
        )


FAR_TRANSFER_PAIRS = [
    {"base": generate_symbol_system("ft_sym_1", difficulty=2), "transfer": None},
    {"base": generate_symbol_system("ft_sym_2", difficulty=3), "transfer": None},
    {"base": generate_number_system("ft_num_1", difficulty=2), "transfer": None},
    {"base": generate_number_system("ft_num_2", difficulty=3), "transfer": None},
]
for pair in FAR_TRANSFER_PAIRS:
    pair["transfer"] = generate_structural_transfer(f"xfer_{pair['base'].name}", pair["base"])

# Hard condition systems — reduced training window (only 3 examples)
# Includes novel rule types: positional and stateful systems
HARD_LEARNING_SYSTEMS = [
    generate_symbol_system("lc_hard_sym_steep", difficulty=3),
    generate_number_system("lc_hard_num_steep", difficulty=3),
    generate_positional_system("lc_hard_positional", difficulty=3),
    generate_stateful_system("lc_hard_stateful", difficulty=3),
]
