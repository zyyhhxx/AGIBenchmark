#!/usr/bin/env python3
"""
Run attention_instruction_update benchmark against all 10 models with Q&A transcript logging.
"""
import json, os, sys, time, re, traceback
import numpy as np
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'benchmarks', 'attention'))

OUT_DIR = os.path.join(REPO, 'sub-workflows', 'benchmark-qa', 'results', 'qa_transcripts', 'attention_instruction_update')
os.makedirs(OUT_DIR, exist_ok=True)

from task_instruction_update import (
    EASY_TRIALS, MEDIUM_TRIALS, HARD_TRIALS,
    normalize_answer, check_answer, extract_json
)

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

config = Config(read_timeout=300, connect_timeout=30, retries={'max_attempts': 0})
bclient = boto3.Session(region_name='us-east-1').client('bedrock-runtime', config=config)


def call_bedrock(invoke_id, prompt, timeout=300, max_retries=3):
    for attempt in range(max_retries + 1):
        try:
            if timeout > 300:
                cfg = Config(read_timeout=timeout, connect_timeout=30, retries={'max_attempts': 0})
                cl = boto3.Session(region_name='us-east-1').client('bedrock-runtime', config=cfg)
            else:
                cl = bclient
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


def score_trial_bedrock(invoke_id, trial, timeout=300):
    """Score a single trial via Bedrock. Returns (records_list, accuracy)."""
    raw = call_bedrock(invoke_id, trial["prompt"], timeout=timeout)
    parsed = extract_json(raw)
    model_answers = parsed.get("answers", [])
    expected = trial["answers"]

    if not model_answers:
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        for line in lines:
            m_line = re.match(r'\d+[\.\):\s]+(.+)', line)
            if m_line:
                model_answers.append(m_line.group(1).strip())

    records = []
    correct = 0
    for i, exp in enumerate(expected):
        ma = str(model_answers[i]) if i < len(model_answers) else ""
        is_correct = check_answer(ma, exp) if ma else False
        if is_correct:
            correct += 1
        records.append({
            "question_id": f"{trial['id']}_item{i+1}",
            "prompt": trial["prompt"],
            "response": raw[:2000],
            "parsed_answer": ma[:200],
            "correct_answer": exp,
            "score": 1.0 if is_correct else 0.0,
            "trial_id": trial["id"],
        })

    acc = correct / len(expected) if expected else 0
    return records, acc


def run_model(model_id, label, invoke_id, timeout=300):
    safe_name = model_id.replace(':', '_').replace('/', '_')
    jsonl_path = os.path.join(OUT_DIR, f"{safe_name}.jsonl")
    summary_path = os.path.join(OUT_DIR, f"{safe_name}.summary.json")

    if os.path.exists(summary_path):
        with open(summary_path) as f:
            s = json.load(f)
        if s.get('score') is not None:
            print(f"  SKIP {label} — already scored: {s['score']:.4f}")
            return s['score']

    print(f"\n{'='*60}")
    print(f"Running attention_instruction_update with {label}")
    print(f"{'='*60}")

    all_records = []
    tier_scores = {"easy": [], "medium": [], "hard": []}
    start = time.time()

    for tier_name, trials in [("easy", EASY_TRIALS), ("medium", MEDIUM_TRIALS), ("hard", HARD_TRIALS)]:
        for trial in trials:
            try:
                records, acc = score_trial_bedrock(invoke_id, trial, timeout=timeout)
                all_records.extend(records)
                tier_scores[tier_name].append(acc)
                print(f"  [{tier_name:6s}] {trial['id']:16s}: {acc:.3f} ({sum(1 for r in records if r['score']==1.0)}/{len(records)} correct)")
            except Exception as e:
                print(f"  [{tier_name:6s}] {trial['id']:16s}: ERROR — {str(e)[:80]}")
                tier_scores[tier_name].append(0.0)
            time.sleep(1)

    elapsed = time.time() - start

    easy_mean = np.mean(tier_scores["easy"]) if tier_scores["easy"] else 0
    medium_mean = np.mean(tier_scores["medium"]) if tier_scores["medium"] else 0
    hard_mean = np.mean(tier_scores["hard"]) if tier_scores["hard"] else 0
    composite = round(float(0.20 * easy_mean + 0.30 * medium_mean + 0.50 * hard_mean), 4)

    with open(jsonl_path, 'w') as f:
        for r in all_records:
            f.write(json.dumps(r) + '\n')

    summary = {
        "model_id": model_id,
        "model_label": label,
        "benchmark": "attention_instruction_update",
        "score": composite,
        "easy_mean": round(float(easy_mean), 4),
        "medium_mean": round(float(medium_mean), 4),
        "hard_mean": round(float(hard_mean), 4),
        "n_trials": len(EASY_TRIALS) + len(MEDIUM_TRIALS) + len(HARD_TRIALS),
        "n_items": sum(len(t["answers"]) for t in EASY_TRIALS + MEDIUM_TRIALS + HARD_TRIALS),
        "duration_s": round(elapsed, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Score: {composite:.4f} (E={easy_mean:.3f}, M={medium_mean:.3f}, H={hard_mean:.3f})")
    print(f"  Time: {elapsed:.1f}s")
    return composite


def main():
    scores = {}
    for model_id in MODEL_CATALOG:
        label, invoke_id = MODEL_CATALOG[model_id]
        timeout = 900 if 'deepseek' in model_id else 300
        try:
            score = run_model(model_id, label, invoke_id, timeout=timeout)
            scores[model_id] = score
        except Exception as e:
            print(f"  FAILED {label}: {e}")
            traceback.print_exc()
            scores[model_id] = None
        time.sleep(3)

    valid = [s for s in scores.values() if s is not None]
    agg = {
        "benchmark": "attention_instruction_update",
        "n_models": len(scores),
        "n_valid": len(valid),
        "n_failed": len(scores) - len(valid),
        "scores": {mid: {"label": MODEL_CATALOG[mid][0], "score": scores[mid]} for mid in scores},
        "mean": round(float(np.mean(valid)), 4) if valid else None,
        "std": round(float(np.std(valid)), 4) if valid else None,
        "min": round(float(np.min(valid)), 4) if valid else None,
        "max": round(float(np.max(valid)), 4) if valid else None,
        "range": round(float(np.max(valid) - np.min(valid)), 4) if valid else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    agg_path = os.path.join(OUT_DIR, 'aggregate_stats.json')
    with open(agg_path, 'w') as f:
        json.dump(agg, f, indent=2)

    print(f"\n{'='*60}")
    print(f"AGGREGATE RESULTS — attention_instruction_update")
    print(f"{'='*60}")
    for mid, s in sorted(scores.items(), key=lambda x: x[1] if x[1] is not None else -1, reverse=True):
        label = MODEL_CATALOG[mid][0]
        print(f"  {label:30s}: {s:.4f}" if s is not None else f"  {label:30s}: FAILED")
    if valid:
        print(f"\n  Mean: {agg['mean']}, Std: {agg['std']}, Range: {agg['range']}")
    print(f"  Coverage: {agg['n_valid']}/{agg['n_models']}")


if __name__ == '__main__':
    main()
