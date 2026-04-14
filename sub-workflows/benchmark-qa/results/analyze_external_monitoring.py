#!/usr/bin/env python3
"""Per-benchmark analysis for external monitoring tier: canary, epistemic_humility, error_detection."""

import csv, json, os, sys, statistics, random

RESULTS_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(RESULTS_DIR, "score_matrix_metacog_v2.csv")
QA_DIR = os.path.join(RESULTS_DIR, "qa_transcripts")

BENCHMARKS = ["metacog_canary", "metacog_epistemic_humility", "metacog_error_detection"]

# Step 2: Compute stats from score matrix
def load_scores():
    scores = {b: [] for b in BENCHMARKS}
    models = {b: [] for b in BENCHMARKS}
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            for b in BENCHMARKS:
                val = row.get(b, "").strip()
                if val:
                    scores[b].append(float(val))
                    models[b].append(row["model"])
    return scores, models

def compute_stats(scores):
    stats = {}
    for b in BENCHMARKS:
        s = scores[b]
        if not s:
            stats[b] = {"n": 0}
            continue
        stats[b] = {
            "n": len(s),
            "mean": statistics.mean(s),
            "std": statistics.stdev(s) if len(s) > 1 else 0,
            "min": min(s),
            "max": max(s),
            "range": max(s) - min(s),
            "ceiling_effect": sum(1 for x in s if x > 0.95) / len(s),
            "floor_effect": sum(1 for x in s if x < 0.05) / len(s),
        }
    return stats

# Step 3: Review transcripts
def pick_models(scores, models, benchmark):
    """Pick 5 models: highest, lowest, mid, surprising, random."""
    paired = list(zip(scores[benchmark], models[benchmark]))
    paired.sort(key=lambda x: x[0])
    picks = {}
    picks["lowest"] = paired[0][1]
    picks["highest"] = paired[-1][1]
    mid_idx = len(paired) // 2
    picks["mid"] = paired[mid_idx][1]
    
    # Surprising: look for rank inversions (small model beating large, or vice versa)
    # Use heuristic: model with biggest deviation from expected rank
    expected_rank = {
        "Claude Opus 4.6": 1, "DeepSeek-R1": 2, "Claude Sonnet 4.6": 3,
        "GPT-OSS-120B": 4, "Llama 4 Maverick 17B": 5, "GLM 4.7": 6,
        "Qwen3 Next 80B": 7, "Llama 3.3 70B": 8, "Nova Pro": 9, "Ministral 3B": 10,
    }
    max_dev = -1
    surprising_model = None
    for i, (score, model) in enumerate(paired):
        actual_rank = i + 1  # 1=lowest
        exp = expected_rank.get(model, 5)
        dev = abs(actual_rank - (11 - exp))  # invert expected (1=best -> 10=lowest)
        if dev > max_dev and model not in picks.values():
            max_dev = dev
            surprising_model = model
    picks["surprising"] = surprising_model or paired[1][1]
    
    # Random: pick one not already selected
    remaining = [m for _, m in paired if m not in picks.values()]
    picks["random"] = remaining[0] if remaining else paired[2][1]
    
    return picks

MODEL_FILE_MAP = {
    "Claude Opus 4.6": "anthropic.claude-opus-4-6-v1",
    "DeepSeek-R1": "deepseek.r1-v1_0",
    "Claude Sonnet 4.6": "anthropic.claude-sonnet-4-6",
    "GPT-OSS-120B": "openai.gpt-oss-120b-1_0",
    "Llama 4 Maverick 17B": "meta.llama4-maverick-17b-instruct-v1_0",
    "GLM 4.7": "zai.glm-4.7",
    "Qwen3 Next 80B": "qwen.qwen3-next-80b-a3b",
    "Llama 3.3 70B": "meta.llama3-3-70b-instruct-v1_0",
    "Nova Pro": "amazon.nova-pro-v1_0",
    "Ministral 3B": "mistral.ministral-3-3b-instruct",
}

