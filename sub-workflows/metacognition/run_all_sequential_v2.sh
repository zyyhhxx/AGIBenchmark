#!/bin/bash
# Run all 10 models sequentially, one at a time.
# Each model saves incrementally after each benchmark.
REPO=/home/ubuntu/.openclaw/workspace-agi-bench/repo
PYTHON=$REPO/.venv/bin/python3
SCRIPT=$REPO/sub-workflows/metacognition/run_single_model.py
LOGS=$REPO/sub-workflows/metacognition/logs

mkdir -p "$LOGS"

MODELS=(
  "mistral.ministral-3-3b-instruct"
  "meta.llama4-maverick-17b-instruct-v1:0"
  "meta.llama3-3-70b-instruct-v1:0"
  "amazon.nova-pro-v1:0"
  "openai.gpt-oss-120b-1:0"
  "qwen.qwen3-next-80b-a3b"
  "deepseek.r1-v1:0"
  "zai.glm-4.7"
  "anthropic.claude-sonnet-4-6"
  "anthropic.claude-opus-4-6-v1"
)

for model in "${MODELS[@]}"; do
  safe=$(echo "$model" | tr ':/' '__')
  echo "[$(date -u +%H:%M:%S)] Starting $model"
  PYTHONUNBUFFERED=1 $PYTHON -u $SCRIPT "$model" >> "$LOGS/${safe}_incr.log" 2>&1
  echo "[$(date -u +%H:%M:%S)] Finished $model (exit=$?)"
  sleep 3
done

echo "[$(date -u +%H:%M:%S)] ALL DONE"

# Show final summary
echo ""
echo "=== Final Result Files ==="
for f in $REPO/sub-workflows/metacognition/results/*.json; do
  [ -f "$f" ] && python3 -c "import json,os; d=json.load(open('$f')); n=len(d.get('scores',{})); print(f'{d.get(\"model_label\",\"?\"):30s}: {n} benchmarks')" 2>/dev/null
done
