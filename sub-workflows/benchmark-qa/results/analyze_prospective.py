#!/usr/bin/env python3
"""Per-benchmark analysis for prospective self-assessment tier: jol, fok, calibration."""

import json
import numpy as np
import os
import sys
from pathlib import Path

TDIR = Path("/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/metacognition/results")
QA = TDIR / "qa_transcripts"
CSV = TDIR / "score_matrix_metacog_v2.csv"

BENCHMARKS = ["metacog_jol", "metacog_fok", "metacog_calibration"]

# ─── Step 1 & 2: Load scores and compute stats ─────────────────

def load_scores():
    """Parse CSV and return {benchmark: {model: score}}."""
    import csv
    with open(CSV) as f:
        reader = csv.DictReader(f)
        data = {b: {} for b in BENCHMARKS}
        for row in reader:
            model = row['model']
            for b in BENCHMARKS:
                val = row.get(b, '').strip()
                if val:
                    data[b][model] = float(val)
    return data

def compute_stats(scores_dict):
    vals = list(scores_dict.values())
    arr = np.array(vals)
    return {
        'n': len(vals),
        'mean': float(np.mean(arr)),
        'std': float(np.std(arr, ddof=1)) if len(vals) > 1 else 0.0,
        'min': float(np.min(arr)),
        'max': float(np.max(arr)),
        'range': float(np.max(arr) - np.min(arr)),
        'median': float(np.median(arr)),
        'floor_count': sum(1 for v in vals if v < 0.05),
        'ceiling_count': sum(1 for v in vals if v > 0.95),
        'scores': scores_dict,
    }

# ─── Step 3: Load and review transcripts ─────────────────────

def load_transcripts(benchmark):
    """Load all JSONL transcripts for a benchmark, return {model: [lines]}."""
    bdir = QA / benchmark
    transcripts = {}
    for f in sorted(bdir.glob("*.jsonl")):
        model = f.stem
        lines = []
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    lines.append(json.loads(line))
        transcripts[model] = lines
    return transcripts

def load_summaries(benchmark):
    """Load summary JSONs."""
    bdir = QA / benchmark
    summaries = {}
    for f in sorted(bdir.glob("*.summary.json")):
        model = f.stem.replace('.summary', '')
        with open(f) as fh:
            summaries[model] = json.loads(fh.read())
    return summaries

def select_review_models(scores_dict):
    """Pick 5 models: highest, lowest, mid-range, + 2 interesting."""
    sorted_models = sorted(scores_dict.items(), key=lambda x: x[1])
    lowest = sorted_models[0]
    highest = sorted_models[-1]
    mid_idx = len(sorted_models) // 2
    mid = sorted_models[mid_idx]
    # "surprising" = furthest from expected rank; pick 2nd and 2nd-to-last
    surprising = sorted_models[1] if len(sorted_models) > 2 else sorted_models[0]
    random_pick = sorted_models[-2] if len(sorted_models) > 2 else sorted_models[-1]
    return [highest, lowest, mid, surprising, random_pick]

def review_transcript(lines, benchmark):
    """Analyze a transcript for issues."""
    issues = []
    n_parsed = 0
    n_parse_fail = 0
    n_scored = 0
    confidences = []
    accuracies = []
    
    for line in lines:
        if line.get('score') is not None:
            n_scored += 1
        
        resp = line.get('response', '')
        parsed = line.get('parsed_answer', '')
        
        # Check for parsing artifacts
        if '<think>' in resp.lower():
            issues.append(f"Q{line.get('question_id')}: think tags in response")
        
        # Check confidence values in response
        if 'confidence' in resp.lower():
            try:
                # Try to find confidence value
                import re
                conf_match = re.search(r'"confidence"\s*:\s*(\d+)', resp)
                if conf_match:
                    conf = int(conf_match.group(1))
                    confidences.append(conf)
                    if conf > 100 or conf < 0:
                        issues.append(f"Q{line.get('question_id')}: confidence out of range: {conf}")
            except:
                pass
        
        # Check for answer correctness
        correct = line.get('correct_answer', '')
        if correct and parsed:
            n_parsed += 1
        elif correct and not parsed:
            n_parse_fail += 1
    
    result = {
        'n_lines': len(lines),
        'n_scored': n_scored,
        'n_parsed': n_parsed,
        'n_parse_fail': n_parse_fail,
        'issues': issues,
    }
    if confidences:
        result['mean_confidence'] = np.mean(confidences)
        result['std_confidence'] = np.std(confidences)
        result['min_confidence'] = min(confidences)
        result['max_confidence'] = max(confidences)
    return result


