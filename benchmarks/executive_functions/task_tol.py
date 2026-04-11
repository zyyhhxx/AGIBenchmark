"""
Executive Functions Benchmark 2: Tower of London (ToL) Planning

Tests planning ability — a core executive function component.

The model is given an initial arrangement of 3 colored balls on 3 pegs (with
capacity constraints) and a goal state. It must plan a sequence of moves to
reach the goal in the minimum number of moves.

Cognitive Science Basis:
- Tower of London (Shallice, 1982)
- Planning is a "look-ahead" executive process (Owen et al., 1990)
- Difficulty scales with optimal move depth (2 < 3 < 4 < 5 moves)
- Frontal patients show deficits at higher move depths (Shallice, 1982)

Metrics:
- Per-tier mean optimality (optimal_moves / actual_moves if goal reached, else 0)
- Three tiers: Easy (2-move, 0.20), Medium (3-move, 0.30), Hard (4-5 move, 0.50)
- Score = weighted sum of per-tier mean optimality

Shortcut Resistance:
- Problems are procedurally generated, not from standard test batteries
- Capacity constraints prevent trivial solutions
- Multiple move depths test genuine planning vs. random search
"""

import kaggle_benchmarks as kbench
import json as _json
def _safe_log(data): print(_json.dumps(data, indent=2, default=str))
import numpy as np
import re
from copy import deepcopy
from data.tol_problems import TOL_PROBLEMS, state_str, PEG_CAPACITY, apply_move, get_valid_moves, state_to_tuple


# ─── Move Parsing ───────────────────────────────────────────────────

def parse_moves(text) -> list:
    """Parse move list from model response into (src, dst) tuples.
    
    Strategy (ordered by reliability):
    1. Find a MOVES: summary line and parse only that line
    2. Find numbered move lines (Move 1: A→B) and extract one move per line
    3. Find the last compact move list on a single line (A→B, B→C)
    Never fall back to full-text search — that picks up reasoning traces.
    """
    if not isinstance(text, str):
        text = str(text)
    
    _arrow = r'(?:→|->|—>|=>)'
    _move_pat = rf'\b([ABC])\s*{_arrow}\s*([ABC])\b'
    
    # === Strategy 1: MOVES: summary line ===
    moves_match = re.search(r'MOVES:\s*(.+)', text, re.IGNORECASE)
    if moves_match:
        line = moves_match.group(1)
        direct = re.findall(_move_pat, line, re.IGNORECASE)
        if direct:
            return [(s.upper(), d.upper()) for s, d in direct]
    
    # === Strategy 2: Numbered move lines ===
    # Match patterns like "Move 1: A→B", "**Move 1:** A→B", "1. A→B", "Step 1: A→B"
    numbered = re.findall(
        rf'(?:(?:Move|Step)\s*\d+[:\.]?\s*\**\s*|\d+\.\s*){_move_pat}',
        text, re.IGNORECASE
    )
    if numbered:
        return [(s.upper(), d.upper()) for s, d in numbered]
    
    # === Strategy 3: Last compact move list on a single line ===
    # Look for lines containing 2+ comma/space-separated arrow moves
    for line in reversed(text.split('\n')):
        line = line.strip()
        found = re.findall(_move_pat, line, re.IGNORECASE)
        if len(found) >= 2:
            return [(s.upper(), d.upper()) for s, d in found]
    
    # === Strategy 4: Numbered "from X to Y" lines ===
    from_to = re.findall(
        r'(?:Move|Step)\s*\d+[:\.]?.*?from\s+(?:peg\s+)?([ABC])\s+to\s+(?:peg\s+)?([ABC])',
        text, re.IGNORECASE
    )
    if from_to:
        return [(s.upper(), d.upper()) for s, d in from_to]
    
    # === Strategy 5: Last MOVES: line with "from X to Y" ===
    if moves_match:
        line = moves_match.group(1)
        ft = re.findall(r'from\s+(?:peg\s+)?([ABC])\s+to\s+(?:peg\s+)?([ABC])', line, re.IGNORECASE)
        if ft:
            return [(s.upper(), d.upper()) for s, d in ft]
    
    return []


