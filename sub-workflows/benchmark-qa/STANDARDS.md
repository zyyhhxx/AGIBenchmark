# STANDARDS.md — Metacognition (AGI Benchmarks)

## What a Complete Task Looks Like

A task is PASS when ALL of the following are true:

1. **Artifacts exist and are non-empty** — every file listed in `artifacts` must exist and contain substantive content
2. **Steps were followed** — each step in the task's `steps` list has a corresponding artifact or finding
3. **Findings are documented** — at least one finding string explains what was learned or the result
4. **Cognitive science rationale** — benchmarks cite relevant literature and explain which cognitive construct is being measured
5. **Contamination-resistant** — benchmark design avoids testing recall of training data; uses procedurally generated stimuli or novel compositions where possible
6. **kbench SDK patterns** — notebooks use `@kbench.task` decorators, `.run()` calls, and follow kaggle-benchmarks SDK conventions
7. **Notebook structure** — see Notebook Quality Standards below
8. **Code passes syntax validation** — all notebook code cells compile (`compile(src, name, 'exec')` succeeds); all `.py` files pass `python3 -m py_compile`
9. **Results are reproducible** — benchmark scores are deterministic given the same model responses (no uncontrolled randomness without fixed seeds)

## What Forces a FAIL (Append Note, Return to Executor)

- Artifact file is empty or contains only boilerplate
- Steps list has incomplete coverage (e.g., task said "run benchmarks" but no scores recorded)
- Findings field is empty
- Benchmark has no cognitive science rationale or cites no literature
- Notebook missing `!pip install kaggle-benchmarks` cell
- Notebook missing `.run()` call
- Notebook violates any rule in Notebook Quality Standards below
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

## Notebook Quality Standards

Every Kaggle benchmark notebook MUST satisfy ALL of the following. No exceptions.

### Cell Structure (exactly 4 cells)

| Cell | Type | Contents |
|------|------|----------|
| 0 | markdown | Title + methodology description (cognitive science basis, scoring formula, what each condition tests) |
| 1 | code | `!pip install -q protobuf==5.29.6 kaggle-benchmarks numpy 2>/dev/null` followed by `import kaggle_benchmarks as kbench` |
| 2 | code | ALL benchmark code inlined (stimuli data + task function). Must include `import kaggle_benchmarks as kbench` at the top. |
| 3 | code | `task_function.run(llm=kbench.llm)` — the ONLY `.run()` call |

### Mandatory Rules

1. **Exactly 1 `.run()` call** — in the final cell only. No double execution.
2. **No local imports** — no `from data.` or `import data.` anywhere. All dependencies (stimuli generators, data files) must be inlined into cell 2.
3. **`import kaggle_benchmarks as kbench`** must appear in BOTH cell 1 (pip cell) AND cell 2 (code cell).
4. **No `if __name__` blocks** — these break Kaggle execution.
5. **No trailing run comments** — no `# --- Run ---` or `# ─── Run ───` at the end of cell 2.
6. **All code cells must compile** — `compile(src, name, 'exec')` must succeed for cells 1 and 2.
7. **`_strip_think()` in every benchmark** — all benchmarks that parse model output must strip `<think>...</think>` tags before parsing (DeepSeek R1 fix).
8. **JS-style comment stripping** — benchmarks that parse JSON must strip `//` comments: `re.sub(r'//.*', '', raw)`.

### Verification Command

Run this for every notebook before considering it done:

```python
import json
nb = json.load(open('notebooks/FILENAME.ipynb'))
cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
assert len(cells) == 3, f"Expected 3 code cells, got {len(cells)}"
assert sum(1 for c in cells if '.run(' in ''.join(c['source'])) == 1, "Must have exactly 1 .run() call"
assert 'kbench' in ''.join(cells[0]['source']), "kbench must be in pip cell"
assert not any('from data.' in ''.join(c['source']) for c in cells), "No local imports"
assert not any('if __name__' in ''.join(c['source']) for c in cells), "No if __name__"
for i, c in enumerate(cells[1:], 1):
    compile(''.join(c['source']), f'cell{i}', 'exec')  # Must not raise
print("ALL CHECKS PASS")
```

### Ground Truth Verification

Every benchmark with deterministic stimuli must have a verification script that:
1. Independently computes expected outputs using the rule/apply functions
2. Compares against stored answer keys (e.g., `correct_response`, `test_items[i]['output']`)
3. Reports any mismatches
4. Prints "ALL GROUND TRUTH VERIFIED" on success

This ensures LLM-generated answer keys are correct — we don't trust ourselves to hand-verify.
