#!/usr/bin/env python3
"""
v7: Fill all gaps. Retry errors and missing benchmarks for all 10 models.
Timeout: 180s per benchmark. Skip after 3 consecutive timeouts per model.
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

ALL_BENCHMARKS = []
for track in BENCHMARKS:
    ALL_BENCHMARKS.extend(BENCHMARKS[track])

class BenchmarkTimeout(Exception):
    pass

def timeout_handler(signum, frame):
    raise BenchmarkTimeout("benchmark timeout")

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
    
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(BENCHMARK_TIMEOUT)
    
    start = time.time()
    try:
        result = task_fn.run(llm=llm)
        signal.alarm(0)
        elapsed = time.time() - start
        score = float(result.result) if hasattr(result, 'result') else float(result)
        return {"score": score, "error": None, "duration_s": round(elapsed, 1)}
    except BenchmarkTimeout:
        signal.alarm(0)
        elapsed = time.time() - start
        return {"score": None, "error": f"timeout ({BENCHMARK_TIMEOUT}s)", "duration_s": round(elapsed, 1)}
    except Exception as e:
        signal.alarm(0)
        elapsed = time.time() - start
        return {"score": None, "error": str(e)[:200], "duration_s": round(elapsed, 1)}
    finally:
        signal.signal(signal.SIGALRM, old_handler)
        signal.alarm(0)

def needs_run(scores, fn_name):
    """Return True if benchmark needs (re)running: missing or errored."""
    if fn_name not in scores:
        return True
    entry = scores[fn_name]
    if entry.get("score") is None:
        return True
    return False

def main():
    start_time = time.time()
    MAX_RUNTIME = 25 * 60  # 25 min hard limit
    
    print(f"Starting run_fill_v7 at {datetime.now(timezone.utc).isoformat()}")
    print(f"Models: {len(MODEL_CATALOG)}, Benchmarks per model: {len(ALL_BENCHMARKS)}")
    print(f"Per-benchmark timeout: {BENCHMARK_TIMEOUT}s, Max runtime: {MAX_RUNTIME}s")
    sys.stdout.flush()
    
    # Sort models by number of gaps (fewest first, so we complete more models)
    model_gaps = []
    for model_id in MODEL_CATALOG:
        data = load_results(model_id)
        gaps = sum(1 for mp, fn in ALL_BENCHMARKS if needs_run(data["scores"], fn))
        model_gaps.append((gaps, model_id))
    model_gaps.sort()
    
    for mi, (gap_count, model_id) in enumerate(model_gaps):
        if time.time() - start_time > MAX_RUNTIME:
            print(f"\n⏰ Time limit reached after {(time.time()-start_time)/60:.1f} min")
            break
            
        entry = MODEL_CATALOG[model_id]
        label, invoke_id = entry[0], entry[1]
        data = load_results(model_id)
        scores = data["scores"]
        
        remaining = [(mp, fn) for mp, fn in ALL_BENCHMARKS if needs_run(scores, fn)]
        if not remaining:
            print(f"\n[{mi+1}/{len(model_gaps)}] ✅ {label}: all {len(scores)} done")
            sys.stdout.flush()
            continue
        
        print(f"\n[{mi+1}/{len(model_gaps)}] {label}: {len(remaining)} gaps to fill")
        sys.stdout.flush()
        
        llm = create_bedrock_llm(invoke_id)
        consecutive_timeouts = 0
        
        for bi, (mod_path, fn_name) in enumerate(remaining):
            if time.time() - start_time > MAX_RUNTIME:
                print(f"  ⏰ Time limit - stopping mid-model")
                break
                
            print(f"  [{bi+1}/{len(remaining)}] {fn_name}...", end=" ", flush=True)
            result = run_one(mod_path, fn_name, llm)
            scores[fn_name] = result
            
            if result["score"] is not None:
                print(f"score={result['score']:.4f} ({result['duration_s']}s)")
                consecutive_timeouts = 0
            else:
                print(f"ERROR: {(result['error'] or '')[:80]} ({result['duration_s']}s)")
                if 'timeout' in (result.get('error') or '').lower():
                    consecutive_timeouts += 1
                else:
                    consecutive_timeouts = 0
            sys.stdout.flush()
            
            data["scores"] = scores
            save_results(data)
            
            if consecutive_timeouts >= 3:
                print(f"  → Skipping {label}: 3 consecutive timeouts")
                sys.stdout.flush()
                break
            
            time.sleep(2)
        
        time.sleep(3)
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    for model_id in MODEL_CATALOG:
        label = MODEL_CATALOG[model_id][0]
        data = load_results(model_id)
        scores = data["scores"]
        total = len(scores)
        valid = sum(1 for s in scores.values() if s.get("score") is not None)
        errors = sum(1 for s in scores.values() if s.get("error") is not None)
        print(f"  {label:30s}  total={total:2d}/26  ok={valid:2d}  errors={errors:2d}")
    
    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed/60:.1f} min at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    main()
