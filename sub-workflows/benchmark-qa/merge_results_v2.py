#!/usr/bin/env python3
"""
Merge all model result JSON files into score_matrix.csv.
Rows = benchmarks, Columns = models, Cells = scores or ERROR.
"""
import json, os, csv, sys

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

def main():
    # Collect all result files
    result_files = sorted([f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')])
    if not result_files:
        print("No result files found!")
        sys.exit(1)
    
    # Load all results
    models = []  # (model_id, label, scores_dict)
    all_benchmarks = set()
    
    for f in result_files:
        path = os.path.join(RESULTS_DIR, f)
        with open(path) as fh:
            data = json.load(fh)
        model_id = data["model"]
        label = data.get("model_label", model_id)
        scores = data.get("scores", {})
        models.append((model_id, label, scores))
        all_benchmarks.update(scores.keys())
    
    # Sort benchmarks by track grouping
    TRACK_ORDER = {
        "metacog_": 0, "learning_": 1, "attention_": 2,
        "exec_func_": 3, "social_cog_": 4,
    }
    def bench_sort_key(name):
        for prefix, order in TRACK_ORDER.items():
            if name.startswith(prefix):
                return (order, name)
        return (99, name)
    
    benchmarks = sorted(all_benchmarks, key=bench_sort_key)
    
    # Write CSV
    out_path = os.path.join(RESULTS_DIR, "score_matrix.csv")
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        # Header
        header = ["benchmark"] + [label for _, label, _ in models]
        writer.writerow(header)
        
        # Rows
        for bench in benchmarks:
            row = [bench]
            for model_id, label, scores in models:
                if bench in scores:
                    entry = scores[bench]
                    if entry.get("score") is not None:
                        row.append(f"{entry['score']:.4f}")
                    else:
                        row.append(f"ERROR: {(entry.get('error','') or '')[:40]}")
                else:
                    row.append("N/A")
            writer.writerow(row)
    
    print(f"Written {out_path}")
    print(f"  Benchmarks: {len(benchmarks)}")
    print(f"  Models: {len(models)}")
    
    # Print summary table
    print(f"\n{'Benchmark':<45s}", end="")
    for _, label, _ in models:
        print(f" {label:>15s}", end="")
    print()
    print("-" * (45 + 16 * len(models)))
    
    for bench in benchmarks:
        print(f"{bench:<45s}", end="")
        for _, _, scores in models:
            if bench in scores:
                entry = scores[bench]
                if entry.get("score") is not None:
                    print(f" {entry['score']:>15.4f}", end="")
                else:
                    print(f" {'ERROR':>15s}", end="")
            else:
                print(f" {'N/A':>15s}", end="")
        print()
    
    # Model averages
    print("-" * (45 + 16 * len(models)))
    print(f"{'AVERAGE':<45s}", end="")
    for _, _, scores in models:
        valid = [s["score"] for s in scores.values() if s.get("score") is not None]
        avg = sum(valid)/len(valid) if valid else 0
        print(f" {avg:>15.4f}", end="")
    print()

if __name__ == "__main__":
    main()
