#!/usr/bin/env python3
"""Run attention_divided benchmark against all 10 Bedrock models with Q&A transcript logging."""

import json, time, re, sys, os
import boto3
from botocore.config import Config

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace-agi-bench/repo/benchmarks/attention")

RESULTS_DIR = "/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/benchmark-qa/results/qa_transcripts/attention_divided"

MODELS = {
    "claude_opus_4.6": "us.anthropic.claude-opus-4-6-v1",
    "claude_sonnet_4.6": "us.anthropic.claude-sonnet-4-6",
    "deepseek_r1": "us.deepseek.r1-v1:0",
    "gpt_oss_120b": "openai.gpt-oss-120b-1:0",
    "llama_3.3_70b": "us.meta.llama3-3-70b-instruct-v1:0",
    "llama_4_maverick_17b": "us.meta.llama4-maverick-17b-instruct-v1:0",
    "nova_pro": "us.amazon.nova-pro-v1:0",
    "ministral_3b": "mistral.ministral-3-3b-instruct",
    "qwen3_next_80b": "qwen.qwen3-next-80b-a3b",
    "glm_4.7": "zai.glm-4.7",
}

TIMEOUT_MODELS = {"deepseek_r1": 900}
DEFAULT_TIMEOUT = 300

config = Config(
    region_name="us-east-1",
    read_timeout=900,
    retries={"max_attempts": 3, "mode": "adaptive"},
)
client = boto3.client("bedrock-runtime", config=config)


def call_model(model_id, prompt, timeout=300):
    """Call a Bedrock model and return the response text."""
    messages = [{"role": "user", "content": [{"text": prompt}]}]
    try:
        resp = client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={"maxTokens": 4096, "temperature": 0.0},
        )
        output = resp.get("output", {}).get("message", {}).get("content", [])
        texts = []
        for block in output:
            if "text" in block:
                texts.append(block["text"])
        return "\n".join(texts) if texts else ""
    except Exception as e:
        return f"ERROR: {e}"


def normalize_answer(text):
    t = str(text).strip().upper().replace(".", "").replace(",", "").replace('"', '').replace("'", "")
    for kw in ("NON-MAMMAL", "MAMMAL", "BIRD", "ODD", "EVEN", "HIGH", "LOW",
               "LARGER", "SMALLER", "EQUAL", "FIRST", "SECOND",
               "POSITIVE", "NEGATIVE", "YES", "NO", "ABOVE", "BELOW"):
        if kw in t:
            return kw
    nums = re.findall(r'-?\d+', t)
    if nums:
        return nums[0]
    letters = re.findall(r'\b([A-Z])\b', t)
    if letters:
        return letters[0]
    return t.split()[0] if t.split() else t


def check_answer(model_answer, expected):
    m = normalize_answer(str(model_answer))
    e = expected.strip().upper()
    return m == e


def extract_json(raw):
    try:
        return json.loads(raw)
    except Exception:
        pass
    m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Find largest JSON object
    best = None
    for m in re.finditer(r'\{.*?\}', raw, re.DOTALL):
        try:
            obj = json.loads(m.group())
            if best is None or len(m.group()) > len(json.dumps(best)):
                best = obj
        except Exception:
            continue
    # Try greedy match for nested
    m = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except Exception:
            pass
    return best or {}


# Import trial data from task_divided
from task_divided import EASY_TRIALS, MEDIUM_TRIALS, HARD_TRIALS


