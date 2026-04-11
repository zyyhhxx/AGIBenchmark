#!/usr/bin/env python3
"""Compare notebook cells against task_*.py source of truth."""

import json
import re
import sys
from pathlib import Path

REPO = Path("/home/ubuntu/.openclaw/workspace-agi-bench/repo")
NB_DIR = REPO / "notebooks"
PY_DIR = REPO / "benchmarks" / "metacognition"

# Mapping: notebook name -> py file name
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

def extract_notebook_code(nb_path):
    """Extract all code cells from a notebook."""
    with open(nb_path) as f:
        nb = json.load(f)
    code_cells = []
    for i, cell in enumerate(nb.get("cells", [])):
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            code_cells.append((i, source))
    return code_cells, nb

def extract_key_elements(code_text):
    """Extract scoring formulas, item counts, prompt templates from code."""
    elements = {}
    
    # Find N_ITEMS / num_items / n_items patterns
    for m in re.finditer(r'(?:N_ITEMS|num_items|n_items|NUM_ITEMS|ITEMS_PER|items_per)\s*[:=]\s*(\d+)', code_text):
        elements.setdefault('item_counts', []).append(m.group(0))
    
    # Find score/scoring patterns
    for m in re.finditer(r'(?:score|scoring|metric)[^\n]{0,200}', code_text, re.IGNORECASE):
        elements.setdefault('scoring', []).append(m.group(0).strip())
    
    # Find prompt templates (triple-quoted strings or prompt variables)
    for m in re.finditer(r'(?:prompt|PROMPT|template|TEMPLATE)\s*[:=]\s*(?:f?"""[\s\S]*?"""|f?\'\'\'[\s\S]*?\'\'\'|f?"[^"]*"|f?\'[^\']*\')', code_text):
        elements.setdefault('prompts', []).append(m.group(0)[:500])
    
    # Find class/function definitions
    for m in re.finditer(r'^(?:class|def)\s+\w+', code_text, re.MULTILINE):
        elements.setdefault('definitions', []).append(m.group(0))
    
    return elements

def compare_pair(nb_name, py_name):
    nb_path = NB_DIR / f"{nb_name}.ipynb"
    py_path = PY_DIR / f"{py_name}.py"
    
    if not nb_path.exists():
        return f"MISSING notebook: {nb_path}"
    if not py_path.exists():
        return f"MISSING py file: {py_path}"
    
    # Read py source
    py_code = py_path.read_text()
    
    # Read notebook code
    code_cells, nb_data = extract_notebook_code(nb_path)
    nb_code = "\n".join(src for _, src in code_cells)
    
    py_elements = extract_key_elements(py_code)
    nb_elements = extract_key_elements(nb_code)
    
    mismatches = []
    
    # Compare item counts
    py_items = set(py_elements.get('item_counts', []))
    nb_items = set(nb_elements.get('item_counts', []))
    if py_items != nb_items:
        mismatches.append(f"  ITEM COUNTS differ:\n    .py: {py_items or 'none found'}\n    .ipynb: {nb_items or 'none found'}")
    
    # Compare class/function definitions
    py_defs = set(py_elements.get('definitions', []))
    nb_defs = set(nb_elements.get('definitions', []))
    py_only = py_defs - nb_defs
    if py_only:
        mismatches.append(f"  DEFINITIONS in .py but not notebook: {py_only}")
    
    # Check if notebook imports from the .py module
    imports_from_py = py_name in nb_code or f"from benchmarks.metacognition.{py_name}" in nb_code
    
    # Deep comparison: check if notebook duplicates logic or imports it
    # Look for key function bodies
    py_funcs = re.findall(r'def\s+(\w+)\s*\([^)]*\):', py_code)
    nb_funcs = re.findall(r'def\s+(\w+)\s*\([^)]*\):', nb_code)
    
    duplicated_funcs = set(py_funcs) & set(nb_funcs)
    if duplicated_funcs and not imports_from_py:
        # Functions exist in both - check if they match
        for func_name in duplicated_funcs:
            # Extract function body from both
            py_match = re.search(rf'def\s+{func_name}\s*\([^)]*\):.*?(?=\ndef\s|\nclass\s|\Z)', py_code, re.DOTALL)
            nb_match = re.search(rf'def\s+{func_name}\s*\([^)]*\):.*?(?=\ndef\s|\nclass\s|\Z)', nb_code, re.DOTALL)
            if py_match and nb_match:
                py_body = py_match.group(0).strip()
                nb_body = nb_match.group(0).strip()
                if py_body != nb_body:
                    # Show first difference
                    py_lines = py_body.split('\n')
                    nb_lines = nb_body.split('\n')
                    for i, (pl, nl) in enumerate(zip(py_lines, nb_lines)):
                        if pl != nl:
                            mismatches.append(f"  FUNCTION '{func_name}' differs at line {i+1}:\n    .py:    {pl.strip()[:120]}\n    .ipynb: {nl.strip()[:120]}")
                            break
                    else:
                        if len(py_lines) != len(nb_lines):
                            mismatches.append(f"  FUNCTION '{func_name}' length differs: .py={len(py_lines)} lines, .ipynb={len(nb_lines)} lines")
    
    # Check prompt templates match
    py_prompts = py_elements.get('prompts', [])
    nb_prompts = nb_elements.get('prompts', [])
    if len(py_prompts) != len(nb_prompts):
        mismatches.append(f"  PROMPT count differs: .py has {len(py_prompts)}, .ipynb has {len(nb_prompts)}")
    
    return mismatches

print("=" * 80)
print("NOTEBOOK vs .PY VALIDATION REPORT")
print("=" * 80)

all_mismatches = {}
for nb_name, py_name in MAPPING.items():
    print(f"\n--- {nb_name}.ipynb vs {py_name}.py ---")
    result = compare_pair(nb_name, py_name)
    if isinstance(result, str):
        print(f"  ERROR: {result}")
    elif result:
        all_mismatches[nb_name] = result
        for m in result:
            print(m)
    else:
        print("  ✅ No mismatches detected")

print(f"\n{'=' * 80}")
print(f"SUMMARY: {len(all_mismatches)} notebooks with mismatches out of {len(MAPPING)}")
if all_mismatches:
    print("Notebooks needing fixes:", list(all_mismatches.keys()))
print("=" * 80)
