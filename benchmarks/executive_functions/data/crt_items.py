"""
Procedurally Generated Cognitive Reflection Test (CRT) Items.

Replaces classic CRT items (bat-and-ball, lily pad, etc.) that frontier models
score 100% on due to training data contamination.

Each generator function produces a CRT item with randomized numeric parameters
so exact answers differ per run, preventing memorization.

Design principles:
- Each item exploits a specific cognitive trap (System 1 bias)
- Intuitive-wrong answer is compellingly wrong
- Correct answer requires deliberate algebraic/logical reasoning (System 2)
- Parameters are randomized within ranges that keep items solvable and traps compelling

Cognitive trap taxonomy used:
1. Algebraic anchoring — misinterpreting "X more than Y" as Y=remainder
2. Rate independence — assuming parallel workers scale time linearly
3. Exponential growth — halving time for half the quantity
4. Complement misread — "all but N" parsed as subtraction
5. Relative position — overtaking doesn't jump to first
6. Percentage asymmetry — markup then discount doesn't cancel
7. Fence-post error — confusing intervals with counts
8. Boundary escape — net-progress problems where final step escapes
9. Self-reference — pattern continuation overrides embedded answer
10. Page-leaf conflation — confusing two-sided pages with sheets
11. Literal vs. arithmetic — "how many times can you X from Y" 
12. Pieces-vs-cuts — n pieces need n-1 cuts
13. Interval counting — first event at t=0, not t=interval
14. Denomination irrelevance — a dozen is always 12
15. Total-time shortcut — sum via total time, not infinite series

References:
- Frederick (2005): The Cognitive Reflection Test
- Kahneman (2011): Thinking, Fast and Slow
- Toplak et al. (2011, 2014): CRT variants and extensions
"""

import random
import math


def _seed_rng(seed=None):
    """Create a seeded RNG for reproducibility."""
    return random.Random(seed)


# ─── Generator Functions ────────────────────────────────────────────

def gen_algebraic_anchor(rng):
    """X and Y together cost T. X costs D more than Y. What does Y cost?
    Trap: answer T-D instead of (T-D)/2."""
    d = rng.choice([20, 25, 30, 35, 40, 45, 50, 60, 70, 80])
    # y should be a nice number; pick y first
    y_times_2 = rng.choice([3, 5, 7, 9, 11, 13])
    y = y_times_2 / 2  # e.g., 1.5, 2.5, 3.5 ...
    total = d + 2 * y
    item_a = rng.choice(["laptop bag", "phone case", "desk lamp", "notebook", "USB drive", "mouse pad"])
    item_b = rng.choice(["charger", "stylus", "adapter", "cable", "stand", "cover"])
    while item_b == item_a:
        item_b = rng.choice(["charger", "stylus", "adapter", "cable", "stand", "cover"])
    total_str = f"{total:.0f}" if total == int(total) else f"{total:.2f}"
    return {
        "question": f"A {item_a} and a {item_b} together cost ${total_str}. The {item_a} costs ${d} more than the {item_b}. How much does the {item_b} cost, in dollars?",
        "intuitive_wrong": str(total - d),
        "correct": f"{y:.2f}" if y != int(y) else str(int(y)),
        "answer_unit": "dollars",
        "explanation": f"Let {item_b} = x. Then {item_a} = x + {d}. So 2x + {d} = {total_str}, x = {y}.",
        "difficulty": "easy",
        "cognitive_trap": "algebraic anchoring — subtracting difference from total instead of solving",
    }


def gen_rate_independence(rng):
    """If N workers do N items in T time, how long for M workers to do M items?
    Trap: answer M (scaling linearly)."""
    n = rng.choice([4, 5, 6, 7, 8])
    t = rng.choice([4, 5, 6, 7, 8, 10, 12, 15])
    m = rng.choice([50, 75, 100, 150, 200, 500])
    worker = rng.choice(["printers", "machines", "ovens", "assemblers", "robots", "looms"])
    product = rng.choice(["parts", "batches", "units", "copies", "items", "rolls"])
    return {
        "question": f"If {n} {worker} can produce {n} {product} in {t} minutes, how many minutes would it take {m} {worker} to produce {m} {product}?",
        "intuitive_wrong": str(m),
        "correct": str(t),
        "answer_unit": "minutes",
        "explanation": f"Each worker produces 1 item in {t} minutes. {m} workers produce {m} items in {t} minutes.",
        "difficulty": "easy",
        "cognitive_trap": "rate independence — assuming parallel workers scale time linearly",
    }


