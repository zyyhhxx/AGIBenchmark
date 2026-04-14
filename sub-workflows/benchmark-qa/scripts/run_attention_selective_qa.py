#!/usr/bin/env python3
"""
Run attention_selective benchmark against all 10 models with Q&A transcript logging.
Saves per-model .jsonl transcripts and .summary.json files.
"""
import json, os, sys, time, re, traceback, signal
import numpy as np
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'benchmarks', 'attention'))

OUT_DIR = os.path.join(REPO, 'sub-workflows', 'benchmark-qa', 'results', 'qa_transcripts', 'attention_selective')
os.makedirs(OUT_DIR, exist_ok=True)

# Import items and scoring from task_selective
from task_selective import ALL_ITEMS, check_answer

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

config = Config(
    read_timeout=300,
    connect_timeout=30,
    retries={'max_attempts': 0}
)
bclient = boto3.Session(region_name='us-east-1').client('bedrock-runtime', config=config)


def call_bedrock(invoke_id, prompt, timeout=300, max_retries=3):
    """Single Bedrock call with retries. Returns raw text response."""
    for attempt in range(max_retries + 1):
        try:
            # Use longer timeout config for DeepSeek
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


def run_model(model_id, label, invoke_id, timeout=300):
    """Run attention_selective for one model, save transcript."""
    safe_name = model_id.replace(':', '_').replace('/', '_')
    jsonl_path = os.path.join(OUT_DIR, f"{safe_name}.jsonl")
    summary_path = os.path.join(OUT_DIR, f"{safe_name}.summary.json")

    # Skip if already completed
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            s = json.load(f)
        if s.get('score') is not None:
            print(f"  SKIP {label} — already scored: {s['score']:.4f}")
            return s['score']

    print(f"\n{'='*60}")
    print(f"Running attention_selective with {label}")
    print(f"{'='*60}")

    records = []
    tier_results = {1: [], 2: [], 3: []}
    start = time.time()

    for item in ALL_ITEMS:
        prompt = (
            f"Follow this instruction carefully and respond with ONLY the answer.\n\n"
            f"{item['instruction']}\n\n"
        )
        if item["text"] and item["text"] not in item["instruction"]:
            prompt += f"Text: {item['text']}\n\n"
        prompt += "Answer:"

        try:
            raw = call_bedrock(invoke_id, prompt, timeout=timeout)
            answer = raw.strip()
        except Exception as e:
            answer = f"ERROR: {e}"
            print(f"    ERROR on {item['id']}: {str(e)[:80]}")

        correct = check_answer(answer, item["correct"], item)
        score_val = 1.0 if correct else 0.0

        record = {
            "question_id": item["id"],
            "prompt": prompt,
            "response": answer,
            "parsed_answer": answer[:200],
            "correct_answer": item["correct"],
            "score": score_val,
            "tier": item["tier"],
        }
        records.append(record)
        tier_results[item["tier"]].append(correct)

        status = "✓" if correct else "✗"
        print(f"  {status} {item['id']} (T{item['tier']}): got '{answer[:50]}', expected '{item['correct'][:50]}'")
        time.sleep(0.5)  # Rate limiting

    elapsed = time.time() - start

    # Compute score
    tier_accs = {}
    for tier in [1, 2, 3]:
        items = tier_results[tier]
        tier_accs[tier] = sum(items) / len(items) if items else 0
    composite = round(0.10 * tier_accs[1] + 0.40 * tier_accs[2] + 0.50 * tier_accs[3], 4)

    # Save transcript
    with open(jsonl_path, 'w') as f:
        for r in records:
            f.write(json.dumps(r) + '\n')

    # Save summary
    summary = {
        "model_id": model_id,
        "model_label": label,
        "benchmark": "attention_selective",
        "score": composite,
        "tier1_acc": round(tier_accs[1], 4),
        "tier2_acc": round(tier_accs[2], 4),
        "tier3_acc": round(tier_accs[3], 4),
        "n_items": len(ALL_ITEMS),
        "n_correct": sum(1 for r in records if r["score"] == 1.0),
        "duration_s": round(elapsed, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Score: {composite:.4f} (T1={tier_accs[1]:.2%}, T2={tier_accs[2]:.2%}, T3={tier_accs[3]:.2%})")
    print(f"  Time: {elapsed:.1f}s")
    print(f"  Saved: {jsonl_path}")
    return composite


def main():
    scores = {}
    model_order = list(MODEL_CATALOG.keys())

    for model_id in model_order:
        label, invoke_id = MODEL_CATALOG[model_id]
        timeout = 900 if 'deepseek' in model_id else 300
        try:
            score = run_model(model_id, label, invoke_id, timeout=timeout)
            scores[model_id] = score
        except Exception as e:
            print(f"  FAILED {label}: {e}")
            traceback.print_exc()
            scores[model_id] = None
        time.sleep(3)  # Delay between models

    # Aggregate stats
    valid = [s for s in scores.values() if s is not None]
    agg = {
        "benchmark": "attention_selective",
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
    print(f"AGGREGATE RESULTS — attention_selective")
    print(f"{'='*60}")
    for mid, s in sorted(scores.items(), key=lambda x: x[1] if x[1] is not None else -1, reverse=True):
        label = MODEL_CATALOG[mid][0]
        print(f"  {label:30s}: {s:.4f}" if s is not None else f"  {label:30s}: FAILED")
    print(f"\n  Mean: {agg['mean']}, Std: {agg['std']}, Range: {agg['range']}")
    print(f"  Coverage: {agg['n_valid']}/{agg['n_models']}")
    print(f"  Saved: {agg_path}")


if __name__ == '__main__':
    main()
