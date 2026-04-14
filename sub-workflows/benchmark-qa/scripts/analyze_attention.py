#!/usr/bin/env python3
"""Analyze attention track Q&A transcripts — all 4 benchmarks."""

import json, os, sys, statistics
from pathlib import Path
from collections import defaultdict

BASE = Path("/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/benchmark-qa/results/qa_transcripts")
RESULTS_DIR = Path("/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/benchmark-qa/results")
SCORE_MATRIX = Path("/home/ubuntu/.openclaw/workspace-agi-bench/repo/results/score_matrix_all_tracks.csv")

BENCHMARKS = ["attention_divided", "attention_selective", "attention_vigilance", "attention_instruction_update"]

def load_aggregate(bench):
    with open(BASE / bench / "aggregate_stats.json") as f:
        return json.load(f)

def load_summaries(bench):
    d = BASE / bench
    summaries = {}
    for p in sorted(d.glob("*.summary.json")):
        with open(p) as f:
            summaries[p.stem.replace(".summary", "")] = json.load(f)
    return summaries

def load_transcripts(bench):
    d = BASE / bench
    transcripts = {}
    for p in sorted(d.glob("*.jsonl")):
        model = p.stem
        lines = []
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        lines.append(json.loads(line))
                    except json.JSONDecodeError:
                        lines.append({"_raw": line, "_parse_error": True})
        transcripts[model] = lines
    return transcripts

def get_scores(agg):
    """Extract per-model scores from aggregate_stats (handles different formats)."""
    if "per_model" in agg:
        return {k: v for k, v in agg["per_model"].items()}
    elif "scores" in agg:
        scores = {}
        for k, v in agg["scores"].items():
            if isinstance(v, dict):
                scores[v.get("label", k)] = v["score"]
            else:
                scores[agg.get("labels", {}).get(k, k)] = v
        return scores
    return {}

def load_phase1_scores():
    """Load Phase 1 scores from score_matrix_all_tracks.csv."""
    if not SCORE_MATRIX.exists():
        return {}
    import csv
    with open(SCORE_MATRIX) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    result = {}
    for row in rows:
        if row["track"] == "attention":
            bench = row["benchmark"]
            scores = {}
            for k, v in row.items():
                if k not in ("track", "benchmark") and v:
                    try:
                        scores[k] = float(v)
                    except ValueError:
                        pass
            result[bench] = scores
    return result

