"""Test ToL benchmark with fixed parser against 3 models."""
import sys, json, re, time
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace-agi-bench/repo')

import boto3
from botocore.config import Config
from copy import deepcopy
import numpy as np

from benchmarks.executive_functions.data.tol_problems import (
    TOL_PROBLEMS, state_str, PEG_CAPACITY, state_to_tuple
)

# Import fixed parse_moves by loading file directly
import importlib.util
_spec = importlib.util.spec_from_file_location(
    'task_tol_mod',
    '/home/ubuntu/.openclaw/workspace-agi-bench/repo/benchmarks/executive_functions/task_tol.py',
    submodule_search_locations=['/home/ubuntu/.openclaw/workspace-agi-bench/repo/benchmarks/executive_functions']
)

# Can't import task_tol due to kbench dependency. Copy the fixed parser.
_arrow = r'(?:→|->|—>|=>)'
_move_pat = rf'\b([ABC])\s*{_arrow}\s*([ABC])\b'

def parse_moves(text) -> list:
    if not isinstance(text, str):
        text = str(text)
    
    # Strategy 1: MOVES: summary line
    moves_match = re.search(r'MOVES:\s*(.+)', text, re.IGNORECASE)
    if moves_match:
        line = moves_match.group(1)
        direct = re.findall(_move_pat, line, re.IGNORECASE)
        if direct:
            return [(s.upper(), d.upper()) for s, d in direct]
    
    # Strategy 2: Numbered move lines
    numbered = re.findall(
        rf'(?:(?:Move|Step)\s*\d+[:\.]?\s*\**\s*|\d+\.\s*){_move_pat}',
        text, re.IGNORECASE
    )
    if numbered:
        return [(s.upper(), d.upper()) for s, d in numbered]
    
    # Strategy 3: Last compact move list
    for line in reversed(text.split('\n')):
        line = line.strip()
        found = re.findall(_move_pat, line, re.IGNORECASE)
        if len(found) >= 2:
            return [(s.upper(), d.upper()) for s, d in found]
    
    # Strategy 4: Numbered from X to Y
    from_to = re.findall(
        r'(?:Move|Step)\s*\d+[:\.]?.*?from\s+(?:peg\s+)?([ABC])\s+to\s+(?:peg\s+)?([ABC])',
        text, re.IGNORECASE
    )
    if from_to:
        return [(s.upper(), d.upper()) for s, d in from_to]
    
    return []

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
    return {'valid': len(errors) == 0, 'reached_goal': reached_goal and len(errors) == 0, 'n_moves': len(moves), 'errors': errors}

TIERS = {'easy': {'depths': [2], 'weight': 0.20}, 'medium': {'depths': [3], 'weight': 0.30}, 'hard': {'depths': [4, 5], 'weight': 0.50}}

# Bedrock setup
session = boto3.Session(region_name='us-east-1')
client = session.client('bedrock-runtime', config=Config(read_timeout=120, retries={'max_attempts': 3}))

MODELS = {
    "opus": "us.anthropic.claude-opus-4-6-v1",
    "nova": "us.amazon.nova-pro-v1:0",
    "ministral": "mistral.ministral-3-3b-instruct",
}

def call_llm(model_id, prompt):
    if 'anthropic' in model_id:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        })
        resp = client.invoke_model(modelId=model_id, body=body)
        result = json.loads(resp['body'].read())
        return result['content'][0]['text']
    else:
        # Use converse API for non-Anthropic models
        resp = client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 1024}
        )
        return resp['output']['message']['content'][0]['text']

def run_tol(model_label, model_id):
    tier_scores = {"easy": [], "medium": [], "hard": []}
    results = []
    
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

        try:
            raw = call_llm(model_id, prompt)
            time.sleep(1)
        except Exception as e:
            print(f"  {problem['problem_id']}: ERROR {e}")
            continue

        moves = parse_moves(raw)
        validation = validate_solution(start, goal, moves)

        if validation["reached_goal"]:
            optimality = min(1.0, optimal / max(validation["n_moves"], 1))
        else:
            optimality = 0.0

        if optimal in TIERS["easy"]["depths"]:
            tier_scores["easy"].append(optimality)
        elif optimal in TIERS["medium"]["depths"]:
            tier_scores["medium"].append(optimality)
        else:
            tier_scores["hard"].append(optimality)

        print(f"  {problem['problem_id']}: parsed={len(moves)} moves, goal={validation['reached_goal']}, opt={optimality:.3f}")

    tier_means = {}
    for t in TIERS:
        scores = tier_scores[t]
        tier_means[t] = float(np.mean(scores)) if scores else 0.0

    score = sum(TIERS[t]["weight"] * tier_means[t] for t in TIERS)
    score = round(float(np.clip(score, 0, 1)), 4)
    
    print(f"\n  {model_label} RESULTS:")
    for t in TIERS:
        print(f"    {t}: {[round(s,3) for s in tier_scores[t]]}, mean={tier_means[t]:.4f}")
    print(f"    COMPOSITE: {score}")
    return score

all_scores = {}
for label, mid in MODELS.items():
    print(f"\n{'='*60}\nRunning {label} ({mid})")
    all_scores[label] = run_tol(label, mid)
    time.sleep(3)

print(f"\n{'='*60}")
print("FINAL SUMMARY:")
scores = list(all_scores.values())
for label, s in all_scores.items():
    print(f"  {label}: {s}")
print(f"  std: {np.std(scores):.4f}")
print(f"  mean: {np.mean(scores):.4f}")
print(f"  range: {max(scores) - min(scores):.4f}")
