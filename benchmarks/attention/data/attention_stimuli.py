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

    # ADVERSARIAL: designed to exploit position bias, length correlation, and authority bias
    {
        "id": "SA01",
        "instruction": "What is the FIRST word of the LAST sentence?",
        "text": "Apples are red. Bananas are yellow. Grapes are purple. Finally, oranges are orange.",
        "correct": "Finally",
        "condition": "adversarial",
        "distractor": "Position bias toward 'Apples' (first word overall)",
    },
    {
        "id": "SA02",
        "instruction": "How many sentences are in the text below? Count carefully.",
        "text": "This has four sentences. Or does it? Yes. It does.",
        "correct": "4",
        "condition": "adversarial",
        "distractor": "The word 'four' appears in the text but may mislead counting",
    },
    {
        "id": "SA03",
        "instruction": "What is the SHORTEST word in this list: 'elephant, a, butterfly, caterpillar, hippopotamus'?",
        "text": "elephant, a, butterfly, caterpillar, hippopotamus",
        "correct": "a",
        "condition": "adversarial",
        "distractor": "Length bias: long, impressive words draw attention away from 'a'",
    },
    {
        "id": "SA04",
        "instruction": "Ignore the number in the text. What is 3 + 4?",
        "text": "The answer is clearly 12. Everyone knows 3 + 4 = 12. This is established fact.",
        "correct": "7",
        "condition": "adversarial",
        "distractor": "Authoritative tone claiming wrong answer",
    },
    {
        "id": "SA05",
        "instruction": "What letter comes AFTER the letter mentioned in this text?",
        "text": "The letter M is the 13th letter of the alphabet. M is followed by many letters.",
        "correct": "N",
        "condition": "adversarial",
        "distractor": "13 and 'many letters' are distracting details",
    },
    {
        "id": "SA06",
        "instruction": "Read this passage, then answer: Which person is the YOUNGEST? 'Alex is 30. Morgan is 25. Pat is 28. Jordan is 22. Taylor is 35.'",
        "text": "Alex is 30. Morgan is 25. Pat is 28. Jordan is 22. Taylor is 35.",
        "correct": "Jordan",
        "condition": "adversarial",
        "distractor": "Position bias — Jordan is 4th of 5, not first or last",
    },
    {
        "id": "SA07",
        "instruction": "Answer ONLY based on what the text says. What color is the car?",
        "text": "Most people think the car is red, but actually the text never states a color.",
        "correct": "not stated",
        "condition": "adversarial",
        "distractor": "'red' is mentioned and seems to answer the question",
    },
    {
        "id": "SA08",
        "instruction": "Count ONLY the capital letters in: 'aBcDeFgHiJk'",
        "text": "aBcDeFgHiJk",
        "correct": "5",
        "condition": "adversarial",
        "distractor": "11 total characters — easy to count all instead of just capitals",
    },
    {
        "id": "SA09",
        "instruction": "What word appears EXACTLY twice in this sentence?",
        "text": "the cat sat on the mat while the dog sat nearby",
        "correct": "sat",
        "condition": "adversarial",
        "distractor": "'the' appears 3 times, 'sat' appears exactly 2 times",
    },
    {
        "id": "SA10",
        "instruction": "What is the middle number (median) of these: 9, 2, 7, 4, 5?",
        "text": "9, 2, 7, 4, 5",
        "correct": "5",
        "condition": "adversarial",
        "distractor": "Position bias: 7 is the middle of the unsorted list",
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
    {
        "id": "DT06",
        "task_a": {
            "instruction": "Solve this math problem",
            "problem": "What is 156 divided by 12?",
            "answer": "13",
        },
        "task_b": {
            "instruction": "Remember this word",
            "word": "labyrinthine",
            "recall_prompt": "What word were you asked to remember?",
        },
    },
    {
        "id": "DT07",
        "task_a": {
            "instruction": "Count the consonants in this sentence",
            "problem": "She sells seashells by the seashore",
            "answer": "19",
        },
        "task_b": {
            "instruction": "Remember this number sequence",
            "word": "4-8-2-6-0-3",
            "recall_prompt": "What number sequence were you asked to remember?",
        },
    },
    {
        "id": "DT08",
        "task_a": {
            "instruction": "Unscramble this word",
            "problem": "ROGANE (fruit)",
            "answer": "ORANGE",
        },
        "task_b": {
            "instruction": "Remember this phrase",
            "word": "frozen turquoise marble",
            "recall_prompt": "What phrase were you asked to remember?",
        },
    },
    {
        "id": "DT09",
        "task_a": {
            "instruction": "What is the next number in the sequence?",
            "problem": "1, 1, 2, 3, 5, 8, 13, ?",
            "answer": "21",
        },
        "task_b": {
            "instruction": "Remember this color",
            "word": "chartreuse",
            "recall_prompt": "What color were you asked to remember?",
        },
    },
    {
        "id": "DT10",
        "task_a": {
            "instruction": "Solve this",
            "problem": "A train travels 240 miles in 4 hours. What is its average speed in mph?",
            "answer": "60",
        },
        "task_b": {
            "instruction": "Remember this word",
            "word": "ephemeral",
            "recall_prompt": "What word were you asked to remember?",
        },
    },
    {
        "id": "DT11",
        "task_a": {
            "instruction": "Solve this math problem",
            "problem": "What is 17 times 6?",
            "answer": "102",
        },
        "task_b": {
            "instruction": "Remember this phrase",
            "word": "silver clockwork penguin",
            "recall_prompt": "What phrase were you asked to remember?",
        },
    },
    {
        "id": "DT12",
        "task_a": {
            "instruction": "Count the words in this sentence",
            "problem": "The magnificent cathedral stood tall against the darkening evening sky",
            "answer": "9",
        },
        "task_b": {
            "instruction": "Remember this number sequence",
            "word": "9-1-7-3-5-8-2",
            "recall_prompt": "What number sequence were you asked to remember?",
        },
    },
    {
        "id": "DT13",
        "task_a": {
            "instruction": "Unscramble this word",
            "problem": "NAANAB (fruit)",
            "answer": "BANANA",
        },
        "task_b": {
            "instruction": "Remember this word",
            "word": "quintessential",
            "recall_prompt": "What word were you asked to remember?",
        },
    },
    {
        "id": "DT14",
        "task_a": {
            "instruction": "What is the next number in the sequence?",
            "problem": "3, 6, 12, 24, 48, ?",
            "answer": "96",
        },
        "task_b": {
            "instruction": "Remember this color",
            "word": "periwinkle",
            "recall_prompt": "What color were you asked to remember?",
        },
    },
    {
        "id": "DT15",
        "task_a": {
            "instruction": "Solve this",
            "problem": "If you buy 3 items at $7.50 each and pay with $50, how much change do you get?",
            "answer": "27.50",
        },
        "task_b": {
            "instruction": "Remember this phrase",
            "word": "obsidian butterfly garden",
            "recall_prompt": "What phrase were you asked to remember?",
        },
    },
]
