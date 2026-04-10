#!/usr/bin/env python3
"""Merge all model JSON result files into score_matrix.csv."""
import json, os, csv, glob

RESULTS_DIR = "/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/metacognition/results"

def main():
    files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json")))
    if not files:
        print("ERROR: No JSON files found in results/")
        return

    # Load all results
    models = []
    all_benchmarks = set()
    for f in files:
        with open(f) as fh:
            d = json.load(fh)
        models.append(d)
        all_benchmarks.update(d.get("scores", {}).keys())

    benchmarks = sorted(all_benchmarks)
    model_labels = [d.get("model_label", d.get("model", "?")) for d in models]

    print(f"Models: {len(models)}")
    print(f"Benchmarks: {len(benchmarks)}")

    # Write CSV
    out = os.path.join(RESULTS_DIR, "score_matrix.csv")
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["benchmark"] + model_labels)
        for bm in benchmarks:
            row = [bm]
            for d in models:
                entry = d.get("scores", {}).get(bm, {})
                score = entry.get("score")
                error = entry.get("error")
                if score is not None:
                    row.append(f"{score:.4f}")
                elif error:
                    row.append(f"ERROR:{error[:40]}")
                else:
                    row.append("MISSING")
            w.writerow(row)

    print(f"Wrote {out}")
    print(f"  {len(benchmarks)} rows × {len(models)} model columns")

    # Summary per model
    print("\nPer-model summary:")
    for d in models:
        label = d.get("model_label", "?")
        scores = d.get("scores", {})
        valid = [v["score"] for v in scores.values() if v.get("score") is not None]
        errors = sum(1 for v in scores.values() if v.get("error"))
        missing = len(benchmarks) - len(scores)
        avg = sum(valid)/len(valid) if valid else 0
        print(f"  {label:30s}  benchmarks={len(scores):2d}/{len(benchmarks)}  avg={avg:.4f}  errors={errors}  missing={missing}")

if __name__ == "__main__":
    main()
