#!/usr/bin/env python3
"""
Run all 5 Executive Functions benchmarks against all 10 models with Q&A transcript logging.
Benchmarks: crt, nback, task_switch, tol, wcst

Fixes retry bias for CRT and N-back by NOT using schema= parameter.
Uses single LLM call + _strip_think() + regex JSON extraction.
"""
import json, os, sys, time, re, traceback
import numpy as np
from datetime import datetime, timezone
from copy import deepcopy

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'benchmarks', 'executive_functions'))

QA_BASE = os.path.join(REPO, 'sub-workflows', 'benchmark-qa', 'results', 'qa_transcripts')

MODEL_CATALOG = {
    "anthropic.claude-opus-4-6-v1":               ("Claude Opus 4.6",        "us.anthropic.claude-opus-4-6-v1"),
    "anthropic.claude-sonnet-4-6":                 ("Claude Sonnet 4.6",      "us.anthropic.claude-sonnet-4-6"),
    "deepseek.r1-v1:0":                           ("DeepSeek-R1",            "us.deepseek.r1-v1:0"),
    "openai.gpt-oss-120b-1:0":                    ("GPT-OSS-120B",           "openai.gpt-oss-120b-1:0"),
    "meta.llama3-3-70b-instruct-v1:0":            ("Llama 3.3 70B",          "us.meta.llama3-3-70b-instruct-v1:0"),
    "meta.llama4-maverick-17b-instruct-v1:0":     ("Llama 4 Maverick 17B",   "us.meta.llama4-maverick-17b-instruct-v1:0"),
    "amazon.nova-pro-v1:0":                        ("Nova Pro",               "us.amazon.nova-pro-v1:0"),
    "mistral.ministral-3-3b-instruct":            ("Ministral 3B",           "mistral.ministral-3-3b-instruct"),
    "qwen.qwen3-next-80b-a3b":                    ("Qwen3 Next 80B",         "qwen.qwen3-next-80b-a3b"),
    "zai.glm-4.7":                                 ("GLM 4.7",                "zai.glm-4.7"),
}

import boto3
from botocore.config import Config

def make_client(timeout=300):
    cfg = Config(read_timeout=timeout, connect_timeout=30, retries={'max_attempts': 0})
    return boto3.Session(region_name='us-east-1').client('bedrock-runtime', config=cfg)

bclient = make_client(300)

