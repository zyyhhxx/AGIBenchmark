#!/usr/bin/env python3
"""Build metacog_final_scores.csv from results/*.json — models only"""
import json, os, csv, statistics

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = os.path.join(REPO, "results")
OUTPUT_CSV = os.path.join(REPO, "results", "metacog_final_scores.csv")
OUTPUT_DIR = os.path.join(REPO, "sub-workflows", "metacognition")

METACOG_BENCHMARKS = [
    "metacog_canary", "metacog_calibration", "metacog_control",
    "metacog_epistemic_humility", "metacog_epistemic_revision",
    "metacog_error_detection", "metacog_fok", "metacog_jol",
    "metacog_learning_monitoring"
]

# Only model files (have model_label and scores with metacog keys)
MODEL_FILES = [
    "amazon.nova-pro-v1_0.json",
    "anthropic.claude-opus-4-6-v1.json",
    "anthropic.claude-sonnet-4-6.json",
    "deepseek.r1-v1_0.json",
    "meta.llama3-3-70b-instruct-v1_0.json",
    "meta.llama4-maverick-17b-instruct-v1_0.json",
    "mistral.ministral-3-3b-instruct.json",
    "openai.gpt-oss-120b-1_0.json",
    "qwen.qwen3-next-80b-a3b.json",
    "zai.glm-4.7.json",
]

rows = []
for fname in MODEL_FILES:
    fpath = os.path.join(RESULTS_DIR, fname)
    if not os.path.exists(fpath):
        continue
    d = json.load(open(fpath))
    label = d.get("model_label", fname)
    for bname in METACOG_BENCHMARKS:
        entry = d.get("scores", {}).get(bname, {})
        rows.append({
            "benchmark": bname,
            "model": label,
            "model_id": d.get("model", fname),
            "score": entry.get("score"),
            "duration_s": entry.get("duration_s"),
            "error": entry.get("error"),
        })

# Write CSV
with open(OUTPUT_CSV, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["benchmark","model","model_id","score","duration_s","error"])
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")

# Per-benchmark stats
print(f"\n{'Benchmark':40s} {'Mean':>6s} {'Std':>6s} {'Min':>6s} {'Max':>6s} {'Range':>6s} {'N':>3s}")
print("-"*80)
all_stds = []
for bname in METACOG_BENCHMARKS:
    scores = [r["score"] for r in rows if r["benchmark"] == bname and r["score"] is not None]
    if len(scores) >= 2:
        m = statistics.mean(scores)
        s = statistics.stdev(scores)
        mn = min(scores)
        mx = max(scores)
        rng = mx - mn
        all_stds.append(s)
        print(f"{bname:40s} {m:6.4f} {s:6.4f} {mn:6.4f} {mx:6.4f} {rng:6.4f} {len(scores):3d}")

if all_stds:
    avg_std = statistics.mean(all_stds)
    print(f"\nAverage std across 9 benchmarks: {avg_std:.4f}")
    print(f"Target: >= 0.10 → {'PASS ✅' if avg_std >= 0.10 else 'FAIL ❌'}")

# Full score matrix
models = sorted(set(r["model"] for r in rows))
print(f"\n\nFULL SCORE MATRIX (10 models × 9 benchmarks)")
print(f"{'Benchmark':40s}" + "".join(f"{m[:15]:>16s}" for m in models))
print("-"*200)
for bname in METACOG_BENCHMARKS:
    line = f"{bname:40s}"
    for model in models:
        match = [r for r in rows if r["benchmark"]==bname and r["model"]==model]
        if match and match[0]["score"] is not None:
            line += f"{match[0]['score']:16.4f}"
        else:
            line += f"{'ERR':>16s}"
    print(line)

# Check KNOWLEDGE baselines
print("\n\nREGRESSION CHECK vs KNOWLEDGE baselines (Claude Sonnet 4 from 2026-04-09):")
BASELINES = {
    "metacog_canary": 0.951, "metacog_epistemic_humility": 0.926,
    "metacog_error_detection": 0.882, "metacog_epistemic_revision": 0.820,
    "metacog_learning_monitoring": 0.698, "metacog_control": 0.689,
    "metacog_jol": 0.465, "metacog_fok": 0.449, "metacog_calibration": 0.000,
}
# Use Claude Sonnet 4.6 as comparison
sonnet_scores = {r["benchmark"]: r["score"] for r in rows if r["model"]=="Claude Sonnet 4.6" and r["score"] is not None}
for bname, baseline in BASELINES.items():
    current = sonnet_scores.get(bname)
    if current is not None:
        delta = current - baseline
        flag = "⚠️ REGRESSION" if delta < -0.05 else "✅ OK"
        print(f"  {bname:40s} baseline={baseline:.4f} current={current:.4f} Δ={delta:+.4f} {flag}")
    else:
        print(f"  {bname:40s} baseline={baseline:.4f} current=ERROR")
