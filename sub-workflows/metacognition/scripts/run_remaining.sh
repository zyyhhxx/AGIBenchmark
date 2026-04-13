#!/bin/bash
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo
PYTHON=.venv/bin/python3
SCRIPT=sub-workflows/metacognition/scripts/run_one_model.py

for idx in 6 7 8 9; do
    echo "=== Starting model index $idx at $(date -u) ==="
    timeout 700 $PYTHON $SCRIPT $idx 2>&1
    echo "=== Finished model index $idx at $(date -u), exit=$? ==="
done

echo "=== ALL DONE ==="
# Print summary
$PYTHON -c "
import json
with open('sub-workflows/metacognition/results/calibration_v2_results.json') as f:
    d = json.load(f)
scores = d['scores']
vals = [v['score'] for v in scores.values() if v.get('score') is not None]
import statistics
print(f'Scored models: {len(vals)}/10')
for k,v in sorted(scores.items()):
    print(f'  {k}: {v}')
if len(vals) >= 2:
    print(f'Mean: {statistics.mean(vals):.4f}')
    print(f'Std:  {statistics.stdev(vals):.4f}')
    print(f'Range: {max(vals)-min(vals):.4f}')
"
