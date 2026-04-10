#!/usr/bin/env python3
"""
Run benchmarks for a SINGLE model. Designed to be launched in parallel for multiple models.
Usage: python3 run_single_model.py <model_key> [--timeout 300]
"""
import json, os, sys, time, signal, importlib, traceback
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
sys.path.insert(0, REPO)

RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
os.makedirs(RESULTS_DIR, exist_ok=True)

from scripts.run_benchmark_bedrock import (
    MODEL_CATALOG, BENCHMARKS, setup_kbench_mocks,
    create_bedrock_llm, get_track_for_benchmark
)

ALL_BENCHMARKS = []
for track in BENCHMARKS:
    ALL_BENCHMARKS.extend(BENCHMARKS[track])

class BenchTimeout(Exception):
    pass

def timeout_handler(signum, frame):
    raise BenchTimeout("timeout")

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
    label = MODEL_CATALOG[model_id][0]
    return {"model": model_id, "model_label": label, "timestamp": "", "scores": {}}

def save_results(data):
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(RESULTS_DIR, f"{safe_name(data['model'])}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def run_one(mod_path, fn_name, llm, timeout_s):
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
    signal.alarm(timeout_s)
    start = time.time()
    try:
        result = task_fn.run(llm=llm)
        signal.alarm(0)
        elapsed = time.time() - start
        score = float(result.result) if hasattr(result, 'result') else float(result)
        return {"score": score, "error": None, "duration_s": round(elapsed, 1)}
    except BenchTimeout:
        signal.alarm(0)
        return {"score": None, "error": f"timeout after {timeout_s}s", "duration_s": round(time.time()-start, 1)}
    except Exception as e:
        signal.alarm(0)
        return {"score": None, "error": str(e)[:200], "duration_s": round(time.time()-start, 1)}
    finally:
        signal.signal(signal.SIGALRM, old_handler)
        signal.alarm(0)

def main():
    model_key = sys.argv[1]
    timeout_s = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    
    if model_key not in MODEL_CATALOG:
        print(f"ERROR: Unknown model {model_key}")
        print(f"Available: {list(MODEL_CATALOG.keys())}")
        sys.exit(1)
    
    entry = MODEL_CATALOG[model_key]
    label, invoke_id = entry[0], entry[1]
    data = load_results(model_key)
    scores = data["scores"]
    
    remaining = [(mp, fn) for mp, fn in ALL_BENCHMARKS if fn not in scores]
    print(f"[{label}] {len(scores)} done, {len(remaining)} remaining, timeout={timeout_s}s")
    sys.stdout.flush()
    
    if not remaining:
        print(f"[{label}] All benchmarks complete!")
        return
    
    llm = create_bedrock_llm(invoke_id)
    
    for i, (mod_path, fn_name) in enumerate(remaining):
        print(f"[{label}] [{i+1}/{len(remaining)}] {fn_name}...", end=" ", flush=True)
        result = run_one(mod_path, fn_name, llm, timeout_s)
        scores[fn_name] = result
        if result["score"] is not None:
            print(f"score={result['score']:.4f} ({result['duration_s']}s)")
        else:
            print(f"ERROR: {(result['error'] or '')[:60]} ({result['duration_s']}s)")
        sys.stdout.flush()
        data["scores"] = scores
        save_results(data)
        time.sleep(2)
    
    print(f"[{label}] COMPLETE: {len(scores)} benchmarks")
    valid = [s["score"] for s in scores.values() if s.get("score") is not None]
    avg = sum(valid)/len(valid) if valid else 0
    errors = sum(1 for s in scores.values() if s.get("error"))
    print(f"[{label}] avg={avg:.4f} ok={len(valid)}/{len(scores)} errors={errors}")

if __name__ == "__main__":
    main()
