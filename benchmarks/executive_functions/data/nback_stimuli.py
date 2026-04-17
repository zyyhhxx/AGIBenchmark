"""
N-back Working Memory v3 — Harder variant for LLMs.

Changes from v2:
- Levels: 2-back, 3-back, 4-back, 5-back (dropped trivial 1-back)
- Batch presentation: model sees a segment of the sequence and must answer for ALL positions
  (no more giving away the N-back letter in the prompt)
- Transformation N-back: at 4-back and 5-back, half the segments require checking if the
  current letter is the NEXT letter in the alphabet from the N-back letter
- Lure trials: ~15% of non-targets match at N±1 (not N), testing precision of position tracking
- Longer sequences: 80 items for 4-back and 5-back
"""

import random
import hashlib


CONSONANTS = list("BCDFGHJKLMNPQRSTVWXZ")

# For transformation n-back: next letter mapping (wraps Z->B since we skip vowels)
_NEXT_CONSONANT = {}
for i, c in enumerate(CONSONANTS):
    _NEXT_CONSONANT[c] = CONSONANTS[(i + 1) % len(CONSONANTS)]


def generate_nback_v3(n_level: int, length: int, seed: str,
                       target_rate: float = 0.22, lure_rate: float = 0.12,
                       transform: bool = False):
    """
    Generate an N-back sequence with optional lure trials and transformation rule.
    
    Args:
        n_level: N value (2-5)
        length: total items
        seed: string seed for reproducibility
        target_rate: fraction of targetable positions that are targets
        lure_rate: fraction of non-targets that are lures (match at N±1)
        transform: if True, target = "next consonant after N-back letter"
    """
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    
    n_targetable = length - n_level
    n_targets = int(n_targetable * target_rate)
    n_lures = int((n_targetable - n_targets) * lure_rate)
    
    # Assign positions
    targetable = list(range(n_level, length))
    rng.shuffle(targetable)
    target_positions = set(targetable[:n_targets])
    lure_candidates = [p for p in targetable[n_targets:] if p > n_level]  # lures need N±1
    rng.shuffle(lure_candidates)
    lure_positions = set(lure_candidates[:n_lures])
    
    items = []
    for i in range(length):
        if i < n_level:
            items.append(rng.choice(CONSONANTS))
        elif i in target_positions:
            ref = items[i - n_level]
            if transform:
                items.append(_NEXT_CONSONANT[ref])
            else:
                items.append(ref)
        elif i in lure_positions:
            # Lure: match at N-1 or N+1, but NOT at N
            ref_n = items[i - n_level]
            offsets = []
            if i - n_level - 1 >= 0:
                offsets.append(items[i - n_level - 1])  # N+1 back
            if i - n_level + 1 < i:
                offsets.append(items[i - n_level + 1])  # N-1 back
            # Pick a lure letter that differs from ref_n
            valid_lures = [l for l in offsets if l != ref_n]
            if transform:
                valid_lures = [l for l in valid_lures if l != _NEXT_CONSONANT[ref_n]]
            if valid_lures:
                items.append(rng.choice(valid_lures))
            else:
                # Fallback: random non-matching
                avoid = {ref_n}
                if transform:
                    avoid.add(_NEXT_CONSONANT[ref_n])
                pool = [c for c in CONSONANTS if c not in avoid]
                items.append(rng.choice(pool))
        else:
            # Non-target, non-lure
            ref_n = items[i - n_level]
            avoid = {ref_n}
            if transform:
                avoid.add(_NEXT_CONSONANT[ref_n])
            # Also avoid matching at N-1 and N+1 (don't accidentally create lures)
            if i - n_level - 1 >= 0:
                avoid.add(items[i - n_level - 1])
            if i - n_level + 1 < i:
                avoid.add(items[i - n_level + 1])
            pool = [c for c in CONSONANTS if c not in avoid]
            if not pool:
                pool = [c for c in CONSONANTS if c != ref_n]
            items.append(rng.choice(pool))
    
    # Build trials
    trials = []
    for i in range(length):
        if i < n_level:
            trial_type = "filler"
            is_target = False
        elif i in target_positions:
            trial_type = "target"
            is_target = True
        elif i in lure_positions:
            trial_type = "lure"
            is_target = False
        else:
            trial_type = "non_target"
            is_target = False
        
        trials.append({
            "position": i,
            "letter": items[i],
            "type": trial_type,
            "is_target": is_target,
            "n_back_letter": items[i - n_level] if i >= n_level else None,
            "correct_response": "YES" if is_target else "NO",
            "quartile": i * 4 // length,
        })
    
    stats = {
        "n_back": n_level,
        "length": length,
        "transform": transform,
        "targets": sum(1 for t in trials if t["type"] == "target"),
        "lures": sum(1 for t in trials if t["type"] == "lure"),
        "non_targets": sum(1 for t in trials if t["type"] == "non_target"),
    }
    
    return {"sequence": trials, "n_back": n_level, "transform": transform, "stats": stats}


# Generate all conditions
NBACK_V3 = {
    "2back": generate_nback_v3(2, 60, "nback_v3_2back"),
    "3back": generate_nback_v3(3, 60, "nback_v3_3back"),
    "4back": generate_nback_v3(4, 80, "nback_v3_4back"),
    "4back_transform": generate_nback_v3(4, 80, "nback_v3_4back_transform", transform=True),
    "5back": generate_nback_v3(5, 80, "nback_v3_5back"),
    "5back_transform": generate_nback_v3(5, 80, "nback_v3_5back_transform", transform=True),
}
