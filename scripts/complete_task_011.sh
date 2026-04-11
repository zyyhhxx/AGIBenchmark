#!/bin/bash
# Complete task metacognitio-20260410-011 steps 4-7
# Run this after all 10 models have finished benchmarking
set -e
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo

echo "=== Checking model completion ==="
COMPLETE=$(.venv/bin/python3 -c "
import json, os
models = [
    'anthropic.claude-opus-4-6-v1', 'deepseek.r1-v1_0', 'openai.gpt-oss-120b-1_0',
    'anthropic.claude-sonnet-4-6', 'zai.glm-4.7', 'qwen.qwen3-next-80b-a3b',
    'meta.llama3-3-70b-instruct-v1_0', 'meta.llama4-maverick-17b-instruct-v1_0',
    'amazon.nova-pro-v1_0', 'mistral.ministral-3-3b-instruct',
]
done = 0
for m in models:
    d = json.load(open(f'results/{m}.json'))
    scores = d.get('scores', {})
    total = sum(1 for v in scores.values() if isinstance(v, dict) and (v.get('score') is not None or v.get('error')))
    if total >= 26:
        done += 1
    else:
        scored = sum(1 for v in scores.values() if isinstance(v, dict) and v.get('score') is not None)
        print(f'INCOMPLETE: {m} at {scored}/26')
print(f'Complete: {done}/10')
")
echo "$COMPLETE"

if echo "$COMPLETE" | grep -q "INCOMPLETE"; then
    echo "Not all models complete yet. Exiting."
    exit 1
fi

echo ""
echo "=== Step 4: Generating score_matrix.csv ==="
.venv/bin/python3 scripts/generate_matrix.py

echo ""
echo "=== Step 5: Checking discriminatory analysis ==="
cat results/discriminatory_analysis.md | grep -E "CEILING|FLOOR|LOW VAR|flagged"

echo ""
echo "=== Done. Steps 6-7 (narrative updates, git commit) need agent intervention ==="
