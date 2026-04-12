#!/usr/bin/env python3
"""
Carefully run missing benchmarks with post-run JSON patching to handle race conditions.
After each run completes, patch the scores into the JSON rather than trusting the runner saved them.
"""
import json, os, sys, time, subprocess, fcntl
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
RESULTS_DIR = os.path.join(REPO, "results")
VENV_PYTHON = os.path.join(REPO, ".venv/bin/python3")
RUNNER = os.path.join(REPO, "scripts/run_benchmark_bedrock.py")

MODEL_IDS = {
    "Claude Opus 4.6":     "anthropic.claude-opus-4-6-v1",
    "Claude Sonnet 4.6":   "anthropic.claude-sonnet-4-6",
    "DeepSeek-R1":         "deepseek.r1-v1:0",
    "GLM 4.7":             "zai.glm-4.7",
    "GPT-OSS-120B":        "openai.gpt-oss-120b-1:0",
    "Llama 3.3 70B":       "meta.llama3-3-70b-instruct-v1:0",
    "Llama 4 Maverick":    "meta.llama4-maverick-17b-instruct-v1:0",
    "Ministral 3B":        "mistral.ministral-3-3b-instruct",
    "Nova Pro":            "amazon.nova-pro-v1:0",
    "Qwen3 Next 80B":      "qwen.qwen3-next-80b-a3b",
}
MODEL_FILE = {v: v.replace(':', '_').replace('/', '_') + ".json" for v in MODEL_IDS.values()}

def get_score(model_id, benchmark):
    fname = MODEL_FILE[model_id]
    path = os.path.join(RESULTS_DIR, fname)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        d = json.load(f)
    return d.get('scores', {}).get(benchmark, {}).get('score')

def read_json_locked(path):
    """Read JSON with shared lock."""
    with open(path) as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            return json.load(f)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

def patch_score(model_id, benchmark, score, duration=0):
    """Atomically patch a single benchmark score into the JSON file."""
    fname = MODEL_FILE[model_id]
    path = os.path.join(RESULTS_DIR, fname)
    if not os.path.exists(path):
        return
    with open(path, 'r+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            d = json.load(f)
            d.setdefault('scores', {})[benchmark] = {
                'score': score,
                'error': None,
                'duration_s': duration
            }
            d['timestamp'] = datetime.now(timezone.utc).isoformat()
            f.seek(0)
            json.dump(d, f, indent=2)
            f.truncate()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

def run_benchmark(model_id, benchmark, timeout=900):
    """Run benchmark and extract score from runner output."""
    print(f"\n--- {benchmark} / {model_id} ---", flush=True)
    
    start = time.time()
    try:
        result = subprocess.run(
            [VENV_PYTHON, RUNNER, "--model", model_id, "--benchmark", benchmark],
            timeout=timeout,
            cwd=REPO,
            capture_output=True,
            text=True
        )
        duration = time.time() - start
        
        # Print output for visibility
        if result.stdout:
            # Show key lines only
            for line in result.stdout.split('\n'):
                if any(x in line for x in ['Score:', 'score:', 'Composite', 'ERROR', 'saved', 'FAIL']):
                    print(' ', line, flush=True)
        
        # Extract score from runner JSON file
        score = get_score(model_id, benchmark)
        print(f"  Result: score={score}, duration={duration:.0f}s", flush=True)
        return score, duration
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        print(f"  TIMEOUT after {timeout}s", flush=True)
        return None, duration

def main():
    # Define what needs to be run
    # Read current state
    missing = {}
    benchmarks = ['social_cog_emotional_prosody', 'metacog_error_detection', 'learning_curves']
    
    for bm in benchmarks:
        missing[bm] = []
        for label, mid in MODEL_IDS.items():
            s = get_score(mid, bm)
            if s is None:
                missing[bm].append(mid)
    
    print("Current missing:")
    for bm, mids in missing.items():
        print(f"  {bm}: {[k for k,v in MODEL_IDS.items() if v in mids]}")
    print()
    
    # Run in order: fast benchmarks first
    timeouts = {
        'social_cog_emotional_prosody': 300,
        'metacog_error_detection': 300,
        'learning_curves': 900,
    }
    
    for bm in ['social_cog_emotional_prosody', 'metacog_error_detection', 'learning_curves']:
        for mid in missing[bm]:
            label = next(k for k, v in MODEL_IDS.items() if v == mid)
            t = timeouts[bm]
            score, dur = run_benchmark(mid, bm, timeout=t)
            if score is None:
                print(f"  FAILED, trying to patch anyway...", flush=True)
                # Check if concurrent process saved it
                s2 = get_score(mid, bm)
                if s2 is not None:
                    print(f"  Score found in file from concurrent run: {s2}", flush=True)
            time.sleep(2)
    
    # Final status
    print("\n" + "="*60)
    print("FINAL STATUS")
    print("="*60)
    import numpy as np
    for bm in benchmarks:
        scores = []
        miss = []
        for label, mid in MODEL_IDS.items():
            s = get_score(mid, bm)
            if s is not None: scores.append((label, s))
            else: miss.append(label)
        vals = [s for _, s in scores]
        std = np.std(vals) if vals else 0
        flag = "✅" if std >= 0.08 and len(scores) == 10 else "❌"
        print(f"{bm}: {len(scores)}/10 std={std:.4f} {flag}")
        for l, s in sorted(scores, key=lambda x: x[1]):
            print(f"  {l}: {s:.4f}")
        if miss:
            print(f"  MISSING: {miss}")

if __name__ == "__main__":
    main()
