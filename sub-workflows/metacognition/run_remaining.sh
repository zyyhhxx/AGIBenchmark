#!/bin/bash
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
source .venv/bin/activate

MODELS=(
    "anthropic.claude-sonnet-4-6"
    "qwen.qwen3-next-80b-a3b"
    "openai.gpt-oss-120b-1:0"
    "zai.glm-4.7"
    "deepseek.r1-v1:0"
    "anthropic.claude-opus-4-6-v1"
)

for m in "${MODELS[@]}"; do
    echo "========== Running: $m =========="
    python3 sub-workflows/metacognition/run_single.py "$m"
    echo ""
done

echo "========== ALL DONE =========="
