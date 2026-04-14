# STANDARDS.md — Metacognition (AGI Benchmarks)

## What a Complete Task Looks Like

A task is PASS when ALL of the following are true:

1. **Artifacts exist and are non-empty** — every file listed in `artifacts` must exist and contain substantive content
2. **Steps were followed** — each step in the task's `steps` list has a corresponding artifact or finding
3. **Findings are documented** — at least one finding string explains what was learned or the result
4. **Cognitive science rationale** — benchmarks cite relevant literature and explain which cognitive construct is being measured
5. **Contamination-resistant** — benchmark design avoids testing recall of training data; uses procedurally generated stimuli or novel compositions where possible
6. **kbench SDK patterns** — notebooks use `@kbench.task` decorators, `.run()` calls, and follow kaggle-benchmarks SDK conventions
7. **Notebook structure** — notebooks include `!pip install kaggle-benchmarks` in cell 0, have markdown rationale cells, and end with `.run()`
8. **Code passes syntax validation** — `python3 -m py_compile <file>` exits 0 for all `.py` files; `jupyter nbconvert --to notebook <file>` exits 0 for all `.ipynb` files
9. **Results are reproducible** — benchmark scores are deterministic given the same model responses (no uncontrolled randomness without fixed seeds)

## What Forces a FAIL (Append Note, Return to Executor)

- Artifact file is empty or contains only boilerplate
- Steps list has incomplete coverage (e.g., task said "run benchmarks" but no scores recorded)
- Findings field is empty
- Benchmark has no cognitive science rationale or cites no literature
- Notebook missing `!pip install kaggle-benchmarks` cell
- Notebook missing `.run()` call
- Python file fails `py_compile` check
- Scores not in expected [0, 1] range
- Benchmark is trivially gameable by pattern matching or recall

## What Counts as a Finding

A finding is substantive if it contains at least one of:
- A numeric result (benchmark score, model accuracy, calibration metric)
- A qualitative insight about model cognitive capabilities not previously in KNOWLEDGE
- Evidence of something NOT working, and why (e.g., "GPT-4o scores 1.0 on X — benchmark too easy")
- A decision made (e.g., "discarded approach X because it tests recall, not metacognition")
- Comparison across models revealing differential performance

## Knowledge Update Policy

When marking a task PASS, the Validator appends to KNOWLEDGE if findings contain:
- New frontier model benchmark results
- A new failure mode or ceiling effect discovered
- A new benchmark design pattern that improved contamination resistance
- Cross-model comparison insights
- Anything that saves the next executor from re-discovering it

Do NOT update KNOWLEDGE with information already present there.
