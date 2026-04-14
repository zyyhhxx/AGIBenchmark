#!/usr/bin/env python3
"""Generate score_matrix_metacog_v2.csv from qa_transcripts summary files."""
import csv, json, os, glob

TRANSCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qa_transcripts')
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'score_matrix_metacog_v2.csv')

# Collect all summaries
data = {}  # {model: {benchmark: score}}
benchmarks = set()

for summary_path in sorted(glob.glob(os.path.join(TRANSCRIPT_DIR, '*', '*.summary.json'))):
    with open(summary_path) as f:
        s = json.load(f)
    model = s['model']
    bench = s['benchmark']
    score = s['score']
    benchmarks.add(bench)
    data.setdefault(model, {})[bench] = score

benchmarks = sorted(benchmarks)
models = sorted(data.keys())

print(f"Found {len(models)} models, {len(benchmarks)} benchmarks")
print(f"Total summaries: {sum(len(v) for v in data.values())}")

with open(OUTPUT, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['model'] + benchmarks + ['mean'])
    for model in models:
        scores = [data[model].get(b) for b in benchmarks]
        valid = [s for s in scores if s is not None]
        mean = sum(valid) / len(valid) if valid else None
        row = [model] + [f'{s:.4f}' if s is not None else '' for s in scores]
        row.append(f'{mean:.4f}' if mean else '')
        writer.writerow(row)

print(f"\nWrote {OUTPUT}")
print(f"\nMatrix preview:")
with open(OUTPUT) as f:
    print(f.read())
