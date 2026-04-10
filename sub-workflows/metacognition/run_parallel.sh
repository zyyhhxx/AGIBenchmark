#!/bin/bash
# Run v12 for each model in parallel as separate background processes
SCRIPT=/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/metacognition/run_fill_v12.py
PYTHON=/home/ubuntu/.openclaw/workspace-agi-bench/repo/.venv/bin/python3
LOGDIR=/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/metacognition/results

MODELS=(
    "anthropic.claude-opus-4-6-v1"
    "deepseek.r1-v1:0"
    "openai.gpt-oss-120b-1:0"
    "qwen.qwen3-next-80b-a3b"
    "anthropic.claude-sonnet-4-6"
    "zai.glm-4.7"
    "amazon.nova-pro-v1:0"
    "mistral.ministral-3-3b-instruct"
)

cd /home/ubuntu/.openclaw/workspace-agi-bench/repo

for m in "${MODELS[@]}"; do
    safe=$(echo "$m" | tr ':/' '__')
    echo "Starting $m -> $LOGDIR/log_v12_${safe}.txt"
    nohup $PYTHON -u $SCRIPT "$m" > "$LOGDIR/log_v12_${safe}.txt" 2>&1 &
done

echo "All started. PIDs:"
ps aux | grep run_fill_v12 | grep -v grep | awk '{print $2, $NF}'
