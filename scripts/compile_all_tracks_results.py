#!/usr/bin/env python3
"""
Compile all non-metacognition benchmark results into score_matrix_all_tracks.csv
and generate per-track discriminatory analysis summaries.
"""
import json, os, csv
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO, "results")

MODEL_FILES = {
    "Claude Opus 4.6":        "anthropic.claude-opus-4-6-v1.json",
    "DeepSeek-R1":            "deepseek.r1-v1_0.json",
    "GPT-OSS-120B":           "openai.gpt-oss-120b-1_0.json",
    "Llama 3.3 70B":          "meta.llama3-3-70b-instruct-v1_0.json",
    "Qwen3 Next 80B":         "qwen.qwen3-next-80b-a3b.json",
    "Nova Pro":               "amazon.nova-pro-v1_0.json",
    "Llama 4 Maverick 17B":   "meta.llama4-maverick-17b-instruct-v1_0.json",
    "Claude Sonnet 4.6":      "anthropic.claude-sonnet-4-6.json",
    "GLM 4.7":                "zai.glm-4.7.json",
    "Ministral 3B":           "mistral.ministral-3-3b-instruct.json",
}

TRACKS = {
    "learning": [
        "learning_curves", "learning_transfer", "learning_interference", "learning_curriculum"
    ],
    "attention": [
        "attention_selective", "attention_vigilance", "attention_divided", "attention_instruction_update"
    ],
    "executive_functions": [
        "exec_func_wcst", "exec_func_tol", "exec_func_task_switch", "exec_func_nback", "exec_func_crt"
    ],
    "social_cognition": [
        "social_cog_false_belief", "social_cog_pragmatic", "social_cog_sarcasm", "social_cog_emotional_prosody"
    ],
}

# Load all results
all_scores = {}  # model_label -> {benchmark -> score or None}
for label, fname in MODEL_FILES.items():
    path = os.path.join(RESULTS_DIR, fname)
    if not os.path.exists(path):
        all_scores[label] = {}
        continue
    with open(path) as f:
        data = json.load(f)
    scores = data.get("scores", {})
    all_scores[label] = {
        b: scores[b]["score"] for b in scores
        if scores[b].get("score") is not None
    }

# All benchmarks (non-metacog)
all_benchmarks = []
for blist in TRACKS.values():
    all_benchmarks.extend(blist)

# === Step 3: Write score_matrix_all_tracks.csv ===
out_csv = os.path.join(RESULTS_DIR, "score_matrix_all_tracks.csv")
models = list(MODEL_FILES.keys())
with open(out_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["track", "benchmark"] + models)
    for track, benchmarks in TRACKS.items():
        for bench in benchmarks:
            row = [track, bench]
            for model in models:
                score = all_scores.get(model, {}).get(bench)
                row.append(f"{score:.4f}" if score is not None else "")
            writer.writerow(row)

print(f"Written: {out_csv}")

# === Step 4: Per-track discriminatory analysis ===
analysis_lines = ["# Per-Track Discriminatory Analysis — Non-Metacognition Benchmarks\n\n"]
analysis_lines.append("Generated from Bedrock multi-model runs (10 models).\n\n")

grand_table = []

for track, benchmarks in TRACKS.items():
    analysis_lines.append(f"## Track: {track}\n\n")
    analysis_lines.append(f"| Benchmark | N_models | Mean | Std | Min | Max | Range |\n")
    analysis_lines.append(f"|-----------|----------|------|-----|-----|-----|-------|\n")
    
    for bench in benchmarks:
        scores = [
            all_scores.get(m, {}).get(bench)
            for m in models
            if all_scores.get(m, {}).get(bench) is not None
        ]
        if not scores:
            analysis_lines.append(f"| {bench} | 0 | — | — | — | — | — |\n")
            continue
        arr = np.array(scores)
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        mn = float(np.min(arr))
        mx = float(np.max(arr))
        rng = mx - mn
        n = len(scores)
        analysis_lines.append(
            f"| {bench} | {n} | {mean:.3f} | {std:.3f} | {mn:.3f} | {mx:.3f} | {rng:.3f} |\n"
        )
        grand_table.append({
            "track": track, "benchmark": bench, "n": n,
            "mean": mean, "std": std, "min": mn, "max": mx, "range": rng
        })
    analysis_lines.append("\n")

# Per-model summary across all non-metacog benchmarks
analysis_lines.append("## Per-Model Summary (Non-Metacog Tracks)\n\n")
analysis_lines.append("| Model | N_benchmarks | Mean Score | Std |\n")
analysis_lines.append("|-------|-------------|------------|-----|\n")
model_summaries = []
for model in models:
    s = [v for b, v in all_scores.get(model, {}).items() if b in all_benchmarks and v is not None]
    if s:
        arr = np.array(s)
        model_summaries.append((model, len(s), float(np.mean(arr)), float(np.std(arr))))
        analysis_lines.append(f"| {model} | {len(s)} | {np.mean(arr):.3f} | {np.std(arr):.3f} |\n")
    else:
        analysis_lines.append(f"| {model} | 0 | — | — |\n")

analysis_lines.append("\n")

# Top discriminating benchmarks
if grand_table:
    sorted_by_std = sorted(grand_table, key=lambda x: -x["std"])
    analysis_lines.append("## Top Discriminating Benchmarks (by std)\n\n")
    analysis_lines.append("| Rank | Benchmark | Track | Std | Range | N |\n")
    analysis_lines.append("|------|-----------|-------|-----|-------|---|\n")
    for i, row in enumerate(sorted_by_std[:10], 1):
        analysis_lines.append(
            f"| {i} | {row['benchmark']} | {row['track']} | {row['std']:.3f} | {row['range']:.3f} | {row['n']} |\n"
        )

# Write analysis
out_md = os.path.join(RESULTS_DIR, "non_metacog_discriminatory_summary.md")
with open(out_md, "w") as f:
    f.writelines(analysis_lines)
print(f"Written: {out_md}")

# Print results to stdout for scribe
print("\n" + "="*60)
print("SCORE MATRIX — NON-METACOGNITION TRACKS (10 models × 17 benchmarks)")
print("="*60)
print(f"{'Benchmark':<40} {'Models scored':>14}")
for row in grand_table:
    print(f"  {row['benchmark']:<38} n={row['n']:2d}  mean={row['mean']:.3f}  std={row['std']:.3f}  range={row['range']:.3f}")

print("\n" + "="*60)
print("PER-MODEL SUMMARY (non-metacog tracks)")
print("="*60)
for model, n, mean, std in model_summaries:
    print(f"  {model:<30}  n={n:2d}  mean={mean:.3f}  std={std:.3f}")

print("\n" + "="*60)
print("TOP 5 DISCRIMINATING BENCHMARKS")
print("="*60)
for i, row in enumerate(sorted_by_std[:5], 1):
    print(f"  {i}. {row['benchmark']:<40} std={row['std']:.3f}  range={row['range']:.3f}")

print("\nArtifacts:")
print(f"  {out_csv}")
print(f"  {out_md}")