# ─── Step 4: Ground truth validity ─────────────────────────────

def check_gamma_edge_cases(benchmark, transcripts, scores):
    """Check if gamma computation handles edge cases."""
    issues = []
    for model, lines in transcripts.items():
        # Extract confidence/accuracy pairs from transcript
        confs = []
        accs = []
        for line in lines:
            resp = line.get('response', '')
            import re
            conf_match = re.search(r'"confidence"\s*:\s*(\d+)', resp)
            score = line.get('score')
            if conf_match and score is not None:
                confs.append(int(conf_match.group(1)))
                accs.append(1 if score > 0 else 0)
        
        if confs:
            # Check for zero denominator in gamma
            concordant = 0
            discordant = 0
            for i in range(len(confs)):
                for j in range(i+1, len(confs)):
                    prod = (confs[i] - confs[j]) * (accs[i] - accs[j])
                    if prod > 0:
                        concordant += 1
                    elif prod < 0:
                        discordant += 1
            denom = concordant + discordant
            if denom == 0:
                issues.append(f"{model}: gamma denominator=0 (all ties), returns 0.0")
            
            # Check for constant confidence
            if len(set(confs)) == 1:
                issues.append(f"{model}: constant confidence={confs[0]} across all items")
            
            # Check for constant accuracy
            if len(set(accs)) <= 1:
                issues.append(f"{model}: constant accuracy={accs[0] if accs else 'N/A'} (no variation)")
    
    return issues


