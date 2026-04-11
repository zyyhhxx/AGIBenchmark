"""
Error Detection benchmark reasoning chains dataset.

Contains math/logic problems with step-by-step solutions.
Some solutions are correct; others have deliberate errors injected
at specific steps. The model must identify:
1. Whether an error exists (binary)
2. Which step contains the error
3. Confidence in its judgment

Categories:
- MATH: Arithmetic and algebra problems
- LOGIC: Logical deduction problems  
- PROBABILITY: Probability/combinatorics

Includes both handcrafted chains (for ecological validity) and
procedurally generated chains (for contamination resistance).
"""

_HANDCRAFTED_CHAINS = [
    # === CORRECT CHAINS ===
    {
        "id": "C01",
        "problem": "Solve for x: 3x + 7 = 22",
        "steps": [
            "Step 1: Subtract 7 from both sides: 3x = 22 - 7 = 15",
            "Step 2: Divide both sides by 3: x = 15 / 3 = 5",
            "Step 3: Check: 3(5) + 7 = 15 + 7 = 22 ✓",
        ],
        "final_answer": "x = 5",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 1,
    },
    {
        "id": "C02",
        "problem": "What is the probability of rolling two dice and getting a sum of 7?",
        "steps": [
            "Step 1: Total possible outcomes when rolling two dice = 6 × 6 = 36",
            "Step 2: Favorable outcomes for sum of 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1) = 6 outcomes",
            "Step 3: Probability = favorable / total = 6/36 = 1/6",
        ],
        "final_answer": "1/6",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 1,
    },
    {
        "id": "C03",
        "problem": "If all roses are flowers, and some flowers are red, can we conclude that some roses are red?",
        "steps": [
            "Step 1: Premise 1: All roses are flowers (roses ⊆ flowers)",
            "Step 2: Premise 2: Some flowers are red (flowers ∩ red ≠ ∅)",
            "Step 3: The red flowers could be non-rose flowers (e.g., tulips, poppies)",
            "Step 4: We cannot conclude that any roses are red — the conclusion does not follow",
        ],
        "final_answer": "No, we cannot conclude that some roses are red",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 2,
    },
    {
        "id": "C04",
        "problem": "Find the area of a triangle with base 12 cm and height 8 cm.",
        "steps": [
            "Step 1: Area formula for a triangle: A = (1/2) × base × height",
            "Step 2: A = (1/2) × 12 × 8",
            "Step 3: A = (1/2) × 96 = 48 cm²",
        ],
        "final_answer": "48 cm²",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 1,
    },
    {
        "id": "C05",
        "problem": "How many ways can 5 people be seated in a row?",
        "steps": [
            "Step 1: The first seat can be filled by any of 5 people",
            "Step 2: The second seat by any of the remaining 4",
            "Step 3: Continuing: 3, then 2, then 1",
            "Step 4: Total = 5! = 5 × 4 × 3 × 2 × 1 = 120",
        ],
        "final_answer": "120",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 1,
    },

    # === CHAINS WITH ERRORS ===
    {
        "id": "E01",
        "problem": "Solve for x: 2(x + 3) = 16",
        "steps": [
            "Step 1: Distribute the 2: 2x + 3 = 16",  # ERROR: should be 2x + 6
            "Step 2: Subtract 3 from both sides: 2x = 13",
            "Step 3: Divide by 2: x = 6.5",
            "Step 4: Check: 2(6.5 + 3) = 2(9.5) = 19 ≠ 16, so let me recheck... Actually 2(6.5 + 3) = 19. Hmm, that's close to 16.",
        ],
        "final_answer": "x = 6.5",
        "has_error": True,
        "error_step": 1,
        "error_description": "Distribution error: 2(x+3) should give 2x + 6, not 2x + 3",
        "difficulty": 1,
    },
    {
        "id": "E02",
        "problem": "What is the probability of getting at least one head in 3 coin flips?",
        "steps": [
            "Step 1: P(at least one head) = 1 - P(no heads) = 1 - P(all tails)",
            "Step 2: P(all tails) = (1/2)³ = 1/6",  # ERROR: should be 1/8
            "Step 3: P(at least one head) = 1 - 1/6 = 5/6",
        ],
        "final_answer": "5/6",
        "has_error": True,
        "error_step": 2,
        "error_description": "Calculation error: (1/2)³ = 1/8, not 1/6",
        "difficulty": 1,
    },
    {
        "id": "E03",
        "problem": "If it rains, the ground is wet. The ground is wet. Did it rain?",
        "steps": [
            "Step 1: Premise: If rain → wet ground",
            "Step 2: Observation: The ground is wet",
            "Step 3: Since wet ground always comes from rain, it must have rained",  # ERROR: affirming the consequent
            "Step 4: Therefore, it rained",
        ],
        "final_answer": "Yes, it rained",
        "has_error": True,
        "error_step": 3,
        "error_description": "Affirming the consequent fallacy: the ground could be wet for other reasons (sprinkler, flood, etc.)",
        "difficulty": 2,
    },
    {
        "id": "E04",
        "problem": "Simplify: (x² - 9) / (x - 3)",
        "steps": [
            "Step 1: Factor the numerator: x² - 9 = (x - 3)(x - 3)",  # ERROR: should be (x-3)(x+3)
            "Step 2: Cancel (x - 3): (x - 3)(x - 3) / (x - 3) = x - 3",
            "Step 3: Result: x - 3 (for x ≠ 3)",
        ],
        "final_answer": "x - 3",
        "has_error": True,
        "error_step": 1,
        "error_description": "Factoring error: x² - 9 = (x-3)(x+3), not (x-3)(x-3). The correct simplification is x + 3.",
        "difficulty": 1,
    },
    {
        "id": "E05",
        "problem": "A train travels 120 km in 1.5 hours. Then it travels 80 km in 1 hour. What is the average speed for the entire trip?",
        "steps": [
            "Step 1: Speed for leg 1: 120/1.5 = 80 km/h",
            "Step 2: Speed for leg 2: 80/1 = 80 km/h",
            "Step 3: Average speed = (80 + 80) / 2 = 80 km/h",  # ERROR: should use total distance / total time
        ],
        "final_answer": "80 km/h",
        "has_error": True,
        "error_step": 3,
        "error_description": "Average speed should be total distance / total time = 200/2.5 = 80 km/h. In this case the answer happens to be correct by coincidence, but the method is wrong (averaging speeds is incorrect in general).",
        "difficulty": 2,
    },
    {
        "id": "E06",
        "problem": "How many diagonals does a hexagon have?",
        "steps": [
            "Step 1: Formula for diagonals of an n-gon: n(n-3)/2",
            "Step 2: For hexagon, n = 6: 6(6-3)/2 = 6 × 3/2 = 18/2 = 9",
        ],
        "final_answer": "9",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 2,
    },
    {
        "id": "E07",
        "problem": "Convert 5/8 to a percentage.",
        "steps": [
            "Step 1: To convert a fraction to a percentage, multiply by 100",
            "Step 2: 5/8 × 100 = 500/8 = 62.5%",
        ],
        "final_answer": "62.5%",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 1,
    },
    {
        "id": "E08",
        "problem": "What is the derivative of f(x) = x³ + 2x² - 5x + 1?",
        "steps": [
            "Step 1: Apply power rule term by term",
            "Step 2: d/dx(x³) = 3x²",
            "Step 3: d/dx(2x²) = 4x",
            "Step 4: d/dx(-5x) = -5",
            "Step 5: d/dx(1) = 1",  # ERROR: derivative of constant is 0
            "Step 6: f'(x) = 3x² + 4x - 5 + 1 = 3x² + 4x - 4",
        ],
        "final_answer": "f'(x) = 3x² + 4x - 4",
        "has_error": True,
        "error_step": 5,
        "error_description": "The derivative of a constant (1) is 0, not 1. Correct answer: f'(x) = 3x² + 4x - 5",
        "difficulty": 2,
    },
    {
        "id": "E09",
        "problem": "A bag contains 3 red and 5 blue balls. Two balls are drawn without replacement. What is the probability both are red?",
        "steps": [
            "Step 1: P(first red) = 3/8",
            "Step 2: After drawing one red, remaining: 2 red, 5 blue = 7 total",
            "Step 3: P(second red | first red) = 2/7",
            "Step 4: P(both red) = (3/8) × (2/7) = 6/56 = 3/28",
        ],
        "final_answer": "3/28",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 2,
    },
    {
        "id": "E10",
        "problem": "Evaluate: log₂(8) + log₂(4)",
        "steps": [
            "Step 1: log₂(8) = 3 (since 2³ = 8)",
            "Step 2: log₂(4) = 2 (since 2² = 4)",
            "Step 3: By the log addition rule: log₂(8) + log₂(4) = log₂(8 × 4) = log₂(32) = 5",
        ],
        "final_answer": "5",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 1,
    },
    {
        "id": "E11",
        "problem": "Find the sum of the interior angles of a pentagon.",
        "steps": [
            "Step 1: Formula: sum of interior angles = (n-2) × 180°",
            "Step 2: For pentagon, n = 5: (5-2) × 180° = 3 × 180° = 480°",  # ERROR: 3 × 180 = 540
        ],
        "final_answer": "480°",
        "has_error": True,
        "error_step": 2,
        "error_description": "Arithmetic error: 3 × 180 = 540, not 480",
        "difficulty": 1,
    },
    {
        "id": "E12",
        "problem": "All cats are mammals. All mammals are warm-blooded. Therefore?",
        "steps": [
            "Step 1: Cats ⊆ Mammals (all cats are mammals)",
            "Step 2: Mammals ⊆ Warm-blooded (all mammals are warm-blooded)",
            "Step 3: By transitivity: Cats ⊆ Warm-blooded",
            "Step 4: Therefore, all cats are warm-blooded",
        ],
        "final_answer": "All cats are warm-blooded",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 1,
    },
    # Additional error chains for balance (targeting ~50/50 ratio)
    {
        "id": "E13",
        "problem": "What is the probability of drawing two aces in a row from a standard deck (without replacement)?",
        "steps": [
            "Step 1: P(first ace) = 4/52 = 1/13",
            "Step 2: After drawing one ace, 3 aces remain in 51 cards",
            "Step 3: P(second ace | first ace) = 3/52",  # ERROR: should be 3/51
            "Step 4: P(both aces) = (4/52) × (3/52) = 12/2704 = 3/676",
        ],
        "final_answer": "3/676",
        "has_error": True,
        "error_step": 3,
        "error_description": "Should be 3/51 (not 3/52) since one card has been removed. Correct answer: 12/2652 = 1/221",
        "difficulty": 2,
    },
    {
        "id": "E14",
        "problem": "Solve: |2x - 6| = 10",
        "steps": [
            "Step 1: |2x - 6| = 10 means either 2x - 6 = 10 or 2x - 6 = -10",
            "Step 2: Case 1: 2x - 6 = 10 → 2x = 16 → x = 8",
            "Step 3: Case 2: 2x - 6 = -10 → 2x = -4 → x = -2",
            "Step 4: Solutions: x = 8 or x = -2",
        ],
        "final_answer": "x = 8 or x = -2",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 2,
    },
    {
        "id": "E15",
        "problem": "What is the volume of a sphere with radius 3 cm?",
        "steps": [
            "Step 1: Volume formula: V = (4/3)πr²",  # ERROR: should be r³
            "Step 2: V = (4/3) × π × 3² = (4/3) × π × 9 = 12π",
            "Step 3: V ≈ 12 × 3.14159 ≈ 37.7 cm³",
        ],
        "final_answer": "37.7 cm³",
        "has_error": True,
        "error_step": 1,
        "error_description": "Volume formula should be (4/3)πr³, not (4/3)πr². Correct: (4/3)π(27) = 36π ≈ 113.1 cm³",
        "difficulty": 1,
    },
    {
        "id": "E16",
        "problem": "If the sequence follows the pattern: 2, 6, 18, 54, ... what is the 6th term?",
        "steps": [
            "Step 1: Find the common ratio: 6/2 = 3",
            "Step 2: This is a geometric sequence with a₁ = 2, r = 3",
            "Step 3: General term: aₙ = a₁ × r^(n-1) = 2 × 3^(n-1)",
            "Step 4: a₆ = 2 × 3^5 = 2 × 243 = 486",
        ],
        "final_answer": "486",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 2,
    },

    # === SUBTLE ERROR CHAINS (difficulty=3) — plausible, easy-to-miss errors ===
    {
        "id": "E17",
        "problem": "How many ways can you choose a committee of 3 from 8 people?",
        "steps": [
            "Step 1: This is a combination problem: C(8,3) = 8! / (3! × 5!)",
            "Step 2: 8! / (3! × 5!) = (8 × 7 × 6) / (3 × 2 × 1)",
            "Step 3: Numerator: 8 × 7 × 6 = 336",
            "Step 4: Denominator: 3 × 2 × 1 = 6",
            "Step 5: 336 / 6 = 56",
        ],
        "final_answer": "56",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E18",
        "problem": "Find the integral of 2x × cos(x²) dx",
        "steps": [
            "Step 1: Let u = x², then du = 2x dx",
            "Step 2: The integral becomes ∫ cos(u) du",
            "Step 3: ∫ cos(u) du = -sin(u) + C",  # ERROR: should be +sin(u)
            "Step 4: Substituting back: -sin(x²) + C",
        ],
        "final_answer": "-sin(x²) + C",
        "has_error": True,
        "error_step": 3,
        "error_description": "Sign error: ∫cos(u)du = sin(u) + C, not -sin(u) + C. Easy to confuse with derivative of sin.",
        "difficulty": 3,
    },
    {
        "id": "E19",
        "problem": "In a group of 30 people, what's the probability that at least 2 share a birthday? (Approximate)",
        "steps": [
            "Step 1: P(at least 2 share) = 1 - P(all different)",
            "Step 2: P(all different) = (365/365) × (364/365) × (363/365) × ... × (336/365)",
            "Step 3: Using the approximation: P(all different) ≈ e^(-n(n-1)/(2×365))",
            "Step 4: n(n-1)/2 = 30 × 29/2 = 435",
            "Step 5: P(all different) ≈ e^(-435/365) ≈ e^(-1.192) ≈ 0.304",
            "Step 6: P(at least 2 share) ≈ 1 - 0.304 = 0.696 ≈ 70%",
        ],
        "final_answer": "≈ 70%",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E20",
        "problem": "A fair die is rolled 3 times. What is the probability of getting exactly 2 sixes?",
        "steps": [
            "Step 1: This follows a binomial distribution: P(X=k) = C(n,k) × p^k × (1-p)^(n-k)",
            "Step 2: n=3, k=2, p=1/6",
            "Step 3: C(3,2) = 3",
            "Step 4: P(X=2) = 3 × (1/6)² × (5/6)¹",
            "Step 5: = 3 × (1/36) × (5/6) = 3 × 5/216 = 15/216",  # ERROR: should be 15/216 = 5/72, but he writes...
            "Step 6: = 15/216 = 5/71",  # ERROR: 15/216 = 5/72 not 5/71
        ],
        "final_answer": "5/71",
        "has_error": True,
        "error_step": 6,
        "error_description": "Simplification error: 15/216 = 5/72, not 5/71. An off-by-one in the denominator.",
        "difficulty": 3,
    },
    {
        "id": "E21",
        "problem": "A test has 90% sensitivity and 95% specificity. If 1% of the population has the disease, what's the probability someone who tests positive actually has it?",
        "steps": [
            "Step 1: Using Bayes' theorem: P(D|+) = P(+|D)×P(D) / P(+)",
            "Step 2: P(+|D) = 0.90 (sensitivity), P(D) = 0.01",
            "Step 3: P(+|¬D) = 1 - 0.95 = 0.05 (false positive rate)",
            "Step 4: P(+) = P(+|D)×P(D) + P(+|¬D)×P(¬D) = 0.90×0.01 + 0.05×0.99",
            "Step 5: P(+) = 0.009 + 0.0495 = 0.0585",
            "Step 6: P(D|+) = 0.009 / 0.0585 ≈ 0.154 ≈ 15.4%",
        ],
        "final_answer": "≈ 15.4%",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E22",
        "problem": "Prove that √2 is irrational (by contradiction)",
        "steps": [
            "Step 1: Assume √2 is rational, so √2 = a/b where a,b are integers with no common factors",
            "Step 2: Then 2 = a²/b², so a² = 2b²",
            "Step 3: Since a² is even, a must be even. Let a = 2k.",
            "Step 4: Then (2k)² = 2b², so 4k² = 2b², so b² = 2k²",  # correct
            "Step 5: Since b² is even, b must be even",
            "Step 6: But then a and b are both even, contradicting our assumption they share no common factors",
            "Step 7: Therefore √2 is irrational ■",
        ],
        "final_answer": "√2 is irrational",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E23",
        "problem": "What is the limit of (1 + 1/n)^n as n → ∞?",
        "steps": [
            "Step 1: Let L = lim(n→∞) (1 + 1/n)^n",
            "Step 2: Take ln of both sides: ln(L) = lim(n→∞) n × ln(1 + 1/n)",
            "Step 3: As n→∞, ln(1 + 1/n) ≈ 1/n - 1/(2n²) (Taylor expansion)",
            "Step 4: So n × ln(1 + 1/n) ≈ n × (1/n - 1/(2n²)) = 1 - 1/(2n) → 1",
            "Step 5: Therefore ln(L) = 1, so L = e¹ = e ≈ 2.718",
        ],
        "final_answer": "e ≈ 2.718",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E24",
        "problem": "How many distinct permutations of the letters in 'MISSISSIPPI'?",
        "steps": [
            "Step 1: MISSISSIPPI has 11 letters",
            "Step 2: Letter counts: M=1, I=4, S=4, P=2",
            "Step 3: Formula: 11! / (1! × 4! × 4! × 2!)",
            "Step 4: 11! = 39916800",
            "Step 5: Denominator: 1 × 24 × 24 × 2 = 1152",
            "Step 6: 39916800 / 1152 = 34650",  # correct
        ],
        "final_answer": "34650",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E25",
        "problem": "Find the determinant of the matrix [[2, 1, 3], [0, -1, 2], [1, 4, -1]]",
        "steps": [
            "Step 1: Expand along the first row: det = 2×det[[-1,2],[4,-1]] - 1×det[[0,2],[1,-1]] + 3×det[[0,-1],[1,4]]",
            "Step 2: det[[-1,2],[4,-1]] = (-1)(-1) - (2)(4) = 1 - 8 = -7",
            "Step 3: det[[0,2],[1,-1]] = (0)(-1) - (2)(1) = -2",
            "Step 4: det[[0,-1],[1,4]] = (0)(4) - (-1)(1) = 0 + 1 = 1",
            "Step 5: det = 2(-7) - 1(-2) + 3(1) = -14 + 2 + 3 = -9",
        ],
        "final_answer": "-9",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E26",
        "problem": "What is the sum of the infinite geometric series: 3 + 3/2 + 3/4 + 3/8 + ...?",
        "steps": [
            "Step 1: First term a = 3, common ratio r = 1/2",
            "Step 2: Since |r| < 1, the series converges",
            "Step 3: Sum = a / (1 - r) = 3 / (1 - 1/2) = 3 / (1/2)",
            "Step 4: = 3 × 2 = 6",
        ],
        "final_answer": "6",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E27",
        "problem": "Find the derivative of f(x) = ln(sin(x²))",
        "steps": [
            "Step 1: Apply chain rule: f'(x) = (1/sin(x²)) × d/dx[sin(x²)]",
            "Step 2: d/dx[sin(x²)] = cos(x²) × d/dx[x²] = cos(x²) × 2x",
            "Step 3: f'(x) = (1/sin(x²)) × cos(x²) × 2x = 2x × cos(x²)/sin(x²)",
            "Step 4: = 2x × cot(x²)",
        ],
        "final_answer": "2x·cot(x²)",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E28",
        "problem": "Evaluate: ∫₀¹ x × e^(x²) dx",
        "steps": [
            "Step 1: Let u = x², then du = 2x dx, so x dx = du/2",
            "Step 2: When x=0, u=0; when x=1, u=1",
            "Step 3: The integral becomes (1/2) ∫₀¹ e^u du",
            "Step 4: = (1/2) [e^u]₀¹ = (1/2)(e¹ - e⁰) = (1/2)(e - 1)",
            "Step 5: ≈ (1/2)(2.718 - 1) = (1/2)(1.718) ≈ 0.859",
        ],
        "final_answer": "(e-1)/2 ≈ 0.859",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E29",
        "problem": "A group of 5 people sit around a circular table. How many distinct seating arrangements are there?",
        "steps": [
            "Step 1: For circular permutations, we fix one person and arrange the rest",
            "Step 2: Number of arrangements = (n-1)! = 4! = 24",
        ],
        "final_answer": "24",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E30",
        "problem": "Solve the recurrence: T(n) = 2T(n/2) + n, T(1) = 1. What is T(8)?",
        "steps": [
            "Step 1: T(1) = 1",
            "Step 2: T(2) = 2T(1) + 2 = 2(1) + 2 = 4",
            "Step 3: T(4) = 2T(2) + 4 = 2(4) + 4 = 12",
            "Step 4: T(8) = 2T(4) + 8 = 2(12) + 8 = 32",
        ],
        "final_answer": "32",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E31",
        "problem": "If P(A) = 0.3, P(B) = 0.5, and P(A∩B) = 0.2, find P(A|B)",
        "steps": [
            "Step 1: P(A|B) = P(A∩B) / P(B)",
            "Step 2: P(A|B) = 0.2 / 0.5 = 0.4",
            "Step 3: Also check: P(A∪B) = P(A) + P(B) - P(A∩B) = 0.3 + 0.5 - 0.2 = 0.6 ✓",
        ],
        "final_answer": "0.4",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
    {
        "id": "E32",
        "problem": "Find the eigenvalues of the matrix [[3, 1], [0, 2]]",
        "steps": [
            "Step 1: det(A - λI) = 0",
            "Step 2: det([[3-λ, 1], [0, 2-λ]]) = (3-λ)(2-λ) - 0 = 0",
            "Step 3: (3-λ)(2-λ) = 0",
            "Step 4: λ = 3 or λ = 2",
        ],
        "final_answer": "λ = 2, 3",
        "has_error": False,
        "error_step": None,
        "error_description": None,
        "difficulty": 3,
    },
]

# ─── Add procedurally generated chains for contamination resistance ───
from data.procedural_error_chains import PROCEDURAL_REASONING_CHAINS

# Combine: 16 handcrafted + 16 procedural = 32 total
REASONING_CHAINS = _HANDCRAFTED_CHAINS + PROCEDURAL_REASONING_CHAINS
