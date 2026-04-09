#!/usr/bin/env python3
"""
Generate FRONTIER_MODEL_RESULTS.md from JSON results files.

Usage:
  .venv/bin/python3 scripts/generate_results_table.py results/gemini_2.5_flash.json results/gpt4o.json
  
Each JSON file should be a list of {"benchmark": str, "model": str, "score": float} objects.
"""
import json, sys, os

def load_results(files):
    """Load results from multiple JSON files."""
    all_results = {}
    models = set()
    for f in files:
        with open(f) as fh:
            data = json.load(fh)
        for item in data:
            benchmark = item['benchmark']
            model = item['model']
            score = item.get('score', item.get('error', 'ERR'))
            models.add(model)
            if benchmark not in all_results:
                all_results[benchmark] = {}
            all_results[benchmark][model] = score
    return all_results, sorted(models)

TRACK_ORDER = {
    "metacognition": [
        "metacog_fok", "metacog_jol", "metacog_calibration",
        "metacog_error_detection", "metacog_learning_monitoring",
        "metacog_canary", "metacog_control", "metacog_epistemic_revision",
        "metacog_epistemic_humility"
    ],
    "learning": [
        "learning_curves", "learning_transfer", "learning_interference",
        "learning_curriculum"
    ],
    "attention": [
        "attention_selective", "attention_vigilance",
        "attention_divided", "attention_instruction_update"
    ],
    "executive_functions": [
        "exec_func_wcst", "exec_func_tol", "exec_func_task_switch",
        "exec_func_nback", "exec_func_crt"
    ],
    "social_cognition": [
        "social_cog_false_belief", "social_cog_pragmatic",
        "social_cog_sarcasm", "social_cog_emotional_prosody"
    ],
}

HUMAN_BASELINES = {
    "metacog_fok": "0.60–0.80",
    "metacog_jol": "0.50–0.70",
    "metacog_calibration": "0.80–0.90",
    "metacog_error_detection": "0.75–0.85",
    "metacog_learning_monitoring": "0.60–0.75",
    "metacog_canary": "1.00",
    "metacog_control": "0.65–0.80",
    "metacog_epistemic_revision": "0.70–0.85",
    "metacog_epistemic_humility": "0.80–0.95",
    "learning_curves": "Power law",
    "learning_transfer": "0.80/0.50",
    "learning_interference": "0.15–0.25",
    "learning_curriculum": "Ordering fx",
    "attention_selective": "0.85–0.95",
    "attention_vigilance": "d' 2.0–3.0",
    "attention_divided": "10–20% cost",
    "attention_instruction_update": "5–15% cost",
    "exec_func_wcst": "0.85 acc",
    "exec_func_tol": "55–90%",
    "exec_func_task_switch": "0.90–0.95",
    "exec_func_nback": "d' 1.5–3.5",
    "exec_func_crt": "0.30–0.48",
    "social_cog_false_belief": "0.80–0.95",
    "social_cog_pragmatic": "0.90–0.95",
    "social_cog_sarcasm": "0.90–0.95",
    "social_cog_emotional_prosody": "0.70–0.85",
}

def generate_markdown(all_results, models):
    lines = ["# Frontier Model Results Summary\n"]
    lines.append(f"> Generated from {len(models)} model(s) across {sum(len(v) for v in TRACK_ORDER.values())} benchmarks\n")
    
    for track_name, benchmarks in TRACK_ORDER.items():
        display = track_name.replace("_", " ").title()
        lines.append(f"\n## {display}\n")
        
        header = "| Benchmark |"
        separator = "|-----------|"
        for m in models:
            short = m.split("/")[-1] if "/" in m else m
            header += f" {short} |"
            separator += "------|"
        header += " Human |"
        separator += "-------|"
        lines.append(header)
        lines.append(separator)
        
        for bench in benchmarks:
            display_bench = bench.replace("_", " ").replace("metacog ", "").replace("exec func ", "").replace("social cog ", "").replace("attention ", "").replace("learning ", "")
            row = f"| {display_bench} |"
            for m in models:
                score = all_results.get(bench, {}).get(m, "—")
                if isinstance(score, (int, float)):
                    row += f" {score:.3f} |"
                else:
                    row += f" {score} |"
            row += f" {HUMAN_BASELINES.get(bench, '—')} |"
            lines.append(row)
    
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_results_table.py <results1.json> [results2.json ...]")
        print("  Each JSON: [{\"benchmark\": str, \"model\": str, \"score\": float}, ...]")
        sys.exit(1)
    
    results, models = load_results(sys.argv[1:])
    md = generate_markdown(results, models)
    
    outpath = os.path.join(os.path.dirname(sys.argv[1]), "FRONTIER_MODEL_RESULTS.md")
    with open(outpath, "w") as f:
        f.write(md)
    print(f"Written to {outpath}")
    print(md[:500])
