# GOALS.md — AGI Benchmark Hackathon (Final Review Phase)

## Active Goal
Final review and polish of the AGI benchmark submission. Deadline: **April 16, 2026**.

## Context
Ian has already completed:
- All 29 benchmarks implemented across 5 tracks
- Notebooks uploaded to Kaggle
- Benchmarks run against 17 models on Kaggle Community Benchmarks
- Discussion thread posted

## Tasks for This Phase

### 1. Architecture Review
Carefully review the general architecture of the entire benchmark suite:
- Repository structure and organization
- Shared code, imports, dependencies between notebooks
- Consistency of benchmark interfaces (`@kbench.task` decorators, `.run()` calls, scoring)
- Are there any design issues, redundancies, or structural problems that need fixing?
- Document any recommended changes

### 2. Notebook Content Audit
For each of the 33 notebooks in `repo/notebooks/`:
- Check for code errors, syntax issues, import problems
- Check for conflicts between notebooks (duplicate function names, conflicting data)
- Verify each notebook runs end-to-end without errors (syntax check, not execution)
- Check consistency of scoring methodology across benchmarks in the same track
- Flag any notebooks that seem incomplete or have placeholder content

### 3. ~~Convert submission_overview.ipynb to Markdown~~ ✅ DONE
`submission_overview.ipynb` has been merged into `SUBMISSION_NARRATIVE.md` and deleted.

### 4. Submission Requirements Checklist
Thoroughly review the competition requirements at: https://www.kaggle.com/competitions/kaggle-measuring-agi/overview
- Cross-reference every requirement against what we've done
- Produce a final TODO list of remaining items for Ian
- Categorize as: must-do (blocks submission), should-do (improves score), nice-to-have
- Ian has already done: notebook uploads, running benchmarks against 17 models, posting discussion thread
- Focus on what's still missing or needs fixing

## Quality Standards
- Be thorough — this is the final review before deadline
- Flag real issues, not cosmetic nitpicks
- Provide actionable recommendations with specific file paths
- Update IAN_TODO.md with the final checklist
