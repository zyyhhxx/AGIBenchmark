"""
Executive Functions Benchmark 2: Tower of London (ToL) Planning

Tests planning ability — a core executive function component.

The model is given an initial arrangement of 3 colored balls on 3 pegs (with
capacity constraints) and a goal state. It must plan a sequence of moves to
reach the goal in the minimum number of moves.

Cognitive Science Basis:
- Tower of London (Shallice, 1982)
- Planning is a "look-ahead" executive process (Owen et al., 1990)
- Difficulty scales with optimal move depth (3 < 4 < 5 moves)
- Frontal patients show deficits at higher move depths (Shallice, 1982)

Metrics:
- Optimality ratio: mean(optimal_moves / actual_moves) per problem
- Validity rate: proportion of solutions with all legal moves reaching goal
- Depth scaling: does performance degrade at higher depths (as in humans)?

Score = 0.50 * optimality + 0.30 * validity + 0.20 * depth_scaling_bonus

Shortcut Resistance:
- Problems are procedurally generated, not from standard test batteries
- Capacity constraints prevent trivial solutions
- Multiple move depths test genuine planning vs. random search
"""

import kaggle_benchmarks as kbench
import json as _json
def _safe_log(data): print(_json.dumps(data, indent=2, default=str))
from dataclasses import dataclass, field
import numpy as np
import re
from copy import deepcopy
from data.tol_problems import TOL_PROBLEMS, state_str, PEG_CAPACITY, apply_move, get_valid_moves, state_to_tuple


# ─── Structured Output Schema ──────────────────────────────────────

@dataclass
class ToLResponse:
    """Model's planned move sequence."""
    moves: list       # List of moves, each as "X→Y" (e.g., "A→B")
    reasoning: str    # Explanation of planning strategy


# ─── Move Validation ────────────────────────────────────────────────

def parse_moves(moves_raw) -> list:
    """Parse move list from model response into (src, dst) tuples."""
    parsed = []
    if isinstance(moves_raw, str):
        # Try to parse "A→B, B→C" or "A->B\nB->C" etc.
        moves_raw = re.findall(r'([ABC])\s*(?:→|->|to)\s*([ABC])', moves_raw, re.IGNORECASE)
        for src, dst in moves_raw:
            parsed.append((src.upper(), dst.upper()))
    elif isinstance(moves_raw, list):
        for m in moves_raw:
            if isinstance(m, str):
                match = re.search(r'([ABC])\s*(?:→|->|to)\s*([ABC])', m, re.IGNORECASE)
                if match:
                    parsed.append((match.group(1).upper(), match.group(2).upper()))
            elif isinstance(m, (list, tuple)) and len(m) >= 2:
                parsed.append((str(m[0]).upper(), str(m[1]).upper()))
    return parsed


