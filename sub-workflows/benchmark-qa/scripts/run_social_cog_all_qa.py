#!/usr/bin/env python3
"""
Run all 4 Social Cognition benchmarks against all 10 models with Q&A transcript logging.
Benchmarks: emotional_prosody, false_belief, pragmatic, sarcasm

Retry bias fix: NO schema= parameter. Single LLM call + _strip_think() + regex JSON extraction.
Backtick fence stripping applied proactively.
"""
import json, os, sys, time, re, traceback
import numpy as np
from datetime import datetime, timezone
from copy import deepcopy

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'benchmarks', 'social_cognition'))

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

def _strip_fences(text):
    """Strip backtick fences and // comments."""
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = text.replace('```', '')
    text = re.sub(r'//.*', '', text)
    return text.strip()

def _parse_json(raw):
    """Strip think tags, fences, comments, then extract JSON object."""
    cleaned = _strip_think(raw)
    cleaned = _strip_fences(cleaned)
    m = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if m:
        return json.loads(m.group())
    return None

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
            retryable = any(k in err for k in ['429', 'Throttl', 'Too many', 'Rate', 'ServiceUnavailable',
                                                  'Timeout', 'ReadTimeout', 'InternalServerException'])
            if retryable and attempt < max_retries:
                delay = 5 * (2 ** attempt)
                print(f"    [retry {attempt+1}] {err[:80]}... waiting {delay}s")
                time.sleep(delay)
            else:
                raise

# ═══════════════════════════════════════════════════════════════════
# Import data modules
# ═══════════════════════════════════════════════════════════════════
sys.path.insert(0, os.path.join(REPO, 'benchmarks', 'social_cognition', 'data'))
from false_belief_scenarios import FALSE_BELIEF_SCENARIOS
from pragmatic_items import PRAGMATIC_ITEMS_DIRECT, PRAGMATIC_ITEMS_INDIRECT, PRAGMATIC_ITEMS_COMPLEX
from sarcasm_items import SARCASM_ITEMS

# Import PROSODY_ITEMS by extracting from task file (it's defined inline)
# We need to import without triggering module-level run
import importlib.util
spec = importlib.util.spec_from_file_location(
    "task_emotional_prosody",
    os.path.join(REPO, 'benchmarks', 'social_cognition', 'task_emotional_prosody.py'),
    submodule_search_locations=[]
)
# Can't import directly due to kbench dependency; parse the items manually
# Instead, let's exec the data portion only
_prosody_ns = {}
prosody_path = os.path.join(REPO, 'benchmarks', 'social_cognition', 'task_emotional_prosody.py')
with open(prosody_path) as f:
    src = f.read()
# Extract just PROSODY_ITEMS, EMOTION_SYNONYMS, EMOTION_KEYWORDS, and helper functions
# by finding the data section and executing it
# Safer: just exec the whole file with kbench mocked
class _MockKbench:
    class chats:
        @staticmethod
        def new(name): return type('ctx', (), {'__enter__': lambda s: s, '__exit__': lambda s,*a: None})()
    @staticmethod
    def task(**kw):
        def dec(fn): fn.run = lambda **k: None; return fn
        return dec
sys.modules['kaggle_benchmarks'] = _MockKbench()
exec(compile(src, prosody_path, 'exec'), _prosody_ns)
PROSODY_ITEMS = _prosody_ns['PROSODY_ITEMS']
EMOTION_SYNONYMS = _prosody_ns['EMOTION_SYNONYMS']
EMOTION_KEYWORDS = _prosody_ns['EMOTION_KEYWORDS']
emotion_match = _prosody_ns['emotion_match']
score_mixed_emotions = _prosody_ns['score_mixed_emotions']
score_masked_emotion = _prosody_ns['score_masked_emotion']
del sys.modules['kaggle_benchmarks']


# ═══════════════════════════════════════════════════════════════════
# BENCHMARK 1: EMOTIONAL PROSODY
# ═══════════════════════════════════════════════════════════════════

