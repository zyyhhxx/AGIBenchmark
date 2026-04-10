#!/usr/bin/env python3
"""
v13: Parallel model runner. Runs all models simultaneously, each in its own
sequential benchmark loop. Uses multiprocessing to parallelize across models.
"""
import json, os, sys, time, subprocess
from datetime import datetime, timezone
from multiprocessing import Pool, cpu_count

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
PYTHON = os.path.join(REPO, ".venv/bin/python3")
BENCHMARK_TIMEOUT = 600
DELAY_BETWEEN = 2

RUNNER_SCRIPT = r'''
import json, sys, os, time, runpy

REPO = sys.argv[1]
model_id = sys.argv[2]
task_file = sys.argv[3]
fn_name = sys.argv[4]
out_file = sys.argv[5]

sys.path.insert(0, REPO)
track_dir = os.path.dirname(task_file)
sys.path.insert(0, track_dir)
os.chdir(track_dir)

from scripts.run_benchmark_bedrock import MODEL_CATALOG, setup_kbench_mocks, create_bedrock_llm
setup_kbench_mocks()
entry = MODEL_CATALOG[model_id]
llm = create_bedrock_llm(entry[1])

mod = runpy.run_path(task_file, run_name="__not_main__")
task_fn = mod[fn_name]

start = time.time()
try:
    result = task_fn.run(llm=llm)
    elapsed = time.time() - start
    score = float(result.result) if hasattr(result, 'result') else float(result)
    out = {"score": score, "error": None, "duration_s": round(elapsed, 1)}
except Exception as e:
    elapsed = time.time() - start
    out = {"score": None, "error": str(e)[:500], "duration_s": round(elapsed, 1)}

with open(out_file, 'w') as f:
    json.dump(out, f)
print(json.dumps(out))
'''

def safe_name(mid):
    return mid.replace(':', '_').replace('/', '_')

