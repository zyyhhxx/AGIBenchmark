"""
Procedurally generated calibration questions for contamination resistance.

These questions use randomly generated parameters so they cannot appear
in any training corpus. They span arithmetic, algebra, geometry, logic,
and unit conversion — domains where correctness is objectively verifiable.

Purpose: Replace/supplement the trivia-heavy CALIBRATION_QUESTIONS with
items that test calibration on genuinely novel content.

Difficulty tiers match the original dataset (1=easy, 2=medium, 3=hard).
"""

import random
import math


def _generate_procedural_calibration(seed=42):
    """Generate ~40 procedural calibration questions across domains."""
    rng = random.Random(seed)
    questions = []

    # ─── TIER 1: Easy (arithmetic, basic conversions) ───────────────
    for i in range(10):
        variant = i % 5
        if variant == 0:
            a, b = rng.randint(11, 99), rng.randint(11, 99)
            ans = a + b
            questions.append({
                "question": f"What is {a} + {b}?",
                "answer": str(ans),
                "domain": "arithmetic",
                "difficulty": 1,
                "accept_patterns": [str(ans)],
            })
        elif variant == 1:
            a = rng.randint(12, 50)
            b = rng.randint(2, 12)
            ans = a * b
            questions.append({
                "question": f"What is {a} × {b}?",
                "answer": str(ans),
                "domain": "arithmetic",
                "difficulty": 1,
                "accept_patterns": [str(ans)],
            })
        elif variant == 2:
            km = rng.choice([5, 10, 15, 20, 25, 42, 50, 100])
            m = km * 1000
            questions.append({
                "question": f"How many meters are in {km} kilometers?",
                "answer": str(m),
                "domain": "conversion",
                "difficulty": 1,
                "accept_patterns": [str(m)],
            })
        elif variant == 3:
            mins = rng.choice([120, 180, 240, 300, 360, 450, 600])
            hrs = mins // 60
            questions.append({
                "question": f"How many hours are in {mins} minutes?",
                "answer": str(hrs),
                "domain": "conversion",
                "difficulty": 1,
                "accept_patterns": [str(hrs)],
            })
        else:
            n = rng.randint(3, 12)
            ans = n * n
            questions.append({
                "question": f"What is {n} squared?",
                "answer": str(ans),
                "domain": "arithmetic",
                "difficulty": 1,
                "accept_patterns": [str(ans)],
            })

    # ─── TIER 2: Medium (multi-step, algebra, geometry) ─────────────
    for i in range(15):
        variant = i % 5
        if variant == 0:
            # Linear equation: ax + b = c
            a = rng.randint(2, 9)
            x_true = rng.randint(-10, 20)
            b = rng.randint(1, 30)
            c = a * x_true + b
            questions.append({
                "question": f"Solve for x: {a}x + {b} = {c}",
                "answer": str(x_true),
                "domain": "algebra",
                "difficulty": 2,
                "accept_patterns": [str(x_true)],
            })
        elif variant == 1:
            # Triangle area
            base = rng.randint(5, 30)
            height = rng.randint(4, 25)
            area = base * height / 2
            ans = str(int(area)) if area == int(area) else str(area)
            questions.append({
                "question": f"What is the area of a triangle with base {base} cm and height {height} cm?",
                "answer": ans,
                "domain": "geometry",
                "difficulty": 2,
                "accept_patterns": [ans],
                "numeric_tolerance": 0.01,
            })
        elif variant == 2:
            # Percentage
            base = rng.randint(50, 500)
            pct = rng.choice([10, 15, 20, 25, 30, 40, 50, 75])
            ans = base * pct / 100
            ans_str = str(int(ans)) if ans == int(ans) else str(ans)
            questions.append({
                "question": f"What is {pct}% of {base}?",
                "answer": ans_str,
                "domain": "arithmetic",
                "difficulty": 2,
                "accept_patterns": [ans_str],
                "numeric_tolerance": 0.01,
            })
        elif variant == 3:
            # Speed-distance-time
            speed = rng.choice([30, 40, 50, 60, 80, 100])
            time_hrs = rng.choice([1.5, 2, 2.5, 3, 4, 5])
            dist = speed * time_hrs
            ans = str(int(dist)) if dist == int(dist) else str(dist)
            questions.append({
                "question": f"A car travels at {speed} km/h for {time_hrs} hours. How far does it go (in km)?",
                "answer": ans,
                "domain": "physics",
                "difficulty": 2,
                "accept_patterns": [ans],
                "numeric_tolerance": 0.01,
            })
        else:
            # Modular arithmetic
            base = rng.randint(100, 999)
            mod = rng.choice([7, 11, 13, 17, 19, 23])
            ans = base % mod
            questions.append({
                "question": f"What is the remainder when {base} is divided by {mod}?",
                "answer": str(ans),
                "domain": "arithmetic",
                "difficulty": 2,
                "accept_patterns": [str(ans)],
            })

    # ─── TIER 3: Hard (multi-step reasoning, combinatorics, series) ─
    for i in range(15):
        variant = i % 5
        if variant == 0:
            # Sum of arithmetic series
            a1 = rng.randint(1, 10)
            d = rng.randint(2, 7)
            n = rng.randint(8, 15)
            an = a1 + (n - 1) * d
            s = n * (a1 + an) // 2
            questions.append({
                "question": f"What is the sum of the first {n} terms of the arithmetic sequence starting at {a1} with common difference {d}?",
                "answer": str(s),
                "domain": "math",
                "difficulty": 3,
                "accept_patterns": [str(s)],
            })
        elif variant == 1:
            # Combinations
            n = rng.randint(5, 10)
            r = rng.randint(2, min(4, n))
            ans = math.comb(n, r)
            questions.append({
                "question": f"How many ways can you choose {r} items from {n} distinct items (combinations)?",
                "answer": str(ans),
                "domain": "combinatorics",
                "difficulty": 3,
                "accept_patterns": [str(ans)],
            })
        elif variant == 2:
            # Quadratic roots (integer roots guaranteed)
            r1 = rng.randint(-8, 8)
            r2 = rng.randint(-8, 8)
            # x^2 - (r1+r2)x + r1*r2 = 0
            b = -(r1 + r2)
            c = r1 * r2
            b_str = f"+ {b}" if b > 0 else f"- {-b}" if b < 0 else ""
            c_str = f"+ {c}" if c > 0 else f"- {-c}" if c < 0 else ""
            smaller, larger = sorted([r1, r2])
            questions.append({
                "question": f"Find the roots of x² {b_str}x {c_str} = 0. Give the smaller root.",
                "answer": str(smaller),
                "domain": "algebra",
                "difficulty": 3,
                "accept_patterns": [str(smaller)],
            })
        elif variant == 3:
            # GCD
            a = rng.randint(50, 500)
            b = rng.randint(50, 500)
            ans = math.gcd(a, b)
            questions.append({
                "question": f"What is the greatest common divisor (GCD) of {a} and {b}?",
                "answer": str(ans),
                "domain": "math",
                "difficulty": 3,
                "accept_patterns": [str(ans)],
            })
        else:
            # Multi-step word problem
            price = rng.randint(20, 100)
            discount_pct = rng.choice([10, 15, 20, 25])
            tax_pct = rng.choice([5, 8, 10])
            after_discount = price * (1 - discount_pct / 100)
            final = after_discount * (1 + tax_pct / 100)
            final_rounded = round(final, 2)
            questions.append({
                "question": (
                    f"An item costs ${price}. It is discounted by {discount_pct}%, "
                    f"then {tax_pct}% tax is added. What is the final price?"
                ),
                "answer": str(final_rounded),
                "domain": "arithmetic",
                "difficulty": 3,
                "accept_patterns": [str(final_rounded)],
                "numeric_tolerance": 0.02,
            })

    # ─── TIER 5: Extreme (difficulty=5) — multi-step reasoning, obscure constants, meta-awareness ─
    # These items require genuine mathematical reasoning or knowledge of obscure
    # constants that LLMs commonly confabulate. Designed to widen score spread
    # above the borderline std=0.083.

    # --- Catalan numbers ---
    # C(n) = (2n)! / ((n+1)! * n!)
    catalan_n = rng.choice([5, 6, 7, 8])
    catalan_val = math.comb(2 * catalan_n, catalan_n) // (catalan_n + 1)
    questions.append({
        "question": f"What is the {catalan_n}th Catalan number C({catalan_n})? (C(0)=1, C(1)=1, C(2)=2, C(3)=5, ...)",
        "answer": str(catalan_val),
        "domain": "combinatorics",
        "difficulty": 5,
        "accept_patterns": [str(catalan_val)],
    })

    # --- Partition function p(n) ---
    # Number of integer partitions
    partition_vals = {10: 42, 12: 77, 15: 176, 20: 627}
    part_n = rng.choice(list(partition_vals.keys()))
    questions.append({
        "question": f"How many integer partitions does {part_n} have? (p({part_n}))",
        "answer": str(partition_vals[part_n]),
        "domain": "number theory",
        "difficulty": 5,
        "accept_patterns": [str(partition_vals[part_n])],
    })

    # --- Multi-step modular arithmetic chain ---
    base_a = rng.randint(7, 15)
    exp_a = rng.randint(3, 6)
    mod_a = rng.choice([13, 17, 19, 23])
    ans_mod = pow(base_a, exp_a, mod_a)
    questions.append({
        "question": f"What is {base_a}^{exp_a} mod {mod_a}?",
        "answer": str(ans_mod),
        "domain": "number theory",
        "difficulty": 5,
        "accept_patterns": [str(ans_mod)],
    })

    # --- Euler's totient ---
    totient_vals = {24: 8, 36: 12, 48: 16, 60: 16, 72: 24, 84: 24, 90: 24, 100: 40}
    tot_n = rng.choice(list(totient_vals.keys()))
    questions.append({
        "question": f"What is Euler's totient function φ({tot_n})?",
        "answer": str(totient_vals[tot_n]),
        "domain": "number theory",
        "difficulty": 5,
        "accept_patterns": [str(totient_vals[tot_n])],
    })

    # --- Derangements D(n) ---
    def derangements(n):
        if n == 0: return 1
        if n == 1: return 0
        return (n - 1) * (derangements(n - 1) + derangements(n - 2))
    der_n = rng.choice([5, 6, 7, 8])
    der_val = derangements(der_n)
    questions.append({
        "question": f"How many derangements (permutations with no fixed points) exist for {der_n} elements? (D({der_n}))",
        "answer": str(der_val),
        "domain": "combinatorics",
        "difficulty": 5,
        "accept_patterns": [str(der_val)],
    })

    # --- Continued fraction convergent ---
    # sqrt(2) = [1; 2, 2, 2, ...], 4th convergent = 17/12
    questions.append({
        "question": "What is the 4th convergent of the continued fraction expansion of √2? Express as a fraction a/b in lowest terms.",
        "answer": "17/12",
        "domain": "number theory",
        "difficulty": 5,
        "accept_patterns": ["17/12"],
    })

    # --- Stirling numbers of the second kind S(n,k) ---
    stirling_vals = {(6, 3): 90, (7, 3): 301, (7, 4): 350, (8, 3): 966}
    stir_key = rng.choice(list(stirling_vals.keys()))
    stir_n, stir_k = stir_key
    questions.append({
        "question": f"What is the Stirling number of the second kind S({stir_n},{stir_k})? (Number of ways to partition a {stir_n}-element set into {stir_k} non-empty subsets.)",
        "answer": str(stirling_vals[stir_key]),
        "domain": "combinatorics",
        "difficulty": 5,
        "accept_patterns": [str(stirling_vals[stir_key])],
    })

    # --- Confidence trap: misleading intuition ---
    # How many trailing zeros in 100! ?
    questions.append({
        "question": "How many trailing zeros does 100! (100 factorial) have?",
        "answer": "24",
        "domain": "math",
        "difficulty": 5,
        "accept_patterns": ["24"],
    })

    # --- Multi-step logical chain with intermediate result ---
    a_val = rng.randint(3, 8)
    b_val = rng.randint(2, 5)
    # (a^b + b^a) mod (a+b)
    result = (a_val**b_val + b_val**a_val) % (a_val + b_val)
    questions.append({
        "question": f"Compute ({a_val}^{b_val} + {b_val}^{a_val}) mod ({a_val}+{b_val}). Give the final integer.",
        "answer": str(result),
        "domain": "arithmetic",
        "difficulty": 5,
        "accept_patterns": [str(result)],
    })

    # --- Ramanujan-related: sum of cubes identity ---
    # 1729 = 12^3 + 1^3 = 10^3 + 9^3. What is the SECOND Hardy-Ramanujan-like taxicab number?
    questions.append({
        "question": "What is the smallest positive integer that can be expressed as the sum of two cubes in two different ways? (The Hardy-Ramanujan number.)",
        "answer": "1729",
        "domain": "number theory",
        "difficulty": 5,
        "accept_patterns": ["1729"],
    })

    # --- Meta-awareness: digit sum chain ---
    big_num = rng.randint(10000, 99999)
    ds = sum(int(d) for d in str(big_num))
    while ds >= 10:
        ds = sum(int(d) for d in str(ds))
    questions.append({
        "question": f"What is the digital root of {big_num}? (Repeatedly sum digits until single digit.)",
        "answer": str(ds),
        "domain": "math",
        "difficulty": 5,
        "accept_patterns": [str(ds)],
    })

    # --- Bernoulli number B(6) ---
    questions.append({
        "question": "What is the 6th Bernoulli number B(6)? Express as a fraction in lowest terms.",
        "answer": "1/42",
        "domain": "number theory",
        "difficulty": 5,
        "accept_patterns": ["1/42"],
    })

    return questions


PROCEDURAL_CALIBRATION_QUESTIONS = _generate_procedural_calibration()