def run_emotional_prosody(invoke_id, model_label, timeout=300):
    """Run emotional prosody benchmark for one model."""
    transcripts = []
    results = []

    for item in PROSODY_ITEMS:
        dialogue_text = "\n".join(
            f"Turn {i+1} [{d['speaker']}]: {d['text']}"
            for i, d in enumerate(item["dialogue"])
        )
        prompt = (
            f"Read this dialogue carefully and analyze the emotional tone.\n\n"
            f"Dialogue:\n{dialogue_text}\n\n"
            f"Questions:\n"
            f"1. Is there a significant emotional tone SHIFT in this dialogue? (yes/no)\n"
            f"2. If yes, at which turn number does the shift occur?\n"
            f"3. What was the emotional tone BEFORE the shift?\n"
            f"4. What was the emotional tone AFTER the shift?\n"
            f"5. What triggered the shift?\n\n"
            f"Respond with ONLY a JSON object:\n"
            f'{{\n'
            f'  "has_shift": true/false,\n'
            f'  "shift_turn": <turn number or 0>,\n'
            f'  "emotion_before": "<emotion>",\n'
            f'  "emotion_after": "<emotion>",\n'
            f'  "trigger": "<what caused the shift>",\n'
            f'  "confidence": <0-100>\n'
            f'}}'
        )

        try:
            raw = call_bedrock(invoke_id, prompt, timeout=timeout)
            parsed = _parse_json(raw)
            if parsed:
                model_has_shift = bool(parsed.get("has_shift", True))
                model_shift_turn = int(parsed.get("shift_turn", 0))
                model_before = str(parsed.get("emotion_before", ""))
                model_after = str(parsed.get("emotion_after", ""))
                model_trigger = str(parsed.get("trigger", ""))
            else:
                model_has_shift = True
                model_shift_turn = 0
                model_before = ""
                model_after = ""
                model_trigger = ""
                raw_lower = raw.lower()
                if "no shift" in raw_lower or '"has_shift": false' in raw_lower or '"has_shift":false' in raw_lower:
                    model_has_shift = False
        except Exception as e:
            raw = f"ERROR: {e}"
            model_has_shift = True
            model_shift_turn = 0
            model_before = ""
            model_after = ""
            model_trigger = ""

        # Score this item
        result = {"id": item["id"], "has_shift_actual": item["has_shift"], "has_shift_model": model_has_shift}

        if item["has_shift"]:
            result["shift_detected"] = model_has_shift
            result["turn_correct"] = model_shift_turn == item["shift_turn"]

            difficulty = item.get("difficulty", "standard")
            use_strict = difficulty in ("expert", "camouflaged", "very_hard", "extreme")
            result["before_correct"] = emotion_match(model_before, item["emotion_before"], strict=use_strict)

            if "mixed_emotions" in item:
                result["after_score"] = score_mixed_emotions(model_after, item["mixed_emotions"])
                result["after_correct"] = result["after_score"] >= 0.5
            elif "surface_emotion" in item and "real_emotion" in item:
                result["after_score"] = score_masked_emotion(model_after, item["surface_emotion"], item["real_emotion"])
                result["after_correct"] = result["after_score"] >= 0.5
            else:
                result["after_correct"] = emotion_match(model_after, item["emotion_after"], strict=use_strict)
                result["after_score"] = 1.0 if result["after_correct"] else 0.0

            stop_words = {"a","an","the","of","in","to","and","or","is","was","that","for","on","with","as","at","by","from","are","be","been","were","this","it","its"}
            trigger_words = set(item["trigger"].lower().split()) - stop_words
            model_trigger_words = set(model_trigger.lower().split()) - stop_words
            overlap = len(trigger_words & model_trigger_words)
            result["trigger_score"] = min(1.0, overlap / max(1, len(trigger_words) * 0.4))
        else:
            result["correct_no_shift"] = not model_has_shift

        results.append(result)

        # Build transcript
        parsed_answer = json.dumps({
            "has_shift": model_has_shift, "shift_turn": model_shift_turn,
            "emotion_before": model_before, "emotion_after": model_after, "trigger": model_trigger
        })
        correct_answer = json.dumps({
            "has_shift": item["has_shift"], "shift_turn": item.get("shift_turn", 0),
            "emotion_before": item.get("emotion_before", ""), "emotion_after": item.get("emotion_after", "")
        })

        item_score = 0.0
        if item["has_shift"]:
            item_score = 1.0 if result.get("shift_detected") and result.get("before_correct") and result.get("after_correct") else 0.0
        else:
            item_score = 1.0 if result.get("correct_no_shift") else 0.0

        transcripts.append({
            "question_id": item["id"],
            "prompt": prompt[:500] + "...",
            "response": raw[:1000] if isinstance(raw, str) else str(raw)[:1000],
            "parsed_answer": parsed_answer,
            "correct_answer": correct_answer,
            "score": item_score
        })

    # Compute composite score (same as task_emotional_prosody.py)
    item_lookup = {item["id"]: item for item in PROSODY_ITEMS}
    shift_items = [r for r in results if r["has_shift_actual"]]
    control_items = [r for r in results if not r["has_shift_actual"]]

    easy_items = [r for r in shift_items if item_lookup.get(r["id"], {}).get("difficulty") == "easy"]
    medium_items = [r for r in shift_items if item_lookup.get(r["id"], {}).get("difficulty", "standard") in ("standard", "subtle", None)]
    hard_items = [r for r in shift_items if item_lookup.get(r["id"], {}).get("difficulty") in ("expert", "camouflaged", "very_hard", "extreme")]

    def compute_shift_metrics(items):
        if not items: return 0, 0, 0, 0
        detection = sum(1 for r in items if r.get("shift_detected", False)) / len(items)
        e_scores, t_scores, turn_scores = [], [], []
        for r in items:
            if r.get("shift_detected", False):
                after_s = r.get("after_score", 1.0 if r.get("after_correct", False) else 0.0)
                before_s = 1.0 if r.get("before_correct", False) else 0.0
                e_scores.append((before_s + after_s) / 2)
                t_scores.append(r.get("trigger_score", 0))
                turn_scores.append(1.0 if r.get("turn_correct", False) else 0.0)
        emotion = np.mean(e_scores) if e_scores else 0
        trigger = np.mean(t_scores) if t_scores else 0
        turn_acc = np.mean(turn_scores) if turn_scores else 0
        return detection, emotion, trigger, turn_acc

    easy_det, easy_emo, _, easy_turn = compute_shift_metrics(easy_items)
    med_det, med_emo, med_trig, med_turn = compute_shift_metrics(medium_items)
    hard_det, hard_emo, hard_trig, hard_turn = compute_shift_metrics(hard_items)

    adv_controls = [r for r in control_items if item_lookup.get(r["id"], {}).get("difficulty") == "adversarial_control"]
    plain_controls = [r for r in control_items if item_lookup.get(r["id"], {}).get("difficulty") != "adversarial_control"]
    plain_fa = sum(1 for r in plain_controls if not r.get("correct_no_shift", True)) / len(plain_controls) if plain_controls else 0
    adv_fa = sum(1 for r in adv_controls if not r.get("correct_no_shift", True)) / len(adv_controls) if adv_controls else 0
    false_alarm_rate = 0.4 * plain_fa + 0.6 * adv_fa

    easy_score = float(easy_emo)
    medium_score = 0.30 * float(med_emo) + 0.70 * float(med_trig)

    hard_perfect_count = 0
    hard_trigger_total = 0.0
    hard_trigger_high = 0
    for r in hard_items:
        if r.get("shift_detected", False):
            after_s = r.get("after_score", 1.0 if r.get("after_correct", False) else 0.0)
            before_s = 1.0 if r.get("before_correct", False) else 0.0
            hard_perfect_count += before_s * after_s
            trig_s = r.get("trigger_score", 0)
            hard_trigger_total += trig_s
            if trig_s >= 0.30: hard_trigger_high += 1
    hard_emo_strict = hard_perfect_count / len(hard_items) if hard_items else 0
    hard_trig_mean = hard_trigger_total / len(hard_items) if hard_items else 0
    hard_trig_high_frac = hard_trigger_high / len(hard_items) if hard_items else 0
    hard_score = max(0.0, 0.40 * float(hard_trig_mean) + 0.30 * float(hard_trig_high_frac) + 0.30 * float(hard_emo_strict))

    score = round(hard_score**0.5 * 0.65 + medium_score * 0.35, 4)

    return score, transcripts, {
        "easy_score": round(easy_score, 4), "medium_score": round(medium_score, 4),
        "hard_score": round(hard_score, 4), "false_alarm_rate": round(false_alarm_rate, 4),
        "n_items": len(PROSODY_ITEMS), "n_shift": len(shift_items), "n_control": len(control_items),
    }