def validate_solution(start_state, goal_state, moves) -> dict:
    """
    Validate a sequence of moves.
    Returns dict with: valid (bool), reached_goal (bool), n_moves, errors list.
    """
    state = deepcopy(start_state)
    errors = []

    for i, (src, dst) in enumerate(moves):
        # Check source peg has balls
        if not state.get(src) or len(state[src]) == 0:
            errors.append(f"Move {i+1}: Peg {src} is empty")
            continue

        # Check destination has capacity
        if len(state.get(dst, [])) >= PEG_CAPACITY.get(dst, 0):
            errors.append(f"Move {i+1}: Peg {dst} is full (capacity {PEG_CAPACITY[dst]})")
            continue

        # Apply move
        ball = state[src].pop()
        state[dst].append(ball)

    reached_goal = state_to_tuple(state) == state_to_tuple(goal_state)

    return {
        "valid": len(errors) == 0,
        "reached_goal": reached_goal and len(errors) == 0,
        "n_moves": len(moves),
        "errors": errors,
        "final_state": state,
    }


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="exec_func_tol")
def exec_func_tol(llm) -> float:
    """
    Tower of London Planning Benchmark.

    Tests multi-step planning by requiring the model to find move sequences
    to rearrange balls on pegs to match a goal state.

    Score = 0.50 * optimality + 0.30 * validity + 0.20 * depth_scaling_bonus

    Cognitive Science Basis: Shallice (1982), Owen et al. (1990).
    Human optimality: ~85% at 3 moves, ~65% at 5 moves.
    """
    results = []
    depth_scores = {3: [], 4: [], 5: []}

    for problem in TOL_PROBLEMS:
        start = problem["start"]
        goal = problem["goal"]
        optimal = problem["optimal_moves"]

        prompt = (
            f"TOWER OF LONDON PUZZLE — {problem['problem_id']}\n\n"
            f"Rules:\n"
            f"- 3 pegs (A, B, C) with capacity limits: A holds 3 balls, B holds 2, C holds 1\n"
            f"- Move only the TOP ball from one peg to another\n"
            f"- Goal: reach the goal state in as FEW moves as possible\n"
            f"- Optimal solution needs {optimal} moves\n\n"
            f"CURRENT STATE:\n{state_str(start)}\n\n"
            f"GOAL STATE:\n{state_str(goal)}\n\n"
            f"Plan your moves carefully. List each move as 'X→Y' (e.g., 'A→B' means "
            f"move top ball from peg A to peg B).\n\n"
            f"Provide your moves as a list and explain your reasoning."
        )

        with kbench.chats.new(f"tol_{problem['problem_id']}"):
            try:
                response = llm.prompt(prompt, schema=ToLResponse)
                moves_raw = response.moves
                reasoning = response.reasoning
            except Exception:
                raw = llm.prompt(prompt)
                moves_raw = raw
                reasoning = raw

        # Parse and validate
        moves = parse_moves(moves_raw)
        validation = validate_solution(start, goal, moves)

        # Compute optimality ratio (capped at 1.0)
        if validation["reached_goal"]:
            optimality = min(1.0, optimal / max(validation["n_moves"], 1))
        else:
            optimality = 0.0

        result = {
            "problem_id": problem["problem_id"],
            "optimal_moves": optimal,
            "model_moves": validation["n_moves"],
            "valid_moves": validation["valid"],
            "reached_goal": validation["reached_goal"],
            "optimality": round(optimality, 4),
            "errors": validation["errors"],
        }
        results.append(result)
        depth_scores[optimal].append(optimality)

    # ── Compute Metrics ──

    # Overall validity rate
    validity = sum(1 for r in results if r["reached_goal"]) / len(results)

    # Overall optimality (only counting valid solutions, but 0 for invalid)
    optimality_scores = [r["optimality"] for r in results]
    mean_optimality = np.mean(optimality_scores)

    # Depth scaling bonus: do scores decrease with depth? (as expected in humans)
    depth_means = {d: np.mean(s) if s else 0 for d, s in depth_scores.items()}
    # Bonus if 3-move > 4-move > 5-move (expected pattern)
    if depth_means[3] > depth_means[4] > depth_means[5]:
        depth_bonus = 1.0  # Shows human-like scaling
    elif depth_means[3] > depth_means[5]:
        depth_bonus = 0.5  # Partial scaling
    else:
        depth_bonus = 0.0  # No scaling or inverse

    # ── Composite Score ──
    score = (
        0.50 * float(mean_optimality) +
        0.30 * float(validity) +
        0.20 * float(depth_bonus)
    )
    score = round(float(np.clip(score, 0, 1)), 4)

    # ── Log ──
    _safe_log({
        "benchmark": "Tower of London",
        "n_problems": len(results),
        "overall_validity": round(float(validity), 4),
        "mean_optimality": round(float(mean_optimality), 4),
        "depth_scaling": {str(d): round(float(m), 4) for d, m in depth_means.items()},
        "depth_bonus": depth_bonus,
        "composite_score": score,
        "per_problem": results,
    })

    return score

exec_func_tol.run(llm=kbench.llm)
