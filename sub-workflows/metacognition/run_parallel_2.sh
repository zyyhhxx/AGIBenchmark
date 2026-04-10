#!/bin/bash
# Run all 10 models with max 2 concurrent to avoid throttling.
# Each model runs all 26 benchmarks sequentially.
REPO=/home/ubuntu/.openclaw/workspace-agi-bench/repo
PYTHON=$REPO/.venv/bin/python3
SCRIPT=$REPO/scripts/run_benchmark_bedrock.py
RESULTS=$REPO/sub-workflows/metacognition/results
LOGS=$REPO/sub-workflows/metacognition/logs

mkdir -p "$RESULTS" "$LOGS"

MAX_PARALLEL=2

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

running=0
for model in "${MODELS[@]}"; do
  safe=$(echo "$model" | tr ':/' '__')
  logfile="$LOGS/${safe}_full.log"
  
  # Check if already complete (26+ benchmarks)
  result_file="$RESULTS/${safe}.json"
  if [ -f "$result_file" ]; then
    count=$(python3 -c "import json; d=json.load(open('$result_file')); print(len(d.get('scores',{})))" 2>/dev/null)
    if [ "$count" -ge 26 ] 2>/dev/null; then
      echo "[$(date -u +%H:%M:%S)] SKIP $model (already $count benchmarks)"
      continue
    fi
  fi
  
  # Wait if at max parallel
  while [ $running -ge $MAX_PARALLEL ]; do
    wait -n 2>/dev/null
    running=$((running - 1))
  done
  
  echo "[$(date -u +%H:%M:%S)] Starting $model"
  PYTHONUNBUFFERED=1 $PYTHON -u $SCRIPT --model "$model" --track all --output-dir "$RESULTS" > "$logfile" 2>&1 &
  running=$((running + 1))
  sleep 5
done

echo "[$(date -u +%H:%M:%S)] All models launched. Waiting for completion..."
wait
echo "[$(date -u +%H:%M:%S)] All models complete!"

echo ""
echo "=== Result Files ==="
for f in "$RESULTS"/*.json; do
  [ -f "$f" ] && python3 -c "
import json, os
d=json.load(open('$f'))
n=len(d.get('scores',{}))
print(f'  {os.path.basename(\"$f\"):55s} {n} benchmarks')
" 2>/dev/null
done
