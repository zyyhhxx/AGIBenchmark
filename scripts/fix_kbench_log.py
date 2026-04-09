#!/usr/bin/env python3
"""Fix kbench.log calls in notebooks — replace with safe print-based logging."""
import json, os

NB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notebooks")

fixed = 0
for f in sorted(os.listdir(NB_DIR)):
    if not f.endswith('.ipynb'):
        continue
    path = os.path.join(NB_DIR, f)
    nb = json.load(open(path))
    changed = False
    
    for cell in nb.get("cells", []):
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        if "kbench.log(" in src:
            # Add safe_log definition if not already present
            new_src = src
            if "_safe_log" not in src:
                new_src = new_src.replace(
                    "import kaggle_benchmarks as kbench",
                    "import kaggle_benchmarks as kbench\nimport json as _json\ndef _safe_log(data): print(_json.dumps(data, indent=2, default=str))"
                )
            new_src = new_src.replace("kbench.log(", "_safe_log(")
            
            if new_src != src:
                cell["source"] = [line + "\n" for line in new_src.split("\n")]
                # Fix last line (no trailing newline)
                if cell["source"] and cell["source"][-1].endswith("\n\n"):
                    cell["source"][-1] = cell["source"][-1][:-1]
                changed = True
    
    if changed:
        with open(path, 'w') as fh:
            json.dump(nb, fh, indent=1)
        print(f"✓ Fixed: {f}")
        fixed += 1

print(f"\nFixed {fixed} notebooks")