# ═══════════════════════════════════════════════════════════════════
# BENCHMARK 2: FALSE BELIEF
# ═══════════════════════════════════════════════════════════════════

def check_answer(model_answer, accept_patterns):
    model_lower = model_answer.lower().strip()
    return any(p.lower() in model_lower for p in accept_patterns)

def check_misleading(model_answer, misleading_patterns):
    model_lower = model_answer.lower().strip()
    return any(p.lower() in model_lower for p in misleading_patterns)

def _extract_answer_from_response(raw):
    """Extract answer from raw response - try JSON first, then plain text."""
    parsed = _parse_json(raw)
    if parsed and "answer" in parsed:
        return str(parsed["answer"])
    # Just use the raw text
    cleaned = _strip_think(raw)
    cleaned = _strip_fences(cleaned)
    return cleaned.strip()

def run_false_belief(invoke_id, model_label, timeout=300):
    """Run false belief benchmark for one model."""
    transcripts = []
    results = []

    for scenario in FALSE_BELIEF_SCENARIOS:
        base_prompt = f"Read this scenario carefully:\n\n{scenario['scenario']}\n\n"

        # Belief question
        belief_prompt = base_prompt + f"Question: {scenario['belief_question']}\nAnswer briefly."
        try:
            raw_belief = call_bedrock(invoke_id, belief_prompt, timeout=timeout)
            belief_answer = _extract_answer_from_response(raw_belief)
        except Exception as e:
            raw_belief = f"ERROR: {e}"
            belief_answer = ""

        belief_correct = check_answer(belief_answer, scenario["belief_accept"])

        # Reality question
        reality_prompt = base_prompt + f"Question: {scenario['reality_question']}\nAnswer briefly."
        try:
            raw_reality = call_bedrock(invoke_id, reality_prompt, timeout=timeout)
            reality_answer = _extract_answer_from_response(raw_reality)
        except Exception as e:
            raw_reality = f"ERROR: {e}"
            reality_answer = ""

        reality_correct = check_answer(reality_answer, scenario["reality_accept"])

        # Memory question
        memory_prompt = base_prompt + f"Question: {scenario['memory_question']}\nAnswer briefly."
        try:
            raw_memory = call_bedrock(invoke_id, memory_prompt, timeout=timeout)
            memory_answer = _extract_answer_from_response(raw_memory)
        except Exception as e:
            raw_memory = f"ERROR: {e}"
            memory_answer = ""

        memory_correct = check_answer(memory_answer, scenario["memory_accept"])

        result = {
            "id": scenario["id"], "order": scenario["order"],
            "belief_correct": belief_correct, "reality_correct": reality_correct,
            "memory_correct": memory_correct,
            "misleading": scenario.get("misleading", False),
        }
        if scenario.get("misleading", False):
            result["gave_misleading_answer"] = check_misleading(belief_answer, scenario.get("misleading_answer", []))

        results.append(result)

        transcripts.append({
            "question_id": scenario["id"],
            "prompt": belief_prompt[:500] + "...",
            "response": (raw_belief[:500] if isinstance(raw_belief, str) else "")[:500],
            "parsed_answer": belief_answer[:200],
            "correct_answer": str(scenario["belief_accept"][:3]),
            "score": 1.0 if belief_correct else 0.0
        })

    # Compute tiered score
    tiers = {1: [], 2: [], 3: [], 4: [], 5: []}
    for r in results:
        tiers.setdefault(r["order"], []).append(r)

    def tier_score(tier_results):
        if not tier_results: return 0.0
        belief_acc = sum(1 for r in tier_results if r["belief_correct"]) / len(tier_results)
        reality_correct = sum(1 for r in tier_results if r["reality_correct"])
        memory_correct = sum(1 for r in tier_results if r["memory_correct"])
        control_acc = (reality_correct + memory_correct) / (2 * len(tier_results))
        control_penalty = max(0, 1.0 - control_acc)
        return max(0, belief_acc - control_penalty)

    t_scores = {i: tier_score(tiers.get(i, [])) for i in range(1, 6)}
    # 0.00*T1 + 0.00*T2 + 0.05*T3 + 0.70*T4 + 0.25*T5
    score = round(float(np.clip(
        0.00 * t_scores[1] + 0.00 * t_scores[2] + 0.05 * t_scores[3] + 0.70 * t_scores[4] + 0.25 * t_scores[5],
        0, 1)), 4)

    return score, transcripts, {
        "n_scenarios": len(results),
        "tier_scores": {str(k): round(v, 4) for k, v in t_scores.items()},
        "tier_counts": {str(k): len(v) for k, v in tiers.items()},
    }


