# Heartbeat Tasks — {Track Name}

This file defines the operational loop for the {track name} sub-workflow.

## Research Loop

### 1. Orient (2 min)
```bash
cd ~/.openclaw/workspace-{name}/repo && git pull
source .venv/bin/activate
```
Then read (in order):
1. `../KNOWLEDGE.md` — shared domain knowledge
2. `sub-workflows/{track}/KNOWLEDGE-{track}.md` — track-specific knowledge
3. `sub-workflows/{track}/GOALS.md` — this sub-workflow's objectives
4. `sub-workflows/{track}/TODO.md` — take the first unchecked `[ ]` item
5. `sub-workflows/{track}/STATUS-{track}.md` — confirm where you left off
6. Check for any updates from the manager (new files in your dir)

### 2. Work (fill the window)
Execute tasks from TODO.md following the standard priority order (P0 → P4).

**Task lifecycle:**
1. Move task to "In Progress" with a progress note
2. Do the work
3. If finished: mark `[x]`, move to Done
4. If timed out: leave in "In Progress" with note — next run will continue

{Add workflow-specific work instructions here}

### 3. Wrap Up (last 3 min)
1. **Update KNOWLEDGE-{track}.md** — learnings from this cycle
2. Update `STATUS-{track}.md` — what you did, where you stopped, what's next
3. Update `TODO.md` — mark completed items, append new tasks
4. `git add -A && git commit -m "{track}: <summary>" && git push`

## File Scope
- **Write to:** `sub-workflows/{track}/` only
- **Read from:** own GOALS.md, root ROADMAP.md, root KNOWLEDGE.md, `manager/` (reference only), `drive/`
- **Never write to:** `manager/`, root files, other sub-workflows

## Key Rules
- **Fill the full time window.** Don't stop after one sub-task if time remains.
- **Never leave TODO empty.** Append new ideas as discovered.
- Python: always use `repo/.venv/bin/python3` — never system python.
