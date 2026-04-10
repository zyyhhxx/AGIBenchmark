#!/usr/bin/env python3
"""
Merge all per-model JSON result files into results/score_matrix.csv.
Rows = benchmarks, Columns = models, Cells = scores or ERROR.
"""
import json, os, csv, sys

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

# All 26 benchmarks in order
BENCHMARKS = [
    "metacog_canary", "metacog_fok", "metacog_jol", "metacog_calibration",
    "metacog_error_detection", "metacog_learning_monitoring", "metacog_control",
    "metacog_epistemic_revision", "metacog_epistemic_humility",
    "learning_curves", "learning_transfer", "learning_interference", "learning_curriculum",
    "attention_selective", "attention_vigilance", "attention_divided", "attention_instruction_update",
    "exec_func_wcst", "exec_func_tol", "exec_func_task_switch", "exec_func_nback", "exec_func_crt",
    "social_cog_false_belief", "social_cog_pragmatic", "social_cog_sarcasm", "social_cog_emotional_prosody",
]

def main():
    # Find all JSON result files
    json_files = sorted(f for f in os.listdir(RESULTS_DIR) if f.endswith('.json'))
    if not json_files:
        print("No JSON result files found in", RESULTS_DIR)
        sys.exit(1)

    # Load all model data
    models = {}  # label -> scores dict
    model_order = []
    for jf in json_files:
        with open(os.path.join(RESULTS_DIR, jf)) as f:
            data = json.load(f)
        label = data.get("model_label", data.get("model", jf))
        models[label] = data.get("scores", {})
        model_order.append(label)

    # Write CSV
    out_path = os.path.join(RESULTS_DIR, "score_matrix.csv")
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["benchmark"] + model_order)
        for bm in BENCHMARKS:
            row = [bm]
            for label in model_order:
                scores = models[label]
                if bm in scores:
                    entry = scores[bm]
                    if entry.get("score") is not None:
                        row.append(f"{entry['score']:.4f}")
                    else:
                        row.append(f"ERROR:{(entry.get('error','')[:30])}")
                else:
                    row.append("")  # not yet run
            writer.writerow(row)

    print(f"Wrote {out_path}")
    print(f"  {len(model_order)} models × {len(BENCHMARKS)} benchmarks")
    
    # Summary stats
    for label in model_order:
        scores = models[label]
        total = len([b for b in BENCHMARKS if b in scores])
        valid = len([b for b in BENCHMARKS if b in scores and scores[b].get("score") is not None])
        print(f"  {label:30s}: {valid}/{total} scored, {total}/{len(BENCHMARKS)} attempted")

if __name__ == "__main__":
    main()
