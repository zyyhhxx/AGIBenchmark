#!/bin/bash
# Run learning_monitoring v2 against all 10 Bedrock models sequentially
# First clear cached scores for this benchmark, then run each model

set -e
REPO="/home/ubuntu/.openclaw/workspace-agi-bench/repo"
VENV="$REPO/.venv/bin/python3"
RESULTS_DIR="$REPO/results"
OUT_DIR="/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/metacognition/results"
LOG="$OUT_DIR/learning_monitoring_v2_run.log"
CSV="$OUT_DIR/learning_monitoring_v2_scores.csv"

mkdir -p "$OUT_DIR"

# Clear cached learning_monitoring scores from all model result files
echo "Clearing cached learning_monitoring scores..."
for f in "$RESULTS_DIR"/*.json; do
    [ -f "$f" ] || continue
    $VENV -c "
import json, sys
with open('$f') as fh: d = json.load(fh)
if 'metacog_learning_monitoring' in d.get('scores', {}):
    del d['scores']['metacog_learning_monitoring']
    with open('$f', 'w') as fh: json.dump(d, fh, indent=2)
    print(f'  Cleared: $f')
" 2>/dev/null || true
done

# Also clear any .run.json cache
find "$REPO" -name "*learning_monitoring*.run.json" -delete 2>/dev/null || true

echo "Running 10 models sequentially..."
echo "model,label,score,duration_s,error" > "$CSV"

MODELS=(
    "anthropic.claude-opus-4-6-v1|Claude Opus 4.6"
    "anthropic.claude-sonnet-4-6|Claude Sonnet 4.6"
    "deepseek.r1-v1:0|DeepSeek-R1"
    "openai.gpt-oss-120b-1:0|GPT-OSS-120B"
    "meta.llama3-3-70b-instruct-v1:0|Llama 3.3 70B"
    "qwen.qwen3-next-80b-a3b|Qwen3 Next 80B"
    "amazon.nova-pro-v1:0|Nova Pro"
    "meta.llama4-maverick-17b-instruct-v1:0|Llama 4 Maverick 17B"
    "zai.glm-4.7|GLM 4.7"
    "mistral.ministral-3-3b-instruct|Ministral 3B"
)

for entry in "${MODELS[@]}"; do
    IFS='|' read -r MODEL LABEL <<< "$entry"
    echo ""
    echo "============================================================"
    echo "Running: $LABEL ($MODEL)"
    echo "============================================================"
    
    START=$(date +%s)
    
    # Run with timeout (900s for DeepSeek, 600s for GLM, 300s for others)
    TIMEOUT=360
    if [[ "$MODEL" == *"deepseek"* ]]; then TIMEOUT=960; fi
    if [[ "$MODEL" == *"glm"* ]]; then TIMEOUT=660; fi
    
    if timeout "$TIMEOUT" $VENV "$REPO/scripts/run_benchmark_bedrock.py" \
        --model "$MODEL" --benchmark metacog_learning_monitoring \
        2>&1 | tee -a "$LOG"; then
        STATUS="ok"
    else
        STATUS="error"
    fi
    
    END=$(date +%s)
    DURATION=$((END - START))
    
    # Extract score from results file
    SAFE_NAME=$(echo "$MODEL" | tr ':/' '__')
    RESULT_FILE="$RESULTS_DIR/${SAFE_NAME}.json"
    
    SCORE=$($VENV -c "
import json
with open('$RESULT_FILE') as f: d = json.load(f)
s = d.get('scores',{}).get('metacog_learning_monitoring',{}).get('score')
print(s if s is not None else 'None')
" 2>/dev/null || echo "None")
    
    ERROR=""
    if [ "$SCORE" = "None" ]; then
        ERROR=$($VENV -c "
import json
with open('$RESULT_FILE') as f: d = json.load(f)
print(d.get('scores',{}).get('metacog_learning_monitoring',{}).get('error','unknown')[:100])
" 2>/dev/null || echo "no result file")
    fi
    
    echo "$MODEL,$LABEL,$SCORE,$DURATION,$ERROR" >> "$CSV"
    echo ">>> $LABEL: score=$SCORE, duration=${DURATION}s"
    
    sleep 3
done

echo ""
echo "============================================================"
echo "ALL RESULTS: $CSV"
echo "============================================================"
cat "$CSV"

# Compute stats
$VENV -c "
import csv, numpy as np
with open('$CSV') as f:
    rows = list(csv.DictReader(f))
scores = [float(r['score']) for r in rows if r['score'] != 'None']
print(f'\nScored: {len(scores)}/10')
print(f'Scores: {scores}')
print(f'Mean: {np.mean(scores):.4f}')
print(f'Std:  {np.std(scores):.4f}')
print(f'Range: {max(scores)-min(scores):.4f}')
print(f'Min: {min(scores):.4f}, Max: {max(scores):.4f}')
"
