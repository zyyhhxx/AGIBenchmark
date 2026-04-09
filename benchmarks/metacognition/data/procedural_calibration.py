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

    return questions


PROCEDURAL_CALIBRATION_QUESTIONS = _generate_procedural_calibration()