def _strip_think(text):
    """Strip <think>...</think> tags from response."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def call_bedrock(invoke_id, prompt, timeout=300, max_retries=3):
    for attempt in range(max_retries + 1):
        try:
            cl = make_client(timeout) if timeout > 300 else bclient
            resp = cl.converse(
                modelId=invoke_id,
                messages=[{'role': 'user', 'content': [{'text': prompt}]}],
                inferenceConfig={'maxTokens': 4096, 'temperature': 0.0}
            )
            content = resp['output']['message']['content']
            for block in content:
                if 'text' in block:
                    return block['text']
            for block in content:
                if 'reasoningContent' in block:
                    rt = block['reasoningContent']
                    if isinstance(rt, dict) and 'reasoningText' in rt:
                        return rt['reasoningText'].get('text', str(rt))
                    return str(rt)
            return str(content)
        except Exception as e:
            err = str(e)
            retryable = any(k in err for k in ['429', 'Throttl', 'Too many', 'Rate', 'ServiceUnavailable', 'Timeout', 'ReadTimeout'])
            if retryable and attempt < max_retries:
                delay = 5 * (2 ** attempt)
                print(f"    [retry {attempt+1}] {err[:80]}... waiting {delay}s")
                time.sleep(delay)
            else:
                raise


# ═══════════════════════════════════════════════════════════════
# BENCHMARK: CRT
# ═══════════════════════════════════════════════════════════════
from data.crt_items import CRT_ITEMS

# Inline from task_crt.py to avoid module-level .run() trigger
def extract_answer_from_text(text):
    text = text.strip()
    patterns = [
        r'(?:answer|result)\s*(?:is|:)\s*[\*\#]*\s*([^\n\*#]{1,50})',
        r'(?:^|\n)\s*[\*\#]*\s*(\d+(?:\.\d+)?(?:/\d+)?)\s*(?:$|\n|[\*\#])',
        r'(?:=\s*)(\d+(?:\.\d+)?(?:/\d+)?)',
        r'\*\*(\d+(?:\.\d+)?(?:/\d+)?)\*\*',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip().strip('*#')
    if len(text) < 50:
        return text
    m = re.search(r'(\d+(?:\.\d+)?(?:/\d+)?)', text)
    if m:
        return m.group(1)
    return text[:50]

def crt_normalize_answer(answer):
    answer = answer.strip().lower()
    for prefix in ['$', '£', '€']:
        answer = answer.replace(prefix, '')
    answer = re.sub(r'\s*(dollars?|cents?|minutes?|days?|sheep|position|percent|%|leaves?|times?|name).*$', '', answer, flags=re.IGNORECASE)
    return answer.strip().rstrip('.')

def crt_check_answer(model_answer, correct, intuitive_wrong):
    norm_model = crt_normalize_answer(str(model_answer))
    norm_correct = crt_normalize_answer(str(correct))
    norm_intuitive = crt_normalize_answer(str(intuitive_wrong))
    if norm_model == norm_correct:
        return 'correct'
    try:
        if abs(float(norm_model) - float(norm_correct)) < 0.01:
            return 'correct'
    except (ValueError, TypeError):
        pass
    if norm_correct in norm_model and len(norm_correct) >= 3:
        return 'correct'
    if '/' in norm_correct and '/' in norm_model:
        try:
            c = norm_correct.split('/'); m = norm_model.split('/')
            if abs(float(c[0])/float(c[1]) - float(m[0])/float(m[1])) < 0.01:
                return 'correct'
        except (ValueError, ZeroDivisionError):
            pass
    if norm_model == norm_intuitive:
        return 'intuitive_trap'
    try:
        if abs(float(norm_model) - float(norm_intuitive)) < 0.01:
            return 'intuitive_trap'
    except (ValueError, TypeError):
        pass
    return 'other_wrong'

def run_crt(invoke_id, label, timeout=300):
    """Run CRT benchmark for one model. NO schema= — single call + regex."""
    records = []
    difficulty_correct = {"easy": [], "medium": [], "hard": [], "extreme": []}

    for item in CRT_ITEMS:
        prompt = (
            f"Please answer this question. Give ONLY the numerical answer "
            f"(or a short phrase if non-numerical), your confidence level (0-100), "
            f"and a brief explanation of your reasoning.\n\n"
            f"Respond in this JSON format:\n"
            f'{{"answer": "...", "confidence": 50, "reasoning": "..."}}\n\n'
            f"Question: {item['question']}\n\nThink carefully before answering."
        )
        try:
            raw = call_bedrock(invoke_id, prompt, timeout=timeout)
            cleaned = _strip_think(raw)
            # Try JSON extraction
            m = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if m:
                try:
                    parsed = json.loads(m.group())
                    answer = str(parsed.get("answer", ""))
                    confidence = int(parsed.get("confidence", 50))
                except:
                    answer = extract_answer_from_text(cleaned)
                    confidence = 50
            else:
                answer = extract_answer_from_text(cleaned)
                confidence = 50
        except Exception as e:
            raw = f"ERROR: {e}"
            answer = ""
            confidence = 50

        verdict = crt_check_answer(answer, item['correct'], item['intuitive_wrong'])
        is_correct = verdict == 'correct'
        score_val = 1.0 if is_correct else 0.0
        difficulty_correct[item["difficulty"]].append(score_val)

        record = {
            "question_id": item["id"],
            "prompt": prompt,
            "response": raw[:2000] if isinstance(raw, str) else str(raw)[:2000],
            "parsed_answer": answer[:200],
            "correct_answer": item["correct"],
            "intuitive_wrong": item["intuitive_wrong"],
            "verdict": verdict,
            "confidence": confidence,
            "difficulty": item["difficulty"],
            "score": score_val,
        }
        records.append(record)
        status = "✓" if is_correct else ("⚠" if verdict == "intuitive_trap" else "✗")
        print(f"  {status} {item['id']} [{item['difficulty']:6s}] got='{answer[:30]}' correct='{item['correct']}' trap='{item['intuitive_wrong']}'")
        time.sleep(0.5)

    # Compute composite score
    n = len(records)
    n_correct = sum(1 for r in records if r["verdict"] == "correct")
    n_trap = sum(1 for r in records if r["verdict"] == "intuitive_trap")
    accuracy = n_correct / n
    trap_rate = n_trap / n

    diff_weights = {"easy": 1.0, "medium": 1.5, "hard": 2.0, "extreme": 3.0}
    wc, wt = 0, 0
    for diff, scores in difficulty_correct.items():
        w = diff_weights[diff]
        wc += sum(s * w for s in scores)
        wt += len(scores) * w
    difficulty_bonus = wc / wt if wt > 0 else 0

    correct_confs = [r["confidence"] for r in records if r["verdict"] == "correct"]
    wrong_confs = [r["confidence"] for r in records if r["verdict"] != "correct"]
    if correct_confs and wrong_confs:
        calibration = min(1.0, max(0.0, (np.mean(correct_confs) - np.mean(wrong_confs)) / 100 + 0.5))
    else:
        calibration = 0.5

    composite = round(float(np.clip(
        0.40 * accuracy + 0.30 * (1 - trap_rate) + 0.20 * difficulty_bonus + 0.10 * calibration,
        0, 1)), 4)

    return records, composite, {
        "accuracy": round(accuracy, 4), "trap_rate": round(trap_rate, 4),
        "difficulty_bonus": round(difficulty_bonus, 4), "calibration": round(calibration, 4),
        "difficulty_breakdown": {d: round(np.mean(s), 4) if s else 0 for d, s in difficulty_correct.items()},
    }


# ═══════════════════════════════════════════════════════════════
# BENCHMARK: N-BACK
# ═══════════════════════════════════════════════════════════════
from data.nback_stimuli import NBACK_SEQUENCES

def _dprime(hits, misses, fa, cr):
    hit_rate = (hits + 0.5) / (hits + misses + 1)
    fa_rate = (fa + 0.5) / (fa + cr + 1)
    def norminv(p):
        a = [0, -3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
        b = [0, -5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
        c = [0, -7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
        d = [0, 7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
        p_low = 0.02425
        if p < p_low:
            q = np.sqrt(-2 * np.log(p))
            return (((((c[1]*q+c[2])*q+c[3])*q+c[4])*q+c[5])*q+c[6]) / ((((d[1]*q+d[2])*q+d[3])*q+d[4])*q+1)
        elif p <= 1 - p_low:
            q = p - 0.5; r = q * q
            return (((((a[1]*r+a[2])*r+a[3])*r+a[4])*r+a[5])*r+a[6])*q / (((((b[1]*r+b[2])*r+b[3])*r+b[4])*r+b[5])*r+1)
        else:
            q = np.sqrt(-2 * np.log(1 - p))
            return -(((((c[1]*q+c[2])*q+c[3])*q+c[4])*q+c[5])*q+c[6]) / ((((d[1]*q+d[2])*q+d[3])*q+d[4])*q+1)
    return round(norminv(hit_rate) - norminv(fa_rate), 4)

def run_nback(invoke_id, label, timeout=300):
    """Run N-back benchmark. NO schema= — single call + text parsing."""
    records = []
    level_results = {}

    for n_level in [1, 2, 3]:
        sequence = NBACK_SEQUENCES[n_level]
        hits = misses = fa = cr = 0
        
        for i, trial in enumerate(sequence):
            if i < n_level:
                continue
            context_start = max(0, i - n_level - 1)
            context_items = [sequence[j]["item"] for j in range(context_start, i)]
            current_item = trial["item"]

            prompt = (
                f"{n_level}-BACK TASK — Position {trial['position']}\n\n"
                f"Rule: Say 'MATCH' if the current letter is the SAME as the letter "
                f"that appeared {n_level} position{'s' if n_level > 1 else ''} ago. "
                f"Otherwise say 'NO MATCH'.\n\n"
                f"Recent sequence: {' '.join(context_items)}\n"
                f"Current letter: **{current_item}**\n"
                f"Letter {n_level} back: **{sequence[i - n_level]['item']}**\n\n"
                f"Is this a MATCH or NO MATCH? Answer with just MATCH or NO MATCH."
            )
            try:
                raw = call_bedrock(invoke_id, prompt, timeout=timeout)
                cleaned = _strip_think(raw)
                model_says_match = "match" in cleaned.lower() and "no match" not in cleaned.lower()
            except Exception as e:
                raw = f"ERROR: {e}"
                cleaned = raw
                model_says_match = False

            is_target = trial["is_target"]
            if is_target and model_says_match: hits += 1
            elif is_target and not model_says_match: misses += 1
            elif not is_target and model_says_match: fa += 1
            else: cr += 1

            correct = (is_target == model_says_match)
            record = {
                "question_id": f"nback_{n_level}_{trial['position']}",
                "prompt": prompt,
                "response": raw[:1000] if isinstance(raw, str) else str(raw)[:1000],
                "parsed_answer": "MATCH" if model_says_match else "NO MATCH",
                "correct_answer": "MATCH" if is_target else "NO MATCH",
                "score": 1.0 if correct else 0.0,
                "n_level": n_level,
            }
            records.append(record)
            time.sleep(0.3)

        dp = _dprime(hits, misses, fa, cr)
        level_results[n_level] = {
            "d_prime": dp,
            "hit_rate": round(hits / max(hits + misses, 1), 4),
            "fa_rate": round(fa / max(fa + cr, 1), 4),
            "accuracy": round((hits + cr) / max(hits + misses + fa + cr, 1), 4),
            "hits": hits, "misses": misses, "false_alarms": fa, "correct_rejections": cr,
        }
        print(f"    {n_level}-back: d'={dp:.3f}, acc={level_results[n_level]['accuracy']:.2%}")

    # Composite
    weights = {1: 0.2, 2: 0.3, 3: 0.5}
    composite = round(float(np.clip(
        sum(weights[n] * float(np.clip(level_results[n]["d_prime"] / 4.0, 0, 1)) for n in [1,2,3]),
        0, 1)), 4)

    return records, composite, {"per_level": level_results}


# ═══════════════════════════════════════════════════════════════
# BENCHMARK: TASK SWITCH
# ═══════════════════════════════════════════════════════════════
from data.task_switch_stimuli import TASK_SWITCH_BLOCKS

# Inline from task_switching.py to avoid module-level .run() trigger
def ts_normalize(answer, rule):
    answer = answer.lower().strip()
    if rule == 'digit_sum':
        if 'odd' in answer: return 'odd'
        if 'even' in answer: return 'even'
    else:
        if 'before' in answer: return 'before'
        if 'after' in answer: return 'after'
    return answer

def parse_batch_response(response_text, trials):
    lines = response_text.strip().split('\n')
    answers = []
    for line in lines:
        line = line.strip()
        if not line: continue
        m = re.match(r'^(?:#?\d+[\.\):\-\s]+)\s*(.+)$', line)
        if m:
            ans = m.group(1).strip().rstrip('.,;')
            if len(ans) < 60: answers.append(ans)
        elif len(line) < 20 and any(w in line.lower() for w in ['odd', 'even', 'before', 'after']):
            answers.append(line)
    if len(answers) < len(trials) // 2:
        answers = []
        parts = response_text.replace('\n', ' ').split(',')
        for part in parts:
            part = part.strip().rstrip('.,;')
            m = re.match(r'^(?:#?\d+[\.\):\-\s]+)?\s*(.+)$', part)
            if m:
                ans = m.group(1).strip()
                if len(ans) < 30: answers.append(ans)
    return answers

def run_task_switch(invoke_id, label, timeout=300):
    records = []
    block_results = {}

    for block_name in ["baseline", "slow_switch", "rapid_switch", "random_cue"]:
        trials = TASK_SWITCH_BLOCKS[block_name]
        lines = []
        for i, trial in enumerate(trials):
            lines.append(f"{i+1}. {trial['instruction']}  [Rule: {trial['rule_label']}]")
        items_text = "\n".join(lines)

        if block_name == "baseline":
            intro = ("For each item below, determine if the sum of the number's digits is odd or even.\n"
                     "Answer with exactly ONE word per item: 'odd' or 'even'.\n")
        else:
            intro = ("Classify each item below according to its stated rule.\n"
                     "Rules vary between items — pay close attention!\n\n"
                     "- 'Digit Sum Odd/Even': Is the sum of the number's digits odd or even? Answer 'odd' or 'even'\n"
                     "- 'Letter Before/After M': Does the letter come before or after M in the alphabet? Answer 'before' or 'after'\n\n"
                     "For each item, answer with exactly ONE word on a separate line.\n")

        prompt = f"{intro}\nItems:\n{items_text}\n\nProvide your {len(trials)} answers, one per line, numbered to match."

        try:
            raw = call_bedrock(invoke_id, prompt, timeout=timeout)
            cleaned = _strip_think(raw)
        except Exception as e:
            raw = f"ERROR: {e}"
            cleaned = raw

        answers = parse_batch_response(cleaned, trials)

        n_correct = 0
        for i, trial in enumerate(trials):
            model_answer = ts_normalize(answers[i], trial["rule"]) if i < len(answers) else ""
            correct = (model_answer == trial["correct_answer"])
            if correct: n_correct += 1
            record = {
                "question_id": f"ts_{block_name}_{i}",
                "prompt": prompt[:500],
                "response": raw[:1000] if isinstance(raw, str) else str(raw)[:1000],
                "parsed_answer": model_answer,
                "correct_answer": trial["correct_answer"],
                "score": 1.0 if correct else 0.0,
                "block": block_name,
                "is_switch": trial["is_switch_trial"],
                "rule": trial["rule"],
            }
            records.append(record)

        block_results[block_name] = {
            "accuracy": n_correct / len(trials) if trials else 0,
            "n_correct": n_correct, "n_trials": len(trials),
            "n_parsed": len(answers),
        }
        print(f"    {block_name}: {n_correct}/{len(trials)} correct ({len(answers)} parsed)")
        time.sleep(1)

    # Compute composite
    baseline_acc = block_results["baseline"]["accuracy"]
    slow_acc = block_results["slow_switch"]["accuracy"]
    rapid_acc = block_results["rapid_switch"]["accuracy"]

    all_sw_ok = all_sw_n = all_rp_ok = all_rp_n = 0
    for r in records:
        if r["block"] in ["slow_switch", "rapid_switch", "random_cue"]:
            if r["is_switch"]:
                all_sw_n += 1; all_sw_ok += int(r["score"])
            else:
                all_rp_n += 1; all_rp_ok += int(r["score"])
    sw_acc = all_sw_ok / max(all_sw_n, 1)
    rp_acc = all_rp_ok / max(all_rp_n, 1)
    sw_cost = rp_acc - sw_acc
    sw_metric = max(0.0, 1.0 - 2.0 * max(0, sw_cost))

    composite = round(float(np.clip(0.15*baseline_acc + 0.25*slow_acc + 0.35*rapid_acc + 0.25*sw_metric, 0, 1)), 4)
    return records, composite, {"blocks": block_results, "switch_cost": round(sw_cost, 4)}


# ═══════════════════════════════════════════════════════════════
# BENCHMARK: TOWER OF LONDON
# ═══════════════════════════════════════════════════════════════
from data.tol_problems import TOL_PROBLEMS, state_str, PEG_CAPACITY, state_to_tuple

# Inline from task_tol.py
_arrow = r'(?:→|->|—>|=>)'
_move_pat = rf'\b([ABC])\s*{_arrow}\s*([ABC])\b'

def parse_moves(text):
    if not isinstance(text, str): text = str(text)
    moves_match = re.search(r'MOVES:\s*(.+)', text, re.IGNORECASE)
    if moves_match:
        line = moves_match.group(1)
        direct = re.findall(_move_pat, line, re.IGNORECASE)
        if direct: return [(s.upper(), d.upper()) for s, d in direct]
    numbered = re.findall(rf'(?:(?:Move|Step)\s*\d+[:\.]?\s*\**\s*|\d+\.\s*){_move_pat}', text, re.IGNORECASE)
    if numbered: return [(s.upper(), d.upper()) for s, d in numbered]
    for line in reversed(text.split('\n')):
        line = line.strip()
        found = re.findall(_move_pat, line, re.IGNORECASE)
        if len(found) >= 2: return [(s.upper(), d.upper()) for s, d in found]
    if moves_match:
        line = moves_match.group(1)
        ft = re.findall(r'from\s+(?:peg\s+)?([ABC])\s+to\s+(?:peg\s+)?([ABC])', line, re.IGNORECASE)
        if ft: return [(s.upper(), d.upper()) for s, d in ft]
    return []

def validate_solution(start_state, goal_state, moves):
    state = deepcopy(start_state)
    errors = []
    for i, (src, dst) in enumerate(moves):
        if not state.get(src) or len(state[src]) == 0:
            errors.append(f'Move {i+1}: Peg {src} is empty'); continue
        if len(state.get(dst, [])) >= PEG_CAPACITY.get(dst, 0):
            errors.append(f'Move {i+1}: Peg {dst} is full'); continue
        ball = state[src].pop()
        state[dst].append(ball)
    reached_goal = state_to_tuple(state) == state_to_tuple(goal_state)
    return {'valid': len(errors) == 0, 'reached_goal': reached_goal and len(errors) == 0,
            'n_moves': len(moves), 'errors': errors, 'final_state': state}

TIERS = {'easy': {'depths': [2], 'weight': 0.20}, 'medium': {'depths': [3], 'weight': 0.30}, 'hard': {'depths': [4, 5], 'weight': 0.50}}

def run_tol(invoke_id, label, timeout=300):
    records = []
    tier_scores = {"easy": [], "medium": [], "hard": []}

    for problem in TOL_PROBLEMS:
        start = problem["start"]
        goal = problem["goal"]
        optimal = problem["optimal_moves"]

        prompt = (
            f"TOWER OF LONDON PUZZLE — {problem['problem_id']}\n\n"
            f"Rules:\n- 3 pegs (A, B, C) with capacity limits: A holds 3 balls, B holds 2, C holds 1\n"
            f"- Move only the TOP ball from one peg to another\n"
            f"- Goal: reach the goal state in as FEW moves as possible\n"
            f"- Optimal solution needs {optimal} moves\n\n"
            f"CURRENT STATE:\n{state_str(start)}\n\nGOAL STATE:\n{state_str(goal)}\n\n"
            f"Think step by step. Plan your moves carefully.\n\n"
            f"CRITICAL: After your reasoning, you MUST end your response with exactly this format on its own line:\n"
            f"MOVES: A→B, C→A, B→C\n\nThe MOVES: line must be the LAST line of your response."
        )
        try:
            raw = call_bedrock(invoke_id, prompt, timeout=timeout)
            cleaned = _strip_think(raw)
        except Exception as e:
            raw = f"ERROR: {e}"
            cleaned = raw

        moves = parse_moves(cleaned)
        validation = validate_solution(deepcopy(start), goal, moves)
        optimality = min(1.0, optimal / max(validation["n_moves"], 1)) if validation["reached_goal"] else 0.0

        tier = "easy" if optimal in [2] else ("medium" if optimal in [3] else "hard")
        tier_scores[tier].append(optimality)

        record = {
            "question_id": problem["problem_id"],
            "prompt": prompt[:500],
            "response": raw[:2000] if isinstance(raw, str) else str(raw)[:2000],
            "parsed_answer": f"{len(moves)} moves: {moves[:10]}",
            "correct_answer": f"optimal={optimal}",
            "score": round(optimality, 4),
            "reached_goal": validation["reached_goal"],
            "n_moves": validation["n_moves"],
            "optimal_moves": optimal,
        }
        records.append(record)
        icon = "✓" if validation["reached_goal"] else "✗"
        print(f"  {icon} {problem['problem_id']} (opt={optimal}): {len(moves)} moves, opt={optimality:.2f}")
        time.sleep(0.5)

    tier_means = {t: float(np.mean(s)) if s else 0.0 for t, s in tier_scores.items()}
    composite = round(float(np.clip(
        0.20 * tier_means["easy"] + 0.30 * tier_means["medium"] + 0.50 * tier_means["hard"],
        0, 1)), 4)
    return records, composite, {"tier_means": {t: round(m, 4) for t, m in tier_means.items()}}


# ═══════════════════════════════════════════════════════════════
# BENCHMARK: WCST
# ═══════════════════════════════════════════════════════════════
from data.wcst_stimuli import WCST_BLOCKS, card_str, REFERENCE_CARDS, _correct_ref

# Inline from task_wcst.py
def _format_block_prompt(block):
    refs = REFERENCE_CARDS
    lines = ['You are taking a card sorting test. There are 4 reference cards:']
    for i, r in enumerate(refs, 1):
        lines.append(f'  Card {i}: {card_str(r)}')
    lines.append('')
    lines.append('For each trial, a target card must be matched to one of the 4 reference cards. '
                 'The matching rule is based on ONE dimension (color, shape, or number), but '
                 'the rule is NOT stated. You must figure it out from the feedback pattern below.')
    lines.append('')
    lines.append('IMPORTANT: The sorting rule may change. Pay close attention to when '
                 'responses start getting \'Incorrect\' feedback — that means the rule '
                 'has changed and you need to figure out the NEW rule.')
    lines.append('')
    if block['history']:
        lines.append('=== Previous trials (with responses and feedback) ===')
        for h in block['history']:
            lines.append(f"Target: {card_str(h['target'])} → Response: Card {h['response']} → {h['feedback']}")
        lines.append('')
    n_test = len(block['test_trials'])
    lines.append(f'=== Your turn: sort the next {n_test} cards ===')
    lines.append(f'Based on the feedback pattern above, determine the CURRENT sorting rule '
                 f'and sort each card. Respond with EXACTLY {n_test} numbers (1-4), one per line.')
    lines.append('')
    for i, t in enumerate(block['test_trials'], 1):
        lines.append(f"Card {i}: {card_str(t['target'])}")
    lines.append('')
    lines.append(f'Your {n_test} answers (one number 1-4 per line):')
    return '\n'.join(lines)

def _parse_responses(raw, n_expected):
    line_answers = []
    for line in raw.strip().split('\n'):
        line = line.strip()
        if re.match(r'^[1-4]$', line):
            line_answers.append(int(line))
    if len(line_answers) >= n_expected:
        return line_answers[-n_expected:]
    answer_pattern = re.findall(r'(?:^|\n)\s*(?:Card\s+\d+[:\.].*?)?\s*\b([1-4])\s*$', raw, re.MULTILINE)
    if len(answer_pattern) >= n_expected:
        return [int(x) for x in answer_pattern[-n_expected:]]
    all_nums = re.findall(r'\b([1-4])\b', raw)
    if len(all_nums) >= n_expected:
        return [int(n) for n in all_nums[-n_expected:]]
    choices = [int(n) for n in all_nums]
    rng = np.random.RandomState(99)
    while len(choices) < n_expected:
        choices.append(int(rng.randint(1, 5)))
    return choices

def run_wcst(invoke_id, label, timeout=300):
    records = []
    blocks = WCST_BLOCKS["blocks"]
    all_results_internal = []

    for block in blocks:
        prompt = _format_block_prompt(block)
        try:
            raw = call_bedrock(invoke_id, prompt, timeout=timeout)
            cleaned = _strip_think(raw)
        except Exception as e:
            raw = f"ERROR: {e}"
            cleaned = raw

        n_test = len(block["test_trials"])
        choices = _parse_responses(cleaned, n_test)

        for trial, choice in zip(block["test_trials"], choices):
            correct = (choice == trial["correct_answer"])
            error_type = None
            if not correct and trial["is_post_shift"] and trial.get("prev_rule"):
                old_ans = _correct_ref(trial["target"], trial["prev_rule"])
                error_type = "perseverative" if choice == old_ans else "non_perseverative"
            elif not correct:
                error_type = "non_perseverative"

            all_results_internal.append({
                "block_id": block["block_id"], "correct": correct, "choice": choice,
                "expected": trial["correct_answer"], "is_post_shift": trial["is_post_shift"],
                "error_type": error_type, "active_rule": trial["active_rule"],
            })
            record = {
                "question_id": f"wcst_b{block['block_id']}_{trial.get('trial_idx', 0)}",
                "prompt": prompt[:500],
                "response": raw[:1000] if isinstance(raw, str) else str(raw)[:1000],
                "parsed_answer": str(choice),
                "correct_answer": str(trial["correct_answer"]),
                "score": 1.0 if correct else 0.0,
                "block_id": block["block_id"],
                "is_post_shift": trial["is_post_shift"],
                "error_type": error_type,
            }
            records.append(record)
        time.sleep(1)

    # Compute composite
    n_total = len(all_results_internal)
    n_correct = sum(1 for r in all_results_internal if r["correct"])
    accuracy = n_correct / n_total if n_total > 0 else 0

    post_shift = [r for r in all_results_internal if r["is_post_shift"]]
    persev = [r for r in post_shift if not r["correct"] and r["error_type"] == "perseverative"]
    persev_rate = len(persev) / len(post_shift) if post_shift else 0.0

    block_accs = {}
    for r in all_results_internal:
        bid = r["block_id"]
        if bid not in block_accs: block_accs[bid] = {"c": 0, "t": 0}
        block_accs[bid]["t"] += 1
        if r["correct"]: block_accs[bid]["c"] += 1
    cats = sum(1 for v in block_accs.values() if v["t"] > 0 and v["c"]/v["t"] >= 0.66)
    cats_norm = cats / len(block_accs) if block_accs else 0

    composite = round(float(np.clip(0.25*accuracy + 0.45*(1-persev_rate) + 0.30*cats_norm, 0, 1)), 4)
    print(f"    acc={accuracy:.2%}, persev={persev_rate:.2%}, cats={cats}/{len(block_accs)}")
    return records, composite, {"accuracy": round(accuracy, 4), "perseveration_rate": round(persev_rate, 4), "categories_norm": round(cats_norm, 4)}


# ═══════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════

BENCHMARKS = {
    "exec_func_crt": run_crt,
    "exec_func_nback": run_nback,
    "exec_func_task_switch": run_task_switch,
    "exec_func_tol": run_tol,
    "exec_func_wcst": run_wcst,
}

def run_benchmark_for_model(benchmark_name, run_fn, model_id, label, invoke_id, timeout):
    out_dir = os.path.join(QA_BASE, benchmark_name)
    os.makedirs(out_dir, exist_ok=True)
    safe_name = model_id.replace(':', '_').replace('/', '_')
    jsonl_path = os.path.join(out_dir, f"{safe_name}.jsonl")
    summary_path = os.path.join(out_dir, f"{safe_name}.summary.json")

    if os.path.exists(summary_path):
        with open(summary_path) as f:
            s = json.load(f)
        if s.get('score') is not None:
            print(f"  SKIP {label} on {benchmark_name} — already scored: {s['score']:.4f}")
            return s['score']

    print(f"\n{'='*60}")
    print(f"Running {benchmark_name} with {label}")
    print(f"{'='*60}")

    start = time.time()
    records, composite, extra = run_fn(invoke_id, label, timeout=timeout)
    elapsed = time.time() - start

    with open(jsonl_path, 'w') as f:
        for r in records:
            f.write(json.dumps(r, default=str) + '\n')

    summary = {
        "model_id": model_id,
        "model_label": label,
        "benchmark": benchmark_name,
        "score": composite,
        "n_items": len(records),
        "n_correct": sum(1 for r in records if r.get("score", 0) >= 0.99),
        "duration_s": round(elapsed, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **extra,
    }
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Score: {composite:.4f} | Time: {elapsed:.1f}s")
    return composite


def main():
    all_scores = {}
    model_order = list(MODEL_CATALOG.keys())

    for bname, run_fn in BENCHMARKS.items():
        print(f"\n\n{'#'*70}")
        print(f"# BENCHMARK: {bname}")
        print(f"{'#'*70}")

        scores = {}
        for model_id in model_order:
            label, invoke_id = MODEL_CATALOG[model_id]
            timeout = 900 if 'deepseek' in model_id else 300
            try:
                score = run_benchmark_for_model(bname, run_fn, model_id, label, invoke_id, timeout)
                scores[model_id] = score
            except Exception as e:
                print(f"  FAILED {label}: {e}")
                traceback.print_exc()
                scores[model_id] = None
            time.sleep(3)

        # Aggregate
        valid = [s for s in scores.values() if s is not None]
        agg = {
            "benchmark": bname,
            "n_models": len(scores), "n_valid": len(valid), "n_failed": len(scores) - len(valid),
            "scores": {mid: {"label": MODEL_CATALOG[mid][0], "score": scores[mid]} for mid in scores},
            "mean": round(float(np.mean(valid)), 4) if valid else None,
            "std": round(float(np.std(valid)), 4) if valid else None,
            "min": round(float(np.min(valid)), 4) if valid else None,
            "max": round(float(np.max(valid)), 4) if valid else None,
            "range": round(float(np.max(valid) - np.min(valid)), 4) if valid else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        out_dir = os.path.join(QA_BASE, bname)
        with open(os.path.join(out_dir, 'aggregate_stats.json'), 'w') as f:
            json.dump(agg, f, indent=2)

        all_scores[bname] = agg

        print(f"\n{'='*60}")
        print(f"AGGREGATE — {bname}")
        print(f"{'='*60}")
        for mid, s in sorted(scores.items(), key=lambda x: x[1] if x[1] is not None else -1, reverse=True):
            lbl = MODEL_CATALOG[mid][0]
            print(f"  {lbl:30s}: {s:.4f}" if s is not None else f"  {lbl:30s}: FAILED")
        print(f"  Mean={agg['mean']}, Std={agg['std']}, Range={agg['range']}, Coverage={agg['n_valid']}/{agg['n_models']}")

    # Final summary
    print(f"\n\n{'#'*70}")
    print(f"# ALL EXEC FUNC BENCHMARKS — FINAL SUMMARY")
    print(f"{'#'*70}")
    for bname, agg in all_scores.items():
        print(f"  {bname:25s}: mean={agg['mean']}, std={agg['std']}, range={agg['range']}, coverage={agg['n_valid']}/{agg['n_models']}")


if __name__ == '__main__':
    main()
