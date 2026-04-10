#!/usr/bin/env python3
"""
v7: Run each benchmark as a SEPARATE SUBPROCESS with hard kill timeout.
Uses run_single.py which outputs RESULT_JSON:{...} to stdout.
"""
import json, os, subprocess, sys, time, csv
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
TRACK_DIR = os.path.join(REPO, "sub-workflows/metacognition")
RESULTS_DIR = os.path.join(TRACK_DIR, "results")
VENV_PYTHON = os.path.join(REPO, ".venv/bin/python3")
SINGLE_RUNNER = os.path.join(TRACK_DIR, "run_single.py")
TIMEOUT = 900  # 15 min hard kill (some benchmarks take 20+ min with multiple LLM calls)

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
    """Run one benchmark as subprocess, parse RESULT_JSON from stdout."""
    try:
        result = subprocess.run(
            [VENV_PYTHON, SINGLE_RUNNER, model_id, bname],
            capture_output=True, text=True, timeout=TIMEOUT, cwd=REPO
        )
        # Parse RESULT_JSON line from stdout
        for line in (result.stdout or "").splitlines():
            if line.startswith("RESULT_JSON:"):
                return json.loads(line[len("RESULT_JSON:"):])
        # No result line found
        err = (result.stderr or result.stdout or "no output")[-200:]
        return {"score": None, "error": f"no RESULT_JSON in output: {err}", "duration_s": 0}
    except subprocess.TimeoutExpired:
        return {"score": None, "error": f"TIMEOUT after {TIMEOUT}s", "duration_s": TIMEOUT}

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
    print(f"run_all_v7 started at {datetime.now(timezone.utc).isoformat()}")
    print(f"Models: {len(MODEL_CATALOG)}, Benchmarks: {len(ALL_BENCHMARKS)}")
    print(f"Per-benchmark subprocess timeout: {TIMEOUT}s\n")

    # Check status
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

    # Sort: fewest missing first
    ordered = sorted(incomplete.items(), key=lambda x: len(x[1]))
    total_remaining = sum(len(m) for m in incomplete.values())
    print(f"\n{len(incomplete)} models incomplete, {total_remaining} total benchmarks to run\n")

    done_count = 0
    for mid, missing in ordered:
        label = MODEL_CATALOG[mid][0]
        n_done = len(ALL_BENCHMARKS) - len(missing)
        print(f"\n{'='*60}")
        print(f"{label}: {n_done}/{len(ALL_BENCHMARKS)} done, {len(missing)} remaining")
        print(f"{'='*60}")

        for i, bname in enumerate(missing):
            print(f"  [{i+1}/{len(missing)}] {bname}...", end=" ", flush=True)
            result = run_single(mid, bname)
            
            # Merge into existing results
            data = load_results(mid)
            data.setdefault("scores", {})[bname] = result
            save_results(mid, data)
            
            score = result.get("score")
            err = result.get("error")
            dur = result.get("duration_s", 0)
            if score is not None:
                print(f"score={score:.4f} ({dur}s)")
            else:
                print(f"ERROR: {(err or 'unknown')[:80]} ({dur}s)")
            
            done_count += 1
            time.sleep(2)

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

if __name__ == "__main__":
    main()
