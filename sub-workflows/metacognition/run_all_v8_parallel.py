#!/usr/bin/env python3
"""
v8: Parallel runner — one subprocess per model, all 6 incomplete models run concurrently.
Each model subprocess runs its missing benchmarks sequentially via run_single.py.
"""
import json, os, subprocess, sys, time, csv, threading
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
TRACK_DIR = os.path.join(REPO, "sub-workflows/metacognition")
RESULTS_DIR = os.path.join(TRACK_DIR, "results")
VENV_PYTHON = os.path.join(REPO, ".venv/bin/python3")
SINGLE_RUNNER = os.path.join(TRACK_DIR, "run_single.py")
TIMEOUT = 600  # 10 min per benchmark (reduced from 15)

sys.path.insert(0, REPO)
from scripts.run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS

ALL_BENCHMARKS = []
for track in BENCHMARKS:
    for _, fn_name in BENCHMARKS[track]:
        ALL_BENCHMARKS.append(fn_name)

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

def save_results(model_id, data):
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def run_single(model_id, bname):
    try:
        result = subprocess.run(
            [VENV_PYTHON, SINGLE_RUNNER, model_id, bname],
            capture_output=True, text=True, timeout=TIMEOUT, cwd=REPO
        )
        for line in (result.stdout or "").splitlines():
            if line.startswith("RESULT_JSON:"):
                return json.loads(line[len("RESULT_JSON:"):])
        err = (result.stderr or result.stdout or "no output")[-200:]
        return {"score": None, "error": f"no RESULT_JSON: {err}", "duration_s": 0}
    except subprocess.TimeoutExpired:
        return {"score": None, "error": f"TIMEOUT after {TIMEOUT}s", "duration_s": TIMEOUT}

def run_model(model_id, missing_benchmarks):
    """Run all missing benchmarks for one model sequentially."""
    label = MODEL_CATALOG[model_id][0]
    print(f"\n[{label}] Starting {len(missing_benchmarks)} benchmarks", flush=True)
    
    for i, bname in enumerate(missing_benchmarks):
        print(f"  [{label}] [{i+1}/{len(missing_benchmarks)}] {bname}...", end=" ", flush=True)
        result = run_single(model_id, bname)
        
        # Thread-safe: each model writes its own file
        data = load_results(model_id)
        data.setdefault("scores", {})[bname] = result
        save_results(model_id, data)
        
        score = result.get("score")
        dur = result.get("duration_s", 0)
        if score is not None:
            print(f"score={score:.4f} ({dur:.0f}s)", flush=True)
        else:
            err = result.get("error", "unknown")
            print(f"ERROR: {err[:80]} ({dur:.0f}s)", flush=True)
        
        time.sleep(1)
    
    print(f"  [{label}] DONE — all benchmarks complete", flush=True)

def generate_matrix():
    models = sorted(MODEL_CATALOG.keys())
    rows = []
    for bname in ALL_BENCHMARKS:
        row = {"benchmark": bname}
        for mid in models:
            data = load_results(mid)
            scores = data.get("scores", {})
            if bname in scores:
                s = scores[bname].get("score")
                row[mid] = s if s is not None else "ERROR"
            else:
                row[mid] = "MISSING"
        rows.append(row)
    outpath = os.path.join(RESULTS_DIR, "score_matrix.csv")
    with open(outpath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["benchmark"] + models)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {outpath} ({len(rows)} benchmarks x {len(models)} models)")

def main():
    print(f"run_all_v8_parallel started at {datetime.now(timezone.utc).isoformat()}")
    print(f"Models: {len(MODEL_CATALOG)}, Benchmarks: {len(ALL_BENCHMARKS)}")
    
    incomplete = {}
    for mid in MODEL_CATALOG:
        data = load_results(mid)
        done = set(data.get("scores", {}).keys())
        missing = [b for b in ALL_BENCHMARKS if b not in done]
        if missing:
            incomplete[mid] = missing
        else:
            print(f"SKIP {MODEL_CATALOG[mid][0]}: all {len(ALL_BENCHMARKS)} done")

    if not incomplete:
        print("\nAll models complete!")
        generate_matrix()
        return

    total = sum(len(m) for m in incomplete.values())
    print(f"\n{len(incomplete)} models incomplete, {total} total benchmarks to run")
    print(f"Running ALL models in parallel...\n")

    threads = []
    for mid, missing in incomplete.items():
        t = threading.Thread(target=run_model, args=(mid, missing), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Final status
    print(f"\n{'='*60}")
    print("FINAL STATUS")
    print(f"{'='*60}")
    for mid in sorted(MODEL_CATALOG.keys()):
        data = load_results(mid)
        n = len(data.get("scores", {}))
        label = MODEL_CATALOG[mid][0]
        valid = sum(1 for s in data.get("scores", {}).values() if s.get("score") is not None)
        errors = n - valid
        print(f"  {label:30s} {n}/{len(ALL_BENCHMARKS)} ({valid} ok, {errors} errors)")

    generate_matrix()
    print(f"\nCompleted at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    main()
