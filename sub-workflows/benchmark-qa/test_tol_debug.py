"""Debug script: run ToL benchmark against one model, log raw responses and parsing."""
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace-agi-bench/repo')

import json
import boto3
from botocore.config import Config
from copy import deepcopy

from benchmarks.executive_functions.data.tol_problems import (
    TOL_PROBLEMS, state_str, PEG_CAPACITY, state_to_tuple
)
# Import parse_moves/validate_solution/TIERS directly to avoid relative import issue in task_tol.py
import importlib.util, types
spec = importlib.util.spec_from_file_location('task_tol', '/home/ubuntu/.openclaw/workspace-agi-bench/repo/benchmarks/executive_functions/task_tol.py',
    submodule_search_locations=['/home/ubuntu/.openclaw/workspace-agi-bench/repo/benchmarks/executive_functions'])
# We can't import task_tol directly due to relative imports. Copy the functions we need.
import re
from copy import deepcopy

def parse_moves(text) -> list:
    if not isinstance(text, str):
        text = str(text)
    parsed = []
    moves_match = re.search(r'MOVES:\s*(.+)', text, re.IGNORECASE)
    search_text = moves_match.group(1) if moves_match else text
    direct = re.findall(r'\b([ABC])\s*(?:→|->|—>|=>|to)\s*([ABC])\b', search_text, re.IGNORECASE)
    if direct:
        for src, dst in direct:
            parsed.append((src.upper(), dst.upper()))
        return parsed
    from_to = re.findall(r'from\s+(?:peg\s+)?([ABC])\s+to\s+(?:peg\s+)?([ABC])', search_text, re.IGNORECASE)
    if from_to:
        for src, dst in from_to:
            parsed.append((src.upper(), dst.upper()))
        return parsed
    peg_to = re.findall(r'peg\s+([ABC])\s+to\s+peg\s+([ABC])', search_text, re.IGNORECASE)
    if peg_to:
        for src, dst in peg_to:
            parsed.append((src.upper(), dst.upper()))
        return parsed
    return parsed

def validate_solution(start_state, goal_state, moves) -> dict:
    state = deepcopy(start_state)
    errors = []
    for i, (src, dst) in enumerate(moves):
        if not state.get(src) or len(state[src]) == 0:
            errors.append(f'Move {i+1}: Peg {src} is empty')
            continue
        if len(state.get(dst, [])) >= PEG_CAPACITY.get(dst, 0):
            errors.append(f'Move {i+1}: Peg {dst} is full')
            continue
        ball = state[src].pop()
        state[dst].append(ball)
    reached_goal = state_to_tuple(state) == state_to_tuple(goal_state)
    return {'valid': len(errors) == 0, 'reached_goal': reached_goal and len(errors) == 0, 'n_moves': len(moves), 'errors': errors, 'final_state': state}

TIERS = {'easy': {'depths': [2], 'weight': 0.20}, 'medium': {'depths': [3], 'weight': 0.30}, 'hard': {'depths': [4, 5], 'weight': 0.50}}

# Bedrock client
session = boto3.Session(region_name='us-east-1')
client = session.client('bedrock-runtime', config=Config(read_timeout=120, retries={'max_attempts': 3}))

MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"

def call_llm(prompt: str) -> str:
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    })
    resp = client.invoke_model(modelId=MODEL_ID, body=body)
    result = json.loads(resp['body'].read())
    return result['content'][0]['text']

import numpy as np

tier_scores = {"easy": [], "medium": [], "hard": []}
results = []

# Test only a subset for speed: 2 per depth
test_problems = []
for depth in [2, 3, 4, 5]:
    depth_problems = [p for p in TOL_PROBLEMS if p['optimal_moves'] == depth]
    test_problems.extend(depth_problems[:2])

print(f"Testing {len(test_problems)} problems against {MODEL_ID}")
print("=" * 80)

for problem in test_problems:
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
        f"Think step by step. Plan your moves carefully, then list them.\n\n"
        f"Format your answer as:\n"
        f"MOVES: A→B, C→A, B→C\n\n"
        f"Each move is SRC→DST where SRC and DST are peg letters (A, B, or C).\n"
        f"List moves in order, separated by commas."
    )

    try:
        raw = call_llm(prompt)
    except Exception as e:
        print(f"\n{problem['problem_id']}: ERROR calling LLM: {e}")
        continue

    moves = parse_moves(raw)
    validation = validate_solution(start, goal, moves)

    if validation["reached_goal"]:
        optimality = min(1.0, optimal / max(validation["n_moves"], 1))
    else:
        optimality = 0.0

    # Assign tier
    if optimal in TIERS["easy"]["depths"]:
        tier_scores["easy"].append(optimality)
    elif optimal in TIERS["medium"]["depths"]:
        tier_scores["medium"].append(optimality)
    else:
        tier_scores["hard"].append(optimality)

    print(f"\n--- {problem['problem_id']} (optimal={optimal}) ---")
    print(f"RAW RESPONSE (first 500 chars):\n{raw[:500]}")
    print(f"PARSED MOVES: {moves}")
    print(f"VALIDATION: reached_goal={validation['reached_goal']}, n_moves={validation['n_moves']}, errors={validation['errors']}")
    print(f"OPTIMALITY: {optimality}")

# Summary
print("\n" + "=" * 80)
print("TIER SUMMARY:")
for tier_name, scores in tier_scores.items():
    mean = np.mean(scores) if scores else 0.0
    print(f"  {tier_name}: scores={[round(s,3) for s in scores]}, mean={mean:.4f}")

score = sum(TIERS[t]["weight"] * (np.mean(tier_scores[t]) if tier_scores[t] else 0.0) for t in TIERS)
print(f"\nCOMPOSITE SCORE: {score:.4f}")
