#!/usr/bin/env python3
"""
Run all benchmarks across all models IN-PROCESS with signal-based timeouts.
Saves incrementally after each benchmark.
"""
import json, os, sys, time, signal, importlib, traceback
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
sys.path.insert(0, REPO)
os.environ['PYTHONUNBUFFERED'] = '1'

RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
os.makedirs(RESULTS_DIR, exist_ok=True)

BENCHMARK_TIMEOUT = 180  # 3 min per benchmark

from scripts.run_benchmark_bedrock import (
    MODEL_CATALOG, BENCHMARKS, setup_kbench_mocks,
    create_bedrock_llm, get_track_for_benchmark
)

MODELS = list(MODEL_CATALOG.keys())

ALL_BENCHMARKS = []
for track in BENCHMARKS:
    ALL_BENCHMARKS.extend(BENCHMARKS[track])

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("benchmark timeout")

def safe_name(model_id):
    return model_id.replace(':', '_').replace('/', '_')

def load_results(model_id):
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            pass
    label = MODEL_CATALOG[model_id][0] if model_id in MODEL_CATALOG else model_id
    return {"model": model_id, "model_label": label, "timestamp": "", "scores": {}}

def save_results(data):
    model_id = data["model"]
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def run_one(mod_path, fn_name, llm):
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
    
    # Set alarm timeout
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(BENCHMARK_TIMEOUT)
    
    start = time.time()
    try:
        result = task_fn.run(llm=llm)
        signal.alarm(0)
        elapsed = time.time() - start
        score = float(result.result) if hasattr(result, 'result') else float(result)
        return {"score": score, "error": None, "duration_s": round(elapsed, 1)}
    except TimeoutError:
        signal.alarm(0)
        elapsed = time.time() - start
        return {"score": None, "error": f"timeout after {elapsed:.0f}s", "duration_s": round(elapsed, 1)}
    except Exception as e:
        signal.alarm(0)
        elapsed = time.time() - start
        return {"score": None, "error": str(e)[:200], "duration_s": round(elapsed, 1)}
    finally:
        signal.signal(signal.SIGALRM, old_handler)
        signal.alarm(0)

def main():
    print(f"Starting run_all_v5 at {datetime.now(timezone.utc).isoformat()}")
    print(f"Models: {len(MODELS)}, Benchmarks: {len(ALL_BENCHMARKS)}")
    print(f"Per-benchmark timeout: {BENCHMARK_TIMEOUT}s")
    sys.stdout.flush()
    
    for mi, model_id in enumerate(MODELS):
        entry = MODEL_CATALOG[model_id]
        label, invoke_id = entry[0], entry[1]
        data = load_results(model_id)
        scores = data["scores"]
        
        remaining = [(mp, fn) for mp, fn in ALL_BENCHMARKS if fn not in scores]
        if not remaining:
            print(f"\n[{mi+1}/{len(MODELS)}] SKIP {label}: all {len(scores)} done")
            sys.stdout.flush()
            continue
        
        print(f"\n[{mi+1}/{len(MODELS)}] {label}: {len(scores)} done, {len(remaining)} remaining")
        sys.stdout.flush()
        
        llm = create_bedrock_llm(invoke_id)
        
        for bi, (mod_path, fn_name) in enumerate(remaining):
            print(f"  [{bi+1}/{len(remaining)}] {fn_name}...", end=" ", flush=True)
            result = run_one(mod_path, fn_name, llm)
            scores[fn_name] = result
            
            if result["score"] is not None:
                print(f"score={result['score']:.4f} ({result['duration_s']}s)")
            else:
                print(f"ERROR: {(result['error'] or '')[:60]} ({result['duration_s']}s)")
            sys.stdout.flush()
            
            data["scores"] = scores
            save_results(data)
            time.sleep(2)
        
        print(f"  → {label} complete: {len(scores)} benchmarks")
        sys.stdout.flush()
        time.sleep(5)
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    for model_id in MODELS:
        label = MODEL_CATALOG[model_id][0]
        data = load_results(model_id)
        scores = data["scores"]
        valid = [s["score"] for s in scores.values() if s.get("score") is not None]
        errors = sum(1 for s in scores.values() if s.get("error") is not None)
        avg = sum(valid)/len(valid) if valid else 0
        print(f"  {label:30s}  avg={avg:.4f}  ok={len(valid)}/{len(scores)}  errors={errors}")
    
    print(f"\nCompleted at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    main()
