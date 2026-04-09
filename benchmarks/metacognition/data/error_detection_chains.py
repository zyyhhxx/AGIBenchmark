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
]

# ─── Add procedurally generated chains for contamination resistance ───
from data.procedural_error_chains import PROCEDURAL_REASONING_CHAINS

# Combine: 16 handcrafted + 16 procedural = 32 total
REASONING_CHAINS = _HANDCRAFTED_CHAINS + PROCEDURAL_REASONING_CHAINS