def load_results(mid):
    path = os.path.join(RESULTS_DIR, f"{safe_name(mid)}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"model": mid, "model_label": "", "timestamp": "", "scores": {}}

def save_results(data):
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(RESULTS_DIR, f"{safe_name(data['model'])}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def needs_run(entry):
    if entry is None: return True
    if entry.get("score") is not None: return False
    err = entry.get("error", "") or ""
    if "ValidationException" in err: return False
    return True

def find_task_file(mod_path):
    return os.path.join(REPO, *mod_path.split('.')) + '.py'

def run_model(args):
    """Run all missing benchmarks for one model."""
    model_id, label, all_benchmarks, runner_file = args
    data = load_results(model_id)
    data["model_label"] = label
    scores = data.get("scores", {})
    
    gaps = [(mp, fn) for mp, fn in all_benchmarks if needs_run(scores.get(fn))]
    if not gaps:
        ok = sum(1 for _, fn in all_benchmarks if scores.get(fn, {}).get("score") is not None)
        print(f"[{label}] Complete: {ok}/26", flush=True)
        return model_id, 0, 0
    
    print(f"[{label}] Starting {len(gaps)} benchmarks", flush=True)
    ran = ok_count = 0
    
    for bi, (mod_path, fn_name) in enumerate(gaps):
        task_file = find_task_file(mod_path)
        out_file = f"/tmp/_v13_{safe_name(model_id)}_{fn_name}.json"
        if os.path.exists(out_file):
            os.unlink(out_file)
        
        print(f"  [{label}] [{bi+1}/{len(gaps)}] {fn_name}...", end=" ", flush=True)
        
        try:
            proc = subprocess.run(
                [PYTHON, runner_file, REPO, model_id, task_file, fn_name, out_file],
                timeout=BENCHMARK_TIMEOUT, capture_output=True, text=True
            )
            if os.path.exists(out_file):
                with open(out_file) as f:
                    result = json.load(f)
                os.unlink(out_file)
            else:
                stderr = proc.stderr[-300:] if proc.stderr else ""
                result = {"score": None, "error": f"exit {proc.returncode}: {stderr}", "duration_s": 0}
        except subprocess.TimeoutExpired:
            result = {"score": None, "error": f"timeout ({BENCHMARK_TIMEOUT}s)", "duration_s": BENCHMARK_TIMEOUT}
        
        scores[fn_name] = result
        data["scores"] = scores
        save_results(data)
        ran += 1
        
        if result.get("score") is not None:
            ok_count += 1
            print(f"{result['score']:.4f} ({result['duration_s']}s)", flush=True)
        else:
            print(f"ERR: {(result.get('error') or '')[:60]}", flush=True)
        
        time.sleep(DELAY_BETWEEN)
    
    total_ok = sum(1 for _, fn in all_benchmarks if scores.get(fn, {}).get("score") is not None)
    print(f"[{label}] Done: {total_ok}/26 scored", flush=True)
    return model_id, ran, ok_count

def main():
    sys.path.insert(0, REPO)
    from scripts.run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS
    
    all_benchmarks = []
    for track in BENCHMARKS:
        all_benchmarks.extend(BENCHMARKS[track])
    
    runner_file = "/tmp/_v13_runner.py"
    with open(runner_file, 'w') as f:
        f.write(RUNNER_SCRIPT)
    
    print(f"run_fill_v13 started at {datetime.now(timezone.utc).isoformat()}", flush=True)
    print(f"Benchmarks: {len(all_benchmarks)}, Models: {len(MODEL_CATALOG)}", flush=True)
    
    # Build work items — run all models in parallel
    work = [(mid, label, all_benchmarks, runner_file) for mid, (label, _) in MODEL_CATALOG.items()]
    
    # Use pool size = 5 to avoid overwhelming Bedrock
    with Pool(processes=5) as pool:
        results = pool.map(run_model, work)
    
    # Summary
    print(f"\n{'='*60}", flush=True)
    print("FINAL SUMMARY:", flush=True)
    for mid, (label, _) in MODEL_CATALOG.items():
        data = load_results(mid)
        scores = data.get("scores", {})
        ok = sum(1 for _, fn in all_benchmarks if scores.get(fn, {}).get("score") is not None)
        errs = sum(1 for _, fn in all_benchmarks if fn in scores and scores[fn] and scores[fn].get("score") is None)
        miss = 26 - ok - errs
        print(f"  {label:30s} scored={ok:2d}  errors={errs:2d}  missing={miss:2d}", flush=True)
    
    # Generate score_matrix.csv
    models = list(MODEL_CATALOG.items())
    header = ["benchmark"] + [label for _, (label, _) in models]
    rows = [",".join(header)]
    for _, fn in all_benchmarks:
        cells = [fn]
        for mid, (label, _) in models:
            data = load_results(mid)
            entry = data.get("scores", {}).get(fn)
            if entry is None:
                cells.append("")
            elif entry.get("score") is not None:
                cells.append(f"{entry['score']:.4f}")
            else:
                err = (entry.get("error") or "unknown")[:60]
                cells.append(f"ERROR:{err}")
            rows.append(",".join(cells))
    
    # Fix: rows.append should be outside the model loop
    # Rewrite correctly
    rows = [",".join(header)]
    for _, fn in all_benchmarks:
        cells = [fn]
        for mid, (label, _) in models:
            data = load_results(mid)
            entry = data.get("scores", {}).get(fn)
            if entry is None:
                cells.append("")
            elif entry.get("score") is not None:
                cells.append(f"{entry['score']:.4f}")
            else:
                err = (entry.get("error") or "unknown")[:60]
                cells.append(f"ERROR:{err}")
        rows.append(",".join(cells))
    
    csv_path = os.path.join(RESULTS_DIR, "score_matrix.csv")
    with open(csv_path, 'w') as f:
        f.write("\n".join(rows) + "\n")
    print(f"\nWrote {csv_path}")

if __name__ == "__main__":
    main()