# ─── Move Validation ────────────────────────────────────────────────

def validate_solution(start_state, goal_state, moves) -> dict:
    """
    Validate a sequence of moves.
    Returns dict with: valid (bool), reached_goal (bool), n_moves, errors list.
    """
    state = deepcopy(start_state)
    errors = []

    for i, (src, dst) in enumerate(moves):
        if not state.get(src) or len(state[src]) == 0:
            errors.append(f"Move {i+1}: Peg {src} is empty")
            continue
        if len(state.get(dst, [])) >= PEG_CAPACITY.get(dst, 0):
            errors.append(f"Move {i+1}: Peg {dst} is full (capacity {PEG_CAPACITY[dst]})")
            continue
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


# ─── Tier Configuration ────────────────────────────────────────────

TIERS = {
    "easy":   {"depths": [2],    "weight": 0.20},
    "medium": {"depths": [3],    "weight": 0.30},
    "hard":   {"depths": [4, 5], "weight": 0.50},
}


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="exec_func_tol")
def exec_func_tol(llm) -> float:
    """
    Tower of London Planning Benchmark.

    Tests multi-step planning by requiring the model to find move sequences
    to rearrange balls on pegs to match a goal state.

    Score = weighted sum of per-tier mean optimality:
      0.20 * easy(2-move) + 0.30 * medium(3-move) + 0.50 * hard(4-5 move)

    Cognitive Science Basis: Shallice (1982), Owen et al. (1990).
    Human optimality: ~90% at 2 moves, ~85% at 3 moves, ~65% at 5 moves.
    """
    results = []
    tier_scores = {"easy": [], "medium": [], "hard": []}

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
            f"Think step by step. Plan your moves carefully.\n\n"
            f"CRITICAL: After your reasoning, you MUST end your response with exactly this format on its own line:\n"
            f"MOVES: A→B, C→A, B→C\n\n"
            f"Each move is SRC→DST (peg letter → peg letter). List all moves in order, separated by commas.\n"
            f"The MOVES: line must be the LAST line of your response."
        )

        with kbench.chats.new(f"tol_{problem['problem_id']}"):
            raw = llm.prompt(prompt)

        # Parse and validate
        moves = parse_moves(raw)
        validation = validate_solution(start, goal, moves)

        # Compute optimality ratio
        if validation["reached_goal"]:
            optimality = min(1.0, optimal / max(validation["n_moves"], 1))
        else:
            optimality = 0.0

        # Assign to tier
        if optimal in TIERS["easy"]["depths"]:
            tier_scores["easy"].append(optimality)
        elif optimal in TIERS["medium"]["depths"]:
            tier_scores["medium"].append(optimality)
        else:
            tier_scores["hard"].append(optimality)

        result = {
            "problem_id": problem["problem_id"],
            "optimal_moves": optimal,
            "model_moves": validation["n_moves"],
            "parsed_moves": len(moves),
            "reached_goal": validation["reached_goal"],
            "optimality": round(optimality, 4),
            "errors": validation["errors"],
        }
        results.append(result)

    # ── Compute Weighted Score ──
    tier_means = {}
    for tier_name, cfg in TIERS.items():
        scores = tier_scores[tier_name]
        tier_means[tier_name] = float(np.mean(scores)) if scores else 0.0

    score = sum(TIERS[t]["weight"] * tier_means[t] for t in TIERS)
    score = round(float(np.clip(score, 0, 1)), 4)

    # ── Log ──
    _safe_log({
        "benchmark": "Tower of London",
        "n_problems": len(results),
        "tier_means": {t: round(m, 4) for t, m in tier_means.items()},
        "tier_weights": {t: TIERS[t]["weight"] for t in TIERS},
        "composite_score": score,
        "per_problem": results,
    })

    return score

exec_func_tol.run(llm=kbench.llm)
