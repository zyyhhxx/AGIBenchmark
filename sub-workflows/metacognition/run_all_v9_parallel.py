#!/usr/bin/env python3
"""
v9: Parallel runner with reduced timeout (300s). Runs all incomplete models concurrently.
Each model runs its missing benchmarks sequentially in a subprocess.
Saves results incrementally. Generates score_matrix.csv at the end.
"""
import json, os, subprocess, sys, time, csv, threading
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
TRACK_DIR = os.path.join(REPO, "sub-workflows/metacognition")
RESULTS_DIR = os.path.join(TRACK_DIR, "results")
VENV_PYTHON = os.path.join(REPO, ".venv/bin/python3")
SINGLE_RUNNER = os.path.join(TRACK_DIR, "run_single.py")
TIMEOUT = 300  # 5 min per benchmark

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
        with open(path) as f:
            return json.load(f)
    label = MODEL_CATALOG[model_id][0]
    return {"model": model_id, "model_label": label, "timestamp": "", "scores": {}}

def save_results(model_id, data):
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def run_model(model_id, missing):
    label = MODEL_CATALOG[model_id][0]
    print(f"[{label}] Starting {len(missing)} benchmarks", flush=True)
    for i, bname in enumerate(missing):
        print(f"  [{label}] [{i+1}/{len(missing)}] {bname}...", end=" ", flush=True)
        t0 = time.time()
        try:
            result = subprocess.run(
                [VENV_PYTHON, SINGLE_RUNNER, model_id, bname],
                capture_output=True, text=True, timeout=TIMEOUT, cwd=REPO
            )
            found = None
            for line in (result.stdout or "").splitlines():
                if line.startswith("RESULT_JSON:"):
                    found = json.loads(line[len("RESULT_JSON:"):])
                    break
            if not found:
                err = (result.stderr or result.stdout or "no output")[-200:]
                found = {"score": None, "error": f"no RESULT_JSON: {err}", "duration_s": round(time.time()-t0,1)}
        except subprocess.TimeoutExpired:
            found = {"score": None, "error": f"TIMEOUT after {TIMEOUT}s", "duration_s": TIMEOUT}
        
        # Save incrementally (each model has its own file, thread-safe)
        data = load_results(model_id)
        data.setdefault("scores", {})[bname] = found
        save_results(model_id, data)
        
        s = found.get("score")
        d = found.get("duration_s", 0)
        if s is not None:
            print(f"score={s:.4f} ({d:.0f}s)", flush=True)
        else:
            print(f"ERROR: {str(found.get('error',''))[:60]} ({d:.0f}s)", flush=True)
        time.sleep(0.5)
    print(f"[{label}] DONE", flush=True)

def generate_score_matrix():
    print("\nGenerating score_matrix.csv...", flush=True)
    rows = []
    models = sorted(MODEL_CATALOG.keys())
    header = ["benchmark"] + [MODEL_CATALOG[m][0] for m in models]
    rows.append(header)
    for bname in ALL_BENCHMARKS:
        row = [bname]
        for m in models:
            data = load_results(m)
            entry = data.get("scores", {}).get(bname)
            if entry is None:
                row.append("MISSING")
            elif entry.get("score") is not None:
                row.append(str(round(entry["score"], 4)))
            else:
                row.append("ERROR")
        rows.append(row)
    path = os.path.join(RESULTS_DIR, "score_matrix.csv")
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"Saved {path} ({len(rows)-1} benchmarks x {len(models)} models)", flush=True)

if __name__ == "__main__":
    # Find incomplete models
    incomplete = {}
    for model_id in MODEL_CATALOG:
        data = load_results(model_id)
        scored = set(data.get("scores", {}).keys())
        missing = [b for b in ALL_BENCHMARKS if b not in scored]
        if missing:
            incomplete[model_id] = missing
    
    if not incomplete:
        print("All models complete!", flush=True)
        generate_score_matrix()
        sys.exit(0)
    
    total = sum(len(v) for v in incomplete.values())
    print(f"Incomplete: {len(incomplete)} models, {total} benchmarks total", flush=True)
    for m, missing in incomplete.items():
        print(f"  {MODEL_CATALOG[m][0]}: {len(missing)} missing", flush=True)
    
    # Launch all models in parallel threads
    threads = []
    for model_id, missing in incomplete.items():
        t = threading.Thread(target=run_model, args=(model_id, missing))
        t.start()
        threads.append(t)
        time.sleep(2)  # Stagger starts slightly
    
    for t in threads:
        t.join()
    
    # Summary
    print("\n=== FINAL STATUS ===", flush=True)
    for model_id in sorted(MODEL_CATALOG.keys()):
        data = load_results(model_id)
        n = len(data.get("scores", {}))
        print(f"  {MODEL_CATALOG[model_id][0]}: {n}/26", flush=True)
    
    generate_score_matrix()
