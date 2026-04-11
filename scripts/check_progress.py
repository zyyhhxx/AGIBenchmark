#!/usr/bin/env python3
"""Check progress of all 10 model benchmark runs."""
import json, os, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO, "results")

MODELS = {
    "anthropic.claude-opus-4-6-v1": "Claude Opus 4.6",
    "deepseek.r1-v1_0": "DeepSeek-R1",
    "openai.gpt-oss-120b-1_0": "GPT-OSS-120B",
    "meta.llama3-3-70b-instruct-v1_0": "Llama 3.3 70B",
    "qwen.qwen3-next-80b-a3b": "Qwen3 Next 80B",
    "amazon.nova-pro-v1_0": "Nova Pro",
    "meta.llama4-maverick-17b-instruct-v1_0": "Llama 4 Maverick 17B",
    "anthropic.claude-sonnet-4-6": "Claude Sonnet 4.6",
    "zai.glm-4.7": "GLM 4.7",
    "mistral.ministral-3-3b-instruct": "Ministral 3B",
}

total_complete = 0
for safe_name, label in sorted(MODELS.items(), key=lambda x: x[1]):
    path = os.path.join(RESULTS_DIR, f"{safe_name}.json")
    if os.path.exists(path):
        d = json.load(open(path))
        n = len(d.get('scores', {}))
        errs = sum(1 for v in d['scores'].values() if v.get('error'))
        status = "✅ DONE" if n == 26 else f"⏳ {n}/26"
        if n == 26:
            total_complete += 1
        print(f"{label:30s} {status:>12s}  ({errs} errors)")
    else:
        print(f"{label:30s}    NO FILE")

# Check if processes still running
result = subprocess.run(['pgrep', '-f', 'run_benchmark_bedrock'], capture_output=True, text=True)
running = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0

print(f"\n{total_complete}/10 models complete | {running} processes still running")
if total_complete == 10:
    print("\n🎉 All models done! Run: .venv/bin/python3 scripts/generate_matrix.py")
