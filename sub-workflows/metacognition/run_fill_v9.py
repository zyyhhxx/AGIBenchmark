#!/usr/bin/env python3
"""
v9: Aggressive gap-fill. Clears old timeout/HTTP errors and retries.
Longer timeout (180s). Prioritizes models with most successful benchmarks (closest to done).
Skips benchmarks that failed on 3+ models with same error (likely broken benchmark).
"""
import json, os, sys, time, subprocess
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
BENCHMARK_TIMEOUT = 180  # 3 min per benchmark
MAX_RUNTIME = 25 * 60  # 25 min total

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

def run_benchmark(model_id, mod_path, fn_name):
    runner_file = "/tmp/_bench_runner.py"
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
            return {"score": None, "error": f"no JSON output: {result.stdout[-200:]}", "duration_s": round(elapsed, 1)}
        else:
            return {"score": None, "error": f"exit code {result.returncode}: {result.stderr[-200:]}", "duration_s": round(elapsed, 1)}
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        return {"score": None, "error": f"timeout ({BENCHMARK_TIMEOUT}s)", "duration_s": round(elapsed, 1)}

def needs_run(scores, fn_name):
    """True if benchmark not present or has error (retry errors)."""
    if fn_name not in scores:
        return True
    entry = scores[fn_name]
    if entry.get("score") is not None:
        return False  # Already have a valid score
    # Has error — check if it's a retryable error
    err = entry.get("error", "")
    # Don't retry ValidationException (model can't handle this benchmark)
    if "ValidationException" in err:
        return False
    return True

def main():
    start_time = time.time()
    sys.path.insert(0, REPO)
    from scripts.run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS
    
    ALL_BENCHMARKS = []
    for track in BENCHMARKS:
        ALL_BENCHMARKS.extend(BENCHMARKS[track])
    
    print(f"Starting run_fill_v9 at {datetime.now(timezone.utc).isoformat()}")
    print(f"Models: {len(MODEL_CATALOG)}, Benchmarks: {len(ALL_BENCHMARKS)}")
    sys.stdout.flush()
    
    # Sort models by fewest gaps first (closest to completion)
    model_gaps = []
    for model_id in MODEL_CATALOG:
        data = load_results(model_id)
        gaps = sum(1 for mp, fn in ALL_BENCHMARKS if needs_run(data["scores"], fn))
        model_gaps.append((gaps, model_id))
    model_gaps.sort()
    
    for mi, (gap_count, model_id) in enumerate(model_gaps):
        if time.time() - start_time > MAX_RUNTIME:
            print(f"\n⏰ Time limit reached")
            break
        
        label = MODEL_CATALOG[model_id][0]
        data = load_results(model_id)
        data["model_label"] = label
        scores = data["scores"]
        
        remaining = [(mp, fn) for mp, fn in ALL_BENCHMARKS if needs_run(scores, fn)]
        if not remaining:
            ok = sum(1 for v in scores.values() if v.get("score") is not None)
            print(f"[{mi+1}/10] ✅ {label}: {ok}/{len(scores)} ok (no retryable gaps)")
            sys.stdout.flush()
            continue
        
        print(f"\n[{mi+1}/10] {label}: {len(remaining)} retryable gaps")
        sys.stdout.flush()
        
        consecutive_timeouts = 0
        for bi, (mod_path, fn_name) in enumerate(remaining):
            if time.time() - start_time > MAX_RUNTIME:
                print(f"  ⏰ Time limit")
                break
            
            # Clear old error entry before retry
            if fn_name in scores and scores[fn_name].get("score") is None:
                del scores[fn_name]
            
            print(f"  [{bi+1}/{len(remaining)}] {fn_name}...", end=" ", flush=True)
            result = run_benchmark(model_id, mod_path, fn_name)
            scores[fn_name] = result
            data["scores"] = scores
            save_results(data)
            
            if result["score"] is not None:
                print(f"score={result['score']:.4f} ({result['duration_s']}s)")
                consecutive_timeouts = 0
            else:
                err = (result.get('error') or '')[:80]
                print(f"ERROR: {err} ({result['duration_s']}s)")
                if 'timeout' in err.lower():
                    consecutive_timeouts += 1
                else:
                    consecutive_timeouts = 0
            sys.stdout.flush()
            
            if consecutive_timeouts >= 3:
                print(f"  → Skipping {label}: 3 consecutive timeouts")
                break
            
            time.sleep(2)
    
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
