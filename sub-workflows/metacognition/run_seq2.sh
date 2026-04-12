#!/bin/bash
# Sequential benchmark runner - one process at a time
# Saves results to a separate JSON and updates model result files
set -o pipefail
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
PYTHON=.venv/bin/python3
RESULTS_DIR=results
LOG=/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/metacognition/results/rerun_4bench.log

mkdir -p sub-workflows/metacognition/results

echo "$(date): Starting 4-benchmark rerun" | tee $LOG

# Function to check if a score exists in results JSON
check_score() {
    local model_file="$1"
    local bench="$2"
    if [ ! -f "$RESULTS_DIR/$model_file" ]; then
        return 1
    fi
    $PYTHON -c "
import json
with open('$RESULTS_DIR/$model_file') as f:
    d = json.load(f)
s = d.get('scores',{}).get('$bench')
if s and s.get('score') is not None:
    exit(0)
exit(1)
" 2>/dev/null
}

# Function to save result into model JSON file
save_result() {
    local model_file="$1"
    local bench="$2"
    local score="$3"
    local duration="$4"
    local model_id="$5"
    local model_label="$6"
    
    $PYTHON -c "
import json, os
from datetime import datetime, timezone
path = '$RESULTS_DIR/$model_file'
if os.path.exists(path):
    with open(path) as f:
        d = json.load(f)
else:
    d = {'model': '$model_id', 'model_label': '$model_label', 'scores': {}}
d.setdefault('scores', {})
d['scores']['$bench'] = {'score': $score, 'error': None, 'duration_s': $duration}
d['timestamp'] = datetime.now(timezone.utc).isoformat()
with open(path, 'w') as f:
    json.dump(d, f, indent=2)
print('Saved $bench=$score to $model_file')
"
}

# Model map: model_id -> file -> label
declare -A MODEL_MAP
MODEL_MAP["anthropic.claude-opus-4-6-v1"]="anthropic.claude-opus-4-6-v1.json|Claude Opus 4.6"
MODEL_MAP["anthropic.claude-sonnet-4-6"]="anthropic.claude-sonnet-4-6.json|Claude Sonnet 4.6"
MODEL_MAP["deepseek.r1-v1:0"]="deepseek.r1-v1_0.json|DeepSeek-R1"
MODEL_MAP["zai.glm-4.7"]="zai.glm-4.7.json|GLM 4.7"
MODEL_MAP["openai.gpt-oss-120b-1:0"]="openai.gpt-oss-120b-1_0.json|GPT-OSS-120B"
MODEL_MAP["meta.llama3-3-70b-instruct-v1:0"]="meta.llama3-3-70b-instruct-v1_0.json|Llama 3.3 70B"
MODEL_MAP["meta.llama4-maverick-17b-instruct-v1:0"]="meta.llama4-maverick-17b-instruct-v1_0.json|Llama 4 Maverick 17B"
MODEL_MAP["mistral.ministral-3-3b-instruct"]="mistral.ministral-3-3b-instruct.json|Ministral 3B"
MODEL_MAP["amazon.nova-pro-v1:0"]="amazon.nova-pro-v1_0.json|Nova Pro"
MODEL_MAP["qwen.qwen3-next-80b-a3b"]="qwen.qwen3-next-80b-a3b.json|Qwen3 Next 80B"

BENCHMARKS="attention_selective learning_curves social_cog_emotional_prosody metacog_error_detection"
MODELS="anthropic.claude-opus-4-6-v1 anthropic.claude-sonnet-4-6 deepseek.r1-v1:0 zai.glm-4.7 openai.gpt-oss-120b-1:0 meta.llama3-3-70b-instruct-v1:0 meta.llama4-maverick-17b-instruct-v1:0 mistral.ministral-3-3b-instruct amazon.nova-pro-v1:0 qwen.qwen3-next-80b-a3b"

total=0
completed=0
skipped=0
failed=0

for bench in $BENCHMARKS; do
    for model in $MODELS; do
        total=$((total + 1))
        IFS='|' read -r model_file model_label <<< "${MODEL_MAP[$model]}"
        
        # Check if already done
        if check_score "$model_file" "$bench"; then
            echo "$(date): SKIP $bench x $model_label (already scored)" | tee -a $LOG
            skipped=$((skipped + 1))
            continue
        fi
        
        echo "" | tee -a $LOG
        echo "$(date): RUN $bench x $model_label ($model)" | tee -a $LOG
        
        # Run using run_single.py and capture output
        OUTPUT=$(timeout 900 $PYTHON sub-workflows/metacognition/run_single.py "$model" "$bench" 2>&1) || true
        
        # Extract result JSON
        RESULT_LINE=$(echo "$OUTPUT" | grep "^RESULT_JSON:" | tail -1)
        if [ -n "$RESULT_LINE" ]; then
            RESULT_JSON="${RESULT_LINE#RESULT_JSON:}"
            SCORE=$($PYTHON -c "import json; d=json.loads('$RESULT_JSON'); print(d['score'])" 2>/dev/null)
            DURATION=$($PYTHON -c "import json; d=json.loads('$RESULT_JSON'); print(d['duration_s'])" 2>/dev/null)
            ERROR=$($PYTHON -c "import json; d=json.loads('$RESULT_JSON'); print(d.get('error',''))" 2>/dev/null)
            
            if [ "$SCORE" != "None" ] && [ -n "$SCORE" ]; then
                save_result "$model_file" "$bench" "$SCORE" "$DURATION" "$model" "$model_label"
                echo "  ✅ Score=$SCORE Duration=${DURATION}s" | tee -a $LOG
                completed=$((completed + 1))
            else
                echo "  ❌ Error: $ERROR" | tee -a $LOG
                failed=$((failed + 1))
            fi
        else
            echo "  ❌ No result output. Last 5 lines:" | tee -a $LOG
            echo "$OUTPUT" | tail -5 | tee -a $LOG
            failed=$((failed + 1))
        fi
        
        sleep 2
    done
done

echo "" | tee -a $LOG
echo "$(date): SUMMARY: total=$total completed=$completed skipped=$skipped failed=$failed" | tee -a $LOG
