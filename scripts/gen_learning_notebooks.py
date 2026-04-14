#!/usr/bin/env python3
"""Generate learning_transfer.ipynb and learning_interference.ipynb with inlined sources."""

import json
import re


def make_notebook(cells):
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11.0"}
        },
        "cells": cells
    }


def markdown_cell(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code_cell(source):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": source}


def strip_local_imports(src):
    lines = src.split('\n')
    out = []
    for line in lines:
        if 'from data.rule_systems import' in line or 'import data.' in line:
            continue
        if line.strip().startswith('import kaggle_benchmarks') or 'import kaggle_benchmarks as kbench' in line:
            continue
        out.append(line)
    return '\n'.join(out)


def strip_run_call_and_main(src):
    """Remove top-level run() calls and if __name__ block."""
    lines = src.split('\n')
    out = []
    in_main = False
    for line in lines:
        if re.match(r'if __name__\s*==\s*["\']__main__["\']', line):
            in_main = True
            continue
        if in_main:
            continue
        if re.match(r'^learning_(transfer|interference)\.run\(', line.strip()):
            continue
        # Also strip the run section header comment
        if line.strip() in ('# ─── Run ────────────────────────────────────────────────────────────',):
            continue
        out.append(line)
    # Strip trailing blank/comment lines
    while out and (not out[-1].strip() or out[-1].strip().startswith('#')):
        out.pop()
    return '\n'.join(out)


rule_systems_src = open('/home/ubuntu/.openclaw/workspace-agi-bench/repo/benchmarks/learning/data/rule_systems.py').read()
task_transfer_src = open('/home/ubuntu/.openclaw/workspace-agi-bench/repo/benchmarks/learning/task_transfer.py').read()
task_interference_src = open('/home/ubuntu/.openclaw/workspace-agi-bench/repo/benchmarks/learning/task_interference.py').read()

pip_cell = '!pip install -q protobuf==5.29.6 kaggle-benchmarks numpy 2>/dev/null\nimport kaggle_benchmarks as kbench'


# ── learning_transfer.ipynb ──────────────────────────────────────────

transfer_md = """# Near vs. Far Transfer Benchmark (v3)

Tests whether models can genuinely transfer learned structure to novel contexts —
NOT just follow explicit instructions.

## Methodology

**Core fix over v1/v2:** Previous versions gave all rules in every condition, reducing the task
to instruction-following. v3 forces actual abstraction:

| Condition | Weight | What is given |
|-----------|--------|---------------|
| Identical | 0.15 | Same system, all rules, held-out items (baseline) |
| Near transfer | 0.25 | Same domain (symbol), **1 rule omitted** — must infer from context |
| Far transfer | 0.30 | Different domain (number), **NO rules** — only 2 worked examples |
| Zero-shot structural | 0.30 | Stateful system, **NO rules** — only 1 worked example |

**Score** = 0.15 × identical + 0.25 × near + 0.30 × far + 0.30 × zero_shot

## Cognitive Science Basis
- Thorndike & Woodworth (1901): Transfer of practice
- Barnett & Ceci (2002): Taxonomy of far transfer
- Anderson (1987): ACT* theory — procedural vs. declarative transfer
"""

transfer_cell2_src = (
    rule_systems_src
    + '\n\n'
    + strip_run_call_and_main(strip_local_imports(task_transfer_src))
)

transfer_cells = [
    markdown_cell(transfer_md),
    code_cell(pip_cell),
    code_cell(transfer_cell2_src),
    code_cell("learning_transfer.run(llm=kbench.llm)"),
]

transfer_nb = make_notebook(transfer_cells)
with open('/home/ubuntu/.openclaw/workspace-agi-bench/repo/notebooks/learning_transfer.ipynb', 'w') as f:
    json.dump(transfer_nb, f, indent=1)
print("Written: learning_transfer.ipynb")


# ── learning_interference.ipynb ──────────────────────────────────────

interference_md = """# Proactive & Retroactive Interference Benchmark (v4)

Tests whether competing rule systems in context interfere with correct application
of a target system. Measures genuine interference resistance.

## Methodology

Four tiers of increasing difficulty:

| Tier | Weight | Design |
|------|--------|--------|
| Easy | 0.10 | 1 distractor, difficulty=1 |
| Medium | 0.25 | Cross-contamination: shared symbols, different rules |
| Hard | 0.35 | 3 distractors, difficulty=3, DELAYED interference (5 filler items), rule conflicts |
| Extreme | 0.30 | 4 systems difficulty=3, interleaved (target: 2 examples vs. 6 each for distractors) |

**Per tier:** score = 0.30 × control + 0.70 × interference_accuracy

**Composite** = 0.10 × easy + 0.25 × medium + 0.35 × hard + 0.30 × extreme

## Cognitive Science Basis
- Underwood (1957): Proactive inhibition in retention
- Postman (1961): Retroactive inhibition
- Anderson (2003): Retrieval-induced forgetting
- Wickens (1972): Release from proactive interference

## Key Design Insight (v4)
Rules are always present in the prompt — interference arises from MULTIPLE competing
systems being presented simultaneously. The model must resist applying the wrong system.
"""

interference_cell2_src = (
    rule_systems_src
    + '\n\n'
    + strip_run_call_and_main(strip_local_imports(task_interference_src))
)

interference_cells = [
    markdown_cell(interference_md),
    code_cell(pip_cell),
    code_cell(interference_cell2_src),
    code_cell("learning_interference.run(llm=kbench.llm)"),
]

interference_nb = make_notebook(interference_cells)
with open('/home/ubuntu/.openclaw/workspace-agi-bench/repo/notebooks/learning_interference.ipynb', 'w') as f:
    json.dump(interference_nb, f, indent=1)
print("Written: learning_interference.ipynb")
