#!/usr/bin/env python3
"""
Run all benchmarks against all 10 models SEQUENTIALLY with incremental saves.
Resumes from where it left off by checking existing result files.
"""
import json, os, sys, time, subprocess
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
PYTHON = f"{REPO}/.venv/bin/python3"
SCRIPT = f"{REPO}/scripts/run_benchmark_bedrock.py"
RESULTS_DIR = f"{REPO}/sub-workflows/metacognition/results"

MODELS = [
    "mistral.ministral-3-3b-instruct",
    "meta.llama4-maverick-17b-instruct-v1:0",
    "meta.llama3-3-70b-instruct-v1:0",
    "amazon.nova-pro-v1:0",
    "openai.gpt-oss-120b-1:0",
    "qwen.qwen3-next-80b-a3b",
    "deepseek.r1-v1:0",
    "zai.glm-4.7",
    "anthropic.claude-sonnet-4-6",
    "anthropic.claude-opus-4-6-v1",
]

EXPECTED_BENCHMARKS = 26  # actual count per KNOWLEDGE.md

os.makedirs(RESULTS_DIR, exist_ok=True)

def safe_name(model_id):
    return model_id.replace(':', '_').replace('/', '_')

def get_completed(model_id):
    """Check how many benchmarks already completed for a model."""
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    if not os.path.exists(path):
        return 0
    try:
        with open(path) as f:
            d = json.load(f)
        return len(d.get("scores", {}))
    except:
        return 0

def run_model(model_id):
    """Run all benchmarks for one model."""
    completed = get_completed(model_id)
    if completed >= EXPECTED_BENCHMARKS:
        print(f"SKIP {model_id}: already has {completed} benchmarks")
        return True
    
    print(f"\n{'='*60}")
    print(f"RUNNING: {model_id} ({completed} already done, starting fresh)")
    print(f"Started: {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
    print(f"{'='*60}")
    
    cmd = [
        PYTHON, SCRIPT,
        "--model", model_id,
        "--track", "all",
        "--output-dir", RESULTS_DIR,
    ]
    
    start = time.time()
    try:
        result = subprocess.run(cmd, timeout=1800, capture_output=False)
        elapsed = time.time() - start
        new_count = get_completed(model_id)
        print(f"DONE: {model_id} → {new_count} benchmarks in {elapsed:.0f}s (exit={result.returncode})")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"TIMEOUT: {model_id} after {elapsed:.0f}s")
        return False
    except Exception as e:
        print(f"ERROR: {model_id} → {e}")
        return False

def main():
    print(f"Starting sequential run of {len(MODELS)} models")
    print(f"Results dir: {RESULTS_DIR}")
    
    results = {}
    for i, model_id in enumerate(MODELS):
        print(f"\n[{i+1}/{len(MODELS)}] {model_id}")
        ok = run_model(model_id)
        results[model_id] = ok
        
        # Brief pause between models
        if i < len(MODELS) - 1:
            time.sleep(3)
    
    # Summary
    print(f"\n{'='*60}")
    print("FINAL STATUS")
    print(f"{'='*60}")
    for model_id, ok in results.items():
        count = get_completed(model_id)
        status = "✓" if count >= EXPECTED_BENCHMARKS else f"partial ({count})"
        print(f"  {model_id:55s} → {status}")
    
    # List result files
    print(f"\nResult files:")
    for f in sorted(os.listdir(RESULTS_DIR)):
        if f.endswith('.json'):
            path = os.path.join(RESULTS_DIR, f)
            try:
                d = json.load(open(path))
                n = len(d.get("scores", {}))
                print(f"  {f}: {n} benchmarks")
            except:
                print(f"  {f}: (invalid)")

if __name__ == "__main__":
    main()
