# Heartbeat Tasks — AGI Benchmark: Metacognition Track

## Research Loop

### CRITICAL: This is a WORK SESSION, not a status check.
You have up to 55 minutes. Self-manage your time. Keep working until 50 minutes
elapsed, then wrap up. The cron timeout is a safety net, NOT your exit path.

### 1. Orient (2 min MAX)
```bash
START_TIME=$(date +%s)
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo && git pull
```
Read in order:
1. `sub-workflows/metacognition/GOALS.md` — competition requirements, success criteria, research directions
2. `sub-workflows/metacognition/HANDOFF.md` — orders from last cycle
3. `sub-workflows/metacognition/TODO.md` — task queue

**If HANDOFF says a script is running:**
- Check: `ps -p <PID> -o pid,etime,args`
- If finished: read the output file, log results
- If still running: note it, check partial output, move on

### 2. Determine Cycle Type
Count unchecked `[ ]` items in TODO.md Queue section (exclude In Progress and Done).
- **≥ 5 items → EXECUTION cycle.** Go to step 3.
- **< 5 items → EXPLORATION cycle.** Go to step 4.

### 3. Execution Loop
Loop until time runs out:
  a. **Time check:** `echo $(( $(date +%s) - START_TIME ))`
     - If > 3000 (50 min) → go to step 5 (WRAP UP) immediately
     - If > 2700 (45 min) → only start tasks that finish in 5 min
  b. **Pick task:** whatever HANDOFF says, or first unchecked `[ ]` from TODO
  c. Move to "In Progress" in TODO
  d. **Execute:**
     - For benchmark design: write docs in `benchmarks/<track>/DESIGN.md`
     - For implementation: write code in `benchmarks/<track>/`
     - Run: `timeout 300 repo/.venv/bin/python3 benchmarks/<script>.py > results/<name>_output.txt 2>&1`
     - For long-running scripts: launch in background, poll periodically
     - If script still running at 50 min: record PID + output file in HANDOFF, do NOT kill it
  e. Mark task `[x]` in TODO, move to Done
  f. **Back to (a)** — start next task

### 4. Exploration
The queue is running low. Spawn a thinking sub-agent to plan.

```
sessions_spawn(
  task: "You are a research planner for the AGI Benchmark hackathon.

Your workspace is at: /home/ubuntu/.openclaw/workspace-agi-bench/repo/

Read the files you need to understand the current state — at minimum:
- sub-workflows/metacognition/GOALS.md (competition requirements, tracks, Research Directions section)
- sub-workflows/metacognition/TODO.md (current queue + Done section for what's been completed)
- sub-workflows/metacognition/HANDOFF.md (latest cycle state)
- Any benchmark designs or code in benchmarks/ that help assess what exists.

Then generate a list of 20+ concrete, actionable TODO items. Requirements:
- Each item must be executable in 1-2 cycles (~55 min each).
- Each item must be specific enough to start without further planning.
  Good: 'Implement FOK benchmark: generate 50 trivia questions, prompt model for confidence, measure calibration curve'
  Bad: 'Design metacognition benchmarks'
- At least 2 items must be entirely new approaches not yet explored.
- Include [1 cycle] or [2 cycles] estimates.
- Do NOT duplicate items already in the Done section.
- Draw from the Research Directions in GOALS.md for inspiration.
- Remember the deadline is April 16, 2026 — prioritize submittable benchmarks.

Output format — a flat list ready to append to the Queue section:
- [ ] Item description [N cycles]
- [ ] Item description [N cycles]
...",
  model: "amazon-bedrock/us.anthropic.claude-opus-4-6-v1",
  thinking: "high",
  runTimeoutSeconds: 2700,
  cleanup: "delete"
)
```

After sub-agent returns: merge output into TODO.md. Go to step 5 (WRAP UP).

### 5. Wrap Up (budget 5 min — always runs)
1. **Write HANDOFF.md** (overwrite entire file):
   - Cycle type, timestamp, duration
   - What was completed
   - If a script is still running: PID, output file, what it's doing
   - Next action for following cycle
   - Queue depth
2. **Append one JSON object (single line) to CYCLE_LOG.jsonl** with fields:
   timestamp, cycle_type, duration_min, tasks_completed (name/result/outcome/artifact),
   tasks_partial, script_handoff (pid/output_file/script/started or null),
   queue_before, queue_after, git_commit, notes.
   For EXPLORATION: items_generated, themes instead of tasks fields.
3. Update `TODO.md` — mark completed `[x]`, move to Done
4. `git add -A && git commit -m "agi-bench: <summary>" && git push`

## Key Rules
- **KEEP WORKING until 50 min elapsed.** Do not stop early.
- **Self-manage time.** Check elapsed time between tasks. Wrap up at 50 min.
- **TODO is FIFO.** Work top-down. Append new items at the bottom.
- **Long scripts survive across sessions.** Don't kill them — hand off via HANDOFF.md.
- **Deadline: April 16, 2026.** Prioritize submittable benchmarks over perfection.
- Python: ALWAYS use `repo/.venv/bin/python3` — never system python.
- All sub-workflow files (GOALS, TODO, HANDOFF, CYCLE_LOG) are in `sub-workflows/metacognition/`.
- Benchmark code goes in `benchmarks/` (repo root). Research notes in `research/`.
