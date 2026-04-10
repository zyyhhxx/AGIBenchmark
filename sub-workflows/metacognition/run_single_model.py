#!/usr/bin/env python3
"""
Run benchmarks for a single model with INCREMENTAL saves after each benchmark.
Resumes by skipping already-completed benchmarks.

Usage:
  python3 run_single_model.py <model_id>
"""
import json, os, sys, time, importlib, traceback
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
sys.path.insert(0, REPO)

# Import from the main runner
sys.path.insert(0, os.path.join(REPO, "scripts"))
from run_benchmark_bedrock import (
    MODEL_CATALOG, BENCHMARKS, create_bedrock_llm, run_one, 
    setup_kbench_mocks, get_benchmarks_for_track, DELAY_BETWEEN_BENCHMARKS
)

RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")

def safe_name(model_id):
    return model_id.replace(':', '_').replace('/', '_')

def run_model_incremental(model_id):
    entry = MODEL_CATALOG.get(model_id)
    if not entry:
        print(f"Unknown model: {model_id}")
        sys.exit(1)
    
    label, invoke_id = entry
    out_path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Load existing results
    existing = {}
    if os.path.exists(out_path):
        try:
            with open(out_path) as f:
                d = json.load(f)
            existing = d.get("scores", {})
            print(f"Resuming {label}: {len(existing)} benchmarks already done")
        except:
            pass
    
    benchmarks = get_benchmarks_for_track("all")
    llm = create_bedrock_llm(invoke_id)
    scores = dict(existing)
    
    print(f"Model: {label} ({model_id})")
    print(f"Total benchmarks: {len(benchmarks)}, already done: {len(existing)}")
    
    for i, (mod_path, fn_name) in enumerate(benchmarks):
        if fn_name in scores and scores[fn_name].get("score") is not None:
            print(f"  SKIP {fn_name} (already done: {scores[fn_name]['score']})")
            continue
        
        r = run_one(mod_path, fn_name, llm, model_id, label)
        scores[fn_name] = {
            "score": r["score"],
            "error": r["error"],
            "duration_s": r["duration_s"],
        }
        
        # Save incrementally
        output = {
            "model": model_id,
            "model_label": label,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scores": scores,
        }
        with open(out_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        done = sum(1 for s in scores.values() if s.get("score") is not None or s.get("error"))
        print(f"  [{done}/{len(benchmarks)}] Saved. Tokens: in={llm._total_input_tokens}, out={llm._total_output_tokens}")
        
        if i < len(benchmarks) - 1:
            time.sleep(DELAY_BETWEEN_BENCHMARKS)
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"COMPLETE: {label}")
    print(f"{'='*60}")
    for bname, data in scores.items():
        if data.get("score") is not None:
            print(f"  {bname:45s} → {data['score']:.4f}")
        else:
            print(f"  {bname:45s} → ERROR: {(data.get('error') or '')[:50]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_single_model.py <model_id>")
        print("Models:", list(MODEL_CATALOG.keys()))
        sys.exit(1)
    run_model_incremental(sys.argv[1])