# ═══════════════════════════════════════════════════════════════════
# BENCHMARK 3: PRAGMATIC INFERENCE
# ═══════════════════════════════════════════════════════════════════

def check_patterns(text, patterns):
    text_lower = text.lower()
    return any(p.lower() in text_lower for p in patterns)

def run_pragmatic(invoke_id, model_label, timeout=300):
    """Run pragmatic inference benchmark for one model."""
    transcripts = []
    all_results = []

    all_tiers = [
        ("direct", PRAGMATIC_ITEMS_DIRECT, 0.15),
        ("indirect", PRAGMATIC_ITEMS_INDIRECT, 0.35),
        ("complex", PRAGMATIC_ITEMS_COMPLEX, 0.50),
    ]
    tier_scores = {}

    for tier_label, items, weight in all_tiers:
        tier_results = []
        for item in items:
            prompt = (
                f"Read this situation carefully:\n\n"
                f"Context: {item['context']}\n\n"
                f"Question: {item['question']}\n\n"
                f"Consider both the literal meaning and what the speaker actually intends "
                f"to communicate. What is the speaker's TRUE intended meaning?\n\n"
                f"Respond with ONLY a JSON object:\n"
                f'{{\n'
                f'  "speaker_intent": "<what the speaker actually means>",\n'
                f'  "is_literal": true/false,\n'
                f'  "reasoning": "<brief explanation>"\n'
                f'}}'
            )

            try:
                raw = call_bedrock(invoke_id, prompt, timeout=timeout)
                parsed = _parse_json(raw)
                if parsed:
                    speaker_intent = str(parsed.get("speaker_intent", ""))
                    is_literal = bool(parsed.get("is_literal", False))
                else:
                    speaker_intent = _strip_think(raw)
                    is_literal = False
            except Exception as e:
                raw = f"ERROR: {e}"
                speaker_intent = ""
                is_literal = False

            got_intended = check_patterns(speaker_intent, item["intended_accept"])
            got_literal = check_patterns(speaker_intent, item["literal_accept"])
            if got_intended: got_literal = False

            tier_results.append({
                "id": item["id"], "type": item["type"], "tier": tier_label,
                "got_intended": got_intended, "got_literal": got_literal,
            })

            transcripts.append({
                "question_id": item["id"],
                "prompt": prompt[:500] + "...",
                "response": raw[:1000] if isinstance(raw, str) else str(raw)[:1000],
                "parsed_answer": speaker_intent[:200],
                "correct_answer": str(item["intended_accept"][:3]),
                "score": 1.0 if got_intended else 0.0
            })

        n = len(tier_results)
        intended_acc = sum(1 for r in tier_results if r["got_intended"]) / max(n, 1)
        literal_trap = sum(1 for r in tier_results if r["got_literal"]) / max(n, 1)
        ts = max(0.0, intended_acc - 0.1 * literal_trap)
        tier_scores[tier_label] = {"score": round(ts, 4), "intended_acc": round(intended_acc, 4),
                                    "literal_trap": round(literal_trap, 4), "n": n}
        all_results.extend(tier_results)

    composite = round(float(np.clip(
        0.15 * tier_scores["direct"]["score"] + 0.35 * tier_scores["indirect"]["score"] + 0.50 * tier_scores["complex"]["score"],
        0, 1)), 4)

    return composite, transcripts, {"n_items": len(all_results), "tier_scores": tier_scores}


