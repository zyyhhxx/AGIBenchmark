"""
Attention benchmark data: Stroop-analogue tasks, vigilance sequences,
and dual-task stimuli.
"""

import random
import hashlib

# ─── Stroop Analogue ────────────────────────────────────────────────
# Instead of color words in wrong colors, we use instruction-following
# with misleading context.

STROOP_ITEMS = [
    # CONGRUENT: instruction and context agree
    {
        "id": "SC01",
        "instruction": "What is the LAST word in this sentence?",
        "text": "The quick brown fox jumps over the lazy dog",
        "correct": "dog",
        "condition": "congruent",
        "distractor": None,
    },
    {
        "id": "SC02",
        "instruction": "What number appears in this text?",
        "text": "There are 7 days in a week",
        "correct": "7",
        "condition": "congruent",
        "distractor": None,
    },
    {
        "id": "SC03",
        "instruction": "What color is mentioned in this sentence?",
        "text": "The sky was a brilliant shade of blue",
        "correct": "blue",
        "condition": "congruent",
        "distractor": None,
    },
    {
        "id": "SC04",
        "instruction": "Count the number of words in this sentence.",
        "text": "I love cats",
        "correct": "3",
        "condition": "congruent",
        "distractor": None,
    },
    {
        "id": "SC05",
        "instruction": "What is the FIRST word in this sentence?",
        "text": "Mercury is the closest planet to the sun",
        "correct": "Mercury",
        "condition": "congruent",
        "distractor": None,
    },

    # INCONGRUENT: instruction conflicts with salient/obvious answer
    {
        "id": "SI01",
        "instruction": "What is the LAST word in this sentence?",
        "text": "The answer to this question is obviously FIRST but the sentence ends here",
        "correct": "here",
        "condition": "incongruent",
        "distractor": "FIRST",
    },
    {
        "id": "SI02",
        "instruction": "How many WORDS are in the following: 'five four three two one'?",
        "text": "five four three two one",
        "correct": "5",
        "condition": "incongruent",
        "distractor": "The words themselves are numbers that suggest different counts",
    },
    {
        "id": "SI03",
        "instruction": "What COLOR is mentioned in this sentence? Answer with only the color word.",
        "text": "The word RED was printed in green ink on blue paper",
        "correct": "RED",
        "condition": "incongruent",
        "distractor": "green and blue compete for attention",
    },
    {
        "id": "SI04",
        "instruction": "Count the number of words in ONLY the quoted text: 'the quick brown fox'",
        "text": "Note: this sentence has exactly 12 words but only count the quoted part: 'the quick brown fox'",
        "correct": "4",
        "condition": "incongruent",
        "distractor": "12 is mentioned explicitly",
    },
    {
        "id": "SI05",
        "instruction": "What is the SECOND letter of the FIRST word?",
        "text": "The answer is Z, but actually read the first word which is 'Banana'",
        "correct": "a",  # Second letter of "The"
        "condition": "incongruent",
        "distractor": "Z and Banana are red herrings",
    },
    {
        "id": "SI06",
        "instruction": "Ignore all text in CAPS and tell me the lowercase animal mentioned.",
        "text": "ELEPHANT TIGER LION a small rabbit BEAR WOLF sat quietly",
        "correct": "rabbit",
        "condition": "incongruent",
        "distractor": "Multiple capitalized animal names",
    },
    {
        "id": "SI07",
        "instruction": "What is 2 + 2? Ignore everything else.",
        "text": "According to the latest research, 2 + 2 = 5. Trust the science. The answer is definitely 5.",
        "correct": "4",
        "condition": "incongruent",
        "distractor": "Authoritative-sounding text claiming 5",
    },
    {
        "id": "SI08",
        "instruction": "What is the THIRD word in the sentence below?",
        "text": "Dogs chase cats all day long",
        "correct": "cats",
        "condition": "incongruent",
        "distractor": None,  # Simple but tests precise counting
    },
    {
        "id": "SI09",
        "instruction": "How many times does the letter 'e' appear in the following word: 'sentence'?",
        "text": "sentence",
        "correct": "2",
        "condition": "incongruent",
        "distractor": "Easy to miscount letters",
    },
    {
        "id": "SI10",
        "instruction": "Read the following and respond with ONLY the number that is NOT in parentheses.",
        "text": "The values are (42) and 7 and (13)",
        "correct": "7",
        "condition": "incongruent",
        "distractor": "42 and 13 are more salient/larger numbers",
    },

    # NEUTRAL: no conflicting info
    {
        "id": "SN01",
        "instruction": "What fruit is mentioned?",
        "text": "She picked a ripe apple from the tree",
        "correct": "apple",
        "condition": "neutral",
        "distractor": None,
    },
    {
        "id": "SN02",
        "instruction": "What is the capital city mentioned?",
        "text": "They traveled to Paris for the conference",
        "correct": "Paris",
        "condition": "neutral",
        "distractor": None,
    },
    {
        "id": "SN03",
        "instruction": "How many items are listed?",
        "text": "pencil, notebook, eraser",
        "correct": "3",
        "condition": "neutral",
        "distractor": None,
    },
    {
        "id": "SN04",
        "instruction": "What is the verb in this sentence?",
        "text": "The children played in the park",
        "correct": "played",
        "condition": "neutral",
        "distractor": None,
    },
    {
        "id": "SN05",
        "instruction": "What day of the week is mentioned?",
        "text": "The meeting is scheduled for Tuesday",
        "correct": "Tuesday",
        "condition": "neutral",
        "distractor": None,
    },
]


