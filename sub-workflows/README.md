# Sub-Workflows — AGI Benchmark

## Active Tracks

### metacognition
- **Focus:** Metacognition + Learning tracks for the AGI hackathon
- **Heartbeat:** `metacognition/HEARTBEAT-metacognition.md`
- **Cron:** Every 1 hour (isolated session)
- **Files:** GOALS.md, TODO.md, HANDOFF.md, CYCLE_LOG.jsonl, KNOWLEDGE-metacognition.md

## Adding a New Track

1. Create `sub-workflows/<track-name>/`
2. Copy files from metacognition/ as template
3. Create `HEARTBEAT-<track>.md` with the research loop
4. Add cron job pointing to the new heartbeat
5. Update health monitor and daily progress cron payloads
