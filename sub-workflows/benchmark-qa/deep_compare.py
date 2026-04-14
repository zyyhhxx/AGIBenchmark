#!/usr/bin/env python3
"""Deep comparison of notebook cells vs task_*.py files.
Extracts function bodies, class definitions, scoring logic, prompts, item data."""

import json
import re
import difflib
from pathlib import Path

REPO = Path("/home/ubuntu/.openclaw/workspace-agi-bench/repo")
NB_DIR = REPO / "notebooks"
PY_DIR = REPO / "benchmarks" / "metacognition"

MAPPING = {
    "metacog_calibration": "task_calibration",
    "metacog_canary": "task_canary",
    "metacog_control": "task_metacognitive_control",
    "metacog_epistemic_humility": "task_epistemic_humility",
    "metacog_epistemic_revision": "task_epistemic_revision",
    "metacog_error_detection": "task_error_detection",
    "metacog_fok": "task_fok",
    "metacog_jol": "task_jol",
    "metacog_learning_monitoring": "task_learning_monitoring",
}

def get_nb_code(nb_path):
    with open(nb_path) as f:
        nb = json.load(f)
    return "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")

def extract_functions(code):
    """Extract dict of function_name -> function_body."""
    funcs = {}
    lines = code.split('\n')
    current_name = None
    current_lines = []
    indent = 0
    for line in lines:
        m = re.match(r'^( *)def\s+(\w+)\s*\(', line)
        if m:
            if current_name:
                funcs[current_name] = '\n'.join(current_lines)
            current_name = m.group(2)
            current_lines = [line]
            indent = len(m.group(1))
        elif current_name:
            # Check if we've left the function
            stripped = line.strip()
            if stripped and not line.startswith(' ' * (indent + 1)) and not line.startswith(' ' * indent + ' '):
                if re.match(r'^(?:def |class |@)', stripped) or (stripped and not line[0].isspace() and indent == 0):
                    funcs[current_name] = '\n'.join(current_lines)
                    current_name = None
                    current_lines = []
                    # Re-check if this is a new function
                    m2 = re.match(r'^( *)def\s+(\w+)\s*\(', line)
                    if m2:
                        current_name = m2.group(2)
                        current_lines = [line]
                        indent = len(m2.group(1))
                    continue
            current_lines.append(line)
    if current_name:
        funcs[current_name] = '\n'.join(current_lines)
    return funcs

def extract_classes(code):
    """Extract class names and their method signatures."""
    classes = {}
    for m in re.finditer(r'class\s+(\w+)[^:]*:', code):
        classes[m.group(1)] = True
    return set(classes.keys())

def extract_scored_metrics(code):
    """Find scoring-related patterns."""
    patterns = []
    for m in re.finditer(r'(score\w*|metric\w*|accuracy|ece|brier|calibration)\s*[=:+\-*/].*', code, re.IGNORECASE):
        patterns.append(m.group(0).strip()[:200])
    return patterns

def normalize(text):
    """Normalize whitespace for comparison."""
    return re.sub(r'\s+', ' ', text).strip()

total_mismatches = 0

for nb_name, py_name in sorted(MAPPING.items()):
    nb_path = NB_DIR / f"{nb_name}.ipynb"
    py_path = PY_DIR / f"{py_name}.py"
    
    py_code = py_path.read_text()
    nb_code = get_nb_code(nb_path)
    
    py_funcs = extract_functions(py_code)
    nb_funcs = extract_functions(nb_code)
    
    print(f"\n{'='*70}")
    print(f"{nb_name} vs {py_name}")
    print(f"  .py functions: {sorted(py_funcs.keys())}")
    print(f"  .ipynb functions: {sorted(nb_funcs.keys())}")
    
    mismatches = []
    
    # Compare shared functions
    shared = set(py_funcs.keys()) & set(nb_funcs.keys())
    py_only = set(py_funcs.keys()) - set(nb_funcs.keys())
    nb_only = set(nb_funcs.keys()) - set(py_funcs.keys())
    
    if py_only:
        print(f"  Functions in .py only: {py_only}")
    if nb_only:
        print(f"  Functions in .ipynb only: {nb_only}")
    
    for func_name in sorted(shared):
        py_body = normalize(py_funcs[func_name])
        nb_body = normalize(nb_funcs[func_name])
        if py_body != nb_body:
            # Get a unified diff
            py_lines = py_funcs[func_name].strip().split('\n')
            nb_lines = nb_funcs[func_name].strip().split('\n')
            diff = list(difflib.unified_diff(py_lines, nb_lines, 
                                              fromfile=f"{py_name}.py", 
                                              tofile=f"{nb_name}.ipynb",
                                              lineterm=''))
            if diff:
                # Only show first 20 diff lines
                diff_text = '\n'.join(diff[:30])
                mismatches.append((func_name, diff_text, len(diff)))
    
    if mismatches:
        total_mismatches += len(mismatches)
        for func_name, diff_text, diff_len in mismatches:
            print(f"\n  ❌ MISMATCH in function '{func_name}' ({diff_len} diff lines):")
            print(f"    {diff_text[:1000]}")
    else:
        if shared:
            print(f"  ✅ All {len(shared)} shared functions match")
        else:
            print(f"  ⚠️  No shared function names to compare")
    
    # Compare classes
    py_classes = extract_classes(py_code)
    nb_classes = extract_classes(nb_code)
    if py_classes != nb_classes:
        print(f"  Classes .py: {py_classes}")
        print(f"  Classes .ipynb: {nb_classes}")

print(f"\n{'='*70}")
print(f"TOTAL FUNCTION MISMATCHES: {total_mismatches}")
print(f"{'='*70}")
