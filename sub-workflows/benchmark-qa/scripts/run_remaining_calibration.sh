#!/bin/bash
# Run metacog_calibration for remaining models
# Designed to run independently via nohup

cd /home/ubuntu/.openclaw/workspace-agi-bench/repo

for model in "zai.glm-4.7" "mistral.ministral-3-3b-instruct" "qwen.qwen3-next-80b-a3b" "openai.gpt-oss-120b-1:0"; do
    echo "=== $(date): Starting $model ==="
    .venv/bin/python3 scripts/run_benchmark_bedrock.py --benchmark metacog_calibration --model "$model" 2>&1 | grep -E "metacog_calibration|ERROR|Summary|\[1/1\]"
    echo "=== $(date): Done $model, exit=$? ==="
    sleep 5
done
echo "ALL DONE $(date)"
