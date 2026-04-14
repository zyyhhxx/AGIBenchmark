#!/bin/bash
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
source .venv/bin/activate
python3 sub-workflows/benchmark-qa/scripts/run_attention_selective_qa.py
