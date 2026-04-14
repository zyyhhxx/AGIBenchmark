#!/usr/bin/env python3
"""
Re-run sarcasm benchmark with 3-tier scoring against all 10 models.
Produces Q&A transcripts matching task_sarcasm.py scoring exactly.
"""
import json, os, sys, time, re, traceback
import numpy as np
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'benchmarks', 'social_cognition', 'data'))

from sarcasm_items import SARCASM_ITEMS

QA_DIR = os.path.join(REPO, 'sub-workflows', 'benchmark-qa', 'results', 'qa_transcripts', 'social_cog_sarcasm')
os.makedirs(QA_DIR, exist_ok=True)

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

def call_bedrock(invoke_id, prompt, timeout=300, max_retries=3):
    for attempt in range(max_retries + 1):
        try:
            cl = make_client(timeout)
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

def _strip_think(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def _strip_fences(text):
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = text.replace('```', '')
    text = re.sub(r'//.*', '', text)
    return text.strip()

def compute_auc(ratings, labels):
    ratings = np.array(ratings, dtype=float)
    labels = np.array(labels, dtype=float)
    if labels.sum() == 0 or labels.sum() == len(labels):
        return 0.5
    sorted_idx = np.argsort(-ratings)
    sorted_labels = labels[sorted_idx]
    tpr_list = [0.0]
    fpr_list = [0.0]
    tp = fp = 0
    pos = labels.sum()
    neg = len(labels) - pos
    for label in sorted_labels:
        if label == 1: tp += 1
        else: fp += 1
        tpr_list.append(tp / pos)
        fpr_list.append(fp / neg)
    auc = 0.0
    for i in range(1, len(tpr_list)):
        auc += (fpr_list[i] - fpr_list[i-1]) * (tpr_list[i] + tpr_list[i-1]) / 2
    return round(float(auc), 4)


def compute_tier_composite(results_tier):
    """Compute composite score for a single difficulty tier — matches task_sarcasm.py exactly."""
    if not results_tier:
        return {"auc": 0.5, "cal_error": 0.5, "threshold_acc": 0.0, "composite": 0.0, "n": 0}
    sincerity_ratings = [r["sincerity_rating"] for r in results_tier]
    true_labels = [1 if not r["is_sarcastic"] else 0 for r in results_tier]
    auc = compute_auc(sincerity_ratings, true_labels)
    binary_correct = sum(1 for r in results_tier if r["binary_correct"])
    threshold_acc = binary_correct / len(results_tier)
    ratings_norm = np.array(sincerity_ratings) / 100.0
    labels = np.array(true_labels, dtype=float)
    n_bins = 5
    bin_edges = np.linspace(0, 1, n_bins + 1)
    cal_error = 0.0
    total_in_bins = 0
    for i in range(n_bins):
        if i == n_bins - 1:
            mask = (ratings_norm >= bin_edges[i]) & (ratings_norm <= bin_edges[i+1])
        else:
            mask = (ratings_norm >= bin_edges[i]) & (ratings_norm < bin_edges[i+1])
        if mask.sum() == 0: continue
        avg_rating = ratings_norm[mask].mean()
        avg_sincere = labels[mask].mean()
        cal_error += mask.sum() * abs(avg_rating - avg_sincere)
        total_in_bins += mask.sum()
    cal_error = cal_error / total_in_bins if total_in_bins > 0 else 0.5
    composite = 0.50 * auc + 0.30 * (1.0 - cal_error) + 0.20 * threshold_acc
    composite = round(float(np.clip(composite, 0, 1)), 4)
    return {"auc": auc, "cal_error": round(float(cal_error), 4), "threshold_acc": round(threshold_acc, 4), "composite": composite, "n": len(results_tier)}


def run_sarcasm_model(model_id, invoke_id, model_label, timeout=300):
    """Run 3-tier sarcasm benchmark for one model with Q&A transcripts."""
    print(f"\n{'='*60}")
    print(f"Running social_cog_sarcasm v2 (3-tier) with {model_label}")
    print(f"Items: {len(SARCASM_ITEMS)} (T1={sum(1 for i in SARCASM_ITEMS if i['difficulty']==1)}, T2={sum(1 for i in SARCASM_ITEMS if i['difficulty']==2)}, T3={sum(1 for i in SARCASM_ITEMS if i['difficulty']==3)})")
    print(f"{'='*60}")

    transcripts = []
    results = []
    start = time.time()

    for idx, item in enumerate(SARCASM_ITEMS):
        prompt = (
            f"Read this conversation carefully:\n\n"
            f"Context: {item['context']}\n"
            f"Utterance: \"{item['utterance']}\"\n\n"
            f"Rate the SINCERITY of this utterance on a scale from 0 to 100.\n"
            f"0 = Definitely sarcastic (the speaker means the OPPOSITE of what they say)\n"
            f"100 = Definitely sincere (the speaker genuinely means what they say)\n\n"
            f"Consider the context carefully before judging."
            f'\n\nRespond in JSON format: {{"sincerity_rating": <0-100>, "is_sarcastic": <true/false>, "reasoning": "<brief>"}}'
        )

        try:
            raw = call_bedrock(invoke_id, prompt, timeout=timeout)
            cleaned = _strip_think(raw)
            cleaned = _strip_fences(cleaned)
            m = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if m:
                data = json.loads(m.group())
                rating = max(0, min(100, int(data.get("sincerity_rating", 50))))
                model_says_sarcastic = bool(data.get("is_sarcastic", False))
            else:
                nums = re.findall(r'\b(\d{1,3})\b', cleaned)
                rating = max(0, min(100, int(nums[0]))) if nums else 50
                model_says_sarcastic = "sarcas" in cleaned.lower()
        except Exception as e:
            raw = f"ERROR: {e}"
            rating = 50
            model_says_sarcastic = False

        results.append({
            "id": item["id"], "is_sarcastic": item["is_sarcastic"],
            "difficulty": item["difficulty"],
            "sincerity_rating": rating, "model_says_sarcastic": model_says_sarcastic,
            "binary_correct": (model_says_sarcastic == item["is_sarcastic"]),
        })

        transcripts.append({
            "question_id": item["id"],
            "difficulty": item["difficulty"],
            "prompt": prompt[:500] + "...",
            "response": raw[:1000] if isinstance(raw, str) else str(raw)[:1000],
            "parsed_answer": json.dumps({"sincerity_rating": rating, "is_sarcastic": model_says_sarcastic}),
            "correct_answer": json.dumps({"is_sarcastic": item["is_sarcastic"]}),
            "score": 1.0 if (model_says_sarcastic == item["is_sarcastic"]) else 0.0
        })

        if (idx + 1) % 10 == 0:
            print(f"  [{idx+1}/{len(SARCASM_ITEMS)}] items done...")

    elapsed = time.time() - start

    # 3-tier scoring
    tier1 = compute_tier_composite([r for r in results if r["difficulty"] == 1])
    tier2 = compute_tier_composite([r for r in results if r["difficulty"] == 2])
    tier3 = compute_tier_composite([r for r in results if r["difficulty"] == 3])
    tier3_score = tier3["threshold_acc"]
    score = round(float(np.clip(0.05 * tier1["composite"] + 0.15 * tier2["composite"] + 0.80 * tier3_score, 0, 1)), 4)

    print(f"  Score: {score:.4f} (T1={tier1['composite']:.4f}, T2={tier2['composite']:.4f}, T3_binary={tier3['threshold_acc']:.4f})")
    print(f"  Time: {elapsed:.1f}s")

    # Save transcripts
    jsonl_path = os.path.join(QA_DIR, f"{model_id}.jsonl")
    with open(jsonl_path, 'w') as f:
        for t in transcripts:
            f.write(json.dumps(t) + '\n')

    summary = {
        "model": model_id, "model_label": model_label,
        "benchmark": "social_cog_sarcasm",
        "score": score, "duration_s": round(elapsed, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": {
            "n_items": len(SARCASM_ITEMS),
            "tier1": tier1, "tier2": tier2, "tier3": tier3,
            "tier_weights": {"tier1": 0.05, "tier2": 0.15, "tier3": 0.80},
            "tier3_score_metric": "binary_accuracy",
        }
    }
    summary_path = os.path.join(QA_DIR, f"{model_id}.summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    return score


def main():
    print(f"Sarcasm items: {len(SARCASM_ITEMS)} total")
    print(f"  Tier 1 (obvious): {sum(1 for i in SARCASM_ITEMS if i['difficulty']==1)}")
    print(f"  Tier 2 (contextual): {sum(1 for i in SARCASM_ITEMS if i['difficulty']==2)}")
    print(f"  Tier 3 (subtle): {sum(1 for i in SARCASM_ITEMS if i['difficulty']==3)}")

    all_scores = {}
    models = list(MODEL_CATALOG.items())
    EXPECTED_N = len(SARCASM_ITEMS)

    for i, (model_id, (label, invoke_id)) in enumerate(models):
        # Skip if already scored with current item count
        summary_path = os.path.join(QA_DIR, f"{model_id}.summary.json")
        if os.path.exists(summary_path):
            try:
                existing = json.load(open(summary_path))
                if existing.get('details', {}).get('n_items') == EXPECTED_N:
                    print(f"  [{i+1}/{len(models)}] {label} — already scored ({existing['score']:.4f}, n={EXPECTED_N}), skipping")
                    all_scores[model_id] = existing['score']
                    continue
            except Exception:
                pass
        try:
            score = run_sarcasm_model(model_id, invoke_id, label)
            all_scores[model_id] = score
        except Exception as e:
            print(f"  FAILED: {e}")
            traceback.print_exc()
            all_scores[model_id] = None

        if i < len(models) - 1:
            time.sleep(2)

    # Aggregate stats
    valid = {k: v for k, v in all_scores.items() if v is not None}
    vals = list(valid.values())
    agg = {
        "benchmark": "social_cog_sarcasm",
        "n_models": len(valid),
        "mean": round(float(np.mean(vals)), 4),
        "std": round(float(np.std(vals)), 4),
        "min": round(float(min(vals)), 4),
        "max": round(float(max(vals)), 4),
        "range": round(float(max(vals) - min(vals)), 4),
        "scores": {k: round(v, 4) for k, v in valid.items()},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(os.path.join(QA_DIR, 'aggregate_stats.json'), 'w') as f:
        json.dump(agg, f, indent=2)

    print(f"\n{'='*60}")
    print("SARCASM v2 (3-TIER) — FINAL RESULTS")
    print(f"{'='*60}")
    for mid, s in sorted(valid.items(), key=lambda x: -x[1]):
        label = MODEL_CATALOG[mid][0]
        print(f"  {label:30s} {s:.4f}")
    print(f"\n  mean={agg['mean']:.4f}  std={agg['std']:.4f}  range={agg['range']:.4f}")
    print(f"  std >= 0.08? {agg['std'] >= 0.08}")


if __name__ == "__main__":
    main()
