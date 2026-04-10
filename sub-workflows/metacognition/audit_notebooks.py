#!/usr/bin/env python3
"""Audit all notebooks in repo/notebooks/ for structure, syntax, and consistency."""
import json, os, subprocess, sys, re
from pathlib import Path
from collections import defaultdict

NB_DIR = Path("/home/ubuntu/.openclaw/workspace-agi-bench/repo/notebooks")
OUT = Path("/home/ubuntu/.openclaw/workspace-agi-bench/repo/NOTEBOOK_AUDIT.md")

notebooks = sorted(NB_DIR.glob("*.ipynb"))
print(f"Found {len(notebooks)} notebooks\n")

# Step 1: Categorize
tracks = {"metacog": [], "learning": [], "attention": [], "exec_func": [], "social_cog": [], "other": []}
for nb in notebooks:
    name = nb.stem
    matched = False
    for prefix in ["metacog", "learning", "attention", "exec_func", "social_cog"]:
        if name.startswith(prefix):
            tracks[prefix].append(nb)
            matched = True
            break
    if not matched:
        tracks["other"].append(nb)

print("=== Step 1: Categorization ===")
for t, nbs in tracks.items():
    print(f"  {t}: {len(nbs)} — {[n.stem for n in nbs]}")

# Step 2: JSON/syntax validation via nbconvert
print("\n=== Step 2: Syntax Validation (nbconvert) ===")
syntax_results = {}
for nb in notebooks:
    r = subprocess.run(
        ["/home/ubuntu/.openclaw/workspace-agi-bench/repo/.venv/bin/jupyter", "nbconvert", "--to", "notebook", "--stdout", str(nb)],
        capture_output=True, timeout=30
    )
    ok = r.returncode == 0
    syntax_results[nb.stem] = ok
    if not ok:
        print(f"  FAIL: {nb.stem} — {r.stderr.decode()[:200]}")
    else:
        print(f"  OK: {nb.stem}")

# Step 3 & 5: Content checks
print("\n=== Step 3: Content Checks ===")
content_results = {}  # name -> {pip_install, kbench_task, choose_cell, no_direct_imports, todos, stubs}

for nb in notebooks:
    with open(nb) as f:
        data = json.load(f)
    cells = data.get("cells", [])
    sources = [(i, "".join(c.get("source", []))) for i, c in enumerate(cells)]
    
    info = {
        "pip_install_cell0": False,
        "has_kbench_task": False,
        "has_choose": False,
        "no_direct_imports": True,
        "todos": [],
        "stubs": [],
        "num_cells": len(cells),
        "scoring_pattern": None,
    }
    
    # Check cell 0 for pip install
    if sources:
        cell0 = sources[0][1]
        if "pip install" in cell0 and "kaggle-benchmarks" in cell0:
            info["pip_install_cell0"] = True
    
    all_source = "\n".join(s for _, s in sources)
    
    # kbench.task decorator
    if "@kbench.task" in all_source:
        info["has_kbench_task"] = True
    
    # %choose in final code cell
    code_cells = [(i, s) for i, s in sources if cells[i].get("cell_type") == "code" and s.strip()]
    if code_cells:
        last_code = code_cells[-1][1]
        if "%choose" in last_code or ".run(" in last_code:
            info["has_choose"] = True
    
    # Direct imports
    for line in all_source.split("\n"):
        stripped = line.strip()
        if re.match(r"^(import|from)\s+(openai|anthropic)\b", stripped):
            info["no_direct_imports"] = False
    
    # TODOs and stubs
    for i, src in sources:
        for line in src.split("\n"):
            if "TODO" in line or "FIXME" in line:
                info["todos"].append((i, line.strip()))
            if "placeholder" in line.lower() or "stub" in line.lower():
                info["stubs"].append((i, line.strip()))
    
    # Scoring pattern detection (for step 4)
    if "brier" in all_source.lower() or "bss" in all_source.lower() or "brier_skill" in all_source.lower():
        info["scoring_pattern"] = "BSS/Brier"
    elif "accuracy" in all_source.lower():
        info["scoring_pattern"] = "accuracy"
    if "normalize" in all_source.lower():
        info["scoring_pattern"] = (info["scoring_pattern"] or "") + "+normalize"
    
    content_results[nb.stem] = info
    
    issues = []
    if not info["pip_install_cell0"]: issues.append("no pip install cell0")
    if not info["has_kbench_task"]: issues.append("no @kbench.task")
    if not info["has_choose"]: issues.append("no %choose/.run()")
    if not info["no_direct_imports"]: issues.append("direct openai/anthropic import")
    if info["todos"]: issues.append(f"{len(info['todos'])} TODOs")
    if info["stubs"]: issues.append(f"{len(info['stubs'])} stubs")
    
    status = "PASS" if not issues else f"ISSUES: {', '.join(issues)}"
    print(f"  {nb.stem}: {status}")

