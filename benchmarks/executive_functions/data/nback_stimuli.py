"""
Stimuli generator for N-back working memory benchmark.

Generates sequences of items where the model must identify when the current
item matches the one N positions back. Varies N from 1 to 3.
"""

import random
import string

def generate_nback_sequence(n_level: int, length: int = 60, target_rate: float = 0.25, seed: int = None):
    """
    Generate an N-back sequence.
    
    Args:
        n_level: N value (1, 2, or 3)
        length: total items in sequence
        target_rate: approximate proportion of target (match) trials
        seed: random seed
    
    Returns list of dicts with item, is_target, position.
    """
    if seed is not None:
        random.seed(seed)
    
    # Use single uppercase letters as stimuli
    alphabet = list("BCDFGHJKLMNPQRSTVWXZ")  # 20 consonants (avoid vowels to prevent words)
    
    sequence = []
    n_targets = int(length * target_rate)
    
    # Pre-decide which positions will be targets (must be >= n_level)
    possible_target_positions = list(range(n_level, length))
    random.shuffle(possible_target_positions)
    target_positions = set(possible_target_positions[:n_targets])
    
    # Generate sequence
    items = []
    for i in range(length):
        if i in target_positions and i >= n_level:
            # This should be a target: match the item N steps back
            items.append(items[i - n_level])
        else:
            # Non-target: pick a letter that does NOT match N steps back
            if i >= n_level:
                avoid = items[i - n_level]
                choices = [c for c in alphabet if c != avoid]
            else:
                choices = alphabet
            items.append(random.choice(choices))
    
    # Build trial list
    trials = []
    for i, item in enumerate(items):
        is_target = (i >= n_level and items[i] == items[i - n_level])
        trials.append({
            "position": i + 1,
            "item": item,
            "is_target": is_target,
            "n_back_item": items[i - n_level] if i >= n_level else None,
        })
    
    return trials


def generate_all_nback_sequences(seed=42):
    """Generate sequences for N=1, 2, 3."""
    sequences = {}
    for n in [1, 2, 3]:
        sequences[n] = generate_nback_sequence(
            n_level=n, length=60, target_rate=0.25, seed=seed + n
        )
    return sequences


NBACK_SEQUENCES = generate_all_nback_sequences(seed=42)

if __name__ == "__main__":
    for n, seq in NBACK_SEQUENCES.items():
        targets = sum(1 for t in seq if t["is_target"])
        print(f"N={n}: {len(seq)} items, {targets} targets ({targets/len(seq)*100:.1f}%)")
        print(f"  First 15: {' '.join(t['item'] for t in seq[:15])}")
        print(f"  Targets at positions: {[t['position'] for t in seq if t['is_target']][:10]}...")
