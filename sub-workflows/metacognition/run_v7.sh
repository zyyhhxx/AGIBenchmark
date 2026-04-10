#!/bin/bash
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
source .venv/bin/activate
python3 sub-workflows/metacognition/run_all_v6.py 2>&1 | tee sub-workflows/metacognition/results/run_all_v7.log
