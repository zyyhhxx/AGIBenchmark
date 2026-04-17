"""
Vigilance benchmark stimuli — N-back sustained attention task.

Generates long sequences where the model must identify n-back matches
(current item same as item N positions back) among near-miss distractors.

Cognitive basis:
- Kirchner (1958): N-back task for working memory / sustained attention
- Mackworth (1948): Vigilance decrement over time
- Parasuraman & Davies (1977): Signal detection in sustained monitoring
"""

import random
import hashlib


# Stimulus pool: letters chosen to maximize confusability (near-miss distractors)
# Groups of visually/phonetically similar items increase false alarm potential
STIMULUS_POOL = list("BCDGPTVFHKLMNRSXZ")

# Confusable pairs — used to generate near-miss distractors
CONFUSABLE = {
    "B": ["D", "P"],
    "D": ["B", "G"],
    "G": ["C", "D"],
    "P": ["B", "T"],
    "T": ["P", "D"],
    "V": ["F", "B"],
    "F": ["V", "H"],
    "H": ["K", "F"],
    "K": ["H", "X"],
    "L": ["M", "N"],
    "M": ["N", "L"],
    "N": ["M", "L"],
    "R": ["S", "L"],
    "S": ["X", "Z"],
    "X": ["K", "S"],
    "Z": ["S", "X"],
    "C": ["G", "S"],
}


def generate_nback_sequence(
    seed: str,
    length: int = 80,
    n_back: int = 3,
    target_rate: float = 0.20,
    near_miss_rate: float = 0.10,
) -> dict:
    """
    Generate an n-back sequence with targets, near-miss distractors, and non-targets.

    - target: current letter == letter n positions back (correct response: YES)
    - near_miss: current letter is confusable with letter n positions back (correct: NO)
    - non_target: no match (correct: NO)

    Target rate decreases linearly from target_rate*1.2 to target_rate*0.8 across
    the sequence, simulating decreasing signal frequency (vigilance demand).
    """
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))

    sequence = []
    letters = []

    for i in range(length):
        progress = i / length  # 0.0 → 1.0

        if i < n_back:
            # Initial n items: just random, no n-back possible
            letter = rng.choice(STIMULUS_POOL)
            item_type = "filler"
        else:
            ref_letter = letters[i - n_back]
            # Decrease target rate over time to increase vigilance demand
            local_target_rate = target_rate * (1.2 - 0.4 * progress)
            local_near_miss_rate = near_miss_rate * (0.8 + 0.4 * progress)  # increase near-misses over time

            roll = rng.random()
            if roll < local_target_rate:
                letter = ref_letter  # exact match = target
                item_type = "target"
            elif roll < local_target_rate + local_near_miss_rate:
                # near-miss: pick a confusable letter
                confusables = [c for c in CONFUSABLE.get(ref_letter, []) if c != ref_letter]
                if confusables:
                    letter = rng.choice(confusables)
                    item_type = "near_miss"
                else:
                    letter = rng.choice([s for s in STIMULUS_POOL if s != ref_letter])
                    item_type = "non_target"
            else:
                # non-target: any letter that isn't the ref or confusable
                avoid = set([ref_letter] + CONFUSABLE.get(ref_letter, []))
                pool = [s for s in STIMULUS_POOL if s not in avoid]
                if not pool:
                    pool = [s for s in STIMULUS_POOL if s != ref_letter]
                letter = rng.choice(pool)
                item_type = "non_target"

        letters.append(letter)

        quartile = i * 4 // length  # 0,1,2,3
        sequence.append({
            "position": i,
            "letter": letter,
            "type": item_type,
            "quartile": quartile,
            "n_back_ref": letters[i - n_back] if i >= n_back else None,
            "correct_response": "YES" if item_type == "target" else "NO",
        })

    stats = {
        "total": length,
        "n_back": n_back,
        "targets": sum(1 for s in sequence if s["type"] == "target"),
        "near_misses": sum(1 for s in sequence if s["type"] == "near_miss"),
        "non_targets": sum(1 for s in sequence if s["type"] == "non_target"),
        "fillers": sum(1 for s in sequence if s["type"] == "filler"),
    }

    return {
        "sequence": sequence,
        "n_back": n_back,
        "seed": seed,
        "stats": stats,
    }


# Pre-generate sequences for 3-back, 4-back, and 6-back conditions
VIGILANCE_3BACK = generate_nback_sequence("vig_3back_v2", length=80, n_back=3, near_miss_rate=0.15)
VIGILANCE_4BACK = generate_nback_sequence("vig_4back_v2", length=60, n_back=4, near_miss_rate=0.15)
VIGILANCE_6BACK = generate_nback_sequence("vig_6back_v2", length=80, n_back=6, near_miss_rate=0.18)
