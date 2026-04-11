#!/usr/bin/env python3
"""Generate score_matrix.csv and discriminatory_analysis.md from result JSON files."""
import json, os, csv, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO, "results")

# The 10 canonical models from MODEL_CATALOG
CANONICAL_MODELS = {
    "anthropic.claude-opus-4-6-v1",
    "deepseek.r1-v1:0",
    "openai.gpt-oss-120b-1:0",
    "meta.llama3-3-70b-instruct-v1:0",
    "qwen.qwen3-next-80b-a3b",
    "amazon.nova-pro-v1:0",
    "meta.llama4-maverick-17b-instruct-v1:0",
    "anthropic.claude-sonnet-4-6",
    "zai.glm-4.7",
    "mistral.ministral-3-3b-instruct",
}

def load_results():
    """Load all model result JSON files (only canonical 10 models)."""
    results = {}
    for f in sorted(os.listdir(RESULTS_DIR)):
        if not f.endswith('.json'):
            continue
        path = os.path.join(RESULTS_DIR, f)
        try:
            data = json.load(open(path))
            model_id = data.get('model', '')
            # Normalize : to _ for comparison
            if model_id not in CANONICAL_MODELS:
                # Try with file-safe name
                continue
            if 'scores' in data and 'model_label' in data and len(data['scores']) > 1:
                results[data['model_label']] = data
        except:
            pass
    return results

def generate_score_matrix(results):
    """Generate score_matrix.csv."""
    # Get all benchmark names (union)
    all_benchmarks = set()
    for data in results.values():
        all_benchmarks.update(data['scores'].keys())
    all_benchmarks = sorted(all_benchmarks)
    
    model_labels = sorted(results.keys())
    
    out_path = os.path.join(RESULTS_DIR, "score_matrix.csv")
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["benchmark"] + model_labels)
        for bm in all_benchmarks:
            row = [bm]
            for label in model_labels:
                score = results[label]['scores'].get(bm, {}).get('score')
                row.append(f"{score:.4f}" if score is not None else "ERROR")
            writer.writerow(row)
    
    print(f"Wrote {out_path} ({len(all_benchmarks)} benchmarks × {len(model_labels)} models)")
    return all_benchmarks, model_labels

def generate_discriminatory_analysis(results, all_benchmarks, model_labels):
    """Generate discriminatory_analysis.md."""
    out_path = os.path.join(RESULTS_DIR, "discriminatory_analysis.md")
    
    lines = ["# Discriminatory Power Analysis\n",
             f"**Models:** {len(model_labels)} | **Benchmarks:** {len(all_benchmarks)}\n",
             f"**Models tested:** {', '.join(model_labels)}\n\n"]
    
    lines.append("## Summary Table\n\n")
    lines.append("| Benchmark | Mean | Std | Min | Max | Range | N Valid | Flag |\n")
    lines.append("|-----------|------|-----|-----|-----|-------|---------|------|\n")
    
    flagged = {'ceiling': [], 'floor': [], 'low_var': []}
    
    for bm in all_benchmarks:
        scores = []
        for label in model_labels:
            s = results[label]['scores'].get(bm, {}).get('score')
            if s is not None:
                scores.append(s)
        
        if not scores:
            lines.append(f"| {bm} | — | — | — | — | — | 0 | NO DATA |\n")
            continue
        
        mean = np.mean(scores)
        std = np.std(scores)
        mn = min(scores)
        mx = max(scores)
        rng = mx - mn
        n = len(scores)
        
        flag = ""
        if mn > 0.9:
            flag = "⚠️ CEILING"
            flagged['ceiling'].append((bm, mean, std, scores))
        elif mx < 0.1:
            flag = "⚠️ FLOOR"
            flagged['floor'].append((bm, mean, std, scores))
        elif std < 0.05:
            flag = "⚠️ LOW VAR"
            flagged['low_var'].append((bm, mean, std, scores))
        
        lines.append(f"| {bm} | {mean:.3f} | {std:.3f} | {mn:.3f} | {mx:.3f} | {rng:.3f} | {n} | {flag} |\n")
    
    # Flagged sections
    lines.append("\n## Flagged Benchmarks\n\n")
    
    if flagged['ceiling']:
        lines.append("### Ceiling Effect (all scores > 0.9)\n")
        for bm, mean, std, scores in flagged['ceiling']:
            lines.append(f"- **{bm}**: mean={mean:.3f}, std={std:.3f}, scores={[round(s,3) for s in scores]}\n")
        lines.append("\n")
    
    if flagged['floor']:
        lines.append("### Floor Effect (all scores < 0.1)\n")
        for bm, mean, std, scores in flagged['floor']:
            lines.append(f"- **{bm}**: mean={mean:.3f}, std={std:.3f}, scores={[round(s,3) for s in scores]}\n")
        lines.append("\n")
    
    if flagged['low_var']:
        lines.append("### Low Variance (std < 0.05)\n")
        for bm, mean, std, scores in flagged['low_var']:
            lines.append(f"- **{bm}**: mean={mean:.3f}, std={std:.3f}, scores={[round(s,3) for s in scores]}\n")
        lines.append("\n")
    
    total_flagged = sum(len(v) for v in flagged.values())
    lines.append(f"\n## Overall: {total_flagged}/{len(all_benchmarks)} benchmarks flagged\n")
    
    with open(out_path, 'w') as f:
        f.writelines(lines)
    
    print(f"Wrote {out_path}")
    print(f"Flagged: {len(flagged['ceiling'])} ceiling, {len(flagged['floor'])} floor, {len(flagged['low_var'])} low_var")

if __name__ == "__main__":
    results = load_results()
    if not results:
        print("No result files found with >1 benchmark scored")
        sys.exit(1)
    print(f"Loaded {len(results)} model results")
    all_bm, model_labels = generate_score_matrix(results)
    generate_discriminatory_analysis(results, all_bm, model_labels)
