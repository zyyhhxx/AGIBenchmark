#!/usr/bin/env python3
"""v15: Retry timeouts only, 300s timeout, 2 models parallel."""
import json, os, sys, time, subprocess, threading
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
PYTHON = os.path.join(REPO, ".venv/bin/python3")
BENCHMARK_TIMEOUT = 300
TIME_LIMIT = 18 * 60
START_TIME = time.time()

RUNNER_SCRIPT = r'''
import json, sys, os, time
REPO = sys.argv[1]; model_id = sys.argv[2]; task_file = sys.argv[3]; fn_name = sys.argv[4]; out_file = sys.argv[5]
sys.path.insert(0, REPO); track_dir = os.path.dirname(task_file); sys.path.insert(0, track_dir); os.chdir(track_dir)
from scripts.run_benchmark_bedrock import MODEL_CATALOG, setup_kbench_mocks, create_bedrock_llm
setup_kbench_mocks(); entry = MODEL_CATALOG[model_id]; llm = create_bedrock_llm(entry[1])
import runpy; mod = runpy.run_path(task_file, run_name="__not_main__"); task_fn = mod[fn_name]
start = time.time()
try:
    result = task_fn.run(llm=llm); elapsed = time.time() - start
    score = float(result.result) if hasattr(result, 'result') else float(result)
    out = {"score": score, "error": None, "duration_s": round(elapsed, 1)}
except Exception as e:
    elapsed = time.time() - start
    out = {"score": None, "error": str(e)[:500], "duration_s": round(elapsed, 1)}
with open(out_file, 'w') as f: json.dump(out, f)
'''

lock = threading.Lock()

def safe_name(mid): return mid.replace(':', '_').replace('/', '_')
def load_results(mid):
    path = os.path.join(RESULTS_DIR, f"{safe_name(mid)}.json")
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return {"model": mid, "model_label": "", "timestamp": "", "scores": {}}
def save_results(data):
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(RESULTS_DIR, f"{safe_name(data['model'])}.json")
    with open(path, 'w') as f: json.dump(data, f, indent=2)

def is_timeout(entry):
    if entry is None: return False
    if entry.get("score") is not None: return False
    err = entry.get("error", "") or ""
    return "timeout" in err.lower() or "hung" in err.lower()

def is_missing(entry):
    return entry is None

def run_model(mid, label, benchmark_map, runner_file):
    data = load_results(mid)
    data["model_label"] = label
    scores = data.get("scores", {})
    
    # Retry timeouts + fill missing
    gaps = [fn for fn in benchmark_map if is_timeout(scores.get(fn)) or is_missing(scores.get(fn))]
    if not gaps:
        ok = sum(1 for v in scores.values() if v and v.get("score") is not None)
        print(f"  {label}: no retryable gaps ({ok}/26 ok)", flush=True)
        return
    
    print(f"  {label}: {len(gaps)} to retry", flush=True)
    for fn in gaps:
        if time.time() - START_TIME > TIME_LIMIT:
            print(f"  {label}: TIME LIMIT", flush=True)
            break
        mod_path = benchmark_map[fn]
        parts = mod_path.split('.')
        task_file = os.path.join(REPO, *parts) + '.py'
        if not os.path.exists(task_file): continue
        
        out_file = f"/tmp/_v15_{safe_name(mid)}_{fn}.json"
        if os.path.exists(out_file): os.unlink(out_file)
        try:
            proc = subprocess.run(
                [PYTHON, runner_file, REPO, mid, task_file, fn, out_file],
                timeout=BENCHMARK_TIMEOUT, capture_output=True, text=True)
            if os.path.exists(out_file):
                with open(out_file) as f: result = json.load(f)
                os.unlink(out_file)
            else:
                stderr = proc.stderr[-200:] if proc.stderr else ""
                result = {"score": None, "error": f"exit {proc.returncode}: {stderr}", "duration_s": 0}
        except subprocess.TimeoutExpired:
            result = {"score": None, "error": f"timeout ({BENCHMARK_TIMEOUT}s)", "duration_s": BENCHMARK_TIMEOUT}
        
        scores[fn] = result
        data["scores"] = scores
        with lock: save_results(data)
        status = f"{result['score']:.4f}" if result.get("score") is not None else f"ERR:{(result.get('error',''))[:50]}"
        print(f"    {label}/{fn}: {status} ({result.get('duration_s',0)}s)", flush=True)
        time.sleep(1)

def main():
    sys.path.insert(0, REPO)
    from scripts.run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS
    benchmark_map = {}
    for track in BENCHMARKS:
        for mp, fn in BENCHMARKS[track]:
            benchmark_map[fn] = mp
    
    runner_file = "/tmp/_v15_runner.py"
    with open(runner_file, 'w') as f: f.write(RUNNER_SCRIPT)
    
    print(f"v15 retry started at {datetime.now(timezone.utc).isoformat()}", flush=True)
    
    # Prioritize: Sonnet first (most ok already), then Opus, then others
    priority = [
        "anthropic.claude-sonnet-4-6",
        "anthropic.claude-opus-4-6-v1",
        "deepseek.r1-v1:0",
        "openai.gpt-oss-120b-1:0",
        "qwen.qwen3-next-80b-a3b",
        "zai.glm-4.7",
        "amazon.nova-pro-v1:0",
    ]
    
    # Run 2 at a time
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        for mid in priority:
            if mid not in MODEL_CATALOG: continue
            label = MODEL_CATALOG[mid][0]
            f = executor.submit(run_model, mid, label, benchmark_map, runner_file)
            futures.append((f, label))
        for f, label in futures:
            try: f.result()
            except Exception as e: print(f"  {label} FAILED: {e}", flush=True)
    
    elapsed = time.time() - START_TIME
    print(f"\nDone in {elapsed/60:.1f} min", flush=True)
    
    # Final summary + CSV
    all_fns = [fn for _, fn in sum(BENCHMARKS.values(), [])]
    print("\nFINAL:", flush=True)
    for mid, (label, _) in MODEL_CATALOG.items():
        data = load_results(mid)
        scores = data.get("scores", {})
        ok = sum(1 for fn in all_fns if scores.get(fn, {}).get("score") is not None)
        errs = sum(1 for fn in all_fns if fn in scores and scores[fn] and scores[fn].get("score") is None)
        print(f"  {label:30s} scored={ok:2d}/26 errors={errs:2d}", flush=True)
    
    models = list(MODEL_CATALOG.items())
    header = ["benchmark"] + [label for _, (label, _) in models]
    rows = [",".join(header)]
    for fn in all_fns:
        cells = [fn]
        for mid, (label, _) in models:
            data = load_results(mid)
            entry = data.get("scores", {}).get(fn)
            if entry is None: cells.append("")
            elif entry.get("score") is not None: cells.append(f"{entry['score']:.4f}")
            else: cells.append(f"ERROR:{(entry.get('error',''))[:60]}")
        rows.append(",".join(cells))
    csv_path = os.path.join(RESULTS_DIR, "score_matrix.csv")
    with open(csv_path, 'w') as f: f.write("\n".join(rows) + "\n")
    print(f"\nWrote {csv_path}", flush=True)

if __name__ == "__main__":
    main()
