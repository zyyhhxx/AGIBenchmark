#!/bin/bash
# Run all 10 models in parallel
REPO=/home/ubuntu/.openclaw/workspace-agi-bench/repo
PYTHON=$REPO/.venv/bin/python3
SCRIPT=$REPO/scripts/run_benchmark_bedrock.py
RESULTS=$REPO/sub-workflows/metacognition/results
LOGS=$REPO/sub-workflows/metacognition/logs

mkdir -p "$RESULTS" "$LOGS"
rm -f "$LOGS"/*.log

MODELS=(
  "mistral.ministral-3-3b-instruct"
  "anthropic.claude-opus-4-6-v1"
  "deepseek.r1-v1:0"
  "openai.gpt-oss-120b-1:0"
  "meta.llama3-3-70b-instruct-v1:0"
  "qwen.qwen3-next-80b-a3b"
  "amazon.nova-pro-v1:0"
  "meta.llama4-maverick-17b-instruct-v1:0"
  "anthropic.claude-sonnet-4-6"
  "zai.glm-4.7"
)

for model in "${MODELS[@]}"; do
  safe=$(echo "$model" | tr ':/' '__')
  echo "[$(date -u +%H:%M:%S)] Starting $model"
  $PYTHON $SCRIPT --model "$model" --track all --output-dir "$RESULTS" > "$LOGS/${safe}.log" 2>&1 &
  sleep 3
done

echo "[$(date -u +%H:%M:%S)] All 10 models launched."
echo "Waiting for all to complete..."
wait
echo "[$(date -u +%H:%M:%S)] All models complete!"
echo ""
echo "=== Result Files ==="
ls -la "$RESULTS"/*.json 2>/dev/null
