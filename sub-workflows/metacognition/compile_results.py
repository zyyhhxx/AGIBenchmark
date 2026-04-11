#!/usr/bin/env python3
"""
Compile all benchmark results into score_matrix_all_tracks.csv and generate
per-track discriminatory analysis summaries.
"""
import json, glob, os, csv, sys
import numpy as np
from collections import defaultdict

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = f"{REPO}/results"
OUTPUT_CSV = f"{RESULTS_DIR}/score_matrix_all_tracks.csv"
OUTPUT_DIR = f"{REPO}/sub-workflows/metacognition/results"

# Model files (exclude non-model JSONs)
MODEL_IDS = [
    "anthropic.claude-opus-4-6-v1",
    "anthropic.claude-sonnet-4-6",
    "deepseek.r1-v1_0",
    "zai.glm-4.7",
    "openai.gpt-oss-120b-1_0",
    "meta.llama3-3-70b-instruct-v1_0",
    "meta.llama4-maverick-17b-instruct-v1_0",
    "mistral.ministral-3-3b-instruct",
    "amazon.nova-pro-v1_0",
    "qwen.qwen3-next-80b-a3b",
]

TRACKS = {
    "attention": ["attention_divided", "attention_instruction_update", "attention_selective", "attention_vigilance"],
    "learning": ["learning_curves", "learning_transfer", "learning_interference", "learning_curriculum"],
    "executive_functions": ["exec_func_crt", "exec_func_nback", "exec_func_task_switch", "exec_func_tol", "exec_func_wcst"],
    "social_cognition": ["social_cog_emotional_prosody", "social_cog_false_belief", "social_cog_pragmatic", "social_cog_sarcasm"],
    "metacognition": ["metacog_calibration", "metacog_canary", "metacog_control", "metacog_epistemic_humility",
                       "metacog_epistemic_revision", "metacog_error_detection", "metacog_fok", "metacog_jol",
                       "metacog_learning_monitoring"],
}

ALL_BENCHMARKS = []
for track in ["attention", "learning", "executive_functions", "social_cognition", "metacognition"]:
    ALL_BENCHMARKS.extend(TRACKS[track])

# Load all model data
model_data = {}
for mid in MODEL_IDS:
    fpath = os.path.join(RESULTS_DIR, f"{mid}.json")
    if not os.path.exists(fpath):
        print(f"WARNING: {fpath} not found")
        continue
    with open(fpath) as f:
        data = json.load(f)
    label = data.get("model_label", mid)
    scores = data.get("scores", {})
    model_data[label] = {}
    for bm in ALL_BENCHMARKS:
        val = scores.get(bm)
        if isinstance(val, dict):
            s = val.get("score")
            if s is not None and val.get("error") is None:
                model_data[label][bm] = float(s)
            else:
                model_data[label][bm] = None
        elif isinstance(val, (int, float)):
            model_data[label][bm] = float(val)
        else:
            model_data[label][bm] = None

# Sort models alphabetically
model_labels = sorted(model_data.keys())

# Write score_matrix_all_tracks.csv
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["benchmark"] + model_labels)
    for bm in ALL_BENCHMARKS:
        row = [bm]
        for ml in model_labels:
            val = model_data[ml].get(bm)
            row.append(f"{val:.4f}" if val is not None else "")
        writer.writerow(row)

print(f"Wrote {OUTPUT_CSV}")
print(f"  {len(ALL_BENCHMARKS)} benchmarks × {len(model_labels)} models")

# Count completeness
total = len(ALL_BENCHMARKS) * len(model_labels)
filled = sum(1 for bm in ALL_BENCHMARKS for ml in model_labels if model_data[ml].get(bm) is not None)
print(f"  Completeness: {filled}/{total} ({100*filled/total:.1f}%)")

# Also update the old score_matrix.csv for backward compat
OLD_CSV = f"{RESULTS_DIR}/score_matrix.csv"
with open(OLD_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["benchmark"] + model_labels)
    for bm in ALL_BENCHMARKS:
        row = [bm]
        for ml in model_labels:
            val = model_data[ml].get(bm)
            row.append(f"{val:.4f}" if val is not None else "ERROR")
        writer.writerow(row)
print(f"Updated {OLD_CSV}")

# Generate per-track discriminatory analysis
os.makedirs(OUTPUT_DIR, exist_ok=True)

analysis_lines = ["# Discriminatory Analysis — All Tracks\n"]
analysis_lines.append(f"Generated from {filled}/{total} benchmark-model scores ({100*filled/total:.1f}% complete)\n\n")

for track_name, benchmarks in TRACKS.items():
    analysis_lines.append(f"## {track_name.replace('_', ' ').title()}\n\n")
    analysis_lines.append("| Benchmark | Mean | Std | Min | Max | Range | N |\n")
    analysis_lines.append("|-----------|------|-----|-----|-----|-------|---|\n")
    
    track_scores_all = []
    for bm in benchmarks:
        vals = [model_data[ml][bm] for ml in model_labels if model_data[ml].get(bm) is not None]
        if vals:
            arr = np.array(vals)
            analysis_lines.append(
                f"| {bm} | {arr.mean():.4f} | {arr.std():.4f} | {arr.min():.4f} | {arr.max():.4f} | {arr.max()-arr.min():.4f} | {len(vals)} |\n"
            )
            track_scores_all.extend(vals)
        else:
            analysis_lines.append(f"| {bm} | — | — | — | — | — | 0 |\n")
    
    if track_scores_all:
        arr = np.array(track_scores_all)
        analysis_lines.append(f"\n**Track summary:** mean={arr.mean():.4f}, std={arr.std():.4f}, range=[{arr.min():.4f}, {arr.max():.4f}]\n\n")
    analysis_lines.append("\n")

# Model rankings per track
analysis_lines.append("## Model Rankings by Track\n\n")
for track_name, benchmarks in TRACKS.items():
    analysis_lines.append(f"### {track_name.replace('_', ' ').title()}\n\n")
    model_avgs = []
    for ml in model_labels:
        vals = [model_data[ml][bm] for bm in benchmarks if model_data[ml].get(bm) is not None]
        if vals:
            model_avgs.append((ml, np.mean(vals), len(vals)))
    model_avgs.sort(key=lambda x: -x[1])
    analysis_lines.append("| Rank | Model | Avg Score | Benchmarks Completed |\n")
    analysis_lines.append("|------|-------|-----------|---------------------|\n")
    for i, (ml, avg, n) in enumerate(model_avgs, 1):
        analysis_lines.append(f"| {i} | {ml} | {avg:.4f} | {n}/{len(benchmarks)} |\n")
    analysis_lines.append("\n")

analysis_path = os.path.join(OUTPUT_DIR, "discriminatory_analysis_all_tracks.md")
with open(analysis_path, "w") as f:
    f.writelines(analysis_lines)
print(f"Wrote {analysis_path}")

# Also write to repo/results/
with open(os.path.join(RESULTS_DIR, "discriminatory_analysis_all_tracks.md"), "w") as f:
    f.writelines(analysis_lines)
print(f"Wrote {RESULTS_DIR}/discriminatory_analysis_all_tracks.md")
