# Sub-Workflows

This directory contains isolated research tracks under the {name} workflow.

## Pattern

Each sub-workflow gets:
- Its own directory: `sub-workflows/<name>/`
- Dedicated heartbeat: `HEARTBEAT-<name>.md`
- Dedicated status: `STATUS-<name>.md`
- Dedicated knowledge: `KNOWLEDGE-<name>.md`
- Own TODO and artifacts

## Rules

1. **Sub-workflows are self-contained.** All code a sub-workflow needs lives within its own directory.
2. **Sub-workflows only write to their own directory.** Never to another sub-workflow's directory or `manager/`.
3. **Root-level files** (AGENTS.md, ROADMAP.md, KNOWLEDGE.md) are read-only for sub-workflows.
4. **`manager/`** holds extracted code patterns and reports curated by the manager. Sub-workflows can read them for inspiration but are not required to use them.
5. **The manager** curates reference artifacts in `manager/code/` and `manager/reports/`, and synthesizes cross-cutting knowledge into root KNOWLEDGE.md.

## Active Sub-Workflows

| Name | Session | Schedule | Purpose |
|------|---------|----------|---------|
| {track} | `session:{name}-{track}` | Every 31 min | {description} |

The **manager** (`session:{name}-manager`, daily) lives at `repo/manager/` — it is not a sub-workflow.

## Spinning Up a New Sub-Workflow

1. Create directory: `sub-workflows/<name>/`
2. Create: HEARTBEAT-<name>.md, STATUS-<name>.md, KNOWLEDGE-<name>.md, TODO.md
3. Create cron job with `session:{workflow}-<name>` (persistent session)
4. Update this README with the new entry
5. Update Daily Progress Update and Health Monitor crons
