#!/bin/bash
# Run social_cog_emotional_prosody and remaining metacog_error_detection
set -o pipefail
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
PYTHON=.venv/bin/python3
RUNNER=scripts/run_benchmark_bedrock.py
LOG=sub-workflows/metacognition/results/rerun_social_metacog.log
TMPOUT=$(mktemp)

echo "$(date): Starting social_cog + metacog_error_detection reruns" | tee $LOG

MODELS="anthropic.claude-opus-4-6-v1 anthropic.claude-sonnet-4-6 deepseek.r1-v1:0 zai.glm-4.7 openai.gpt-oss-120b-1:0 meta.llama3-3-70b-instruct-v1:0 meta.llama4-maverick-17b-instruct-v1:0 mistral.ministral-3-3b-instruct amazon.nova-pro-v1:0 qwen.qwen3-next-80b-a3b"

for bench in social_cog_emotional_prosody metacog_error_detection; do
    for model in $MODELS; do
        echo "$(date): $bench x $model" | tee -a $LOG
        timeout 600 $PYTHON $RUNNER --model "$model" --benchmark "$bench" > $TMPOUT 2>&1
        rc=$?
        SCORE=$(grep "Score:" $TMPOUT | tail -1 | awk '{print $2}')
        SKIP=$(grep "already scored" $TMPOUT | head -1)
        if [ -n "$SKIP" ]; then
            echo "  SKIP" | tee -a $LOG
        elif [ $rc -eq 0 ] && [ -n "$SCORE" ]; then
            echo "  ✅ $SCORE" | tee -a $LOG
        else
            echo "  ❌ rc=$rc" | tee -a $LOG
            tail -3 $TMPOUT | tee -a $LOG
        fi
        sleep 1
    done
done

# Also run learning_curves - try 3 fast models first  
for model in mistral.ministral-3-3b-instruct amazon.nova-pro-v1:0 qwen.qwen3-next-80b-a3b meta.llama3-3-70b-instruct-v1:0 meta.llama4-maverick-17b-instruct-v1:0 zai.glm-4.7 openai.gpt-oss-120b-1:0 deepseek.r1-v1:0 anthropic.claude-sonnet-4-6 anthropic.claude-opus-4-6-v1; do
    echo "$(date): learning_curves x $model" | tee -a $LOG
    timeout 900 $PYTHON $RUNNER --model "$model" --benchmark "learning_curves" > $TMPOUT 2>&1
    rc=$?
    SCORE=$(grep "Score:" $TMPOUT | tail -1 | awk '{print $2}')
    SKIP=$(grep "already scored" $TMPOUT | head -1)
    if [ -n "$SKIP" ]; then
        echo "  SKIP" | tee -a $LOG
    elif [ $rc -eq 0 ] && [ -n "$SCORE" ]; then
        echo "  ✅ $SCORE" | tee -a $LOG
    elif [ $rc -eq 124 ]; then
        echo "  ⏰ TIMEOUT" | tee -a $LOG
    else
        echo "  ❌ rc=$rc" | tee -a $LOG
    fi
    sleep 1
done

echo "$(date): ALL DONE" | tee -a $LOG
rm -f $TMPOUT