# ═══════════════════════════════════════════════════════════════════
# BENCHMARK 4: SARCASM DETECTION
# ═══════════════════════════════════════════════════════════════════

def compute_auc(ratings, labels):
    ratings = np.array(ratings, dtype=float)
    labels = np.array(labels, dtype=float)
    if labels.sum() == 0 or labels.sum() == len(labels): return 0.5
    sorted_idx = np.argsort(-ratings)
    sorted_labels = labels[sorted_idx]
    tpr_list, fpr_list = [0.0], [0.0]
    tp, fp = 0, 0
    pos, neg = labels.sum(), len(labels) - labels.sum()
    for label in sorted_labels:
        if label == 1: tp += 1
        else: fp += 1
        tpr_list.append(tp / pos)
        fpr_list.append(fp / neg)
    auc = sum((fpr_list[i] - fpr_list[i-1]) * (tpr_list[i] + tpr_list[i-1]) / 2 for i in range(1, len(tpr_list)))
    return round(float(auc), 4)

def run_sarcasm(invoke_id, model_label, timeout=300):
    """Run sarcasm detection benchmark for one model."""
    transcripts = []
    results = []
    sincerity_ratings = []
    true_labels = []

    for item in SARCASM_ITEMS:
        prompt = (
            f"Read this conversation carefully:\n\n"
            f"Context: {item['context']}\n"
            f"Utterance: \"{item['utterance']}\"\n\n"
            f"Rate the SINCERITY of this utterance on a scale from 0 to 100.\n"
            f"0 = Definitely sarcastic (the speaker means the OPPOSITE of what they say)\n"
            f"100 = Definitely sincere (the speaker genuinely means what they say)\n\n"
            f"Consider the context carefully before judging.\n\n"
            f"Respond with ONLY a JSON object:\n"
            f'{{\n'
            f'  "sincerity_rating": <0-100>,\n'
            f'  "is_sarcastic": true/false,\n'
            f'  "reasoning": "<brief explanation>"\n'
            f'}}'
        )

        try:
            raw = call_bedrock(invoke_id, prompt, timeout=timeout)
            parsed = _parse_json(raw)
            if parsed:
                rating = max(0, min(100, int(parsed.get("sincerity_rating", 50))))
                model_says_sarcastic = bool(parsed.get("is_sarcastic", False))
            else:
                cleaned = _strip_think(raw)
                nums = re.findall(r'\b(\d{1,3})\b', cleaned)
                rating = max(0, min(100, int(nums[0]))) if nums else 50
                model_says_sarcastic = "sarcas" in cleaned.lower()
        except Exception as e:
            raw = f"ERROR: {e}"
            rating = 50
            model_says_sarcastic = False

        is_sincere = not item["is_sarcastic"]
        results.append({
            "id": item["id"], "is_sarcastic": item["is_sarcastic"],
            "sincerity_rating": rating, "model_says_sarcastic": model_says_sarcastic,
            "binary_correct": (model_says_sarcastic == item["is_sarcastic"]),
        })
        sincerity_ratings.append(rating)
        true_labels.append(1 if is_sincere else 0)

        transcripts.append({
            "question_id": item["id"],
            "prompt": prompt[:500] + "...",
            "response": raw[:1000] if isinstance(raw, str) else str(raw)[:1000],
            "parsed_answer": json.dumps({"sincerity_rating": rating, "is_sarcastic": model_says_sarcastic}),
            "correct_answer": json.dumps({"is_sarcastic": item["is_sarcastic"]}),
            "score": 1.0 if (model_says_sarcastic == item["is_sarcastic"]) else 0.0
        })

    # Compute metrics
    auc = compute_auc(sincerity_ratings, true_labels)
    binary_correct = sum(1 for r in results if r["binary_correct"])
    threshold_acc = binary_correct / len(results) if results else 0

    ratings_norm = np.array(sincerity_ratings) / 100.0
    labels = np.array(true_labels, dtype=float)
    n_bins = 5
    bin_edges = np.linspace(0, 1, n_bins + 1)
    cal_error = 0.0
    total_in_bins = 0
    for i in range(n_bins):
        mask = (ratings_norm >= bin_edges[i]) & (ratings_norm < bin_edges[i+1])
        if i == n_bins - 1:
            mask = (ratings_norm >= bin_edges[i]) & (ratings_norm <= bin_edges[i+1])
        if mask.sum() == 0: continue
        avg_rating = ratings_norm[mask].mean()
        avg_sincere = labels[mask].mean()
        cal_error += mask.sum() * abs(avg_rating - avg_sincere)
        total_in_bins += mask.sum()
    cal_error = cal_error / total_in_bins if total_in_bins > 0 else 0.5

    score = round(float(np.clip(0.50 * auc + 0.30 * (1.0 - cal_error) + 0.20 * threshold_acc, 0, 1)), 4)

    return score, transcripts, {
        "n_items": len(results), "auc": auc,
        "calibration_error": round(float(cal_error), 4),
        "threshold_accuracy": round(threshold_acc, 4),
    }