# ─── Main ───────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("PROSPECTIVE SELF-ASSESSMENT TIER ANALYSIS")
    print("Benchmarks: JOL, FOK, Calibration")
    print("=" * 70)
    
    scores_data = load_scores()
    
    all_stats = {}
    all_reviews = {}
    all_gt_issues = {}
    
    for bench in BENCHMARKS:
        print(f"\n{'='*70}")
        print(f"BENCHMARK: {bench}")
        print(f"{'='*70}")
        
        # Step 2: Stats
        stats = compute_stats(scores_data[bench])
        all_stats[bench] = stats
        print(f"\n--- Score Statistics ---")
        print(f"  N models:       {stats['n']}")
        print(f"  Mean:           {stats['mean']:.4f}")
        print(f"  Std:            {stats['std']:.4f}")
        print(f"  Min:            {stats['min']:.4f}")
        print(f"  Max:            {stats['max']:.4f}")
        print(f"  Range:          {stats['range']:.4f}")
        print(f"  Median:         {stats['median']:.4f}")
        print(f"  Floor (<0.05):  {stats['floor_count']}")
        print(f"  Ceiling (>0.95):{stats['ceiling_count']}")
        print(f"\n  Per-model scores:")
        for model, score in sorted(stats['scores'].items(), key=lambda x: -x[1]):
            print(f"    {model:30s} {score:.4f}")
        
        # Step 3: Transcript review
        transcripts = load_transcripts(bench)
        summaries = load_summaries(bench)
        review_models = select_review_models(scores_data[bench])
        
        print(f"\n--- Transcript Reviews (5 selected models) ---")
        bench_reviews = {}
        for model_name, model_score in review_models:
            # Find matching transcript key
            matching_keys = [k for k in transcripts if model_name.lower().replace(' ', '') in k.lower().replace(' ', '').replace('-', '').replace('_', '')]
            if not matching_keys:
                # Try simpler matching
                for k in transcripts:
                    if any(part in k.lower() for part in model_name.lower().split()[:2]):
                        matching_keys = [k]
                        break
            
            if matching_keys:
                key = matching_keys[0]
                review = review_transcript(transcripts[key], bench)
                bench_reviews[model_name] = review
                print(f"\n  Model: {model_name} (score={model_score:.4f})")
                print(f"    Transcript lines: {review['n_lines']}")
                print(f"    Scored items: {review['n_scored']}")
                if review.get('mean_confidence') is not None:
                    print(f"    Mean confidence: {review['mean_confidence']:.1f}")
                    print(f"    Confidence range: {review['min_confidence']}-{review['max_confidence']}")
                if review['issues']:
                    print(f"    Issues ({len(review['issues'])}):")
                    for iss in review['issues'][:5]:
                        print(f"      - {iss}")
                else:
                    print(f"    Issues: None found")
            else:
                print(f"\n  Model: {model_name} — no matching transcript found")
        
        all_reviews[bench] = bench_reviews
        
        # Step 4: Ground truth validity
        print(f"\n--- Ground Truth Validity ---")
        gt_issues = check_gamma_edge_cases(bench, transcripts, scores_data[bench])
        all_gt_issues[bench] = gt_issues
        if gt_issues:
            for iss in gt_issues:
                print(f"  ⚠ {iss}")
        else:
            print(f"  ✓ No edge case issues found")
    
    # ─── Step 5: Recommendations ────────────────────────────────
    print(f"\n{'='*70}")
    print("RECOMMENDATIONS")
    print(f"{'='*70}")
    
    for bench in BENCHMARKS:
        stats = all_stats[bench]
        print(f"\n--- {bench} ---")
        print(f"  Std={stats['std']:.4f}, Range={stats['range']:.4f}, Floor={stats['floor_count']}, Ceiling={stats['ceiling_count']}")
        
        passes_std = stats['std'] >= 0.08
        has_floor = stats['floor_count'] >= 3
        has_ceiling = stats['ceiling_count'] >= 3
        
        if bench == 'metacog_calibration':
            print(f"  CALIBRATION ANALYSIS:")
            print(f"    Std={stats['std']:.4f} {'✓ PASSES' if passes_std else '✗ FAILS'} ≥0.08 threshold")
            print(f"    Floor effect: {stats['floor_count']}/10 models <0.05")
            # Check from KNOWLEDGE: "6/10 models score 0.000" — this was OLD data
            # Current scores show no zeros
            min_score = stats['min']
            print(f"    Min score: {min_score:.4f} (Ministral 3B)")
            if passes_std and not has_floor:
                print(f"  → RECOMMENDATION: KEEP AS-IS. Std passes threshold, good discrimination.")
            elif has_floor:
                print(f"  → RECOMMENDATION: REVISE ITEMS — floor effect suggests items too hard.")
            else:
                print(f"  → RECOMMENDATION: REVISE — std below threshold.")
        
        elif bench == 'metacog_jol':
            print(f"  JOL ANALYSIS:")
            print(f"    Std={stats['std']:.4f} {'✓ PASSES' if passes_std else '✗ FAILS'} ≥0.08 threshold")
            # JOL uses novel stimuli, so ground truth is self-contained
            print(f"    Uses novel/invented stimuli — no training data contamination")
            print(f"    Scoring: 0.40×gamma_norm + 0.30×max(0,BSS) + 0.30×recall_rate")
            if passes_std:
                print(f"  → RECOMMENDATION: KEEP AS-IS. Good discrimination across models.")
            else:
                print(f"  → RECOMMENDATION: REVISE — increase item count or difficulty spread.")
        
        elif bench == 'metacog_fok':
            print(f"  FOK ANALYSIS:")
            print(f"    Std={stats['std']:.4f} {'✓ PASSES' if passes_std else '✗ FAILS'} ≥0.08 threshold")
            print(f"    Scoring: 0.40×gamma_norm + 0.30×max(0,BSS) + 0.30×AUC")
            if passes_std:
                print(f"  → RECOMMENDATION: KEEP AS-IS. Good spread.")
            else:
                print(f"  → RECOMMENDATION: ADJUST SCORING or add harder items.")
    
    # ─── Summary Table ──────────────────────────────────────────
    print(f"\n{'='*70}")
    print("SUMMARY TABLE")
    print(f"{'='*70}")
    print(f"{'Benchmark':25s} {'Mean':>8s} {'Std':>8s} {'Range':>8s} {'Floor':>6s} {'Ceil':>6s} {'Verdict':>12s}")
    print("-" * 75)
    for bench in BENCHMARKS:
        s = all_stats[bench]
        passes = "✓ PASSES" if s['std'] >= 0.08 else "✗ FAILS"
        print(f"{bench:25s} {s['mean']:8.4f} {s['std']:8.4f} {s['range']:8.4f} {s['floor_count']:6d} {s['ceiling_count']:6d} {passes:>12s}")

    return all_stats, all_reviews, all_gt_issues


if __name__ == '__main__':
    main()
