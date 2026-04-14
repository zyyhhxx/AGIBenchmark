#!/bin/bash
cd /home/ubuntu/.openclaw/workspace-agi-bench
source repo/.venv/bin/activate
python3 repo/sub-workflows/benchmark-qa/run_attention_divided.py