# ═══════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════

BENCHMARKS = {
    "social_cog_emotional_prosody": run_emotional_prosody,
    "social_cog_false_belief": run_false_belief,
    "social_cog_pragmatic": run_pragmatic,
    "social_cog_sarcasm": run_sarcasm,
}

def run_all():
    all_scores = {}  # benchmark -> {model_key -> score}

    for bench_name, bench_fn in BENCHMARKS.items():
        out_dir = os.path.join(QA_BASE, bench_name)
        os.makedirs(out_dir, exist_ok=True)

        bench_scores = {}
        print(f"\n{'='*70}")
        print(f"BENCHMARK: {bench_name}")
        print(f"{'='*70}")

        for model_key, (model_label, invoke_id) in MODEL_CATALOG.items():
            # Skip if already scored
            summary_path = os.path.join(out_dir, f"{model_key}.summary.json")
            if os.path.exists(summary_path):
                try:
                    with open(summary_path) as f:
                        existing = json.load(f)
                    if existing.get("score") is not None:
                        bench_scores[model_key] = existing["score"]
                        print(f"  [skip] {model_label}: {existing['score']:.4f} (already scored)")
                        continue
                except Exception:
                    pass

            timeout = 900 if "deepseek" in model_key else (600 if "glm" in model_key else 300)

            print(f"  Running {model_label} (timeout={timeout}s)...", end=" ", flush=True)
            t0 = time.time()

            try:
                score, transcripts, details = bench_fn(invoke_id, model_label, timeout=timeout)
                duration = time.time() - t0
                print(f"score={score:.4f} ({duration:.0f}s)")

                # Save transcript
                transcript_path = os.path.join(out_dir, f"{model_key}.jsonl")
                with open(transcript_path, 'w') as f:
                    for t in transcripts:
                        f.write(json.dumps(t) + "\n")

                # Save summary
                summary = {
                    "model": model_key, "model_label": model_label,
                    "benchmark": bench_name, "score": score,
                    "duration_s": round(duration, 1),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": details,
                }
                with open(summary_path, 'w') as f:
                    json.dump(summary, f, indent=2)

                bench_scores[model_key] = score
            except Exception as e:
                duration = time.time() - t0
                print(f"FAILED ({duration:.0f}s): {e}")
                traceback.print_exc()
                # Save error summary
                summary = {
                    "model": model_key, "model_label": model_label,
                    "benchmark": bench_name, "score": None,
                    "error": str(e), "duration_s": round(duration, 1),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                with open(summary_path, 'w') as f:
                    json.dump(summary, f, indent=2)

            time.sleep(2)  # Rate limit between models

        all_scores[bench_name] = bench_scores

        # Compute aggregate stats for this benchmark
        valid_scores = [s for s in bench_scores.values() if s is not None]
        if valid_scores:
            agg = {
                "benchmark": bench_name,
                "n_models": len(valid_scores),
                "mean": round(float(np.mean(valid_scores)), 4),
                "std": round(float(np.std(valid_scores)), 4),
                "min": round(float(np.min(valid_scores)), 4),
                "max": round(float(np.max(valid_scores)), 4),
                "range": round(float(np.max(valid_scores) - np.min(valid_scores)), 4),
                "scores": {k: v for k, v in bench_scores.items()},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            agg_path = os.path.join(out_dir, "aggregate_stats.json")
            with open(agg_path, 'w') as f:
                json.dump(agg, f, indent=2)

            print(f"\n  Aggregate: mean={agg['mean']:.4f}, std={agg['std']:.4f}, range={agg['range']:.4f}, coverage={len(valid_scores)}/10")
        print()

    # Final summary
    print("\n" + "="*70)
    print("SOCIAL COGNITION — ALL BENCHMARKS COMPLETE")
    print("="*70)
    for bench_name, scores in all_scores.items():
        valid = [s for s in scores.values() if s is not None]
        if valid:
            print(f"  {bench_name}: mean={np.mean(valid):.4f}, std={np.std(valid):.4f}, range={np.max(valid)-np.min(valid):.4f}, n={len(valid)}/10")
        else:
            print(f"  {bench_name}: NO VALID SCORES")


if __name__ == "__main__":
    run_all()
