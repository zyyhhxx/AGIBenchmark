#!/bin/bash
set -e
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
source .venv/bin/activate
exec python3 sub-workflows/benchmark-qa/run_learning_qa.py "$@"