# Step 4: Scoring consistency
print("\n=== Step 4: Scoring Consistency ===")
for track, nbs in tracks.items():
    if not nbs or track == "other":
        continue
    patterns = {nb.stem: content_results[nb.stem]["scoring_pattern"] for nb in nbs}
    unique = set(patterns.values())
    print(f"  {track}: scoring patterns = {dict(patterns)}")
    if len(unique) > 1:
        print(f"    ⚠ INCONSISTENT scoring across {track} track")

# Step 5: Incomplete notebooks summary
print("\n=== Step 5: Incomplete Notebooks ===")
incomplete = []
for name, info in content_results.items():
    if info["todos"] or info["stubs"] or info["num_cells"] < 3:
        incomplete.append((name, info))
        print(f"  {name}: {len(info['todos'])} TODOs, {len(info['stubs'])} stubs, {info['num_cells']} cells")
        for idx, line in info["todos"][:3]:
            print(f"    cell {idx}: {line[:100]}")

if not incomplete:
    print("  None found.")

# Step 6: Write NOTEBOOK_AUDIT.md
print("\n=== Step 6: Writing NOTEBOOK_AUDIT.md ===")
lines = ["# Notebook Audit Report\n"]
lines.append(f"**Total notebooks:** {len(notebooks)}\n")
lines.append("## Notebooks by Track\n")
for t, nbs in tracks.items():
    lines.append(f"- **{t}**: {len(nbs)} — {', '.join(n.stem for n in nbs)}")
lines.append("")

# Pass/fail table
lines.append("## Per-Notebook Results\n")
lines.append("| Notebook | Syntax | pip install | @kbench.task | %choose/.run() | No direct imports | TODOs | Stubs | Overall |")
lines.append("|----------|--------|-------------|--------------|----------------|-------------------|-------|-------|---------|")
for nb in notebooks:
    name = nb.stem
    s = syntax_results[name]
    c = content_results[name]
    issues = []
    if not s: issues.append("syntax")
    if not c["pip_install_cell0"]: issues.append("pip")
    if not c["has_kbench_task"]: issues.append("decorator")
    if not c["has_choose"]: issues.append("choose")
    if not c["no_direct_imports"]: issues.append("imports")
    if c["todos"]: issues.append("todos")
    if c["stubs"]: issues.append("stubs")
    overall = "✅ PASS" if not issues else "❌ FAIL"
    lines.append(f"| {name} | {'✅' if s else '❌'} | {'✅' if c['pip_install_cell0'] else '❌'} | {'✅' if c['has_kbench_task'] else '❌'} | {'✅' if c['has_choose'] else '❌'} | {'✅' if c['no_direct_imports'] else '❌'} | {len(c['todos'])} | {len(c['stubs'])} | {overall} |")

# Scoring consistency
lines.append("\n## Scoring Consistency\n")
for track, nbs in tracks.items():
    if not nbs or track == "other":
        continue
    patterns = {nb.stem: content_results[nb.stem]["scoring_pattern"] for nb in nbs}
    unique = set(patterns.values())
    consistency = "✅ Consistent" if len(unique) <= 1 else "⚠️ Inconsistent"
    lines.append(f"### {track} ({consistency})\n")
    for name, pat in patterns.items():
        lines.append(f"- {name}: `{pat}`")
    lines.append("")

# Issues to fix
lines.append("## Issues to Fix\n")
issue_count = 0
for nb in notebooks:
    name = nb.stem
    s = syntax_results[name]
    c = content_results[name]
    nb_issues = []
    if not s: nb_issues.append("Fix JSON syntax error")
    if not c["pip_install_cell0"]: nb_issues.append("Add `!pip install kaggle-benchmarks` to cell 0")
    if not c["has_kbench_task"]: nb_issues.append("Add `@kbench.task()` decorator")
    if not c["has_choose"]: nb_issues.append("Add `%choose` or `.run()` to final cell")
    if not c["no_direct_imports"]: nb_issues.append("Remove direct openai/anthropic imports")
    for idx, line in c["todos"]:
        nb_issues.append(f"TODO in cell {idx}: {line[:80]}")
    for idx, line in c["stubs"]:
        nb_issues.append(f"Stub in cell {idx}: {line[:80]}")
    if nb_issues:
        issue_count += len(nb_issues)
        lines.append(f"### {name}\n")
        for issue in nb_issues:
            lines.append(f"- {issue}")
        lines.append("")

if issue_count == 0:
    lines.append("No issues found! All notebooks pass.\n")

lines.append(f"\n---\n*Audit generated automatically. {issue_count} total issues across {len(notebooks)} notebooks.*\n")

OUT.write_text("\n".join(lines))
print(f"Written to {OUT} ({issue_count} total issues)")