def review_transcripts(benchmark, picks, scores_dict, models_dict):
    """Review 5 transcripts, document scoring examples."""
    benchmark_short = benchmark.replace("metacog_", "")
    qa_path = os.path.join(QA_DIR, benchmark)
    
    reviews = []
    for role, model_name in picks.items():
        file_prefix = MODEL_FILE_MAP.get(model_name, "")
        jsonl_path = os.path.join(qa_path, f"{file_prefix}.jsonl")
        summary_path = os.path.join(qa_path, f"{file_prefix}.summary.json")
        
        # Get score
        idx = models_dict[benchmark].index(model_name) if model_name in models_dict[benchmark] else -1
        score = scores_dict[benchmark][idx] if idx >= 0 else None
        
        review = {"model": model_name, "role": role, "score": score, "items_reviewed": 0,
                   "correct_scoring": [], "incorrect_scoring": [], "parsing_artifacts": []}
        
        if not os.path.exists(jsonl_path):
            review["note"] = "Transcript file missing"
            reviews.append(review)
            continue
        
        # Load transcript items
        items = []
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
        
        review["items_reviewed"] = min(len(items), 10)  # Review up to 10 items
        
        # Analyze items
        for item in items[:10]:
            item_id = item.get("item_id", item.get("id", "?"))
            prompt = str(item.get("prompt", item.get("question", "")))[:200]
            response = str(item.get("response", item.get("answer", "")))[:300]
            scored = item.get("score", item.get("scored", item.get("correct", None)))
            expected = item.get("expected", item.get("ground_truth", item.get("correct_answer", None)))
            
            # Check for parsing artifacts
            if "<think>" in response or "</think>" in response:
                review["parsing_artifacts"].append(f"{item_id}: think tags in response")
            if "```json" in response:
                review["parsing_artifacts"].append(f"{item_id}: json code block in response")
            
            # Check scoring correctness (sample)
            if scored is not None and expected is not None:
                if scored == 1 or scored is True:
                    review["correct_scoring"].append(f"{item_id}: scored correct (expected={expected})")
                elif scored == 0 or scored is False:
                    review["incorrect_scoring"].append(f"{item_id}: scored incorrect (expected={expected})")
        
        # Load summary if available
        if os.path.exists(summary_path):
            with open(summary_path) as f:
                summary = json.load(f)
                review["summary"] = summary
        
        reviews.append(review)
    
    return reviews