def gen_exponential_growth(rng):
    """Doubles daily, fills container in D days. When is it half full?
    Trap: D/2."""
    d = rng.choice([20, 24, 28, 36, 40, 48, 50, 60])
    organism = rng.choice(["bacteria colony", "moss patch", "mold culture", "algae bloom", "fungus cluster", "lichen patch"])
    container = rng.choice(["petri dish", "tank", "vessel", "chamber", "pool", "tray"])
    return {
        "question": f"A {organism} in a {container} doubles in size every day. If it fills the entire {container} on day {d}, on what day was it exactly half full?",
        "intuitive_wrong": str(d // 2),
        "correct": str(d - 1),
        "answer_unit": "days",
        "explanation": f"If full on day {d} and it doubles daily, it was half full on day {d - 1}.",
        "difficulty": "easy",
        "cognitive_trap": "exponential growth — halving the time for half the quantity",
    }


def gen_complement_misread(rng):
    """A person has N items. All but K escape/break/leave. How many remain?
    Trap: N - K."""
    n = rng.choice([12, 17, 20, 23, 25, 28, 30, 35])
    k = rng.choice([x for x in [5, 6, 7, 8, 9, 11, 13] if x < n])
    animal = rng.choice(["chickens", "goats", "fish", "rabbits", "ducks", "pigeons"])
    event = rng.choice(["escape", "fly away", "run off", "wander away"])
    return {
        "question": f"A farmer has {n} {animal}. All but {k} {event}. How many {animal} does the farmer still have?",
        "intuitive_wrong": str(n - k),
        "correct": str(k),
        "answer_unit": animal,
        "explanation": f"'All but {k}' means {k} remain.",
        "difficulty": "medium",
        "cognitive_trap": "complement misread — 'all but N' parsed as subtraction N-K",
    }


def gen_percentage_asymmetry(rng):
    """Mark up by P%, then discount by P%. Net change?
    Trap: 0%."""
    p = rng.choice([10, 15, 20, 25, 30, 40, 50])
    net = round((1 + p/100) * (1 - p/100) * 100 - 100, 4)
    context = rng.choice([
        "A store raises all prices", "A website increases fees", "A landlord raises rent",
        "A service raises subscription costs"
    ])
    return {
        "question": f"{context} by {p}%, then offers a {p}% discount on the new price. What is the net percentage change from the original price?",
        "intuitive_wrong": "0",
        "correct": f"{net}",
        "answer_unit": "percent",
        "explanation": f"(1 + {p}/100) × (1 - {p}/100) = {1 - (p/100)**2}. Net change = {net}%.",
        "difficulty": "hard",
        "cognitive_trap": "percentage asymmetry — +P% and -P% seem to cancel",
    }


def gen_fencepost_strikes(rng):
    """Clock takes S seconds for N strikes. How long for M strikes?
    Trap: S * M / N."""
    n = rng.choice([4, 5, 6, 8])
    gap_time = rng.choice([1, 2, 3])
    s = (n - 1) * gap_time
    m = rng.choice([x for x in [9, 10, 11, 12] if x > n])
    correct_time = (m - 1) * gap_time
    naive = s * m // n  # the trap answer
    return {
        "question": f"A bell takes {s} seconds to ring {n} times. How many seconds does it take to ring {m} times?",
        "intuitive_wrong": str(naive),
        "correct": str(correct_time),
        "answer_unit": "seconds",
        "explanation": f"{n} rings = {n-1} gaps of {gap_time}s each. {m} rings = {m-1} gaps = {correct_time}s.",
        "difficulty": "hard",
        "cognitive_trap": "fence-post error — confusing ring count with gap count",
    }


def gen_boundary_escape(rng):
    """Climber gains G per day, loses L per night. Height H. How many days?
    Trap: H / (G - L)."""
    g = rng.choice([3, 4, 5, 6])
    l = rng.choice([x for x in [1, 2, 3, 4] if x < g])
    net = g - l
    # Choose H so that the last day the climber reaches exactly H
    # After d-1 full days: (d-1)*net. On day d climbs g: (d-1)*net + g >= H
    # d >= (H - g)/net + 1
    days_trap_raw = rng.choice([8, 10, 12, 15, 20])
    h = days_trap_raw * net  # This makes the naive answer = days_trap_raw
    # Actual: after (d-1) days at net progress, day d climbs g to reach h
    # (d-1)*net + g >= h  =>  d >= (h - g)/net + 1
    actual = math.ceil((h - g) / net) + 1
    return {
        "question": f"A caterpillar climbs {g} meters up a tree during the day but slides back {l} meter{'s' if l > 1 else ''} at night. The tree is {h} meters tall. How many days does it take to reach the top?",
        "intuitive_wrong": str(days_trap_raw),
        "correct": str(actual),
        "answer_unit": "days",
        "explanation": f"Net progress per full day-night cycle is {net}m. After {actual-1} days: {(actual-1)*net}m. Day {actual}: climbs {g}m to reach {(actual-1)*net + g}m ≥ {h}m.",
        "difficulty": "hard",
        "cognitive_trap": "boundary escape — dividing total by net rate ignores the final day's escape",
    }


def gen_self_reference(rng):
    """X's parent has N children named A, B, C, ... What's the Nth child?
    Trap: next in pattern."""
    names_sets = [
        (["Monday", "Tuesday", "Wednesday"], "Thursday", "days of the week"),
        (["Alpha", "Beta", "Gamma"], "Delta", "Greek letters"),
        (["Spring", "Summer", "Autumn"], "Winter", "seasons"),
        (["Red", "Orange", "Yellow"], "Green", "colors of the rainbow"),
        (["Do", "Re", "Mi"], "Fa", "musical notes"),
        (["Mercury", "Venus", "Earth"], "Mars", "planets"),
    ]
    pattern_names, trap_name, _desc = rng.choice(names_sets)
    child_name = rng.choice(["Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Quinn"])
    n = len(pattern_names) + 1
    return {
        "question": f"{child_name}'s father has {n} children. The first is named {pattern_names[0]}, the second is {pattern_names[1]}, the third is {pattern_names[2]}. What is the name of the {_ordinal(n)} child?",
        "intuitive_wrong": trap_name,
        "correct": child_name,
        "answer_unit": "name",
        "explanation": f"The question says '{child_name}'s father' — the {_ordinal(n)} child is {child_name}.",
        "difficulty": "medium",
        "cognitive_trap": "self-reference — pattern continuation overrides the embedded answer",
    }


def gen_cuts_vs_pieces(rng):
    """Cut a thing into N pieces. How many cuts?
    Trap: N."""
    n = rng.choice([4, 5, 6, 7, 8, 10, 12])
    obj = rng.choice(["log", "pipe", "ribbon", "plank", "rod", "wire", "board"])
    return {
        "question": f"A {obj} is cut into {n} equal pieces. How many cuts were made?",
        "intuitive_wrong": str(n),
        "correct": str(n - 1),
        "answer_unit": "cuts",
        "explanation": f"N pieces require N-1 cuts. {n} pieces = {n - 1} cuts.",
        "difficulty": "easy",
        "cognitive_trap": "pieces-vs-cuts — equating piece count with cut count",
    }


def gen_interval_counting(rng):
    """Take N pills, one every T minutes. How long to finish?
    Trap: N * T."""
    n = rng.choice([4, 5, 6, 7, 8])
    t = rng.choice([15, 20, 25, 30, 40, 45])
    total_correct = (n - 1) * t
    total_trap = n * t
    medicine = rng.choice(["tablets", "capsules", "doses", "pills"])
    return {
        "question": f"A doctor gives you {n} {medicine} and tells you to take one every {t} minutes. How many minutes does it take to finish all {n}?",
        "intuitive_wrong": str(total_trap),
        "correct": str(total_correct),
        "answer_unit": "minutes",
        "explanation": f"Take first at t=0, last at t={(n-1)}×{t}={total_correct} minutes.",
        "difficulty": "medium",
        "cognitive_trap": "interval counting — forgetting first dose is at t=0",
    }


def gen_dozen_denomination(rng):
    """If there are 12 X-cent stamps in a dozen, how many Y-cent stamps in a dozen?
    Trap: 12 * X / Y."""
    x = rng.choice([1, 2, 3, 5])
    y_choices = [v for v in [1, 2, 3, 5, 10, 15, 20, 25, 50] if v != x]
    y = rng.choice(y_choices)
    trap = 12 * x // y if y != 0 else 6
    return {
        "question": f"If there are 12 {x}-cent stamps in a dozen, how many {y}-cent stamps are in a dozen?",
        "intuitive_wrong": str(trap),
        "correct": "12",
        "answer_unit": "stamps",
        "explanation": f"A dozen is always 12, regardless of the denomination of the stamps.",
        "difficulty": "medium",
        "cognitive_trap": "denomination irrelevance — dividing by value ratio",
    }


def gen_total_time_shortcut(rng):
    """Two objects approach each other. A third moves between them. How far does the third travel?
    Trap: complex infinite series instead of simple total-time calculation."""
    d = rng.choice([100, 150, 200, 300, 400, 500])
    v_each = rng.choice([25, 30, 40, 50, 60])
    v_fly = rng.choice([x for x in [60, 75, 80, 90, 100, 120, 150] if x > v_each])
    meet_time = d / (2 * v_each)
    fly_dist = v_fly * meet_time
    # Make sure fly_dist is clean
    if fly_dist != int(fly_dist):
        # Retry with values that give clean answer
        d = 200
        v_each = 50
        v_fly = 75
        meet_time = d / (2 * v_each)
        fly_dist = v_fly * meet_time
    vehicle = rng.choice(["cyclists", "cars", "trains", "boats", "runners"])
    flyer = rng.choice(["bird", "drone", "bee", "butterfly", "messenger"])
    return {
        "question": f"Two {vehicle} start {d} km apart and travel toward each other, each at {v_each} km/h. A {flyer} starts at one and flies back and forth between them at {v_fly} km/h until they meet. How far does the {flyer} travel in total?",
        "intuitive_wrong": "complicated",
        "correct": str(int(fly_dist) if fly_dist == int(fly_dist) else fly_dist),
        "answer_unit": "km",
        "explanation": f"They meet in {d}/(2×{v_each}) = {meet_time} hours. {flyer} travels {v_fly} × {meet_time} = {fly_dist} km.",
        "difficulty": "hard",
        "cognitive_trap": "total-time shortcut — attempting infinite series instead of simple time × speed",
    }


def gen_brick_weight(rng):
    """A brick weighs W kg plus half a brick. How much does the brick weigh?
    Trap: W + W/2 = 1.5W."""
    w = rng.choice([1, 2, 3, 4, 5])
    correct = 2 * w
    trap = w + w  # Actually the trap is W * 1.5
    trap_val = w * 1.5
    return {
        "question": f"A crate weighs {w} kg plus half a crate. How much does the crate weigh in kg?",
        "intuitive_wrong": str(trap_val if trap_val == int(trap_val) else trap_val),
        "correct": str(correct),
        "answer_unit": "kg",
        "explanation": f"Let crate = c. c = {w} + c/2 → c/2 = {w} → c = {correct} kg.",
        "difficulty": "medium",
        "cognitive_trap": "treating 'half a crate' as half the given weight instead of half the unknown",
    }


def gen_meeting_point(rng):
    """Person A starts at city X, person B at city Y, D apart. A walks at Va, B at Vb.
    When they meet, who is closer to city X?
    Trap: the slower one (thinking they haven't gone as far)."""
    return {
        "question": "Two hikers start walking toward each other from opposite ends of a 60 km trail. Hiker A walks at 4 km/h and Hiker B walks at 6 km/h. When they meet, which hiker is closer to Hiker A's starting point?",
        "intuitive_wrong": "Hiker B",
        "correct": "same",
        "answer_unit": "distance",
        "explanation": "When they meet, they are at the SAME point — both are equally close to any location. The question is a trick: both are at the meeting point.",
        "difficulty": "medium",
        "cognitive_trap": "computing distances instead of realizing they meet at the same point",
    }


def gen_half_of_half(rng):
    """You take half of a collection, then half of what's left, etc. 
    After K halvings, what fraction of original is left?
    Trap: 1/(2K) instead of 1/2^K."""
    k = rng.choice([3, 4, 5])
    correct_frac_denom = 2 ** k
    trap_denom = 2 * k
    item = rng.choice(["a pile of coins", "a stack of cards", "a bag of marbles", "a jar of candies"])
    return {
        "question": f"You have {item}. You remove half. Then you remove half of what remains. You do this {k} times total. What fraction of the original amount is left?",
        "intuitive_wrong": f"1/{trap_denom}",
        "correct": f"1/{correct_frac_denom}",
        "answer_unit": "fraction",
        "explanation": f"Each halving multiplies remainder by 1/2. After {k} halvings: (1/2)^{k} = 1/{correct_frac_denom}.",
        "difficulty": "hard",
        "cognitive_trap": "linear vs exponential — assuming 1/(2×K) instead of 1/2^K",
    }


# ─── Helpers ────────────────────────────────────────────────────────

def _ordinal(n):
    """Return ordinal string for integer n."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


# ─── All Generators ─────────────────────────────────────────────────

GENERATORS = [
    gen_algebraic_anchor,
    gen_rate_independence,
    gen_exponential_growth,
    gen_complement_misread,
    gen_percentage_asymmetry,
    gen_fencepost_strikes,
    gen_boundary_escape,
    gen_self_reference,
    gen_cuts_vs_pieces,
    gen_interval_counting,
    gen_dozen_denomination,
    gen_total_time_shortcut,
    gen_brick_weight,
    gen_meeting_point,
    gen_half_of_half,
]


def generate_crt_items(seed=42, n_items=15):
    """
    Generate n_items CRT items with randomized parameters.

    Args:
        seed: Random seed for reproducibility. Change seed to get different
              numeric parameters while keeping the same cognitive trap structures.
        n_items: Number of items to generate (max = len(GENERATORS) = 15).

    Returns:
        List of CRT item dicts compatible with the benchmark task.
    """
    rng = _seed_rng(seed)
    items = []
    generators = GENERATORS[:n_items]

    for i, gen_func in enumerate(generators):
        item = gen_func(rng)
        item["id"] = f"CRT{i+1:02d}"
        items.append(item)

    return items


# ─── Default items (seed=42 for reproducibility) ───────────────────

CRT_ITEMS = generate_crt_items(seed=42, n_items=15)
