#!/usr/bin/env python3
"""Run sarcasm v2 benchmark against all 10 models via Bedrock."""
import json, os, sys, time, traceback
from datetime import datetime, timezone

os.environ['PYTHONUNBUFFERED'] = '1'

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
os.environ.pop('AWS_PROFILE', None)

RESULTS_DIR = os.path.join(REPO, 'sub-workflows/benchmark-qa/results/qa_transcripts/social_cog_sarcasm_v2')
os.makedirs(RESULTS_DIR, exist_ok=True)

MODEL_CATALOG = {
    "anthropic.claude-opus-4-6-v1":              ("Claude Opus 4.6",        "us.anthropic.claude-opus-4-6-v1"),
    "deepseek.r1-v1:0":                          ("DeepSeek-R1",            "us.deepseek.r1-v1:0"),
    "openai.gpt-oss-120b-1:0":                   ("GPT-OSS-120B",           "openai.gpt-oss-120b-1:0"),
    "meta.llama3-3-70b-instruct-v1:0":           ("Llama 3.3 70B",          "us.meta.llama3-3-70b-instruct-v1:0"),
    "qwen.qwen3-next-80b-a3b":                   ("Qwen3 Next 80B",         "qwen.qwen3-next-80b-a3b"),
    "amazon.nova-pro-v1:0":                       ("Nova Pro",               "us.amazon.nova-pro-v1:0"),
    "meta.llama4-maverick-17b-instruct-v1:0":    ("Llama 4 Maverick 17B",   "us.meta.llama4-maverick-17b-instruct-v1:0"),
    "anthropic.claude-sonnet-4-6":                ("Claude Sonnet 4.6",      "us.anthropic.claude-sonnet-4-6"),
    "zai.glm-4.7":                                ("GLM 4.7",                "zai.glm-4.7"),
    "mistral.ministral-3-3b-instruct":           ("Ministral 3B",           "mistral.ministral-3-3b-instruct"),
}

import re, numpy as np
from benchmarks.social_cognition.data.sarcasm_items import SARCASM_ITEMS

