#!/bin/bash
# Run missing benchmarks one at a time, checking for already-running processes first
set -e
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
PYTHON=.venv/bin/python3
RUNNER=scripts/run_benchmark_bedrock.py

BENCHMARKS="attention_selective learning_curves social_cog_emotional_prosody metacog_error_detection"
MODELS="anthropic.claude-opus-4-6-v1 anthropic.claude-sonnet-4-6 deepseek.r1-v1:0 zai.glm-4.7 openai.gpt-oss-120b-1:0 meta.llama3-3-70b-instruct-v1:0 meta.llama4-maverick-17b-instruct-v1:0 mistral.ministral-3-3b-instruct amazon.nova-pro-v1:0 qwen.qwen3-next-80b-a3b"

# Wait for any existing benchmark processes to finish
while pgrep -f "run_benchmark_bedrock.py\|run_single.py" > /dev/null 2>&1; do
    echo "$(date): Waiting for existing benchmark processes..."
    sleep 30
done

echo "$(date): All clear. Starting sequential runs."

for bench in $BENCHMARKS; do
    for model in $MODELS; do
        echo ""
        echo "========================================"
        echo "$(date): $bench x $model"
        echo "========================================"
        timeout 900 $PYTHON $RUNNER --model "$model" --benchmark "$bench" || echo "FAILED: $bench x $model (rc=$?)"
        sleep 2
    done
done

echo ""
echo "$(date): ALL DONE"
