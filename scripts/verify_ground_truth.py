#!/usr/bin/env python3
"""
Ground truth verification for learning benchmarks.

For every test item in every system used by learning_transfer (v3)
and learning_interference (v4), independently recomputes expected output
and compares against stored test_item["output"].

Exits with non-zero status if any mismatch is found.
"""

import sys
import os
import random
import hashlib

# Add benchmarks/learning to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'benchmarks', 'learning'))

from data.rule_systems import (
    # Transfer v3
    TRANSFER_TRAIN_V3,
    _NEAR_FULL_V3,
    TRANSFER_NEAR_V3,
    TRANSFER_FAR_V3,
    TRANSFER_ZERO_SHOT_V3,
    # Interference v4
    INTERF_EASY_TARGET_V4,
    INTERF_EASY_DISTRACT_V4,
    INTERF_MED_TARGET_V4,
    INTERF_MED_DISTRACT_V4,
    INTERF_HARD_TARGET_V4,
    INTERF_HARD_DIST1_V4,
    INTERF_HARD_DIST2_V4,
    INTERF_HARD_DIST3_V4,
    INTERF_HARD_FILLER_V4,
    INTERF_EXT_TARGET_V4,
    INTERF_EXT_DIST1_V4,
    INTERF_EXT_DIST2_V4,
    INTERF_EXT_DIST3_V4,
    generate_symbol_system,
    generate_number_system,
    generate_stateful_system,
    _make_rng,
)


def _verify_symbol_system(system, seed, difficulty):
    """Recompute outputs for a symbol system and verify against stored items."""
    # Rebuild the apply function from seed
    rng = _make_rng(seed)
    shapes = ["△", "○", "□", "◇", "★", "⬡", "⬟", "▽"]

    if difficulty == 1:
        src = rng.sample(shapes[:4], 3)
        dst = rng.sample(shapes[4:], 3) + [rng.choice(shapes[4:])]
        mapping = dict(zip(src, dst[:3]))

        def apply_rules(seq):
            return [mapping.get(s, s) for s in seq]

    elif difficulty == 2:
        src = rng.sample(shapes[:5], 4)
        dst = rng.sample(shapes[4:], 3) + [rng.choice(shapes)]
        mapping = dict(zip(src[:3], dst[:3]))
        pair_rule = (src[0], src[1], dst[3])

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
        src = rng.sample(shapes[:6], 5)
        dst = rng.sample(shapes, 5)
        mapping1 = {src[0]: dst[0], src[1]: dst[1]}
        mapping2 = {dst[0]: dst[2]}
        cond = src[2]
        extra_map = {src[3]: dst[3]}

        def apply_rules(seq):
            result = [mapping1.get(s, s) for s in seq]
            result = [mapping2.get(s, s) for s in result]
            if cond in seq:
                result = [extra_map.get(s, s) for s in result]
            return result

    mismatches = []
    for item in system.test_items:
        seq = item["input"].split()
        expected_seq = apply_rules(seq)
        expected = " ".join(expected_seq)
        stored = item["output"]
        if expected != stored:
            mismatches.append({
                "system": system.name, "input": item["input"],
                "stored": stored, "recomputed": expected
            })
    return mismatches


def _verify_number_system(system, seed, difficulty):
    """Recompute outputs for a number system and verify against stored items."""
    rng = _make_rng(seed)
    op_names = ["grok", "flim", "zorp", "quex", "blix"]
    ops = rng.sample(op_names, 3)

    if difficulty == 1:
        a_op, b_op = ops[0], ops[1]
        a_fn = lambda x, y: x + y + 1
        b_fn = lambda x, y: abs(x - y)
        op_map = {a_op: a_fn, b_op: b_fn}
    elif difficulty == 2:
        a_op, b_op, c_op = ops[0], ops[1], ops[2]
        a_fn = lambda x, y: x * 2 + y
        b_fn = lambda x, y: (x + y) % 10
        c_fn = lambda x, y: max(x, y) - min(x, y) + 1
        op_map = {a_op: a_fn, b_op: b_fn, c_op: c_fn}
    else:
        a_op, b_op = ops[0], ops[1]
        a_fn = lambda x, y: x + y + 1
        b_fn = lambda x, y: x * y
        op_map = {a_op: a_fn, b_op: b_fn}

    import re

    def eval_expr(expr):
        expr = expr.strip()
        # Try nested: op(op(x, y), z)
        nested = re.match(r'(\w+)\((\w+)\((\d+),\s*(\d+)\),\s*(\d+)\)', expr)
        if nested:
            outer_op, inner_op = nested.group(1), nested.group(2)
            x, y, z = int(nested.group(3)), int(nested.group(4)), int(nested.group(5))
            inner_result = op_map[inner_op](x, y)
            return op_map[outer_op](inner_result, z)
        # Simple: op(x, y)
        simple = re.match(r'(\w+)\((\d+),\s*(\d+)\)', expr)
        if simple:
            op_name, x, y = simple.group(1), int(simple.group(2)), int(simple.group(3))
            return op_map[op_name](x, y)
        return None

    mismatches = []
    for item in system.test_items:
        computed = eval_expr(item["input"])
        if computed is None:
            mismatches.append({
                "system": system.name, "input": item["input"],
                "stored": item["output"], "recomputed": "PARSE_FAILED"
            })
            continue
        if str(computed) != item["output"]:
            mismatches.append({
                "system": system.name, "input": item["input"],
                "stored": item["output"], "recomputed": str(computed)
            })
    return mismatches


