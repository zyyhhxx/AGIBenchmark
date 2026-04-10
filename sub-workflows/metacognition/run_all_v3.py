#!/usr/bin/env python3
"""
Run all benchmarks against all 10 models with incremental JSON saves.
Resumes from existing results. Designed to run as nohup background process.
"""
import json, os, sys, time, importlib, traceback
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
sys.path.insert(0, REPO)
os.environ['PYTHONUNBUFFERED'] = '1'

RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
os.makedirs(RESULTS_DIR, exist_ok=True)

MODELS = [
    "mistral.ministral-3-3b-instruct",
    "meta.llama4-maverick-17b-instruct-v1:0",
    "meta.llama3-3-70b-instruct-v1:0",
    "amazon.nova-pro-v1:0",
    "openai.gpt-oss-120b-1:0",
    "qwen.qwen3-next-80b-a3b",
    "deepseek.r1-v1:0",
    "zai.glm-4.7",
    "anthropic.claude-sonnet-4-6",
    "anthropic.claude-opus-4-6-v1",
]

from scripts.run_benchmark_bedrock import (
    MODEL_CATALOG, BENCHMARKS, setup_kbench_mocks,
    create_bedrock_llm, get_track_for_benchmark
)

ALL_BENCHMARKS = []
for track in BENCHMARKS:
    ALL_BENCHMARKS.extend(BENCHMARKS[track])

def safe_name(model_id):
    return model_id.replace(':', '_').replace('/', '_')

def load_existing(model_id):
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            pass
    return None

def save_result(model_id, model_label, scores):
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    with open(path, 'w') as f:
        json.dump({
            "model": model_id,
            "model_label": model_label,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scores": scores,
        }, f, indent=2)

def run_one_benchmark(mod_path, fn_name, llm):
    """Run a single benchmark, return dict with score/error/duration."""
    # Clean data module cache
    for key in list(sys.modules.keys()):
        if key == 'data' or key.startswith('data.'):
            del sys.modules[key]

    track = get_track_for_benchmark(fn_name)
    track_dir = os.path.join(REPO, 'benchmarks', track)
    if track_dir not in sys.path:
        sys.path.insert(0, track_dir)

    setup_kbench_mocks()

    if mod_path in sys.modules:
        del sys.modules[mod_path]
    mod = importlib.import_module(mod_path)
    task_fn = getattr(mod, fn_name)

    start = time.time()
    try:
        result = task_fn.run(llm=llm)
        elapsed = time.time() - start
        score = float(result.result) if hasattr(result, 'result') else float(result)
        return {"score": score, "error": None, "duration_s": round(elapsed, 1)}
    except Exception as e:
        elapsed = time.time() - start
        return {"score": None, "error": str(e)[:200], "duration_s": round(elapsed, 1)}

def main():
    print(f"Starting run_all_v3 at {datetime.now(timezone.utc).isoformat()}")
    print(f"Models: {len(MODELS)}, Benchmarks: {len(ALL_BENCHMARKS)}")
    
    for mi, model_id in enumerate(MODELS):
        entry = MODEL_CATALOG.get(model_id)
        label = entry[0] if entry else model_id
        invoke_id = entry[1] if entry else model_id
        
        # Load existing results
        existing = load_existing(model_id)
        scores = existing["scores"] if existing else {}
        
        # Check which benchmarks still need to run
        remaining = [(mp, fn) for mp, fn in ALL_BENCHMARKS if fn not in scores]
        if not remaining:
            print(f"\n[{mi+1}/{len(MODELS)}] SKIP {label}: all {len(scores)} benchmarks done")
            continue
        
        print(f"\n[{mi+1}/{len(MODELS)}] {label}: {len(scores)} done, {len(remaining)} remaining")
        
        llm = create_bedrock_llm(invoke_id)
        
        for bi, (mod_path, fn_name) in enumerate(remaining):
            print(f"  [{bi+1}/{len(remaining)}] {fn_name}...", end=" ", flush=True)
            result = run_one_benchmark(mod_path, fn_name, llm)
            scores[fn_name] = result
            
            if result["score"] is not None:
                print(f"score={result['score']:.4f} ({result['duration_s']}s)")
            else:
                print(f"ERROR: {result['error'][:60]} ({result['duration_s']}s)")
            
            # Save after every benchmark
            save_result(model_id, label, scores)
            
            # Rate limit
            if bi < len(remaining) - 1:
                time.sleep(2)
        
        print(f"  → {label} complete: {len(scores)} benchmarks")
        
        # Pause between models
        if mi < len(MODELS) - 1:
            time.sleep(5)
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    for model_id in MODELS:
        entry = MODEL_CATALOG.get(model_id)
        label = entry[0] if entry else model_id
        existing = load_existing(model_id)
        if existing:
            scores = existing["scores"]
            valid = [s["score"] for s in scores.values() if s["score"] is not None]
            errors = sum(1 for s in scores.values() if s["error"] is not None)
            avg = sum(valid)/len(valid) if valid else 0
            print(f"  {label:30s}  avg={avg:.4f}  ok={len(valid)}/{len(scores)}  errors={errors}")
        else:
            print(f"  {label:30s}  NO RESULTS")
    
    print(f"\nCompleted at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    main()
