#!/usr/bin/env python3
"""Patch notebooks to match their task_*.py source of truth."""

import json
import re
from pathlib import Path

REPO = Path("/home/ubuntu/.openclaw/workspace-agi-bench/repo")
NB_DIR = REPO / "notebooks"
PY_DIR = REPO / "benchmarks" / "metacognition"

def read_py(name):
    return (PY_DIR / f"{name}.py").read_text()

def load_nb(name):
    path = NB_DIR / f"{name}.ipynb"
    with open(path) as f:
        return json.load(f), path

def save_nb(nb, path):
    with open(path, 'w') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write('\n')

def get_cell_code(cell):
    return "".join(cell["source"])

def set_cell_code(cell, code):
    """Set cell source from a string, preserving notebook format."""
    lines = code.split('\n')
    source = []
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            source.append(line + '\n')
        else:
            source.append(line)
    # Remove trailing empty string if it exists
    if source and source[-1] == '':
        source.pop()
    cell["source"] = source

def extract_function(code, func_name):
    """Extract a function definition from code, returning (start_pos, end_pos, body)."""
    pattern = rf'^( *)def\s+{re.escape(func_name)}\s*\('
    match = re.search(pattern, code, re.MULTILINE)
    if not match:
        return None
    
    start = match.start()
    indent = len(match.group(1))
    lines = code[start:].split('\n')
    
    func_lines = [lines[0]]
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == '':
            func_lines.append(line)
            continue
        # Check if this line is at same or lower indent (new top-level def/class)
        line_indent = len(line) - len(line.lstrip())
        if line_indent <= indent and stripped and not stripped.startswith('#'):
            # Check if it's a new definition
            if re.match(r'(?:def |class |@)', stripped):
                break
            # For indent==0, any non-empty line at indent 0 that's not continuation
            if indent == 0:
                break
        func_lines.append(line)
    
    # Remove trailing blank lines
    while func_lines and func_lines[-1].strip() == '':
        func_lines.pop()
    
    body = '\n'.join(func_lines)
    end = start + len(body)
    return start, end, body

def replace_function_in_code(code, func_name, new_body):
    """Replace a function in code with new_body."""
    result = extract_function(code, func_name)
    if not result:
        return code, False
    start, end, old_body = result
    return code[:start] + new_body + code[end:], True

def insert_function_before(code, before_func, new_body):
    """Insert new_body before before_func in code."""
    result = extract_function(code, before_func)
    if not result:
        return code, False
    start, _, _ = result
    return code[:start] + new_body + '\n\n' + code[start:], True

fixes_applied = 0

# Helper to patch a notebook
def patch_notebook(nb_name, py_name, func_patches, insert_patches=None):
    global fixes_applied
    py_code = read_py(py_name)
    nb, nb_path = load_nb(nb_name)
    
    changed = False
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        cell_code = get_cell_code(cell)
        cell_changed = False
        
        # Apply function replacements
        for func_name in func_patches:
            py_result = extract_function(py_code, func_name)
            if not py_result:
                print(f"  WARNING: {func_name} not found in {py_name}.py")
                continue
            _, _, py_body = py_result
            
            nb_result = extract_function(cell_code, func_name)
            if not nb_result:
                continue
            
            _, _, nb_body = nb_result
            if py_body.strip() != nb_body.strip():
                cell_code, did_replace = replace_function_in_code(cell_code, func_name, py_body)
                if did_replace:
                    cell_changed = True
                    print(f"  Fixed {func_name} in {nb_name}")
                    fixes_applied += 1
        
        # Apply insertions
        if insert_patches:
            for new_func, before_func in insert_patches:
                if new_func in cell_code:
                    continue  # Already exists
                if before_func not in cell_code:
                    continue
                py_result = extract_function(py_code, new_func)
                if not py_result:
                    continue
                _, _, py_body = py_result
                cell_code, did_insert = insert_function_before(cell_code, before_func, py_body)
                if did_insert:
                    cell_changed = True
                    print(f"  Inserted {new_func} in {nb_name}")
                    fixes_applied += 1
        
        if cell_changed:
            set_cell_code(cell, cell_code)
            changed = True
    
    if changed:
        save_nb(nb, nb_path)
        print(f"  Saved {nb_path.name}")
    else:
        print(f"  No changes needed for {nb_name}")

print("=== Patching notebooks ===\n")

# 1. metacog_calibration
print("1. metacog_calibration")
patch_notebook("metacog_calibration", "task_calibration",
               ["brier_skill_score", "compute_ece", "metacog_calibration"])

# 2. metacog_control
print("\n2. metacog_control")
patch_notebook("metacog_control", "task_metacognitive_control",
               ["metacog_control"])

# 3. metacog_epistemic_humility
print("\n3. metacog_epistemic_humility")
patch_notebook("metacog_epistemic_humility", "task_epistemic_humility",
               ["metacog_epistemic_humility"])

# 4. metacog_error_detection (needs norminv inserted + compute_dprime replaced)
print("\n4. metacog_error_detection")
patch_notebook("metacog_error_detection", "task_error_detection",
               ["compute_dprime", "metacog_error_detection"],
               insert_patches=[("norminv", "compute_dprime")])

# 5. metacog_fok
print("\n5. metacog_fok")
patch_notebook("metacog_fok", "task_fok",
               ["brier_skill_score", "metacog_fok"])

# 6. metacog_jol
print("\n6. metacog_jol")
patch_notebook("metacog_jol", "task_jol",
               ["brier_skill_score", "metacog_jol"])

# 7. metacog_learning_monitoring
print("\n7. metacog_learning_monitoring")
patch_notebook("metacog_learning_monitoring", "task_learning_monitoring",
               ["metacog_learning_monitoring"])

print(f"\n=== Total fixes applied: {fixes_applied} ===")
