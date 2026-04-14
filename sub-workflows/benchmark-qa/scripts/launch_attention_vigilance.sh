#!/bin/bash
set -e
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo

PROC_LOG="/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/benchmark-qa/async/attention_vigilance_qa.log"
ASYNC_DIR="/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/benchmark-qa/async"
OUT_DIR="/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/benchmark-qa/results/qa_transcripts/attention_vigilance"
mkdir -p "$ASYNC_DIR" "$OUT_DIR"

# Launch
.venv/bin/python3 sub-workflows/benchmark-qa/scripts/run_attention_vigilance_qa.py > "$PROC_LOG" 2>&1 &
PID=$!

# Read start ticks
START_TICKS=$(awk '{print $22}' /proc/$PID/stat)

# Write .wait file
cat > "$ASYNC_DIR/.wait" << EOF
{
    "pid": $PID,
    "start_ticks": $START_TICKS,
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)",
    "max_wait": 7200,
    "poll_interval": 120,
    "check_interval": 300,
    "description": "Running attention_vigilance benchmark against all 10 Bedrock models with Q&A transcript logging",
    "log_files": ["$PROC_LOG"],
    "output_dir": "$OUT_DIR"
}
EOF

echo "Launched PID $PID. Coordinator will monitor via async wait."
echo "Log: $PROC_LOG"
