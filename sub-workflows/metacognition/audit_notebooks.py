#!/usr/bin/env python3
"""Comprehensive kbench SDK audit for metacognition notebooks."""
import json, os, re

NOTEBOOKS_DIR = "/home/ubuntu/.openclaw/workspace-agi-bench/repo/notebooks"
notebooks = sorted([f for f in os.listdir(NOTEBOOKS_DIR) if f.startswith("metacog_") and f.endswith(".ipynb")])

results = {}

for nb_name in notebooks:
    path = os.path.join(NOTEBOOKS_DIR, nb_name)
    with open(path) as f:
        nb = json.load(f)
    cells = nb.get("cells", [])
    issues = []
    info = {}
    
    # Check pip install (cell 0 typically)
    all_code = ""
    for c in cells:
        if c["cell_type"] == "code":
            all_code += "".join(c["source"]) + "\n"
    
    info["pip_install"] = "kaggle-benchmarks" in all_code or "kaggle_benchmarks" in all_code
    if not info["pip_install"]:
        issues.append("MISSING: pip install kaggle-benchmarks")
    
    # Check for @kbench.task decorator (not in comments)
    code_cells = [(i, "".join(c["source"])) for i, c in enumerate(cells) if c["cell_type"] == "code"]
    
    task_funcs = []
    for ci, src in code_cells:
        # Only count non-commented decorators
        for line_idx, line in enumerate(src.split("\n")):
            stripped = line.strip()
            if stripped.startswith("@") and "kbench.task" in stripped:
                # Find next def
                remaining = src.split("\n")[line_idx:]
                for rl in remaining[1:]:
                    m = re.match(r'\s*def\s+(\w+)\s*\(', rl)
                    if m:
                        task_funcs.append((ci, m.group(1)))
                        break
    
    info["task_funcs"] = task_funcs
    if not task_funcs:
        issues.append("CRITICAL: No @kbench.task() decorated functions found")
    
    # Check for %choose (not commented out)
    choose_cells = []
    for ci, src in code_cells:
        for line in src.split("\n"):
            stripped = line.strip()
            if stripped.startswith("%choose"):
                m = re.match(r'%choose\s+(\w+)', stripped)
                if m:
                    choose_cells.append((ci, m.group(1)))
    
    info["choose"] = choose_cells
    if not choose_cells:
        issues.append("MISSING: %choose cell (uncommented)")
    elif len(choose_cells) > 1:
        issues.append(f"WARNING: Multiple %choose cells: {choose_cells}")
    
    # Validate %choose references existing task
    if choose_cells and task_funcs:
        defined = [n for _, n in task_funcs]
        for ci, cname in choose_cells:
            if cname not in defined:
                issues.append(f"ERROR: %choose {cname} not in defined tasks: {defined}")
    
    # Check %choose is in final code cell
    if choose_cells:
        last_code_idx = code_cells[-1][0] if code_cells else -1
        last_choose_idx = choose_cells[-1][0]
        if last_choose_idx != last_code_idx:
            issues.append(f"WARNING: %choose in cell {last_choose_idx}, but last code cell is {last_code_idx}")
    
    # Check .run() — not needed if using %choose
    has_run = any(".run()" in src for _, src in code_cells if not src.strip().startswith("#"))
    info["has_run"] = has_run
    
    # Check for .evaluate() pattern
    has_evaluate = any(".evaluate(" in src for _, src in code_cells)
    info["has_evaluate"] = has_evaluate
    
    # Check return types in task functions
    info["has_llm_calls"] = any("llm.prompt(" in src or "llm.chat(" in src for _, src in code_cells)
    
    # Check for anti-patterns
    for ci, src in code_cells:
        if "import openai" in src and not src.strip().startswith("#"):
            issues.append(f"Cell {ci}: Uses openai directly instead of kbench LLM API")
        if "import anthropic" in src and not src.strip().startswith("#"):
            issues.append(f"Cell {ci}: Uses anthropic directly instead of kbench LLM API")
    
    if not issues:
        issues.append("PASS — no issues found")
    
    results[nb_name] = {"issues": issues, "info": info, "num_cells": len(cells), "num_code_cells": len(code_cells)}

# Print report
print(f"kbench SDK Compatibility Audit — {len(notebooks)} metacognition notebooks")
print("=" * 70)

critical = 0
warnings = 0
clean = 0

for nb_name, r in results.items():
    real_issues = [i for i in r["issues"] if not i.startswith("PASS")]
    crits = [i for i in real_issues if i.startswith("CRITICAL") or i.startswith("MISSING") or i.startswith("ERROR")]
    warns = [i for i in real_issues if i.startswith("WARNING")]
    
    status = "✅" if not real_issues else "⚠️" if not crits else "❌"
    if not real_issues:
        clean += 1
    
    print(f"\n{status} {nb_name}")
    print(f"   Cells: {r['num_cells']} total, {r['num_code_cells']} code")
    print(f"   Tasks: {[n for _, n in r['info']['task_funcs']]}")
    print(f"   Choose: {r['info']['choose']}")
    for iss in r["issues"]:
        print(f"   → {iss}")
    
    critical += len(crits)
    warnings += len(warns)

print(f"\n{'=' * 70}")
print(f"Summary: {clean}/{len(notebooks)} clean, {critical} critical issues, {warnings} warnings")
print(f"\nNotebooks needing fixes:")
for nb_name, r in results.items():
    crits = [i for i in r["issues"] if i.startswith("CRITICAL") or i.startswith("MISSING") or i.startswith("ERROR")]
    if crits:
        print(f"  - {nb_name}: {'; '.join(crits)}")
