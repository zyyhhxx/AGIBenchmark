#!/usr/bin/env bash
# Run all 10 models with parallelism capped at 4
set -e
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
PYTHON=.venv/bin/python3
SCRIPT=scripts/run_benchmark_bedrock.py
RESULTS=results
LOGDIR=results/logs
mkdir -p "$LOGDIR"

MODELS=(
  "anthropic.claude-opus-4-6-v1"
  "deepseek.r1-v1:0"
  "openai.gpt-oss-120b-1:0"
  "meta.llama3-3-70b-instruct-v1:0"
  "qwen.qwen3-next-80b-a3b"
  "amazon.nova-pro-v1:0"
  "meta.llama4-maverick-17b-instruct-v1:0"
  "anthropic.claude-sonnet-4-6"
  "zai.glm-4.7"
  "mistral.ministral-3-3b-instruct"
)

MAX_PARALLEL=4
running=0
pids=()

for model in "${MODELS[@]}"; do
  safe=$(echo "$model" | tr ':/' '__')
  log="$LOGDIR/${safe}.log"
  echo "[$(date)] Starting $model → $log"
  PYTHONUNBUFFERED=1 $PYTHON -u $SCRIPT --model "$model" --track all --output-dir "$RESULTS" > "$log" 2>&1 &
  pids+=($!)
  running=$((running + 1))
  
  if [ $running -ge $MAX_PARALLEL ]; then
    # Wait for any one to finish
    wait -n "${pids[@]}" 2>/dev/null || true
    running=$((running - 1))
    # Clean up finished pids
    new_pids=()
    for pid in "${pids[@]}"; do
      if kill -0 "$pid" 2>/dev/null; then
        new_pids+=($pid)
      fi
    done
    pids=("${new_pids[@]}")
    running=${#pids[@]}
  fi
done

# Wait for remaining
echo "[$(date)] Waiting for remaining ${#pids[@]} jobs..."
for pid in "${pids[@]}"; do
  wait "$pid" 2>/dev/null || true
done

echo "[$(date)] All models complete."
echo ""
echo "=== Result files ==="
ls -la "$RESULTS"/*.json 2>/dev/null | grep -v mock | grep -v spot | grep -v correlation | grep -v learning | grep -v reliability | grep -v stratified | grep -v metacog_bedrock | grep -v stress