def _strip_think(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def _strip_fences(text):
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    return text.strip()

def compute_auc(ratings, labels):
    ratings = np.array(ratings, dtype=float)
    labels = np.array(labels, dtype=float)
    if labels.sum() == 0 or labels.sum() == len(labels):
        return 0.5
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

def compute_tier_composite(results_tier):
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
        mask = (ratings_norm >= bin_edges[i]) & (ratings_norm < bin_edges[i+1]) if i < n_bins-1 else (ratings_norm >= bin_edges[i]) & (ratings_norm <= bin_edges[i+1])
        if mask.sum() == 0: continue
        cal_error += mask.sum() * abs(ratings_norm[mask].mean() - labels[mask].mean())
        total_in_bins += mask.sum()
    cal_error = cal_error / total_in_bins if total_in_bins > 0 else 0.5
    composite = 0.50 * auc + 0.30 * (1.0 - cal_error) + 0.20 * threshold_acc
    return {"auc": auc, "cal_error": round(float(cal_error), 4), "threshold_acc": round(threshold_acc, 4), "composite": round(float(np.clip(composite, 0, 1)), 4), "n": len(results_tier)}

def create_bedrock_llm(model_id, timeout=600):
    import boto3
    from botocore.config import Config
    config = Config(read_timeout=timeout, connect_timeout=30, retries={'max_attempts': 0})
    client = boto3.Session(region_name='us-east-1').client('bedrock-runtime', config=config)
    
    def call_llm(prompt, max_retries=3):
        for attempt in range(max_retries + 1):
            try:
                resp = client.converse(
                    modelId=model_id,
                    messages=[{'role': 'user', 'content': [{'text': prompt}]}],
                    inferenceConfig={'maxTokens': 4096, 'temperature': 0.0}
                )
                for block in resp.get('output', {}).get('message', {}).get('content', []):
                    if 'text' in block:
                        return block['text']
                return ""
            except Exception as e:
                if attempt < max_retries:
                    time.sleep(5 * (2 ** attempt))
                    continue
                raise
    return call_llm

def run_model(canonical_id, bedrock_id, label):
    # Skip if already scored
    summary_path = os.path.join(RESULTS_DIR, f"{canonical_id}.summary.json")
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            data = json.load(f)
        print(f"  SKIP {label} — already scored: {data.get('weighted_score', '?')}")
        return data.get('weighted_score')

    print(f"  Running {label} ({bedrock_id})...")
    timeout = 900 if 'deepseek' in canonical_id else 600
    llm = create_bedrock_llm(bedrock_id, timeout=timeout)
    
    results = []
    transcript = []
    t0 = time.time()
    
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
            raw = llm(prompt)
            cleaned = _strip_think(raw)
            cleaned = _strip_fences(cleaned)
            # Strip JS-style comments
            cleaned = re.sub(r'//.*', '', cleaned)
            m = re.search(r'\{.*\}', cleaned, re.DOTALL)
            data = json.loads(m.group()) if m else {}
            rating = max(0, min(100, int(data.get("sincerity_rating", 50))))
            model_says_sarcastic = bool(data.get("is_sarcastic", False))
        except Exception as e:
            try:
                nums = re.findall(r'\b(\d{1,3})\b', str(raw))
                rating = max(0, min(100, int(nums[0]))) if nums else 50
                model_says_sarcastic = "sarcas" in str(raw).lower()
            except:
                rating = 50
                model_says_sarcastic = False
            raw = str(raw) if 'raw' in dir() else ""
        
        result = {
            "id": item["id"],
            "is_sarcastic": item["is_sarcastic"],
            "difficulty": item["difficulty"],
            "sincerity_rating": rating,
            "model_says_sarcastic": model_says_sarcastic,
            "binary_correct": (model_says_sarcastic == item["is_sarcastic"]),
        }
        results.append(result)
        transcript.append({
            "question_id": item["id"],
            "prompt": prompt[:500],
            "response": str(raw)[:2000] if 'raw' in dir() else "",
            "parsed_answer": {"sincerity_rating": rating, "is_sarcastic": model_says_sarcastic},
            "correct_answer": {"is_sarcastic": item["is_sarcastic"]},
            "score": 1.0 if result["binary_correct"] else 0.0,
            "difficulty": item["difficulty"],
        })
        
        if (idx + 1) % 10 == 0:
            print(f"    {idx+1}/{len(SARCASM_ITEMS)} items done")
        time.sleep(1)  # rate limit
    
    duration = time.time() - t0
    
    # Compute tiered scores
    t1 = compute_tier_composite([r for r in results if r["difficulty"] == 1])
    t2 = compute_tier_composite([r for r in results if r["difficulty"] == 2])
    t3 = compute_tier_composite([r for r in results if r["difficulty"] == 3])
    
    weighted = round(0.10 * t1["composite"] + 0.35 * t2["composite"] + 0.55 * t3["composite"], 4)
    
    summary = {
        "model": canonical_id,
        "label": label,
        "benchmark": "social_cog_sarcasm_v2",
        "n_items": len(results),
        "weighted_score": weighted,
        "tier1": t1,
        "tier2": t2,
        "tier3": t3,
        "duration_s": round(duration, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    # Save
    with open(os.path.join(RESULTS_DIR, f"{canonical_id}.jsonl"), 'w') as f:
        for t in transcript:
            f.write(json.dumps(t) + '\n')
    with open(os.path.join(RESULTS_DIR, f"{canonical_id}.summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"  {label}: score={weighted} (T1={t1['composite']}, T2={t2['composite']}, T3={t3['composite']}) [{duration:.0f}s]")
    return weighted

def main():
    print(f"=== Sarcasm v2 Benchmark Run ({len(SARCASM_ITEMS)} items, 3 tiers) ===")
    print(f"Items: T1={sum(1 for i in SARCASM_ITEMS if i['difficulty']==1)}, T2={sum(1 for i in SARCASM_ITEMS if i['difficulty']==2)}, T3={sum(1 for i in SARCASM_ITEMS if i['difficulty']==3)}")
    
    scores = {}
    for canonical_id, (label, bedrock_id) in MODEL_CATALOG.items():
        try:
            score = run_model(canonical_id, bedrock_id, label)
            if score is not None:
                scores[label] = score
        except Exception as e:
            print(f"  ERROR {label}: {e}")
            traceback.print_exc()
        time.sleep(5)
    
    print("\n=== RESULTS ===")
    for label, score in sorted(scores.items(), key=lambda x: -x[1]):
        print(f"  {label}: {score}")
    
    vals = list(scores.values())
    if vals:
        mean = np.mean(vals)
        std = np.std(vals)
        rng = max(vals) - min(vals)
        print(f"\nAggregate: mean={mean:.4f}, std={std:.4f}, range={rng:.4f}")
        print(f"std >= 0.08: {'PASS ✅' if std >= 0.08 else 'FAIL ❌'}")
        
        # Save aggregate
        agg = {"scores": scores, "mean": round(float(mean), 4), "std": round(float(std), 4), "range": round(float(rng), 4), "n_models": len(vals)}
        with open(os.path.join(RESULTS_DIR, "aggregate_stats.json"), 'w') as f:
            json.dump(agg, f, indent=2)

if __name__ == '__main__':
    main()