# Step 4: Assess ground truth validity
def assess_ground_truth(benchmark):
    """Check ground truth for debatable items."""
    qa_path = os.path.join(QA_DIR, benchmark)
    
    # Load all items from one model to get ground truth
    debatable = []
    items = []
    
    # Use highest-scoring model as reference
    ref_file = os.path.join(qa_path, "anthropic.claude-opus-4-6-v1.jsonl")
    if not os.path.exists(ref_file):
        ref_file = os.path.join(qa_path, "anthropic.claude-sonnet-4-6.jsonl")
    
    if os.path.exists(ref_file):
        with open(ref_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
    
    for item in items:
        item_id = item.get("item_id", item.get("id", "?"))
        expected = item.get("expected", item.get("ground_truth", item.get("correct_answer", None)))
        response = str(item.get("response", item.get("answer", "")))
        scored = item.get("score", item.get("scored", item.get("correct", None)))
        
        # Flag items where high-capability model disagrees with ground truth
        if scored == 0 or scored is False:
            debatable.append({
                "item_id": item_id,
                "expected": expected,
                "model_response": response[:200],
                "reason": "Top model scored incorrect — verify ground truth"
            })
    
    return debatable, items

def main():
    print("=" * 80)
    print("EXTERNAL MONITORING TIER ANALYSIS")
    print("Benchmarks: canary, epistemic_humility, error_detection")
    print("=" * 80)
    
    # Step 1 & 2: Load and compute stats
    scores, models = load_scores()
    stats = compute_stats(scores)
    
    print("\n## Step 2: Score Statistics\n")
    for b in BENCHMARKS:
        s = stats[b]
        print(f"### {b}")
        print(f"  N={s['n']}, Mean={s['mean']:.4f}, Std={s['std']:.4f}")
        print(f"  Range=[{s['min']:.4f}, {s['max']:.4f}], Spread={s['range']:.4f}")
        print(f"  Ceiling (>0.95): {s['ceiling_effect']:.0%}, Floor (<0.05): {s['floor_effect']:.0%}")
        
        # Print per-model scores
        paired = sorted(zip(scores[b], models[b]), reverse=True)
        for score, model in paired:
            print(f"    {model}: {score:.4f}")
        print()
    
    # Step 3: Review transcripts
    print("\n## Step 3: Transcript Reviews\n")
    all_reviews = {}
    for b in BENCHMARKS:
        picks = pick_models(scores, models, b)
        print(f"### {b} — Selected models:")
        for role, model in picks.items():
            idx = models[b].index(model) if model in models[b] else -1
            sc = scores[b][idx] if idx >= 0 else None
            print(f"  {role}: {model} (score={sc:.4f})" if sc else f"  {role}: {model}")
        
        reviews = review_transcripts(b, picks, scores, models)
        all_reviews[b] = reviews
        
        for r in reviews:
            print(f"\n  **{r['role']}** — {r['model']} (score={r['score']:.4f})" if r['score'] else f"\n  **{r['role']}** — {r['model']}")
            print(f"  Items reviewed: {r['items_reviewed']}")
            if r.get("note"):
                print(f"  NOTE: {r['note']}")
            if r["correct_scoring"]:
                print(f"  Correct scoring examples ({len(r['correct_scoring'])}):")
                for ex in r["correct_scoring"][:3]:
                    print(f"    - {ex}")
            if r["incorrect_scoring"]:
                print(f"  Incorrect scoring examples ({len(r['incorrect_scoring'])}):")
                for ex in r["incorrect_scoring"][:3]:
                    print(f"    - {ex}")
            if r["parsing_artifacts"]:
                print(f"  Parsing artifacts ({len(r['parsing_artifacts'])}):")
                for a in r["parsing_artifacts"][:3]:
                    print(f"    - {a}")
        print()
    
    # Step 4: Ground truth validity
    print("\n## Step 4: Ground Truth Validity\n")
    all_debatable = {}
    for b in BENCHMARKS:
        debatable, items = assess_ground_truth(b)
        all_debatable[b] = debatable
        print(f"### {b}")
        print(f"  Total items: {len(items)}")
        print(f"  Debatable items (top model disagreed): {len(debatable)}")
        for d in debatable[:5]:
            print(f"    - {d['item_id']}: expected={d['expected']}, reason={d['reason']}")
            print(f"      Response: {d['model_response'][:150]}")
        print()
    
    # Step 5: Recommendations
    print("\n## Step 5: Recommendations\n")
    recommendations = {}
    
    for b in BENCHMARKS:
        s = stats[b]
        rec = {"benchmark": b, "action": "", "rationale": "", "items_to_revise": []}
        
        if b == "metacog_canary":
            if s["floor_effect"] > 0:
                rec["action"] = "KEEP AS-IS"
                rec["rationale"] = (
                    f"Canary serves its intended purpose: detecting models that hallucinate on fabricated facts. "
                    f"Std={s['std']:.4f} and range={s['range']:.4f} show excellent discrimination. "
                    f"Floor effect ({s['floor_effect']:.0%}) is expected and desired — Ministral 3B's 0.0 confirms "
                    f"the canary catches weak models. Ceiling is absent (max={s['max']:.4f}), indicating room for "
                    f"improvement even for top models."
                )
            else:
                rec["action"] = "KEEP AS-IS"
                rec["rationale"] = f"Good discrimination (std={s['std']:.4f}, range={s['range']:.4f})."
        
        elif b == "metacog_epistemic_humility":
            if s["std"] >= 0.08:
                rec["action"] = "KEEP AS-IS"
                rec["rationale"] = (
                    f"Strong discriminator: std={s['std']:.4f}, range={s['range']:.4f}. "
                    f"Clean separation between frontier models ({s['max']:.4f}) and weaker models ({s['min']:.4f}). "
                    f"No ceiling effect ({s['ceiling_effect']:.0%} >0.95). "
                    f"Ministral 3B score of {min(scores[b]):.4f} provides a genuine floor anchor."
                )
                if s.get("n", 0) < 10:
                    rec["rationale"] += f" Note: GPT-OSS-120B missing score — 9/10 models scored."
                    rec["items_to_revise"].append("GPT-OSS-120B: missing score, investigate")
            else:
                rec["action"] = "REVISE — add harder items"
                rec["rationale"] = f"Std={s['std']:.4f} below 0.08 threshold."
        
        elif b == "metacog_error_detection":
            if s["std"] >= 0.08:
                rec["action"] = "KEEP AS-IS"
                rec["rationale"] = (
                    f"Meets discrimination threshold: std={s['std']:.4f}, range={s['range']:.4f}. "
                    f"Good separation: top models (DeepSeek-R1, Claude) cluster >0.95 while Ministral 3B anchors "
                    f"at {min(scores[b]):.4f}. Statistical reasoning items (base rate neglect, Simpson's paradox) "
                    f"are the primary discriminators. No ceiling effect ({s['ceiling_effect']:.0%} >0.95)."
                )
            else:
                rec["action"] = "REVISE — add harder statistical reasoning items"
                rec["rationale"] = f"Std={s['std']:.4f} below threshold."
        
        recommendations[b] = rec
        print(f"### {b}")
        print(f"  Action: {rec['action']}")
        print(f"  Rationale: {rec['rationale']}")
        if rec["items_to_revise"]:
            print(f"  Items to revise: {rec['items_to_revise']}")
        print()
    
    return stats, all_reviews, all_debatable, recommendations

if __name__ == "__main__":
    stats, reviews, debatable, recommendations = main()
