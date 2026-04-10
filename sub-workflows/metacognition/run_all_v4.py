#!/usr/bin/env python3
"""
Run all benchmarks across all models using subprocess with per-benchmark timeout.
Each benchmark runs as a separate subprocess to avoid hanging.
"""
import json, os, sys, subprocess, time
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
PYTHON = f"{REPO}/.venv/bin/python3"
SCRIPT = f"{REPO}/scripts/run_benchmark_bedrock.py"
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
os.makedirs(RESULTS_DIR, exist_ok=True)

BENCHMARK_TIMEOUT = 300  # 5 min per benchmark

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

MODEL_LABELS = {
    "mistral.ministral-3-3b-instruct": "Ministral 3B",
    "meta.llama4-maverick-17b-instruct-v1:0": "Llama 4 Maverick 17B",
    "meta.llama3-3-70b-instruct-v1:0": "Llama 3.3 70B",
    "amazon.nova-pro-v1:0": "Nova Pro",
    "openai.gpt-oss-120b-1:0": "GPT-OSS-120B",
    "qwen.qwen3-next-80b-a3b": "Qwen3 Next 80B",
    "deepseek.r1-v1:0": "DeepSeek-R1",
    "zai.glm-4.7": "GLM 4.7",
    "anthropic.claude-sonnet-4-6": "Claude Sonnet 4.6",
    "anthropic.claude-opus-4-6-v1": "Claude Opus 4.6",
}

# All benchmarks by track
ALL_BENCHMARKS = [
    "metacog_canary", "metacog_fok", "metacog_jol", "metacog_calibration",
    "metacog_error_detection", "metacog_learning_monitoring", "metacog_control",
    "metacog_epistemic_revision", "metacog_epistemic_humility",
    "learning_curves", "learning_transfer", "learning_interference", "learning_curriculum",
    "attention_selective", "attention_vigilance", "attention_divided", "attention_instruction_update",
    "exec_func_wcst", "exec_func_tol", "exec_func_task_switch", "exec_func_nback", "exec_func_crt",
    "social_cog_false_belief", "social_cog_pragmatic", "social_cog_sarcasm", "social_cog_emotional_prosody",
]

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
    return {"model": model_id, "model_label": MODEL_LABELS.get(model_id, model_id),
            "timestamp": "", "scores": {}}

def save_results(data):
    model_id = data["model"]
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(RESULTS_DIR, f"{safe_name(model_id)}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def run_single_benchmark(model_id, benchmark_name):
    """Run one benchmark for one model via subprocess. Returns (score, error, duration)."""
    cmd = [PYTHON, SCRIPT, "--model", model_id, "--benchmark", benchmark_name,
           "--output-dir", "/tmp/bench_scratch"]
    os.makedirs("/tmp/bench_scratch", exist_ok=True)
    
    start = time.time()
    try:
        result = subprocess.run(cmd, timeout=BENCHMARK_TIMEOUT, capture_output=True,
                                text=True, cwd=REPO)
        elapsed = time.time() - start
        
        # Parse score from output
        output = result.stdout + result.stderr
        score = None
        for line in output.split('\n'):
            if 'Score:' in line:
                try:
                    score = float(line.split('Score:')[1].strip())
                except:
                    pass
        
        # Also try to read from scratch output
        if score is None:
            scratch_file = f"/tmp/bench_scratch/{safe_name(model_id)}.json"
            if os.path.exists(scratch_file):
                try:
                    with open(scratch_file) as f:
                        d = json.load(f)
                    scores = d.get("scores", {})
                    if benchmark_name in scores:
                        entry = scores[benchmark_name]
                        score = entry.get("score")
                        if score is None:
                            return None, entry.get("error", "unknown error"), elapsed
                except:
                    pass
        
        if score is not None:
            return score, None, elapsed
        
        if result.returncode != 0:
            # Extract error from output
            err_lines = [l for l in output.split('\n') if 'ERROR' in l or 'Error' in l or 'error' in l]
            error = err_lines[-1][:200] if err_lines else f"exit code {result.returncode}"
            return None, error, elapsed
        
        return None, "no score found in output", elapsed
        
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        return None, f"timeout after {BENCHMARK_TIMEOUT}s", elapsed

def main():
    print(f"Starting run_all_v4 at {datetime.now(timezone.utc).isoformat()}")
    print(f"Models: {len(MODELS)}, Benchmarks: {len(ALL_BENCHMARKS)}")
    print(f"Per-benchmark timeout: {BENCHMARK_TIMEOUT}s")
    sys.stdout.flush()
    
    for mi, model_id in enumerate(MODELS):
        label = MODEL_LABELS.get(model_id, model_id)
        data = load_results(model_id)
        scores = data["scores"]
        
        remaining = [b for b in ALL_BENCHMARKS if b not in scores]
        if not remaining:
            print(f"\n[{mi+1}/{len(MODELS)}] SKIP {label}: all {len(scores)} done")
            sys.stdout.flush()
            continue
        
        print(f"\n[{mi+1}/{len(MODELS)}] {label}: {len(scores)} done, {len(remaining)} remaining")
        sys.stdout.flush()
        
        for bi, bench in enumerate(remaining):
            print(f"  [{bi+1}/{len(remaining)}] {bench}...", end=" ", flush=True)
            score, error, duration = run_single_benchmark(model_id, bench)
            
            scores[bench] = {
                "score": score,
                "error": error,
                "duration_s": round(duration, 1),
            }
            
            if score is not None:
                print(f"score={score:.4f} ({duration:.0f}s)")
            else:
                print(f"ERROR: {(error or '')[:60]} ({duration:.0f}s)")
            sys.stdout.flush()
            
            # Save after every benchmark
            data["scores"] = scores
            save_results(data)
            
            time.sleep(2)
        
        print(f"  → {label} complete: {len(scores)} benchmarks")
        sys.stdout.flush()
        time.sleep(5)
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    for model_id in MODELS:
        label = MODEL_LABELS.get(model_id, model_id)
        data = load_results(model_id)
        scores = data["scores"]
        valid = [s["score"] for s in scores.values() if s.get("score") is not None]
        errors = sum(1 for s in scores.values() if s.get("error") is not None)
        avg = sum(valid)/len(valid) if valid else 0
        print(f"  {label:30s}  avg={avg:.4f}  ok={len(valid)}/{len(scores)}  errors={errors}")
    
    print(f"\nCompleted at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    main()
