"""
Stimuli generator for Tower of London (ToL) planning benchmark.

Generates goal states at varying optimal move depths (3, 4, 5 moves).
Uses 3 pegs and 3 colored balls. Each peg has a capacity constraint:
- Peg A: holds 3 balls
- Peg B: holds 2 balls
- Peg C: holds 1 ball

This matches the classic Shallice (1982) setup.
"""

import random
from collections import deque
from itertools import permutations
from copy import deepcopy

# Pegs with capacity constraints
PEG_CAPACITY = {"A": 3, "B": 2, "C": 1}
BALLS = ["red", "blue", "green"]


def state_to_tuple(state):
    """Convert state dict to hashable tuple."""
    return tuple(tuple(state[p]) for p in ["A", "B", "C"])


def tuple_to_state(t):
    """Convert tuple back to state dict."""
    return {"A": list(t[0]), "B": list(t[1]), "C": list(t[2])}


def get_valid_moves(state):
    """Get all valid moves from current state."""
    moves = []
    pegs = ["A", "B", "C"]
    for src in pegs:
        if not state[src]:  # empty peg
            continue
        ball = state[src][-1]  # top ball
        for dst in pegs:
            if dst == src:
                continue
            if len(state[dst]) < PEG_CAPACITY[dst]:
                moves.append((src, dst, ball))
    return moves


def apply_move(state, move):
    """Apply a move and return new state."""
    src, dst, ball = move
    new_state = deepcopy(state)
    new_state[src].pop()
    new_state[dst].append(ball)
    return new_state


def bfs_optimal(start, goal):
    """Find optimal (shortest) move sequence from start to goal using BFS."""
    start_t = state_to_tuple(start)
    goal_t = state_to_tuple(goal)

    if start_t == goal_t:
        return []

    queue = deque([(start_t, [])])
    visited = {start_t}

    while queue:
        current_t, path = queue.popleft()
        current = tuple_to_state(current_t)

        for move in get_valid_moves(current):
            new_state = apply_move(current, move)
            new_t = state_to_tuple(new_state)

            new_path = path + [move]
            if new_t == goal_t:
                return new_path

            if new_t not in visited:
                visited.add(new_t)
                queue.append((new_t, new_path))

    return None  # unreachable


def generate_all_states():
    """Generate all valid states (3 balls distributed across 3 pegs respecting capacity)."""
    states = []
    pegs = ["A", "B", "C"]

    # Each ball can be on any peg (if capacity allows)
    # We place balls one at a time
    def place_balls(balls_remaining, current_state):
        if not balls_remaining:
            states.append(deepcopy(current_state))
            return

        ball = balls_remaining[0]
        for peg in pegs:
            if len(current_state[peg]) < PEG_CAPACITY[peg]:
                current_state[peg].append(ball)
                place_balls(balls_remaining[1:], current_state)
                current_state[peg].pop()

    place_balls(BALLS, {"A": [], "B": [], "C": []})
    return states


def generate_tol_problems(n_per_depth=5, seed=42):
    """
    Generate Tower of London problems at depths 3, 4, and 5.
    Returns problems grouped by optimal move count.
    """
    random.seed(seed)
    all_states = generate_all_states()

    # Find all pairs with known optimal depths
    problems_by_depth = {3: [], 4: [], 5: []}

    for start in all_states:
        for goal in all_states:
            if state_to_tuple(start) == state_to_tuple(goal):
                continue
            optimal = bfs_optimal(start, goal)
            if optimal and len(optimal) in problems_by_depth:
                problems_by_depth[len(optimal)].append({
                    "start": deepcopy(start),
                    "goal": deepcopy(goal),
                    "optimal_moves": len(optimal),
                    "optimal_solution": [(s, d, b) for s, d, b in optimal],
                })

    # Sample n_per_depth problems from each depth
    problems = []
    for depth in [3, 4, 5]:
        candidates = problems_by_depth[depth]
        random.shuffle(candidates)
        selected = candidates[:n_per_depth]
        for i, p in enumerate(selected):
            p["problem_id"] = f"tol_{depth}move_{i+1}"
        problems.extend(selected)

    return problems


def state_str(state):
    """Human-readable state description."""
    parts = []
    for peg in ["A", "B", "C"]:
        if state[peg]:
            balls = ", ".join(state[peg])
            parts.append(f"Peg {peg}: [{balls}] (bottom→top)")
        else:
            parts.append(f"Peg {peg}: [empty]")
    return "\n".join(parts)


TOL_PROBLEMS = generate_tol_problems(n_per_depth=5, seed=42)

if __name__ == "__main__":
    print(f"Generated {len(TOL_PROBLEMS)} Tower of London problems")
    for p in TOL_PROBLEMS:
        print(f"\n{p['problem_id']} ({p['optimal_moves']} moves):")
        print(f"  Start: {p['start']}")
        print(f"  Goal:  {p['goal']}")
        print(f"  Solution: {p['optimal_solution']}")