def run_model(model_label, model_id):
    """Run all trials for one model, save transcripts."""
    print(f"\n{'='*60}")
    print(f"Running: {model_label} ({model_id})")
    print(f"{'='*60}")
    
    timeout = TIMEOUT_MODELS.get(model_label, DEFAULT_TIMEOUT)
    transcripts = []
    tier_scores = {"easy": [], "medium": [], "hard": []}
    
    # EASY trials (flat answers)
    for trial in EASY_TRIALS:
        t0 = time.time()
        raw = call_model(model_id, trial["prompt"], timeout)
        elapsed = time.time() - t0
        
        parsed = extract_json(raw)
        model_answers = parsed.get("answers", [])
        expected = trial["answers"]
        
        correct = 0
        total = len(expected)
        item_scores = []
        for i, exp in enumerate(expected):
            ma = str(model_answers[i]) if i < len(model_answers) else ""
            ok = check_answer(ma, exp)
            if ok:
                correct += 1
            item_scores.append(1.0 if ok else 0.0)
        
        acc = correct / total if total > 0 else 0.0
        tier_scores["easy"].append(acc)
        
        transcripts.append({
            "question_id": trial["id"],
            "tier": "easy",
            "prompt": trial["prompt"],
            "response": raw,
            "parsed_answer": model_answers,
            "correct_answer": expected,
            "item_scores": item_scores,
            "score": acc,
            "duration_s": round(elapsed, 1),
        })
        print(f"  [easy  ] {trial['id']}: {acc:.3f} ({elapsed:.1f}s)")
    
    # MEDIUM trials (flat answers)
    for trial in MEDIUM_TRIALS:
        t0 = time.time()
        raw = call_model(model_id, trial["prompt"], timeout)
        elapsed = time.time() - t0
        
        parsed = extract_json(raw)
        model_answers = parsed.get("answers", [])
        expected = trial["answers"]
        
        correct = 0
        total = len(expected)
        item_scores = []
        for i, exp in enumerate(expected):
            ma = str(model_answers[i]) if i < len(model_answers) else ""
            ok = check_answer(ma, exp)
            if ok:
                correct += 1
            item_scores.append(1.0 if ok else 0.0)
        
        acc = correct / total if total > 0 else 0.0
        tier_scores["medium"].append(acc)
        
        transcripts.append({
            "question_id": trial["id"],
            "tier": "medium",
            "prompt": trial["prompt"],
            "response": raw,
            "parsed_answer": model_answers,
            "correct_answer": expected,
            "item_scores": item_scores,
            "score": acc,
            "duration_s": round(elapsed, 1),
        })
        print(f"  [medium] {trial['id']}: {acc:.3f} ({elapsed:.1f}s)")
    
    # HARD trials (structured results)
    for trial in HARD_TRIALS:
        t0 = time.time()
        raw = call_model(model_id, trial["prompt"], timeout)
        elapsed = time.time() - t0
        
        parsed = extract_json(raw)
        results_list = parsed.get("results", [])
        expected_list = trial["answers"]
        
        correct = 0
        total = 0
        item_scores = []
        parsed_answers = []
        
        for i, exp in enumerate(expected_list):
            if i < len(results_list):
                item = results_list[i]
                parsed_answers.append(item)
                for key in ("A", "B", "C"):
                    total += 1
                    model_val = str(item.get(key, ""))
                    ok = check_answer(model_val, exp[key])
                    if ok:
                        correct += 1
                    item_scores.append(1.0 if ok else 0.0)
            else:
                parsed_answers.append({})
                total += len(exp)
                item_scores.extend([0.0] * len(exp))
        
        acc = correct / total if total > 0 else 0.0
        tier_scores["hard"].append(acc)
        
        transcripts.append({
            "question_id": trial["id"],
            "tier": "hard",
            "prompt": trial["prompt"],
            "response": raw,
            "parsed_answer": parsed_answers,
            "correct_answer": [dict(e) for e in expected_list],
            "item_scores": item_scores,
            "score": acc,
            "duration_s": round(elapsed, 1),
        })
        print(f"  [hard  ] {trial['id']}: {acc:.3f} ({elapsed:.1f}s)")
    
    # Compute composite
    easy_mean = sum(tier_scores["easy"]) / len(tier_scores["easy"]) if tier_scores["easy"] else 0
    medium_mean = sum(tier_scores["medium"]) / len(tier_scores["medium"]) if tier_scores["medium"] else 0
    hard_mean = sum(tier_scores["hard"]) / len(tier_scores["hard"]) if tier_scores["hard"] else 0
    composite = round(0.20 * easy_mean + 0.30 * medium_mean + 0.50 * hard_mean, 4)
    
    print(f"\n  EASY={easy_mean:.3f}  MEDIUM={medium_mean:.3f}  HARD={hard_mean:.3f}")
    print(f"  COMPOSITE: {composite:.4f}")
    
    # Save transcripts
    transcript_path = os.path.join(RESULTS_DIR, f"{model_label}.jsonl")
    with open(transcript_path, "w") as f:
        for t in transcripts:
            f.write(json.dumps(t) + "\n")
    
    # Save summary
    summary = {
        "model_label": model_label,
        "model_id": model_id,
        "composite_score": composite,
        "tier_scores": {
            "easy": easy_mean,
            "medium": medium_mean,
            "hard": hard_mean,
        },
        "per_trial": {t["question_id"]: t["score"] for t in transcripts},
        "total_duration_s": sum(t["duration_s"] for t in transcripts),
        "n_trials": len(transcripts),
    }
    summary_path = os.path.join(RESULTS_DIR, f"{model_label}.summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    return model_label, composite, summary


def main():
    all_scores = {}
    all_summaries = {}
    failures = []
    
    for model_label, model_id in MODELS.items():
        # Skip if already completed
        summary_path = os.path.join(RESULTS_DIR, f"{model_label}.summary.json")
        if os.path.exists(summary_path):
            with open(summary_path) as f:
                existing = json.load(f)
            if existing.get("composite_score") is not None:
                print(f"\nSkipping {model_label} (already scored: {existing['composite_score']})")
                all_scores[model_label] = existing["composite_score"]
                all_summaries[model_label] = existing
                continue
        
        try:
            label, score, summary = run_model(model_label, model_id)
            all_scores[label] = score
            all_summaries[label] = summary
        except Exception as e:
            print(f"\nFAILED: {model_label}: {e}")
            failures.append((model_label, str(e)))
        
        time.sleep(3)  # Rate limit between models
    
    # Retry failures once with doubled timeout
    for model_label, error in list(failures):
        print(f"\nRetrying {model_label} with doubled timeout...")
        model_id = MODELS[model_label]
        orig_timeout = TIMEOUT_MODELS.get(model_label, DEFAULT_TIMEOUT)
        TIMEOUT_MODELS[model_label] = orig_timeout * 2
        try:
            label, score, summary = run_model(model_label, model_id)
            all_scores[label] = score
            all_summaries[label] = summary
            failures.remove((model_label, error))
        except Exception as e:
            print(f"\nRetry FAILED: {model_label}: {e}")
    
    # Aggregate stats
    scores = list(all_scores.values())
    if scores:
        import statistics
        mean_score = statistics.mean(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
        range_score = max(scores) - min(scores)
    else:
        mean_score = std_score = range_score = 0.0
    
    aggregate = {
        "benchmark": "attention_divided",
        "n_models": len(scores),
        "n_failures": len(failures),
        "mean": round(mean_score, 4),
        "std": round(std_score, 4),
        "range": round(range_score, 4),
        "min": round(min(scores), 4) if scores else None,
        "max": round(max(scores), 4) if scores else None,
        "per_model": {k: round(v, 4) for k, v in sorted(all_scores.items(), key=lambda x: -x[1])},
        "failures": [{"model": m, "error": e} for m, e in failures],
    }
    
    agg_path = os.path.join(RESULTS_DIR, "aggregate_stats.json")
    with open(agg_path, "w") as f:
        json.dump(aggregate, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"AGGREGATE RESULTS — attention_divided")
    print(f"{'='*60}")
    print(f"Models scored: {len(scores)}/10")
    print(f"Mean:  {mean_score:.4f}")
    print(f"Std:   {std_score:.4f}")
    print(f"Range: {range_score:.4f}")
    print(f"\nPer-model scores (descending):")
    for m, s in sorted(all_scores.items(), key=lambda x: -x[1]):
        print(f"  {m:30s} {s:.4f}")
    if failures:
        print(f"\nPersistent failures:")
        for m, e in failures:
            print(f"  {m}: {e}")
    
    print(f"\nResults saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
