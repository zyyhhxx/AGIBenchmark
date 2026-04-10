#!/usr/bin/env python3
"""
Merge all model result JSON files into score_matrix.csv.
Rows = benchmarks, Columns = models, Cells = scores or ERROR.
"""
import json, os, csv, glob, sys

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

def main():
    # Find all result JSON files
    files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json")))
    if not files:
        print(f"No JSON files found in {RESULTS_DIR}")
        sys.exit(1)
    
    # Load all results
    models = {}  # model_label -> {benchmark -> score_or_error}
    all_benchmarks = set()
    
    for f in files:
        try:
            with open(f) as fh:
                d = json.load(fh)
            label = d.get("model_label", os.path.basename(f).replace(".json", ""))
            scores = d.get("scores", {})
            if not scores:
                continue
            models[label] = {}
            for bname, bdata in scores.items():
                all_benchmarks.add(bname)
                if bdata.get("score") is not None:
                    models[label][bname] = f"{bdata['score']:.4f}"
                else:
                    models[label][bname] = f"ERROR: {(bdata.get('error') or 'unknown')[:40]}"
        except Exception as e:
            print(f"Warning: could not read {f}: {e}")
    
    if not models:
        print("No valid model results found")
        sys.exit(1)
    
    # Sort benchmarks and model labels
    benchmarks_sorted = sorted(all_benchmarks)
    model_labels = sorted(models.keys())
    
    # Write CSV
    out_path = os.path.join(RESULTS_DIR, "score_matrix.csv")
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["benchmark"] + model_labels)
        for bname in benchmarks_sorted:
            row = [bname]
            for mlabel in model_labels:
                row.append(models[mlabel].get(bname, "N/A"))
            writer.writerow(row)
    
    print(f"Score matrix saved to {out_path}")
    print(f"  Models: {len(model_labels)}")
    print(f"  Benchmarks: {len(benchmarks_sorted)}")
    print(f"  Model labels: {model_labels}")
    
    # Print summary table
    print(f"\n{'Benchmark':<45s}", end="")
    for ml in model_labels:
        print(f" {ml[:12]:>12s}", end="")
    print()
    print("-" * (45 + 13 * len(model_labels)))
    for bname in benchmarks_sorted:
        print(f"{bname:<45s}", end="")
        for ml in model_labels:
            val = models[ml].get(bname, "N/A")
            if val.startswith("ERROR"):
                print(f" {'ERR':>12s}", end="")
            elif val == "N/A":
                print(f" {'N/A':>12s}", end="")
            else:
                print(f" {val:>12s}", end="")
        print()

if __name__ == "__main__":
    main()
