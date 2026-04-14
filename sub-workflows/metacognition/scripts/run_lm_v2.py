#!/usr/bin/env python3
"""Run learning_monitoring v2 against all 10 Bedrock models sequentially."""
import subprocess, sys, os, json, time, csv
from datetime import datetime, timezone

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
VENV_PY = f"{REPO}/.venv/bin/python3"
RESULTS_DIR = "/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/metacognition/results"
OUTPUT_CSV = f"{RESULTS_DIR}/learning_monitoring_v2_scores.csv"
LOG_FILE = f"{RESULTS_DIR}/learning_monitoring_v2_run.log"

MODELS = [
    ("anthropic.claude-opus-4-6-v1", "Claude Opus 4.6", 300),
    ("anthropic.claude-sonnet-4-6", "Claude Sonnet 4.6", 300),
    ("deepseek.r1-v1:0", "DeepSeek-R1", 900),
    ("openai.gpt-oss-120b-1:0", "GPT-OSS-120B", 300),
    ("meta.llama3-3-70b-instruct-v1:0", "Llama 3.3 70B", 300),
    ("qwen.qwen3-next-80b-a3b", "Qwen3 Next 80B", 300),
    ("amazon.nova-pro-v1:0", "Nova Pro", 300),
    ("meta.llama4-maverick-17b-instruct-v1:0", "Llama 4 Maverick 17B", 300),
    ("zai.glm-4.7", "GLM 4.7", 600),
    ("mistral.ministral-3-3b-instruct", "Ministral 3B", 300),
]

os.makedirs(RESULTS_DIR, exist_ok=True)

results = []
with open(LOG_FILE, 'w') as log:
    for model_id, label, timeout in MODELS:
        print(f"\n{'='*60}")
        print(f"Running: {label} ({model_id}) timeout={timeout}s")
        print(f"{'='*60}")
        log.write(f"\n{'='*60}\n{label} ({model_id})\n{'='*60}\n")
        log.flush()
        
        start = time.time()
        try:
            cmd = [
                VENV_PY, f"{REPO}/scripts/run_benchmark_bedrock.py",
                "--model", model_id,
                "--benchmark", "metacog_learning_monitoring",
                "--timeout", str(timeout),
            ]
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout + 60,
                cwd=REPO, env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            elapsed = time.time() - start
            
            output = proc.stdout + proc.stderr
            log.write(output)
            log.flush()
            print(output[-2000:] if len(output) > 2000 else output)
            
            # Extract score from output
            score = None
            for line in output.split('\n'):
                if 'Composite score:' in line:
                    try:
                        score = float(line.split('Composite score:')[1].strip())
                    except:
                        pass
                # Also check JSON result
                if '"metacog_learning_monitoring"' in line and '"score"' in line:
                    try:
                        d = json.loads(line.strip())
                        score = d.get('score')
                    except:
                        pass
            
            # Check results JSON file
            if score is None:
                result_file = f"{REPO}/results/{model_id}.json"
                if os.path.exists(result_file):
                    with open(result_file) as f:
                        rd = json.load(f)
                    sc = rd.get('scores', {}).get('metacog_learning_monitoring', {})
                    score = sc.get('score')
            
            results.append({
                'model': model_id,
                'label': label,
                'score': score,
                'duration': round(elapsed, 1),
                'error': None if score is not None else 'no score extracted'
            })
            print(f"\n>>> {label}: score={score}, duration={elapsed:.0f}s")
            
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            results.append({'model': model_id, 'label': label, 'score': None, 'duration': round(elapsed, 1), 'error': 'timeout'})
            print(f"\n>>> {label}: TIMEOUT after {elapsed:.0f}s")
        except Exception as e:
            elapsed = time.time() - start
            results.append({'model': model_id, 'label': label, 'score': None, 'duration': round(elapsed, 1), 'error': str(e)})
            print(f"\n>>> {label}: ERROR {e}")
        
        # Brief pause between models
        time.sleep(3)

# Write CSV
with open(OUTPUT_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['model', 'label', 'score', 'duration', 'error'])
    w.writeheader()
    w.writerows(results)

print(f"\n{'='*60}")
print(f"ALL RESULTS SAVED TO: {OUTPUT_CSV}")
print(f"{'='*60}")
scores = [r['score'] for r in results if r['score'] is not None]
if scores:
    import numpy as np
    print(f"Scored: {len(scores)}/10 models")
    print(f"Scores: {scores}")
    print(f"Mean: {np.mean(scores):.4f}")
    print(f"Std:  {np.std(scores):.4f}")
    print(f"Range: {max(scores)-min(scores):.4f}")
    print(f"Min: {min(scores):.4f}, Max: {max(scores):.4f}")
