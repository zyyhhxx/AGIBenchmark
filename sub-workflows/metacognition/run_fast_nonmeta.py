#!/usr/bin/env python3
"""Run missing non-metacognition benchmarks, skip known slow ones."""
import json, os, subprocess, sys, time
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
VENV_PYTHON = os.path.join(REPO, ".venv/bin/python3")
SINGLE_RUNNER = os.path.join(REPO, "sub-workflows/metacognition/run_single.py")
TIMEOUT = 300  # 5 min hard timeout per benchmark

sys.path.insert(0, REPO)
from scripts.run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS

NON_META = []
for track in ['attention', 'learning', 'executive_functions', 'social_cognition']:
    for _, fn_name in BENCHMARKS[track]:
        NON_META.append(fn_name)

# Known slow benchmarks - run last with longer timeout
SLOW_BENCHMARKS = {"learning_curves", "exec_func_nback", "learning_transfer", "learning_interference", "learning_curriculum"}
SLOW_TIMEOUT = 600

def safe_name(model_id):
    return model_id.replace(':', '_').replace('/', '_')

def load_results(model_id):
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    label = MODEL_CATALOG[model_id][0]
    return {"model": model_id, "model_label": label, "timestamp": "", "scores": {}}

def save_results(model_id, data):
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def run_single(model_id, bname, timeout):
    try:
        result = subprocess.run(
            [VENV_PYTHON, SINGLE_RUNNER, model_id, bname],
            capture_output=True, text=True, timeout=timeout, cwd=REPO
        )
        for line in (result.stdout or "").splitlines():
            if line.startswith("RESULT_JSON:"):
                return json.loads(line[len("RESULT_JSON:"):])
        err = (result.stderr or result.stdout or "no output")[-200:]
        return {"score": None, "error": f"no RESULT_JSON: {err}", "duration_s": 0}
    except subprocess.TimeoutExpired:
        return {"score": None, "error": f"TIMEOUT after {timeout}s", "duration_s": timeout}

def main():
    print(f"run_fast_nonmeta started at {datetime.now(timezone.utc).isoformat()}")
    
    # Build todo lists
    fast_todo = []
    slow_todo = []
    for mid in sorted(MODEL_CATALOG.keys()):
        data = load_results(mid)
        scores = data.get("scores", {})
        for b in NON_META:
            entry = scores.get(b)
            if entry is None or entry.get("score") is None:
                if b in SLOW_BENCHMARKS:
                    slow_todo.append((mid, b))
                else:
                    fast_todo.append((mid, b))
    
    print(f"Fast benchmarks to run: {len(fast_todo)}")
    print(f"Slow benchmarks to run: {len(slow_todo)}")
    
    todo = fast_todo + slow_todo
    print(f"Total: {len(todo)}\n")
    
    completed = 0
    errors = 0
    for i, (mid, bname) in enumerate(todo):
        label = MODEL_CATALOG[mid][0]
        timeout = SLOW_TIMEOUT if bname in SLOW_BENCHMARKS else TIMEOUT
        print(f"[{i+1}/{len(todo)}] {label} × {bname} (timeout={timeout}s)...", flush=True)
        result = run_single(mid, bname, timeout)
        
        data = load_results(mid)
        data.setdefault("scores", {})[bname] = result
        save_results(mid, data)
        
        score = result.get("score")
        dur = result.get("duration_s", 0)
        if score is not None:
            print(f"  score={score:.4f} ({dur}s)")
            completed += 1
        else:
            print(f"  ERROR: {(result.get('error','unknown'))[:100]} ({dur}s)")
            errors += 1
        
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"DONE: {completed} completed, {errors} errors out of {len(todo)}")

if __name__ == "__main__":
    main()
