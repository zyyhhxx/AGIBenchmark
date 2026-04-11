#!/bin/bash
# Monitor benchmark progress and regenerate matrix when all complete
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo

while true; do
    COMPLETE=$(.venv/bin/python3 scripts/quick_progress.py 2>/dev/null | grep "Complete:" | grep -o '[0-9]*/10')
    echo "[$(date -u +%H:%M:%S)] Progress: $COMPLETE models complete"
    
    if [ "$COMPLETE" = "10/10" ]; then
        echo "All models complete! Regenerating matrix..."
        .venv/bin/python3 scripts/generate_matrix.py
        echo "Done. Matrix and analysis regenerated."
        break
    fi
    
    sleep 300
done
