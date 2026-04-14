#!/usr/bin/env python3
"""Generate score_matrix.csv from all model JSON result files."""
import json, glob, csv, os

RESULTS_DIR = "/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/metacognition/results"

# Load all model results
models = {}
all_benchmarks = set()
for f in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json"))):
    with open(f) as fh:
        data = json.load(fh)
    label = data.get("model_label", data.get("model", os.path.basename(f)))
    scores = data.get("scores", {})
    models[label] = scores
    all_benchmarks.update(scores.keys())

all_benchmarks = sorted(all_benchmarks)
model_labels = sorted(models.keys())

print(f"Models: {len(model_labels)}")
print(f"Benchmarks: {len(all_benchmarks)}")

# Write CSV
out_path = os.path.join(RESULTS_DIR, "score_matrix.csv")
with open(out_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["benchmark"] + model_labels)
    for bm in all_benchmarks:
        row = [bm]
        for ml in model_labels:
            entry = models[ml].get(bm, {})
            if entry.get("score") is not None:
                row.append(f"{entry['score']:.4f}")
            elif entry.get("error"):
                row.append(f"ERROR:{entry['error'][:40]}")
            else:
                row.append("")
        writer.writerow(row)

print(f"Written: {out_path}")
print(f"Shape: {len(all_benchmarks)} rows x {len(model_labels)} columns")
