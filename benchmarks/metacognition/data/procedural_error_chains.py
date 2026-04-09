"""
Procedurally generated error detection chains for contamination resistance.

These reasoning chains use randomly generated numbers and novel problem setups
so they cannot appear in any training corpus. Each chain has a known error
status and error location for objective scoring.
"""

import random


def _generate_procedural_chains(seed=42):
    """Generate ~16 additional reasoning chains with procedural content."""
    rng = random.Random(seed)
    chains = []
    chain_id = 100  # Start from P100 to avoid conflicts

    # ─── Correct chains with novel numbers ───────────────────────────
    for i in range(4):
        a = rng.randint(11, 99)
        b = rng.randint(11, 99)
        product = a * b
        chain_id += 1
        chains.append({
            "id": f"P{chain_id}",
            "problem": f"What is {a} × {b}?",
            "steps": [
                f"Step 1: Break {a} into {a // 10 * 10} + {a % 10}",
                f"Step 2: {a // 10 * 10} × {b} = {(a // 10 * 10) * b}",
                f"Step 3: {a % 10} × {b} = {(a % 10) * b}",
                f"Step 4: {(a // 10 * 10) * b} + {(a % 10) * b} = {product}",
            ],
            "final_answer": str(product),
            "has_error": False,
            "error_step": None,
            "error_description": None,
            "difficulty": 2,
        })

    # ─── Chains with arithmetic errors ───────────────────────────────
    for i in range(4):
        a = rng.randint(12, 50)
        b = rng.randint(12, 50)
        correct_product = a * b
        # Inject an error in the partial product
        wrong_partial = (a // 10 * 10) * b + rng.choice([-10, 10, -1, 1])
        wrong_total = wrong_partial + (a % 10) * b
        chain_id += 1
        chains.append({
            "id": f"P{chain_id}",
            "problem": f"What is {a} × {b}?",
            "steps": [
                f"Step 1: Break {a} into {a // 10 * 10} + {a % 10}",
                f"Step 2: {a // 10 * 10} × {b} = {wrong_partial}",
                f"Step 3: {a % 10} × {b} = {(a % 10) * b}",
                f"Step 4: {wrong_partial} + {(a % 10) * b} = {wrong_total}",
            ],
            "final_answer": str(wrong_total),
            "has_error": True,
            "error_step": 2,
            "error_description": f"Arithmetic error: {a // 10 * 10} × {b} = {(a // 10 * 10) * b}, not {wrong_partial}",
            "difficulty": 2,
        })

    # ─── Correct percentage chains ───────────────────────────────────
    for i in range(2):
        base = rng.randint(100, 900)
        pct = rng.choice([15, 20, 25, 30])
        discount = base * pct / 100
        final = base - discount
        chain_id += 1
        chains.append({
            "id": f"P{chain_id}",
            "problem": f"An item costs ${base}. After a {pct}% discount, what is the price?",
            "steps": [
                f"Step 1: Calculate discount: {pct}% of ${base} = ${base} × {pct}/100 = ${discount:.2f}",
                f"Step 2: Subtract discount: ${base} - ${discount:.2f} = ${final:.2f}",
            ],
            "final_answer": f"${final:.2f}",
            "has_error": False,
            "error_step": None,
            "error_description": None,
            "difficulty": 1,
        })

    # ─── Percentage chains with errors ───────────────────────────────
    for i in range(2):
        base = rng.randint(100, 900)
        pct = rng.choice([15, 20, 25, 30])
        # Error: add instead of subtract
        discount = base * pct / 100
        wrong_final = base + discount  # should be base - discount
        chain_id += 1
        chains.append({
            "id": f"P{chain_id}",
            "problem": f"An item costs ${base}. After a {pct}% discount, what is the price?",
            "steps": [
                f"Step 1: Calculate discount: {pct}% of ${base} = ${base} × {pct}/100 = ${discount:.2f}",
                f"Step 2: Apply discount: ${base} + ${discount:.2f} = ${wrong_final:.2f}",
            ],
            "final_answer": f"${wrong_final:.2f}",
            "has_error": True,
            "error_step": 2,
            "error_description": f"Should subtract the discount, not add it. Correct: ${base} - ${discount:.2f} = ${base - discount:.2f}",
            "difficulty": 1,
        })

    # ─── Correct series sum chains ───────────────────────────────────
    for i in range(2):
        a1 = rng.randint(2, 10)
        d = rng.randint(2, 5)
        n = rng.randint(6, 10)
        an = a1 + (n - 1) * d
        s = n * (a1 + an) // 2
        chain_id += 1
        chains.append({
            "id": f"P{chain_id}",
            "problem": f"Find the sum of the first {n} terms of the arithmetic sequence: {a1}, {a1+d}, {a1+2*d}, ...",
            "steps": [
                f"Step 1: Identify: a₁ = {a1}, d = {d}, n = {n}",
                f"Step 2: Last term: aₙ = {a1} + ({n}-1)×{d} = {a1} + {(n-1)*d} = {an}",
                f"Step 3: Sum = n(a₁ + aₙ)/2 = {n}×({a1} + {an})/2 = {n}×{a1+an}/2 = {s}",
            ],
            "final_answer": str(s),
            "has_error": False,
            "error_step": None,
            "error_description": None,
            "difficulty": 2,
        })

    # ─── Series sum with formula error ───────────────────────────────
    for i in range(2):
        a1 = rng.randint(2, 10)
        d = rng.randint(2, 5)
        n = rng.randint(6, 10)
        an = a1 + (n - 1) * d
        wrong_an = a1 + n * d  # Error: should be (n-1)*d
        wrong_s = n * (a1 + wrong_an) // 2
        chain_id += 1
        chains.append({
            "id": f"P{chain_id}",
            "problem": f"Find the sum of the first {n} terms: {a1}, {a1+d}, {a1+2*d}, ...",
            "steps": [
                f"Step 1: Identify: a₁ = {a1}, d = {d}, n = {n}",
                f"Step 2: Last term: aₙ = {a1} + {n}×{d} = {a1} + {n*d} = {wrong_an}",
                f"Step 3: Sum = n(a₁ + aₙ)/2 = {n}×({a1} + {wrong_an})/2 = {wrong_s}",
            ],
            "final_answer": str(wrong_s),
            "has_error": True,
            "error_step": 2,
            "error_description": f"Formula error: aₙ = a₁ + (n-1)d, not a₁ + nd. Should be {a1} + {(n-1)*d} = {an}",
            "difficulty": 2,
        })

    return chains


PROCEDURAL_REASONING_CHAINS = _generate_procedural_chains()
