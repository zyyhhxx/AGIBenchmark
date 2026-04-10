#!/usr/bin/env python3
"""
v12: Fill gaps in benchmark results. Fixes import issues by running each
benchmark in a subprocess with cwd set to the correct track directory.
"""
import json, os, sys, time, subprocess, tempfile
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
PYTHON = os.path.join(REPO, ".venv/bin/python3")
BENCHMARK_TIMEOUT = 600  # 10 min per benchmark
DELAY_BETWEEN = 2  # seconds between benchmarks

# The subprocess runner script — written to a temp file
RUNNER_SCRIPT = r'''
import json, sys, os, time

REPO = sys.argv[1]
model_id = sys.argv[2]
task_file = sys.argv[3]  # absolute path to task_*.py
fn_name = sys.argv[4]
out_file = sys.argv[5]

# Add repo root and track dir to sys.path
sys.path.insert(0, REPO)
track_dir = os.path.dirname(task_file)
sys.path.insert(0, track_dir)
os.chdir(track_dir)

from scripts.run_benchmark_bedrock import MODEL_CATALOG, setup_kbench_mocks, create_bedrock_llm

setup_kbench_mocks()
entry = MODEL_CATALOG[model_id]
invoke_id = entry[1]
llm = create_bedrock_llm(invoke_id)

# Use runpy to load the task file directly (avoids package import issues)
import runpy
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


def safe_name(model_id):
    return model_id.replace(':', '_').replace('/', '_')


def load_results(model_id):
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"model": model_id, "model_label": "", "timestamp": "", "scores": {}}


def save_results(data):
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(RESULTS_DIR, f"{safe_name(data['model'])}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def needs_run(score_entry):
    """Returns True if this benchmark needs to be (re)run."""
    if score_entry is None:
        return True
    if score_entry.get("score") is not None:
        return False  # already has a score
    err = score_entry.get("error", "") or ""
    # Don't retry ValidationException (model access denied)
    if "ValidationException" in err:
        return False
    return True


def find_task_file(mod_path):
    """Convert module path like 'benchmarks.metacognition.task_fok' to absolute file path."""
    parts = mod_path.split('.')
    return os.path.join(REPO, *parts) + '.py'


def run_single(model_id, task_file, fn_name, runner_file):
    """Run one benchmark for one model. Returns result dict."""
    out_file = f"/tmp/_v12_{safe_name(model_id)}_{fn_name}.json"
    if os.path.exists(out_file):
        os.unlink(out_file)

    try:
        proc = subprocess.run(
            [PYTHON, runner_file, REPO, model_id, task_file, fn_name, out_file],
            timeout=BENCHMARK_TIMEOUT,
            capture_output=True, text=True
        )
        if os.path.exists(out_file):
            with open(out_file) as f:
                result = json.load(f)
            os.unlink(out_file)
            return result
        else:
            stderr = proc.stderr[-300:] if proc.stderr else ""
            stdout = proc.stdout[-300:] if proc.stdout else ""
            return {"score": None, "error": f"exit {proc.returncode}: {stderr or stdout}", "duration_s": 0}
    except subprocess.TimeoutExpired:
        return {"score": None, "error": f"timeout ({BENCHMARK_TIMEOUT}s)", "duration_s": BENCHMARK_TIMEOUT}


def generate_score_matrix():
    """Generate score_matrix.csv from all result files."""
    sys.path.insert(0, REPO)
    from scripts.run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS

    all_fns = []
    for track in BENCHMARKS:
        for mp, fn in BENCHMARKS[track]:
            all_fns.append(fn)

    models = list(MODEL_CATALOG.items())
    header = ["benchmark"] + [label for _, (label, _) in models]

    rows = [",".join(header)]
    for fn in all_fns:
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
    print(f"\nWrote {csv_path} ({len(all_fns)} benchmarks × {len(models)} models)")


def main():
    sys.path.insert(0, REPO)
    from scripts.run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS

    all_benchmarks = []
    for track in BENCHMARKS:
        for mp, fn in BENCHMARKS[track]:
            all_benchmarks.append((mp, fn))

    # Write runner script to temp file
    runner_file = "/tmp/_v12_runner.py"
    with open(runner_file, 'w') as f:
        f.write(RUNNER_SCRIPT)

    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"run_fill_v12 started at {datetime.now(timezone.utc).isoformat()}", flush=True)
    print(f"Benchmarks: {len(all_benchmarks)}, Models: {len(MODEL_CATALOG)}", flush=True)

    if target == "all":
        models = list(MODEL_CATALOG.items())
    else:
        models = [(target, MODEL_CATALOG[target])]

    total_ran = 0
    total_ok = 0
    start_time = time.time()

    for mi, (model_id, (label, _)) in enumerate(models):
        data = load_results(model_id)
        data["model_label"] = label
        scores = data.get("scores", {})

        gaps = [(mp, fn) for mp, fn in all_benchmarks if needs_run(scores.get(fn))]
        if not gaps:
            ok = sum(1 for fn in [fn for _, fn in all_benchmarks] if scores.get(fn, {}).get("score") is not None) if scores else 0
            print(f"\n[{mi+1}/{len(models)}] {label}: no gaps ({ok}/26 scored)", flush=True)
            continue

        print(f"\n[{mi+1}/{len(models)}] {label}: {len(gaps)} gaps to fill", flush=True)

        for bi, (mod_path, fn_name) in enumerate(gaps):
            task_file = find_task_file(mod_path)
            if not os.path.exists(task_file):
                print(f"  [{bi+1}/{len(gaps)}] {fn_name}: SKIP (file not found: {task_file})", flush=True)
                continue

            print(f"  [{bi+1}/{len(gaps)}] {fn_name}...", end=" ", flush=True)
            result = run_single(model_id, task_file, fn_name, runner_file)
            total_ran += 1

            scores[fn_name] = result
            data["scores"] = scores
            save_results(data)

            if result.get("score") is not None:
                total_ok += 1
                print(f"score={result['score']:.4f} ({result['duration_s']}s)", flush=True)
            else:
                err = (result.get("error") or "")[:80]
                print(f"ERROR: {err}", flush=True)

            time.sleep(DELAY_BETWEEN)

    elapsed = time.time() - start_time
    print(f"\n{'='*60}", flush=True)
    print(f"Completed in {elapsed/60:.1f} min. Ran {total_ran} benchmarks, {total_ok} succeeded.", flush=True)

    # Print summary
    print("\nSUMMARY:", flush=True)
    for mid, (label, _) in MODEL_CATALOG.items():
        data = load_results(mid)
        scores = data.get("scores", {})
        ok = sum(1 for _, fn in all_benchmarks if scores.get(fn, {}).get("score") is not None) if scores else 0
        errs = sum(1 for _, fn in all_benchmarks if fn in scores and scores[fn] is not None and scores[fn].get("score") is None) if scores else 0
        print(f"  {label:30s} scored={ok:2d}/26  errors={errs:2d}", flush=True)

    # Generate score matrix
    generate_score_matrix()


if __name__ == "__main__":
    main()
