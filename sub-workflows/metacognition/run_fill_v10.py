#!/usr/bin/env python3
"""
v10: Parallel model execution. Each model runs in its own subprocess.
All models run simultaneously since they use different Bedrock endpoints.
"""
import json, os, sys, time, subprocess
from datetime import datetime, timezone
from concurrent.futures import ProcessPoolExecutor, as_completed

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
BENCHMARK_TIMEOUT = 180
MAX_RUNTIME = 25 * 60

RUNNER_SCRIPT = '''
import json, sys, os, time, importlib
REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
sys.path.insert(0, REPO)
os.environ['PYTHONUNBUFFERED'] = '1'

model_id = sys.argv[1]
mod_path = sys.argv[2]
fn_name = sys.argv[3]

from scripts.run_benchmark_bedrock import (
    MODEL_CATALOG, BENCHMARKS, setup_kbench_mocks,
    create_bedrock_llm, get_track_for_benchmark
)

track = get_track_for_benchmark(fn_name)
track_dir = os.path.join(REPO, 'benchmarks', track)
if track_dir not in sys.path:
    sys.path.insert(0, track_dir)

setup_kbench_mocks()

entry = MODEL_CATALOG[model_id]
invoke_id = entry[1]
llm = create_bedrock_llm(invoke_id)

mod = importlib.import_module(mod_path)
task_fn = getattr(mod, fn_name)

start = time.time()
try:
    result = task_fn.run(llm=llm)
    elapsed = time.time() - start
    score = float(result.result) if hasattr(result, 'result') else float(result)
    print(json.dumps({"score": score, "error": None, "duration_s": round(elapsed, 1)}))
except Exception as e:
    elapsed = time.time() - start
    print(json.dumps({"score": None, "error": str(e)[:200], "duration_s": round(elapsed, 1)}))
'''

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
    return {"model": model_id, "model_label": model_id, "timestamp": "", "scores": {}}

def save_results(data):
    model_id = data["model"]
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def run_one_benchmark(model_id, mod_path, fn_name):
    runner_file = f"/tmp/_bench_runner_{os.getpid()}.py"
    with open(runner_file, 'w') as f:
        f.write(RUNNER_SCRIPT)
    python = os.path.join(REPO, ".venv/bin/python3")
    start = time.time()
    try:
        result = subprocess.run(
            [python, runner_file, model_id, mod_path, fn_name],
            capture_output=True, text=True, timeout=BENCHMARK_TIMEOUT,
            cwd=REPO
        )
        elapsed = time.time() - start
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in reversed(lines):
                line = line.strip()
                if line.startswith('{'):
                    return json.loads(line)
            return {"score": None, "error": f"no JSON: {result.stdout[-200:]}", "duration_s": round(elapsed, 1)}
        else:
            return {"score": None, "error": f"exit {result.returncode}: {result.stderr[-200:]}", "duration_s": round(elapsed, 1)}
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        return {"score": None, "error": f"timeout ({BENCHMARK_TIMEOUT}s)", "duration_s": round(elapsed, 1)}

def run_model(model_id, label, all_benchmarks, start_time):
    """Run all missing benchmarks for a single model. Called in parallel."""
    data = load_results(model_id)
    data["model_label"] = label
    scores = data["scores"]
    
    remaining = []
    for mp, fn in all_benchmarks:
        if fn in scores and scores[fn].get("score") is not None:
            continue  # Already have valid score
        remaining.append((mp, fn))
    
    if not remaining:
        ok = sum(1 for v in scores.values() if v.get("score") is not None)
        return f"✅ {label}: {ok}/26 ok (complete)"
    
    results_log = [f"{label}: {len(remaining)} gaps"]
    consecutive_timeouts = 0
    
    for bi, (mod_path, fn_name) in enumerate(remaining):
        if time.time() - start_time > MAX_RUNTIME:
            results_log.append(f"  ⏰ Time limit after {bi} benchmarks")
            break
        
        result = run_one_benchmark(model_id, mod_path, fn_name)
        scores[fn_name] = result
        data["scores"] = scores
        save_results(data)
        
        if result["score"] is not None:
            results_log.append(f"  {fn_name}: {result['score']:.4f} ({result['duration_s']}s)")
            consecutive_timeouts = 0
        else:
            err = (result.get('error') or '')[:80]
            results_log.append(f"  {fn_name}: ERROR {err} ({result['duration_s']}s)")
            if 'timeout' in err.lower():
                consecutive_timeouts += 1
            else:
                consecutive_timeouts = 0
        
        if consecutive_timeouts >= 3:
            results_log.append(f"  → Stopped: 3 consecutive timeouts")
            break
        
        time.sleep(2)
    
    ok = sum(1 for v in scores.values() if v.get("score") is not None)
    total = len(scores)
    results_log.append(f"  Final: {ok}/{total} ok")
    return "\n".join(results_log)

def main():
    start_time = time.time()
    sys.path.insert(0, REPO)
    from scripts.run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS
    
    ALL_BENCHMARKS = []
    for track in BENCHMARKS:
        ALL_BENCHMARKS.extend(BENCHMARKS[track])
    
    print(f"Starting run_fill_v10 (PARALLEL) at {datetime.now(timezone.utc).isoformat()}")
    print(f"Models: {len(MODEL_CATALOG)}, Benchmarks per model: {len(ALL_BENCHMARKS)}")
    print(f"Running all models in parallel...")
    sys.stdout.flush()
    
    # Run all models in parallel (max 5 at a time to not overwhelm the machine)
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for model_id in MODEL_CATALOG:
            label = MODEL_CATALOG[model_id][0]
            f = executor.submit(run_model, model_id, label, ALL_BENCHMARKS, start_time)
            futures[f] = label
        
        for f in as_completed(futures):
            label = futures[f]
            try:
                result = f.result()
                print(f"\n{result}")
            except Exception as e:
                print(f"\n{label}: EXCEPTION {e}")
            sys.stdout.flush()
    
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
        missing = 26 - total
        print(f"  {label:30s}  total={total:2d}/26  ok={valid:2d}  errors={errors:2d}  missing={missing:2d}")
    
    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed/60:.1f} min")

if __name__ == "__main__":
    main()