def _verify_stateful_system(system, seed):
    """Recompute outputs for a stateful system and verify against stored items."""
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

    mismatches = []
    for item in system.test_items:
        seq = item["input"].split()
        expected = apply_rules(seq)
        if expected != item["output"]:
            mismatches.append({
                "system": system.name, "input": item["input"],
                "stored": item["output"], "recomputed": expected
            })
    return mismatches


def main():
    all_mismatches = []

    # ── Transfer v3 systems ──────────────────────────────────────────

    checks = [
        ("TRANSFER_TRAIN_V3", TRANSFER_TRAIN_V3, "symbol", "v3_transfer_train", 2),
        ("_NEAR_FULL_V3 (pre-incomplete)", _NEAR_FULL_V3, "symbol", "v3_transfer_near", 2),
        # TRANSFER_NEAR_V3 has same test_items as _NEAR_FULL_V3, rules trimmed only
        ("TRANSFER_NEAR_V3 (incomplete)", TRANSFER_NEAR_V3, "symbol", "v3_transfer_near", 2),
        ("TRANSFER_FAR_V3", TRANSFER_FAR_V3, "number", "v3_transfer_far", 2),
        ("TRANSFER_ZERO_SHOT_V3", TRANSFER_ZERO_SHOT_V3, "stateful", "v3_transfer_zeroshot", 3),
    ]

    # ── Interference v4 systems ──────────────────────────────────────
    interference_checks = [
        ("INTERF_EASY_TARGET_V4", INTERF_EASY_TARGET_V4, "symbol", "v4_easy_target", 1),
        ("INTERF_EASY_DISTRACT_V4", INTERF_EASY_DISTRACT_V4, "symbol", "v4_easy_distract", 1),
        ("INTERF_MED_TARGET_V4", INTERF_MED_TARGET_V4, "symbol", "v4_med_target", 2),
        ("INTERF_MED_DISTRACT_V4", INTERF_MED_DISTRACT_V4, "symbol", "v4_med_distract", 2),
        ("INTERF_HARD_TARGET_V4", INTERF_HARD_TARGET_V4, "symbol", "v4_hard_target", 3),
        ("INTERF_HARD_DIST1_V4", INTERF_HARD_DIST1_V4, "symbol", "v4_hard_dist1", 3),
        ("INTERF_HARD_DIST2_V4", INTERF_HARD_DIST2_V4, "symbol", "v4_hard_dist2", 3),
        ("INTERF_HARD_DIST3_V4", INTERF_HARD_DIST3_V4, "symbol", "v4_hard_dist3", 3),
        ("INTERF_HARD_FILLER_V4", INTERF_HARD_FILLER_V4, "symbol", "v4_hard_filler", 2),
        ("INTERF_EXT_TARGET_V4", INTERF_EXT_TARGET_V4, "symbol", "v4_ext_target", 3),
        ("INTERF_EXT_DIST1_V4", INTERF_EXT_DIST1_V4, "symbol", "v4_ext_dist1", 3),
        ("INTERF_EXT_DIST2_V4", INTERF_EXT_DIST2_V4, "symbol", "v4_ext_dist2", 3),
        ("INTERF_EXT_DIST3_V4", INTERF_EXT_DIST3_V4, "symbol", "v4_ext_dist3", 3),
    ]

    all_checks = checks + interference_checks

    print("Ground Truth Verification")
    print("=" * 60)

    for label, system, domain, seed, difficulty in all_checks:
        if domain == "symbol":
            mismatches = _verify_symbol_system(system, seed, difficulty)
        elif domain == "number":
            mismatches = _verify_number_system(system, seed, difficulty)
        elif domain == "stateful":
            mismatches = _verify_stateful_system(system, seed)
        else:
            print(f"  [SKIP] {label}: unknown domain '{domain}'")
            continue

        if mismatches:
            print(f"  [FAIL] {label}: {len(mismatches)} mismatch(es)")
            for m in mismatches:
                print(f"         input={m['input']!r} stored={m['stored']!r} recomputed={m['recomputed']!r}")
            all_mismatches.extend(mismatches)
        else:
            n_items = len(system.test_items)
            print(f"  [OK]   {label}: {n_items} test items verified")

    print("=" * 60)
    if all_mismatches:
        print(f"RESULT: {len(all_mismatches)} MISMATCH(ES) FOUND — answer keys are INCORRECT")
        sys.exit(1)
    else:
        print("RESULT: All answer keys verified correct ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
