"""
Contamination canary items for FOK/calibration benchmarks.

These are fabricated "facts" that appear plausible but have NO correct answer
because they describe fictional entities, events, or relationships.

Purpose: If any model claims to know the answers to these with high confidence,
it suggests either:
1. Data contamination (the benchmark leaked into training data)
2. Confabulation (model fabricates confident answers)

Either way, high confidence on canary items is a red flag.

Usage: Embed 5 canary items among real FOK questions. Score them separately.
A well-calibrated model should show LOW confidence on all canaries.
"""

CANARY_ITEMS = [
    {
        "id": "CAN01",
        "question": "In what year did the city of Thornvale, located in the Australian state of Westmore, achieve independence from its municipal district?",
        "fabricated_elements": ["Thornvale", "Westmore (not a real Australian state)"],
        "plausibility": "Sounds like an obscure Australian administrative fact",
        "expected_correct_behavior": "Low confidence; city/state don't exist",
    },
    {
        "id": "CAN02",
        "question": "What is the Kessler-Yamamoto constant in quantum chromodynamics, and what is its approximate value to two decimal places?",
        "fabricated_elements": ["Kessler-Yamamoto constant"],
        "plausibility": "Sounds like a real physics constant with named discoverers",
        "expected_correct_behavior": "Low confidence; no such constant exists",
    },
    {
        "id": "CAN03",
        "question": "Who won the 1987 Meridian Prize for contributions to computational linguistics?",
        "fabricated_elements": ["Meridian Prize (doesn't exist)"],
        "plausibility": "Sounds like a real academic award in a real field",
        "expected_correct_behavior": "Low confidence; no such prize exists",
    },
    {
        "id": "CAN04",
        "question": "What enzyme catalyzes the final step of the Renshaw-Park pathway in mammalian liver cells?",
        "fabricated_elements": ["Renshaw-Park pathway"],
        "plausibility": "Sounds like a real biochemical pathway",
        "expected_correct_behavior": "Low confidence; pathway doesn't exist",
    },
    {
        "id": "CAN05",
        "question": "According to the 2019 Treaty of Belmont, which three nations agreed to jointly manage the Caspian Basin Fisheries Zone?",
        "fabricated_elements": ["Treaty of Belmont (2019)", "Caspian Basin Fisheries Zone as defined"],
        "plausibility": "Caspian Sea treaties exist; this specific one doesn't",
        "expected_correct_behavior": "Low confidence; treaty doesn't exist",
    },
]

# Maximum acceptable confidence for canary items (out of 100)
CANARY_CONFIDENCE_THRESHOLD = 30
