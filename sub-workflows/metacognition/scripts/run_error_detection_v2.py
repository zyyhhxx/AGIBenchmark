#!/usr/bin/env python3
"""Run error_detection v2 against all 10 Bedrock models sequentially."""
import sys, os, json, time, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'benchmarks', 'metacognition'))

import boto3
from botocore.config import Config
import numpy as np
import re

from data.error_detection_chains import REASONING_CHAINS

MODELS = [
    ("Claude Opus 4.6", "us.anthropic.claude-opus-4-6-v1"),
    ("Claude Sonnet 4.5", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"),
    ("DeepSeek-R1", "us.deepseek.r1-v1:0"),
    ("GPT-OSS-120B", "openai.gpt-oss-120b-1:0"),
    ("Llama 3.3 70B", "meta.llama3-3-70b-instruct-v1:0"),
    ("Llama 4 Maverick 17B", "us.meta.llama4-maverick-17b-instruct-v1:0"),
    ("GLM 4.7", "zai.glm-4.7"),
    ("Qwen3 Next 80B", "qwen.qwen3-next-80b-a3b"),
    ("Nova Pro", "amazon.nova-pro-v1:0"),
    ("Ministral 3B", "mistral.ministral-3-3b-instruct"),
]

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(RESULTS_DIR, 'error_detection_v2_scores.csv')

config = Config(read_timeout=300, retries={'max_attempts': 3, 'mode': 'adaptive'})
client = boto3.client('bedrock-runtime', region_name='us-east-1', config=config)


def strip_think(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def call_model(model_id, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            body = json.dumps({
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024,
                "temperature": 0,
            })
            # Use converse API for broader compatibility
            resp = client.converse(
                modelId=model_id,
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 1024, "temperature": 0},
            )
            text = resp['output']['message']['content'][0]['text']
            return strip_think(text)
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 5 * (2 ** attempt)
                print(f"    Retry {attempt+1} after error: {e}")
                time.sleep(wait)
            else:
                raise


def parse_response(raw):
    try:
        parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
        return (
            bool(parsed.get("has_error", False)),
            int(parsed.get("error_step", 0)),
            max(0, min(100, int(parsed.get("confidence", 50)))),
        )
    except Exception:
        raw_lower = raw.lower()
        has_err = any(w in raw_lower for w in ["error", "mistake", "incorrect", "wrong"])
        return has_err, 0, 50


def compute_f1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) > 0 else 0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0


def compute_ece(confidences, accuracies, n_bins=5):
    conf = np.array(confidences) / 100.0
    acc = np.array(accuracies, dtype=float)
    boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total = len(conf)
    for i in range(n_bins):
        lo, hi = boundaries[i], boundaries[i + 1]
        mask = (conf >= lo) & (conf <= hi) if i == 0 else (conf > lo) & (conf <= hi)
        if mask.sum() == 0:
            continue
        ece += (mask.sum() / total) * abs(acc[mask].mean() - conf[mask].mean())
    return round(float(ece), 4)


def goodman_kruskal_gamma(x, y):
    n = len(x)
    conc = disc = 0
    for i in range(n):
        for j in range(i + 1, n):
            prod = (x[i] - x[j]) * (y[i] - y[j])
            if prod > 0: conc += 1
            elif prod < 0: disc += 1
    denom = conc + disc
    return (conc - disc) / denom if denom > 0 else 0.0


def score_model(model_label, model_id):
    print(f"\n{'='*60}")
    print(f"Running: {model_label} ({model_id})")
    print(f"{'='*60}")

    results = []
    diff_map = {1: 1.0, 2: 2.0, 3: 3.0}

    for i, chain in enumerate(REASONING_CHAINS):
        steps_text = "\n".join(chain["steps"])
        prompt = (
            f"Review the following step-by-step solution for errors.\n\n"
            f"**Problem:** {chain['problem']}\n\n"
            f"**Solution:**\n{steps_text}\n\n"
            f"**Final answer:** {chain['final_answer']}\n\n"
            f"Carefully check each step. Does this solution contain an error?\n\n"
            f"Respond with ONLY a JSON object:\n"
            f'{{"has_error": true/false, "error_step": <step number or 0>, '
            f'"explanation": "<explain the error or why correct>", '
            f'"confidence": <0-100>}}'
        )
        try:
            raw = call_model(model_id, prompt)
            pred_has_error, pred_step, confidence = parse_response(raw)
        except Exception as e:
            print(f"  [{chain['id']}] ERROR: {e}")
            pred_has_error, pred_step, confidence = False, 0, 50

        actual_has_error = chain["has_error"]
        detection_correct = pred_has_error == actual_has_error
        localization_correct = (actual_has_error and pred_has_error and
                                chain["error_step"] is not None and
                                pred_step == chain["error_step"])

        results.append({
            "detection_correct": detection_correct,
            "localization_correct": localization_correct,
            "confidence": confidence,
            "actual_has_error": actual_has_error,
            "pred_has_error": pred_has_error,
            "difficulty": chain["difficulty"],
        })

        if (i + 1) % 10 == 0:
            print(f"  Completed {i+1}/{len(REASONING_CHAINS)} items")
        time.sleep(1)  # Rate limit

    # Compute score (same formula as task_error_detection.py)
    tp = sum(1 for r in results if r["actual_has_error"] and r["pred_has_error"])
    fp = sum(1 for r in results if not r["actual_has_error"] and r["pred_has_error"])
    fn = sum(1 for r in results if r["actual_has_error"] and not r["pred_has_error"])

    f1 = compute_f1(tp, fp, fn)

    weighted_correct = sum(diff_map.get(r["difficulty"], 1.0) for r in results if r["detection_correct"])
    weighted_total = sum(diff_map.get(r["difficulty"], 1.0) for r in results)
    weighted_detection = weighted_correct / weighted_total if weighted_total > 0 else 0

    error_chains = [r for r in results if r["actual_has_error"] and r["pred_has_error"]]
    if error_chains:
        loc_weighted = sum(diff_map.get(r["difficulty"], 1.0) for r in error_chains if r["localization_correct"])
        loc_total = sum(diff_map.get(r["difficulty"], 1.0) for r in error_chains)
        localization_acc = loc_weighted / loc_total if loc_total > 0 else 0
    else:
        localization_acc = 0.0

    confidences = [r["confidence"] for r in results]
    detection_accuracies = [r["detection_correct"] for r in results]
    ece = compute_ece(confidences, detection_accuracies)
    gamma = goodman_kruskal_gamma(confidences, [int(a) for a in detection_accuracies])
    gamma_norm = (gamma + 1) / 2

    score = round(0.30 * weighted_detection + 0.10 * f1 + 0.25 * localization_acc + 0.20 * (1 - ece) + 0.15 * gamma_norm, 4)

    print(f"  F1={f1:.4f}, WeightedDet={weighted_detection:.4f}, Loc={localization_acc:.4f}, ECE={ece:.4f}, Gamma={gamma:.4f}")
    print(f"  SCORE: {score:.4f}")

    return score, f1, weighted_detection, localization_acc, ece, gamma


def main():
    rows = []
    for model_label, model_id in MODELS:
        try:
            score, f1, wdet, loc, ece, gamma = score_model(model_label, model_id)
            rows.append({
                "model": model_label,
                "model_id": model_id,
                "score": score,
                "f1": f1,
                "weighted_detection": wdet,
                "localization_acc": loc,
                "ece": ece,
                "gamma": gamma,
            })
        except Exception as e:
            print(f"FAILED: {model_label}: {e}")
            rows.append({
                "model": model_label,
                "model_id": model_id,
                "score": "ERROR",
                "f1": "", "weighted_detection": "", "localization_acc": "", "ece": "", "gamma": "",
            })
        time.sleep(3)

    # Write CSV
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["model", "model_id", "score", "f1", "weighted_detection", "localization_acc", "ece", "gamma"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'='*60}")
    print(f"Results saved to {OUTPUT_CSV}")
    print(f"{'='*60}")

    # Summary
    valid = [r for r in rows if r["score"] != "ERROR"]
    if valid:
        scores = [float(r["score"]) for r in valid]
        print(f"\nSummary ({len(valid)} models):")
        print(f"  Mean:  {np.mean(scores):.4f}")
        print(f"  Std:   {np.std(scores):.4f}")
        print(f"  Range: {max(scores) - min(scores):.4f}")
        print(f"  Min:   {min(scores):.4f} ({[r['model'] for r in valid if float(r['score']) == min(scores)][0]})")
        print(f"  Max:   {max(scores):.4f} ({[r['model'] for r in valid if float(r['score']) == max(scores)][0]})")
        above_95 = sum(1 for s in scores if s > 0.95)
        print(f"  Models > 0.95: {above_95}/{len(valid)} ({100*above_95/len(valid):.0f}%)")


if __name__ == '__main__':
    main()
