# Heartbeat Tasks — Workflow Manager

This file defines the operational loop for the workflow manager.
The manager runs daily with a 12-hour timeout window.

## Purpose
Extract valuable patterns from sub-workflows. Curate reusable code and reports.
Synthesize domain knowledge. Resolve duplication.

**The manager does NOT compile status reports.** Each sub-workflow maintains its own
STATUS file, and the main agent reads those directly for daily updates and health monitoring.

## Manager Loop

### 1. Audit Sub-Workflows
```bash
cd ~/.openclaw/workspace-{name}/repo && git pull
source .venv/bin/activate
```

Scan `sub-workflows/` for all active sub-workflows. For each:
1. Read `KNOWLEDGE-<name>.md` — any new learnings since last manager run?
2. Review recent git commits: `git log --oneline --since="24 hours ago" -- sub-workflows/<name>/`
3. Scan code for patterns worth extracting

### 2. Knowledge Synthesis
Review all sub-workflow KNOWLEDGE files for cross-cutting insights:
- Techniques that apply to multiple sub-workflows
- Lessons learned (failures are as valuable as successes)

Update root `KNOWLEDGE.md` with distilled cross-cutting knowledge.
**Do not duplicate sub-workflow-specific details** — only promote generalizable insights.

### 3. Artifact Extraction
When a sub-workflow produces code or analysis worth preserving independently:
1. Extract a clean, standalone copy to `manager/code/` or `manager/reports/`
2. Add docstrings and usage context
3. Update `manager/KNOWLEDGE-manager.md` index with a row describing it

`manager/code/` and `manager/reports/` are **reference artifacts**, not dependencies.
Sub-workflows can read them for inspiration but write their own implementations.

### 4. Deduplication Check
If two sub-workflows independently developed similar code:
1. Identify the better implementation (or merge the best of both)
2. Extract the merged version to `manager/code/` as the reference
3. Note in KNOWLEDGE-manager.md that both sub-workflows have similar code

### 5. Wrap Up
1. `git add -A && git commit -m "manager: <summary>" && git push`

## File Scope
- **Read from:** all sub-workflows, all root files
- **Write to:** `manager/`, root `KNOWLEDGE.md`
- **Never:** change sub-workflow logic, priorities, or research direction

## Key Rules
- **The manager aggregates knowledge, it does not direct.**
- **Extract conservatively.** Only extract code/reports that have cross-cutting value.
- **KNOWLEDGE-manager.md is the index.** Keep it concise — point to files in `code/` and `reports/`.