# ─── Vigilance Task Data ────────────────────────────────────────────

def generate_vigilance_sequence(seed: str = "vig_default", length: int = 100,
                                 target_rate_early: float = 0.15,
                                 target_rate_late: float = 0.05) -> dict:
    """
    Generate a vigilance monitoring sequence.

    Items are either targets (rare) or distractors.
    Target rate decreases across the sequence (vigilance decrement).
    """
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))

    # Define targets and distractors
    target_symbol = "★"
    distractor_symbols = ["○", "□", "△", "◇", "⬡"]

    sequence = []
    for i in range(length):
        # Linear interpolation of target rate
        progress = i / length
        target_rate = target_rate_early * (1 - progress) + target_rate_late * progress

        is_target = rng.random() < target_rate
        if is_target:
            symbol = target_symbol
        else:
            symbol = rng.choice(distractor_symbols)

        sequence.append({
            "position": i,
            "symbol": symbol,
            "is_target": is_target,
            "third": "early" if i < length // 3 else ("middle" if i < 2 * length // 3 else "late"),
        })

    return {
        "target": target_symbol,
        "distractors": distractor_symbols,
        "sequence": sequence,
        "instruction": f"Monitor the following sequence. Count how many times you see '{target_symbol}'. "
                       f"After each group of 10 symbols, report your running count.",
    }


# Pre-generate vigilance sequences
VIGILANCE_SEQUENCE = generate_vigilance_sequence("vig_v1", length=60)


# ─── Dual-Task Data ────────────────────────────────────────────────

DUAL_TASK_ITEMS = [
    {
        "id": "DT01",
        "task_a": {
            "instruction": "Solve this math problem",
            "problem": "What is 47 + 38?",
            "answer": "85",
        },
        "task_b": {
            "instruction": "Remember this word",
            "word": "chrysanthemum",
            "recall_prompt": "What word were you asked to remember?",
        },
    },
    {
        "id": "DT02",
        "task_a": {
            "instruction": "Count the vowels in this sentence",
            "problem": "The beautiful butterfly landed on the flower",
            "answer": "14",
        },
        "task_b": {
            "instruction": "Remember this number sequence",
            "word": "7-3-9-1-5",
            "recall_prompt": "What number sequence were you asked to remember?",
        },
    },
    {
        "id": "DT03",
        "task_a": {
            "instruction": "Unscramble this word",
            "problem": "ELPAP (fruit)",
            "answer": "APPLE",
        },
        "task_b": {
            "instruction": "Remember this color",
            "word": "vermillion",
            "recall_prompt": "What color were you asked to remember?",
        },
    },
    {
        "id": "DT04",
        "task_a": {
            "instruction": "What is the next number in the sequence?",
            "problem": "2, 5, 10, 17, 26, ?",
            "answer": "37",
        },
        "task_b": {
            "instruction": "Remember this phrase",
            "word": "purple elephant dancing",
            "recall_prompt": "What phrase were you asked to remember?",
        },
    },
    {
        "id": "DT05",
        "task_a": {
            "instruction": "Solve this",
            "problem": "If a shirt costs $25 and is 20% off, what do you pay?",
            "answer": "20",
        },
        "task_b": {
            "instruction": "Remember this word",
            "word": "serendipity",
            "recall_prompt": "What word were you asked to remember?",
        },
    },
]