def select_review_models(scores):
    """Select 5 models for transcript review: highest, lowest, mid, surprising, random."""
    if not scores:
        return []
    sorted_models = sorted(scores.items(), key=lambda x: x[1])
    highest = sorted_models[-1][0]
    lowest = sorted_models[0][0]
    mid_idx = len(sorted_models) // 2
    mid = sorted_models[mid_idx][0]
    # "Most surprising" = model whose rank changed most from expected (use middle-low as proxy)
    surprising_idx = max(1, len(sorted_models) // 4)
    surprising = sorted_models[surprising_idx][0]
    # Random = pick one not already selected
    selected = {highest, lowest, mid, surprising}
    for name, _ in sorted_models:
        if name not in selected:
            selected.add(name)
            break
    return list(selected)[:5]

def check_think_tags(transcripts):
    """Check for <think> tag leakage in responses."""
    issues = []
    for model, entries in transcripts.items():
        for i, entry in enumerate(entries):
            resp = json.dumps(entry) if isinstance(entry, dict) else str(entry)
            if "<think>" in resp.lower() or "</think>" in resp.lower():
                issues.append(f"{model} entry {i}: think-tag leakage")
    return issues

def check_json_parse_errors(transcripts):
    """Check for JSON extraction failures."""
    issues = []
    for model, entries in transcripts.items():
        for i, entry in enumerate(entries):
            if isinstance(entry, dict) and entry.get("_parse_error"):
                issues.append(f"{model} entry {i}: JSONL parse error")
            # Check for entries where scoring failed
            if isinstance(entry, dict):
                if entry.get("score") is None and entry.get("error"):
                    issues.append(f"{model} entry {i}: scoring error - {entry.get('error','')[:100]}")
    return issues

def analyze_benchmark(bench):
    """Full analysis for one benchmark."""
    print(f"\n{'='*80}")
    print(f"BENCHMARK: {bench}")
    print(f"{'='*80}")
    
    agg = load_aggregate(bench)
    scores = get_scores(agg)
    summaries = load_summaries(bench)
    transcripts = load_transcripts(bench)
    
    # Step 2: Score distribution
    vals = list(scores.values())
    mean = statistics.mean(vals)
    std = statistics.stdev(vals) if len(vals) > 1 else 0
    rng = max(vals) - min(vals)
    
    print(f"\n--- Score Distribution ---")
    print(f"Mean: {mean:.4f}")
    print(f"Std:  {std:.4f} {'⚠️ LOW' if std < 0.08 else '✅'}")
    print(f"Range: {rng:.4f}")
    print(f"N models: {len(vals)}")
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for name, score in sorted_scores:
        print(f"  {name:30s} {score:.4f}")
    
    # Step 2: Flag low std
    if std < 0.08:
        print(f"\n⚠️ FLAG: std={std:.4f} < 0.08 threshold")
    
    # Step 3: Ceiling check
    ceiling_models = [n for n, s in scores.items() if s > 0.95]
    if ceiling_models:
        print(f"\nCeiling effect (>0.95): {ceiling_models}")
    
    # Step 4: Transcript review
    print(f"\n--- Transcript Review ---")
    review_models = select_review_models(scores)
    print(f"Reviewing models: {review_models}")
    
    think_issues = check_think_tags(transcripts)
    if think_issues:
        print(f"\nThink-tag leakage ({len(think_issues)} instances):")
        for issue in think_issues[:10]:
            print(f"  {issue}")
    else:
        print("Think-tag leakage: None detected")
    
    parse_issues = check_json_parse_errors(transcripts)
    if parse_issues:
        print(f"\nJSON parse errors ({len(parse_issues)} instances):")
        for issue in parse_issues[:10]:
            print(f"  {issue}")
    else:
        print("JSON parse errors: None detected")
    
    # Examine specific transcript entries for review models
    for model_key in review_models:
        # Find matching transcript key
        matching_keys = [k for k in transcripts if model_key.lower().replace(" ", "_").replace(".", "") in k.lower().replace(" ", "_").replace(".", "") or 
                         k.lower().replace("_", "").replace(".", "").replace("-","") in model_key.lower().replace("_","").replace(" ","").replace(".", "").replace("-","")]
        if not matching_keys:
            # Try partial match
            matching_keys = [k for k in transcripts if any(part in k.lower() for part in model_key.lower().split()[:2])]
        
        if matching_keys:
            tk = matching_keys[0]
            entries = transcripts[tk]
            print(f"\n  {model_key} ({len(entries)} entries):")
            # Show first 2 entries briefly
            for i, entry in enumerate(entries[:2]):
                if isinstance(entry, dict):
                    # Show key fields
                    trial = entry.get("trial_id", entry.get("item_id", entry.get("id", f"entry_{i}")))
                    score = entry.get("score", entry.get("correct", "?"))
                    expected = entry.get("expected", entry.get("correct_answer", "?"))
                    actual = entry.get("model_answer", entry.get("response", entry.get("answer", "?")))
                    if isinstance(actual, str) and len(actual) > 200:
                        actual = actual[:200] + "..."
                    print(f"    Trial {trial}: score={score}, expected={expected}")
                    if actual != "?":
                        print(f"      answer: {str(actual)[:150]}")
    
    # Summary output
    return {
        "benchmark": bench,
        "mean": mean,
        "std": std,
        "range": rng,
        "n_models": len(vals),
        "ceiling_models": ceiling_models,
        "think_tag_issues": len(think_issues),
        "parse_errors": len(parse_issues),
        "scores": dict(sorted_scores),
    }

def main():
    phase1 = load_phase1_scores()
    results = {}
    
    for bench in BENCHMARKS:
        r = analyze_benchmark(bench)
        results[bench] = r
        
        # Phase 1 comparison
        if bench in phase1:
            p1_vals = list(phase1[bench].values())
            p1_mean = statistics.mean(p1_vals)
            p1_std = statistics.stdev(p1_vals) if len(p1_vals) > 1 else 0
            print(f"\n--- Phase 1 Comparison ---")
            print(f"Phase 1: mean={p1_mean:.4f}, std={p1_std:.4f}")
            print(f"Phase 2: mean={r['mean']:.4f}, std={r['std']:.4f}")
            print(f"Delta std: {r['std'] - p1_std:+.4f}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY — All 4 Attention Benchmarks")
    print(f"{'='*80}")
    for bench, r in results.items():
        flag = "⚠️" if r["std"] < 0.08 else "✅"
        print(f"{bench:40s} mean={r['mean']:.4f} std={r['std']:.4f} {flag} range={r['range']:.4f} ceiling={len(r['ceiling_models'])}")

if __name__ == "__main__":
    main()
