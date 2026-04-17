"""
JOL (Judgment-of-Learning) question/stimulus dataset.

Novel association pairs that CANNOT be in training data.
Each pair consists of an invented word and a definition,
or a nonsense rule system. The model must:
1. Study the associations
2. Rate confidence of future recall (JOL)
3. Perform distractor tasks
4. Be tested on recall

Categories:
- WORD_DEF: Invented word → definition mappings
- RULE: Novel rule systems (e.g., "In Zaplang, X means Y")
- SEQUENCE: Novel pattern sequences to memorize

Stimuli are procedurally varied across runs to prevent memorization.
"""

import random
import hashlib


def _seeded_word(seed: str, length: int = 6) -> str:
    """Generate a pronounceable pseudoword from a seed."""
    h = hashlib.sha256(seed.encode()).hexdigest()
    consonants = "bcdfghjklmnprstvwz"
    vowels = "aeiou"
    word = ""
    for i in range(length):
        idx = int(h[i * 2:i * 2 + 2], 16)
        if i % 2 == 0:
            word += consonants[idx % len(consonants)]
        else:
            word += vowels[idx % len(vowels)]
    return word.capitalize()


# Fixed stimuli for reproducibility (but designed to be novel)
JOL_WORD_PAIRS = [
    # Easy pairs (concrete, imageable)
    {"word": "Brelkano", "definition": "a small wooden bridge over a stream",
     "difficulty": 1, "imageability": "high"},
    {"word": "Tunnefex", "definition": "the sound of rain hitting a tin roof",
     "difficulty": 1, "imageability": "high"},
    {"word": "Glopwren", "definition": "a bird that only sings at dawn",
     "difficulty": 1, "imageability": "high"},
    {"word": "Verdashi", "definition": "a green gemstone found only in caves",
     "difficulty": 1, "imageability": "high"},
    {"word": "Plonkrit", "definition": "a heavy clay pot used for storing grain",
     "difficulty": 1, "imageability": "high"},

    # Medium pairs (semi-abstract)
    {"word": "Feltromi", "definition": "the feeling of recognizing a place you've never been",
     "difficulty": 2, "imageability": "medium"},
    {"word": "Drasquil", "definition": "the moment just before understanding clicks",
     "difficulty": 2, "imageability": "medium"},
    {"word": "Wenvotch", "definition": "a tradition of leaving the last bite of food",
     "difficulty": 2, "imageability": "medium"},
    {"word": "Kelmapho", "definition": "the skill of navigating by starlight alone",
     "difficulty": 2, "imageability": "medium"},
    {"word": "Crinjota", "definition": "a pattern of cracks in dried mud",
     "difficulty": 2, "imageability": "medium"},

    # Hard pairs (abstract, low imageability)
    {"word": "Phaxendu", "definition": "the property of being simultaneously necessary and impossible",
     "difficulty": 3, "imageability": "low"},
    {"word": "Zorblint", "definition": "a mathematical operator that reverses parity while preserving magnitude",
     "difficulty": 3, "imageability": "low"},
    {"word": "Quellmaf", "definition": "the tendency of systems to resist their optimal configuration",
     "difficulty": 3, "imageability": "low"},
    {"word": "Narvexti", "definition": "a logical relationship where A implies B only when C is unknown",
     "difficulty": 3, "imageability": "low"},
    {"word": "Blekthor", "definition": "the ratio of perceived complexity to actual information content",
     "difficulty": 3, "imageability": "low"},
]


# Novel rule systems for testing rule-based learning
JOL_RULE_SYSTEMS = [
    {
        "rule_name": "Zaplang Number System",
        "rules": [
            "In Zaplang, 'ko' means 1, 'bo' means 2, 'mo' means 3",
            "Adding '-ra' multiplies by 10 (e.g., 'ko-ra' = 10)",
            "Adding '-fi' adds 5 (e.g., 'bo-fi' = 7)",
            "Numbers combine left-to-right: 'mo-ra bo-fi' = 37",
        ],
        "test_questions": [
            {"q": "What is 'bo-ra ko-fi' in Zaplang?", "a": "26"},
            {"q": "What is 'ko-ra mo' in Zaplang?", "a": "13"},
            {"q": "How do you say 15 in Zaplang?", "a": "ko-ra bo-fi"},
        ],
        "difficulty": 2,
    },
    {
        "rule_name": "Gridwalker Movement",
        "rules": [
            "Start at position (0,0) on a grid",
            "'vex' moves +1 in x, 'nux' moves +1 in y",
            "'rev' reverses the direction of the NEXT command only",
            "'dub' doubles the distance of the NEXT command only",
        ],
        "test_questions": [
            {"q": "After 'vex nux vex', what is the position?", "a": "(2, 1)"},
            {"q": "After 'vex rev nux vex', what is the position?", "a": "(2, -1)"},
            {"q": "After 'dub vex nux', what is the position?", "a": "(2, 1)"},
        ],
        "difficulty": 3,
    },
]


# Distractor questions (unrelated, to create temporal distance)
DISTRACTOR_QUESTIONS = [
    "Name three countries in South America.",
    "What is the square root of 144?",
    "List the primary colors of light.",
    "What is the chemical formula for glucose?",
    "Name the four cardinal directions.",
    "What is 17 times 13?",
    "List three types of cloud formations.",
    "What planet has the most moons?",
]
