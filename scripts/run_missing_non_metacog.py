#!/usr/bin/env python3
"""Run only missing non-metacognition benchmark/model combinations, ≤4 concurrent."""
import json, os, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO, "results")
RUNNER = os.path.join(REPO, "scripts", "run_benchmark_bedrock.py")
PYTHON = os.path.join(REPO, ".venv", "bin", "python3")

NON_METACOG_BENCHMARKS = [
    'learning_curves', 'learning_transfer', 'learning_interference', 'learning_curriculum',
    'attention_selective', 'attention_vigilance', 'attention_divided', 'attention_instruction_update',
    'exec_func_wcst', 'exec_func_tol', 'exec_func_task_switch', 'exec_func_nback', 'exec_func_crt',
    'social_cog_false_belief', 'social_cog_pragmatic', 'social_cog_sarcasm', 'social_cog_emotional_prosody',
]

MODELS = [
    'anthropic.claude-opus-4-6-v1', 'deepseek.r1-v1:0', 'openai.gpt-oss-120b-1:0',
    'meta.llama3-3-70b-instruct-v1:0', 'qwen.qwen3-next-80b-a3b', 'amazon.nova-pro-v1:0',
    'meta.llama4-maverick-17b-instruct-v1:0', 'anthropic.claude-sonnet-4-6',
    'zai.glm-4.7', 'mistral.ministral-3-3b-instruct',
]

def get_missing(model_id):
    safe = model_id.replace(':', '_').replace('/', '_')
    path = os.path.join(RESULTS_DIR, f"{safe}.json")
    if not os.path.exists(path):
        return NON_METACOG_BENCHMARKS[:]
    with open(path) as f:
        data = json.load(f)
    scores = data.get('scores', {})
    missing = []
    for b in NON_METACOG_BENCHMARKS:
        if b not in scores or scores[b].get('score') is None:
            missing.append(b)
    return missing

def run_one(model_id, benchmark):
    """Run a single model+benchmark combo."""
    print(f"[START] {model_id} × {benchmark}")
    try:
        result = subprocess.run(
            [PYTHON, RUNNER, "--model", model_id, "--benchmark", benchmark],
            capture_output=True, text=True, timeout=600, cwd=REPO
        )
        # Check output for score
        for line in result.stdout.split('\n'):
            if 'Score:' in line:
                print(f"[DONE]  {model_id} × {benchmark}: {line.strip()}")
                return (model_id, benchmark, "ok", line.strip())
            if 'ERROR:' in line:
                print(f"[ERR]   {model_id} × {benchmark}: {line.strip()}")
                return (model_id, benchmark, "error", line.strip())
        print(f"[DONE]  {model_id} × {benchmark}: completed (check results json)")
        return (model_id, benchmark, "ok", "")
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {model_id} × {benchmark}")
        return (model_id, benchmark, "timeout", "")
    except Exception as e:
        print(f"[FAIL]  {model_id} × {benchmark}: {e}")
        return (model_id, benchmark, "fail", str(e))

def main():
    # Build work queue
    work = []
    for model in MODELS:
        missing = get_missing(model)
        if missing:
            print(f"{model}: {len(missing)} missing benchmarks")
            for b in missing:
                work.append((model, b))
        else:
            print(f"{model}: complete ✓")
    
    print(f"\nTotal runs needed: {len(work)}")
    if not work:
        print("All done!")
        return
    
    # Run with ≤4 concurrent processes
    results = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(run_one, m, b): (m, b) for m, b in work}
        for fut in as_completed(futures):
            results.append(fut.result())
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    ok = sum(1 for r in results if r[2] == "ok")
    err = sum(1 for r in results if r[2] != "ok")
    print(f"Completed: {ok}/{len(results)}, Errors: {err}")
    for r in results:
        if r[2] != "ok":
            print(f"  FAILED: {r[0]} × {r[1]}: {r[2]} - {r[3]}")

if __name__ == "__main__":
    main()
