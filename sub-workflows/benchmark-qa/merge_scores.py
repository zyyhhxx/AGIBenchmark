#!/usr/bin/env python3
"""Merge all model result JSON files into score_matrix.csv."""
import json, os, csv, sys

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

ALL_BENCHMARKS = [
    'metacog_canary','metacog_fok','metacog_jol','metacog_calibration','metacog_error_detection',
    'metacog_learning_monitoring','metacog_control','metacog_epistemic_revision','metacog_epistemic_humility',
    'learning_curves','learning_transfer','learning_interference','learning_curriculum',
    'attention_selective','attention_vigilance','attention_divided','attention_instruction_update',
    'exec_func_wcst','exec_func_tol','exec_func_task_switch','exec_func_nback','exec_func_crt',
    'social_cog_false_belief','social_cog_pragmatic','social_cog_sarcasm','social_cog_emotional_prosody',
]

def main():
    # Load all result files
    models = {}
    for f in sorted(os.listdir(RESULTS_DIR)):
        if not f.endswith('.json'): continue
        path = os.path.join(RESULTS_DIR, f)
        try:
            data = json.load(open(path))
            label = data.get("model_label", f.replace('.json',''))
            models[label] = data.get("scores", {})
        except: continue

    if not models:
        print("No result files found!"); return

    # Sort models by name
    model_names = sorted(models.keys())
    
    # Write CSV
    out_path = os.path.join(RESULTS_DIR, "score_matrix.csv")
    with open(out_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["benchmark"] + model_names)
        
        for bench in ALL_BENCHMARKS:
            row = [bench]
            for m in model_names:
                scores = models[m]
                if bench in scores:
                    entry = scores[bench]
                    if entry.get("error"):
                        row.append(f"ERROR:{entry['error'][:40]}")
                    elif entry.get("score") is not None:
                        row.append(f"{entry['score']:.4f}")
                    else:
                        row.append("ERROR:null")
                else:
                    row.append("")  # not yet run
            w.writerow(row)

    print(f"Score matrix written to {out_path}")
    print(f"  Benchmarks: {len(ALL_BENCHMARKS)}")
    print(f"  Models: {len(model_names)}")
    for m in model_names:
        scores = models[m]
        ok = sum(1 for b in ALL_BENCHMARKS if b in scores and scores[b].get("score") is not None and not scores[b].get("error"))
        err = sum(1 for b in ALL_BENCHMARKS if b in scores and scores[b].get("error"))
        miss = sum(1 for b in ALL_BENCHMARKS if b not in scores)
        print(f"  {m:30s}: {ok:2d} ok, {err:2d} err, {miss:2d} missing")

    # Print the matrix
    print(f"\n{'='*60}")
    print("SCORE MATRIX")
    print(f"{'='*60}")
    header = f"{'benchmark':45s}" + "".join(f"{m[:12]:>13s}" for m in model_names)
    print(header)
    print("-" * len(header))
    for bench in ALL_BENCHMARKS:
        row = f"{bench:45s}"
        for m in model_names:
            scores = models[m]
            if bench in scores:
                entry = scores[bench]
                if entry.get("error"):
                    row += f"{'ERROR':>13s}"
                elif entry.get("score") is not None:
                    row += f"{entry['score']:13.4f}"
                else:
                    row += f"{'null':>13s}"
            else:
                row += f"{'':>13s}"
        print(row)

if __name__ == "__main__":
    main()
