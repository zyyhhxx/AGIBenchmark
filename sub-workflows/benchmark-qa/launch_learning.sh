#!/bin/bash
set -e
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
source .venv/bin/activate

LOGFILE=/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/benchmark-qa/async/learning_run.log
WAIT_FILE=/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/benchmark-qa/async/.wait
ASYNC_DIR=/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/benchmark-qa/async

mkdir -p "$ASYNC_DIR"

# Launch with unbuffered python
python3 -u sub-workflows/benchmark-qa/run_learning_qa.py > "$LOGFILE" 2>&1 &
PID=$!

START_TICKS=$(awk '{print $22}' /proc/$PID/stat)

cat > "$WAIT_FILE" << EOF
{
    "pid": $PID,
    "start_ticks": $START_TICKS,
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)",
    "max_wait": 10800,
    "poll_interval": 300,
    "check_interval": 600,
    "description": "Running all 4 Learning benchmarks (curriculum, curves, interference, transfer) against all 10 models with Q&A transcript logging",
    "log_files": ["$LOGFILE"],
    "output_dir": "/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/benchmark-qa/results/qa_transcripts"
}
EOF

echo "Launched PID $PID (start_ticks=$START_TICKS). Coordinator will monitor via async wait."
