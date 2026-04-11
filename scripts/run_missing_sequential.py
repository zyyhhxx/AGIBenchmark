#!/usr/bin/env python3
"""Run missing non-metacognition benchmarks sequentially (one at a time to avoid OOM)."""
import json, os, subprocess, sys

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

def main():
    work = []
    for model in MODELS:
        missing = get_missing(model)
        if missing:
            print(f"{model}: {len(missing)} missing", flush=True)
            for b in missing:
                work.append((model, b))
        else:
            print(f"{model}: complete ✓", flush=True)
    
    print(f"\nTotal runs: {len(work)}\n", flush=True)
    
    ok = 0
    errs = 0
    for i, (model, bench) in enumerate(work):
        print(f"[{i+1}/{len(work)}] {model} × {bench}...", flush=True)
        try:
            result = subprocess.run(
                [PYTHON, RUNNER, "--model", model, "--benchmark", bench],
                capture_output=True, text=True, timeout=600, cwd=REPO
            )
            # Extract score line
            score_line = ""
            for line in result.stdout.split('\n'):
                if 'Score:' in line:
                    score_line = line.strip()
                    break
            if score_line:
                print(f"  {score_line}", flush=True)
                ok += 1
            elif 'ERROR' in result.stdout:
                for line in result.stdout.split('\n'):
                    if 'ERROR' in line:
                        print(f"  {line.strip()}", flush=True)
                        break
                errs += 1
            else:
                print(f"  done (no score line found)", flush=True)
                ok += 1
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT (600s)", flush=True)
            errs += 1
        except Exception as e:
            print(f"  FAIL: {e}", flush=True)
            errs += 1
    
    print(f"\n{'='*60}")
    print(f"DONE: {ok} ok, {errs} errors out of {len(work)} total")

if __name__ == "__main__":
    main()
