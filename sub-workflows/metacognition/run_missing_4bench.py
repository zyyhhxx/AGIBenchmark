#!/usr/bin/env python3
"""Run the 4 failing benchmarks for all missing model combinations."""
import json, os, sys, subprocess, time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS_DIR = os.path.join(REPO, "results")
VENV_PYTHON = os.path.join(REPO, ".venv", "bin", "python3")
RUNNER = os.path.join(REPO, "scripts", "run_benchmark_bedrock.py")

MODEL_IDS = [
    "anthropic.claude-opus-4-6-v1",
    "anthropic.claude-sonnet-4-6",
    "deepseek.r1-v1:0",
    "zai.glm-4.7",
    "openai.gpt-oss-120b-1:0",
    "meta.llama3-3-70b-instruct-v1:0",
    "meta.llama4-maverick-17b-instruct-v1:0",
    "mistral.ministral-3-3b-instruct",
    "amazon.nova-pro-v1:0",
    "qwen.qwen3-next-80b-a3b",
]

MODEL_FILES = {
    "anthropic.claude-opus-4-6-v1": "anthropic.claude-opus-4-6-v1.json",
    "anthropic.claude-sonnet-4-6": "anthropic.claude-sonnet-4-6.json",
    "deepseek.r1-v1:0": "deepseek.r1-v1_0.json",
    "zai.glm-4.7": "zai.glm-4.7.json",
    "openai.gpt-oss-120b-1:0": "openai.gpt-oss-120b-1_0.json",
    "meta.llama3-3-70b-instruct-v1:0": "meta.llama3-3-70b-instruct-v1_0.json",
    "meta.llama4-maverick-17b-instruct-v1:0": "meta.llama4-maverick-17b-instruct-v1_0.json",
    "mistral.ministral-3-3b-instruct": "mistral.ministral-3-3b-instruct.json",
    "amazon.nova-pro-v1:0": "amazon.nova-pro-v1_0.json",
    "qwen.qwen3-next-80b-a3b": "qwen.qwen3-next-80b-a3b.json",
}

BENCHMARKS = ["attention_selective", "learning_curves", "social_cog_emotional_prosody", "metacog_error_detection"]

def is_missing(model_id, bench):
    fname = MODEL_FILES[model_id]
    path = os.path.join(RESULTS_DIR, fname)
    if not os.path.exists(path):
        return True
    with open(path) as f:
        d = json.load(f)
    s = d.get("scores", {}).get(bench)
    return s is None or s.get("score") is None

def main():
    # Build work list
    work = []
    for bench in BENCHMARKS:
        for model_id in MODEL_IDS:
            if is_missing(model_id, bench):
                work.append((bench, model_id))
    
    print(f"Total missing: {len(work)} model-benchmark combinations")
    for i, (bench, model_id) in enumerate(work):
        print(f"  [{i+1}] {bench} x {model_id}")
    
    print(f"\nStarting sequential runs...")
    completed = 0
    failed = 0
    
    for i, (bench, model_id) in enumerate(work):
        print(f"\n{'='*70}")
        print(f"[{i+1}/{len(work)}] Running {bench} with {model_id}")
        print(f"{'='*70}")
        sys.stdout.flush()
        
        start = time.time()
        try:
            result = subprocess.run(
                [VENV_PYTHON, RUNNER, "--model", model_id, "--benchmark", bench],
                cwd=REPO,
                timeout=900,  # 15 min timeout for learning_curves
                capture_output=False,
            )
            elapsed = time.time() - start
            if result.returncode == 0:
                completed += 1
                print(f"  ✅ Completed in {elapsed:.0f}s")
            else:
                failed += 1
                print(f"  ❌ Failed (rc={result.returncode}) in {elapsed:.0f}s")
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            failed += 1
            print(f"  ⏰ Timed out after {elapsed:.0f}s")
        except Exception as e:
            failed += 1
            print(f"  ❌ Error: {e}")
        
        sys.stdout.flush()
        time.sleep(2)  # brief pause between runs
    
    print(f"\n{'='*70}")
    print(f"DONE: {completed} completed, {failed} failed out of {len(work)}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
