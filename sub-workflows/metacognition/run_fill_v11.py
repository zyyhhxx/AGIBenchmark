#!/usr/bin/env python3
"""
v11: Smart parallel runner. Runs each model as a background process.
Monitors progress without blocking. Handles all missing benchmarks.
"""
import json, os, sys, time, subprocess
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
BENCHMARK_TIMEOUT = 300  # 5 min per benchmark
MAX_RUNTIME = 50 * 60  # 50 min total (will be managed externally)

BENCH_RUNNER = '''#!/usr/bin/env python3
import json, sys, os, time, importlib
REPO = sys.argv[1]
model_id = sys.argv[2]
mod_path = sys.argv[3]
fn_name = sys.argv[4]
out_file = sys.argv[5]

sys.path.insert(0, REPO)

from scripts.run_benchmark_bedrock import (
    MODEL_CATALOG, setup_kbench_mocks, create_bedrock_llm, get_track_for_benchmark
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
    out = {"score": score, "error": None, "duration_s": round(elapsed, 1)}
except Exception as e:
    elapsed = time.time() - start
    out = {"score": None, "error": str(e)[:300], "duration_s": round(elapsed, 1)}

with open(out_file, 'w') as f:
    json.dump(out, f)
print(json.dumps(out))
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

def is_complete(score_entry):
    if score_entry is None:
        return False
    return score_entry.get("score") is not None

def should_skip(score_entry):
    """Skip if ValidationException (model incapable)."""
    if score_entry is None:
        return False
    err = score_entry.get("error", "") or ""
    return "ValidationException" in err

def run_model_sequential(model_id, label, all_benchmarks):
    """Run all benchmarks for a model sequentially, writing results as we go."""
    python = os.path.join(REPO, ".venv/bin/python3")
    runner_file = f"/tmp/_v11_runner_{os.getpid()}.py"
    with open(runner_file, 'w') as f:
        f.write(BENCH_RUNNER)
    
    start_time = time.time()
    data = load_results(model_id)
    data["model_label"] = label
    scores = data["scores"]
    
    remaining = [(mp, fn) for mp, fn in all_benchmarks
                 if not is_complete(scores.get(fn)) and not should_skip(scores.get(fn))]
    
    if not remaining:
        ok = sum(1 for v in scores.values() if is_complete(v))
        print(f"[{label}] Already complete: {ok}/26", flush=True)
        return
    
    print(f"[{label}] Starting {len(remaining)} benchmarks", flush=True)
    
    for bi, (mod_path, fn_name) in enumerate(remaining):
        if time.time() - start_time > MAX_RUNTIME:
            print(f"[{label}] ⏰ Time limit at benchmark {bi+1}", flush=True)
            break
        
        out_file = f"/tmp/_v11_out_{safe_name(model_id)}_{fn_name}.json"
        print(f"[{label}] [{bi+1}/{len(remaining)}] {fn_name}...", end=" ", flush=True)
        
        try:
            proc = subprocess.run(
                [python, runner_file, REPO, model_id, mod_path, fn_name, out_file],
                timeout=BENCHMARK_TIMEOUT,
                capture_output=True, text=True, cwd=REPO
            )
            if os.path.exists(out_file):
                with open(out_file) as f:
                    result = json.load(f)
                os.unlink(out_file)
            elif proc.returncode == 0:
                # Parse stdout
                lines = proc.stdout.strip().split('\n')
                result = None
                for line in reversed(lines):
                    line = line.strip()
                    if line.startswith('{'):
                        result = json.loads(line)
                        break
                if result is None:
                    result = {"score": None, "error": f"no output: {proc.stdout[-200:]}", "duration_s": 0}
            else:
                result = {"score": None, "error": f"exit {proc.returncode}: {proc.stderr[-200:]}", "duration_s": 0}
        except subprocess.TimeoutExpired:
            result = {"score": None, "error": f"timeout ({BENCHMARK_TIMEOUT}s)", "duration_s": BENCHMARK_TIMEOUT}
        
        scores[fn_name] = result
        data["scores"] = scores
        save_results(data)
        
        if result["score"] is not None:
            print(f"score={result['score']:.4f} ({result['duration_s']}s)", flush=True)
        else:
            err = (result.get("error") or "")[:80]
            print(f"ERROR: {err} ({result['duration_s']}s)", flush=True)
        
        time.sleep(1)
    
    ok = sum(1 for v in scores.values() if is_complete(v))
    total = len(scores)
    print(f"[{label}] Done: {ok}/{total} benchmarks with scores", flush=True)

def main():
    sys.path.insert(0, REPO)
    from scripts.run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS
    
    ALL_BENCHMARKS = []
    for track in BENCHMARKS:
        ALL_BENCHMARKS.extend(BENCHMARKS[track])
    
    # Get target model from command line arg, or run all
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    print(f"run_fill_v11 at {datetime.now(timezone.utc).isoformat()}", flush=True)
    
    if target == "all":
        models = list(MODEL_CATALOG.items())
    else:
        models = [(target, MODEL_CATALOG[target])]
    
    for model_id, (label, _) in models:
        run_model_sequential(model_id, label, ALL_BENCHMARKS)
    
    # Summary
    print(f"\n{'='*60}", flush=True)
    print("SUMMARY", flush=True)
    for model_id, (label, _) in MODEL_CATALOG.items():
        data = load_results(model_id)
        scores = data["scores"]
        ok = sum(1 for v in scores.values() if is_complete(v))
        total = len(scores)
        missing = 26 - total
        print(f"  {label:30s} ok={ok:2d}/26  total_attempted={total:2d}  missing={missing:2d}", flush=True)

if __name__ == "__main__":
    main()
