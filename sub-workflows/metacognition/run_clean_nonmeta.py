#!/usr/bin/env python3
"""Run missing non-meta benchmarks one at a time. Kills orphans before each run."""
import json, os, signal, subprocess, sys, time, psutil
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
VENV_PYTHON = os.path.join(REPO, ".venv/bin/python3")
SINGLE_RUNNER = os.path.join(REPO, "sub-workflows/metacognition/run_single.py")

sys.path.insert(0, REPO)
from scripts.run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS

NON_META = []
for track in ['attention', 'learning', 'executive_functions', 'social_cognition']:
    for _, fn_name in BENCHMARKS[track]:
        NON_META.append(fn_name)

# Time limits per benchmark type
TIMEOUTS = {
    "learning_curves": 600,
    "exec_func_nback": 600,
    "learning_transfer": 400,
    "learning_interference": 400,
    "learning_curriculum": 400,
    "social_cog_false_belief": 400,
    "social_cog_pragmatic": 400,
}
DEFAULT_TIMEOUT = 300

def kill_benchmark_orphans():
    """Kill any leftover benchmark subprocess python processes."""
    killed = 0
    my_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmd = ' '.join(proc.info['cmdline'] or [])
            if 'run_single.py' in cmd or ('run_benchmark_bedrock.py' in cmd and '--benchmark' in cmd):
                if proc.pid != my_pid:
                    proc.kill()
                    killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if killed:
        print(f"  [cleanup] killed {killed} orphan process(es)")
        time.sleep(1)

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

def run_single(model_id, bname):
    timeout = TIMEOUTS.get(bname, DEFAULT_TIMEOUT)
    kill_benchmark_orphans()
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
    print(f"run_clean_nonmeta started at {datetime.now(timezone.utc).isoformat()}")
    kill_benchmark_orphans()
    
    # Build todo list: fast first, slow models (deepseek, qwen) last
    fast_models = [m for m in MODEL_CATALOG if m not in {"deepseek.r1-v1:0", "qwen.qwen3-next-80b-a3b"}]
    slow_models = ["deepseek.r1-v1:0", "qwen.qwen3-next-80b-a3b"]
    
    todo = []
    for mid in fast_models + slow_models:
        data = load_results(mid)
        scores = data.get("scores", {})
        for b in NON_META:
            if scores.get(b) is None or scores[b].get("score") is None:
                todo.append((mid, b))
    
    print(f"Total missing: {len(todo)}\n")
    
    completed = errors = 0
    for i, (mid, bname) in enumerate(todo):
        label = MODEL_CATALOG[mid][0]
        timeout = TIMEOUTS.get(bname, DEFAULT_TIMEOUT)
        print(f"[{i+1}/{len(todo)}] {label} × {bname} (t={timeout}s)...", flush=True)
        result = run_single(mid, bname)
        
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
        
        time.sleep(2)
    
    print(f"\nDONE: {completed} completed, {errors} errors / {len(todo)} total")

if __name__ == "__main__":
    main()
