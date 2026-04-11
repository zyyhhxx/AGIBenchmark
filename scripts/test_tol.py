#!/usr/bin/env python3
"""Test ToL benchmark against 3 Bedrock models using the runner's approach."""
import sys, os, json, time
os.environ.pop('AWS_PROFILE', None)
os.environ['PYTHONUNBUFFERED'] = '1'

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'benchmarks', 'executive_functions'))

import boto3, numpy as np
from botocore.config import Config

config = Config(read_timeout=120, retries={"max_attempts": 3, "mode": "adaptive"})
client = boto3.Session(region_name='us-east-1').client('bedrock-runtime', config=config)

# Import problem data and parsing functions directly (avoid module-level run)
from data.tol_problems import TOL_PROBLEMS, state_str, PEG_CAPACITY, state_to_tuple
from copy import deepcopy
import re

TIERS = {
    "easy":   {"depths": [2],    "weight": 0.20},
    "medium": {"depths": [3],    "weight": 0.30},
    "hard":   {"depths": [4, 5], "weight": 0.50},
}

def parse_moves(text):
    if not isinstance(text, str):
        text = str(text)
    parsed = []
    moves_match = re.search(r'MOVES:\s*(.+)', text, re.IGNORECASE)
    search_text = moves_match.group(1) if moves_match else text
    direct = re.findall(r'\b([ABC])\s*(?:→|->|—>|=>|to)\s*([ABC])\b', search_text, re.IGNORECASE)
    if direct:
        return [(s.upper(), d.upper()) for s, d in direct]
    from_to = re.findall(r'from\s+(?:peg\s+)?([ABC])\s+to\s+(?:peg\s+)?([ABC])', search_text, re.IGNORECASE)
    if from_to:
        return [(s.upper(), d.upper()) for s, d in from_to]
    peg_to = re.findall(r'peg\s+([ABC])\s+to\s+peg\s+([ABC])', search_text, re.IGNORECASE)
    if peg_to:
        return [(s.upper(), d.upper()) for s, d in peg_to]
    return parsed

def validate_solution(start_state, goal_state, moves):
    state = deepcopy(start_state)
    errors = []
    for i, (src, dst) in enumerate(moves):
        if not state.get(src) or len(state[src]) == 0:
            errors.append(f"Move {i+1}: Peg {src} is empty")
            continue
        if len(state.get(dst, [])) >= PEG_CAPACITY.get(dst, 0):
            errors.append(f"Move {i+1}: Peg {dst} is full")
            continue
        ball = state[src].pop()
        state[dst].append(ball)
    reached_goal = state_to_tuple(state) == state_to_tuple(goal_state)
    return {"reached_goal": reached_goal and len(errors) == 0, "n_moves": len(moves), "errors": errors}

def call_model(model_id, text):
    if "anthropic" in model_id:
        body = json.dumps({"anthropic_version": "bedrock-2023-05-31", "max_tokens": 2048, "messages": [{"role": "user", "content": text}]})
        resp = client.invoke_model(modelId=model_id, body=body, contentType="application/json")
        return json.loads(resp["body"].read())["content"][0]["text"]
    elif "amazon" in model_id:
        body = json.dumps({"messages": [{"role": "user", "content": [{"text": text}]}], "inferenceConfig": {"maxTokens": 2048}})
        resp = client.invoke_model(modelId=model_id, body=body, contentType="application/json")
        return json.loads(resp["body"].read())["output"]["message"]["content"][0]["text"]
    elif "mistral" in model_id:
        body = json.dumps({"messages": [{"role": "user", "content": text}], "max_tokens": 2048})
        resp = client.invoke_model(modelId=model_id, body=body, contentType="application/json")
        return json.loads(resp["body"].read())["choices"][0]["message"]["content"]

MODELS = [
    ("Claude Opus 4.6", "us.anthropic.claude-opus-4-6-v1"),
    ("Nova Pro", "us.amazon.nova-pro-v1:0"),
    ("Ministral 3B", "mistral.ministral-3-3b-instruct"),
]

print(f"Total problems: {len(TOL_PROBLEMS)}")
print(f"Depths: {sorted(set(p['optimal_moves'] for p in TOL_PROBLEMS))}")

scores = {}
for label, model_id in MODELS:
    print(f"\n{'='*60}")
    print(f"Testing: {label}")
    print(f"{'='*60}", flush=True)
    
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
            f"Think step by step. Plan your moves carefully, then list them.\n\n"
            f"Format your answer as:\nMOVES: A→B, C→A, B→C\n\n"
            f"Each move is SRC→DST where SRC and DST are peg letters (A, B, or C).\n"
            f"List moves in order, separated by commas."
        )
        
        try:
            raw = call_model(model_id, prompt)
            moves = parse_moves(raw)
            validation = validate_solution(start, goal, moves)
            
            if validation["reached_goal"]:
                optimality = min(1.0, optimal / max(validation["n_moves"], 1))
            else:
                optimality = 0.0
            
            tier = "easy" if optimal in [2] else "medium" if optimal in [3] else "hard"
            tier_scores[tier].append(optimality)
            
            status = "✓" if validation["reached_goal"] else "✗"
            print(f"  {problem['problem_id']}: {status} parsed={len(moves)} goal={validation['reached_goal']} opt={optimality:.2f}", flush=True)
            if not moves:
                print(f"    RAW (first 200): {raw[:200]}", flush=True)
        except Exception as e:
            print(f"  {problem['problem_id']}: ERROR {e}", flush=True)
            tier = "easy" if optimal in [2] else "medium" if optimal in [3] else "hard"
            tier_scores[tier].append(0.0)
    
    tier_means = {t: float(np.mean(s)) if s else 0.0 for t, s in tier_scores.items()}
    score = sum(TIERS[t]["weight"] * tier_means[t] for t in TIERS)
    scores[label] = round(score, 4)
    
    print(f"\n  Tier means: {tier_means}")
    print(f"  >>> {label} SCORE: {scores[label]}", flush=True)
    time.sleep(2)

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
valid = [v for v in scores.values() if v is not None]
for label, score in scores.items():
    print(f"  {label}: {score}")
if len(valid) >= 2:
    print(f"\n  Mean: {np.mean(valid):.4f}")
    print(f"  Std:  {np.std(valid):.4f}")
    print(f"  Range: {max(valid) - min(valid):.4f}")
