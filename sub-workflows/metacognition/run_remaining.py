#!/usr/bin/env python3
"""Run remaining missing non-metacognition benchmarks for Qwen3 Next 80B."""
import subprocess, sys, time, json, os

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
VENV_PYTHON = f"{REPO}/.venv/bin/python3"
RUNNER = f"{REPO}/scripts/run_benchmark_bedrock.py"
RESULTS_FILE = f"{REPO}/results/qwen.qwen3-next-80b-a3b.json"
TIMEOUT = 600  # 10 min per benchmark

MODEL = "qwen.qwen3-next-80b-a3b"
MISSING = [
    "exec_func_nback", "exec_func_task_switch", "exec_func_tol",
    "learning_curves", "social_cog_emotional_prosody",
    "social_cog_false_belief", "social_cog_pragmatic"
]

for i, bm in enumerate(MISSING):
    # Check if already done (in case of restart)
    with open(RESULTS_FILE) as f:
        data = json.load(f)
    if bm in data.get("scores", {}) and not data["scores"][bm].get("error"):
        print(f"[{i+1}/{len(MISSING)}] {bm} already complete, skipping")
        continue
    
    print(f"[{i+1}/{len(MISSING)}] Running {MODEL} × {bm}...", flush=True)
    t0 = time.time()
    try:
        result = subprocess.run(
            [VENV_PYTHON, RUNNER, "--model", MODEL, "--benchmark", bm],
            capture_output=True, text=True, timeout=TIMEOUT, cwd=REPO
        )
        elapsed = time.time() - t0
        # Re-read results file to get score
        with open(RESULTS_FILE) as f:
            data = json.load(f)
        score_data = data.get("scores", {}).get(bm, {})
        score = score_data.get("score", "N/A") if isinstance(score_data, dict) else score_data
        print(f"  ✓ score={score} ({elapsed:.1f}s)", flush=True)
        if result.returncode != 0:
            print(f"  stderr: {result.stderr[-200:]}", flush=True)
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        print(f"  ✗ TIMEOUT after {elapsed:.1f}s", flush=True)
    except Exception as e:
        print(f"  ✗ ERROR: {e}", flush=True)

print("\nAll done!", flush=True)
