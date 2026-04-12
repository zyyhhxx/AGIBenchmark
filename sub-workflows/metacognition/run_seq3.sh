#!/bin/bash
# Run 4 failing benchmarks against all models, ONE AT A TIME
# Uses run_benchmark_bedrock.py which saves results to results/*.json
set -o pipefail
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
PYTHON=.venv/bin/python3
RUNNER=scripts/run_benchmark_bedrock.py
LOG=sub-workflows/metacognition/results/rerun_log.txt
TMPOUT=$(mktemp)

echo "$(date): Starting 4-benchmark sequential rerun" | tee $LOG

BENCHMARKS="attention_selective learning_curves social_cog_emotional_prosody metacog_error_detection"
MODELS="anthropic.claude-opus-4-6-v1 anthropic.claude-sonnet-4-6 deepseek.r1-v1:0 zai.glm-4.7 openai.gpt-oss-120b-1:0 meta.llama3-3-70b-instruct-v1:0 meta.llama4-maverick-17b-instruct-v1:0 mistral.ministral-3-3b-instruct amazon.nova-pro-v1:0 qwen.qwen3-next-80b-a3b"

completed=0
failed=0

for bench in $BENCHMARKS; do
    for model in $MODELS; do
        echo "" | tee -a $LOG
        echo "$(date): $bench x $model" | tee -a $LOG
        
        # run_benchmark_bedrock.py already skips if score exists in the results JSON
        timeout 900 $PYTHON $RUNNER --model "$model" --benchmark "$bench" > $TMPOUT 2>&1
        rc=$?
        
        # Extract score from output
        SCORE=$(grep "Score:" $TMPOUT | tail -1 | awk '{print $2}')
        SKIP=$(grep "already scored" $TMPOUT | head -1)
        
        if [ -n "$SKIP" ]; then
            echo "  SKIP (already scored)" | tee -a $LOG
        elif [ $rc -eq 0 ] && [ -n "$SCORE" ]; then
            echo "  ✅ Score=$SCORE" | tee -a $LOG
            completed=$((completed + 1))
        elif [ $rc -eq 124 ]; then
            echo "  ⏰ TIMEOUT" | tee -a $LOG
            failed=$((failed + 1))
        else
            echo "  ❌ FAILED (rc=$rc)" | tee -a $LOG
            tail -5 $TMPOUT | tee -a $LOG
            failed=$((failed + 1))
        fi
        
        sleep 1
    done
done

echo "" | tee -a $LOG
echo "$(date): DONE completed=$completed failed=$failed" | tee -a $LOG
rm -f $TMPOUT
