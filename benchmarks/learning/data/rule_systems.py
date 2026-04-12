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


# ── Abstract rule systems for far-transfer ──────────────────────────
def generate_abstract_system(seed: str, base_system: RuleSystem) -> RuleSystem:
    """Generate a far-transfer system: same abstract rules, different surface features."""
    rng = _make_rng(seed)
    if base_system.domain == "symbol":
        animals = ["cat", "dog", "fish", "bird", "frog", "ant", "bee", "owl"]
        shapes_used = sorted({s for rule in base_system.rules for s in ["\u25b3","\u25cb","\u25a1","\u25c7","\u2605","\u2b21","\u2b1f","\u25bd"] if s in rule})
        animal_pool = rng.sample(animals, min(len(shapes_used)+2, len(animals)))
        shape_map = {s: animal_pool[i % len(animal_pool)] for i, s in enumerate(shapes_used)}
        def remap(text):
            for s, a in shape_map.items():
                text = text.replace(s, a)
            return text
        return RuleSystem(
            name=f"AbstractTransfer-{seed}",
            description="Apply transformation rules to animal-name sequences (same structure, different surface)",
            rules=[remap(r) for r in base_system.rules],
            examples=[{"input": remap(e["input"]), "output": remap(e["output"])} for e in base_system.examples],
            test_items=[{"input": remap(t["input"]), "output": remap(t["output"])} for t in base_system.test_items],
            difficulty=base_system.difficulty + 1,
            n_rules=len(base_system.rules),
            domain="abstract",
        )
    else:
        new_rules = [r.replace("add","combine").replace("multiply","merge").replace("double","twin") for r in base_system.rules]
        return RuleSystem(
            name=f"AbstractTransfer-{seed}",
            description="Evaluate expressions using renamed operators (same math, different names)",
            rules=new_rules,
            examples=base_system.examples,
            test_items=base_system.test_items,
            difficulty=base_system.difficulty + 1,
            n_rules=len(new_rules),
            domain="abstract",
        )


FAR_TRANSFER_PAIRS = [
    {"base": generate_symbol_system("ft_sym_1", difficulty=2), "transfer": None},
    {"base": generate_symbol_system("ft_sym_2", difficulty=3), "transfer": None},
    {"base": generate_number_system("ft_num_1", difficulty=2), "transfer": None},
    {"base": generate_number_system("ft_num_2", difficulty=3), "transfer": None},
]
for pair in FAR_TRANSFER_PAIRS:
    pair["transfer"] = generate_abstract_system(f"xfer_{pair['base'].name}", pair["base"])

# Hard condition systems — reduced training window (only 3 examples)
HARD_LEARNING_SYSTEMS = [
    generate_symbol_system("lc_hard_sym_steep", difficulty=3),
    generate_number_system("lc_hard_num_steep", difficulty=3),
    generate_symbol_system("lc_hard_abstract_1", difficulty=3),
    generate_number_system("lc_hard_abstract_2", difficulty=3),
]
