#!/usr/bin/env python3
"""Fix notebook source arrays — ensure each line ends with newline."""
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
        src = cell.get("source", [])
        if isinstance(src, list):
            new_src = []
            for i, line in enumerate(src):
                if not line.endswith('\n') and i < len(src) - 1:
                    new_src.append(line + '\n')
                    changed = True
                else:
                    new_src.append(line)
            cell["source"] = new_src
    
    if changed:
        with open(path, 'w') as fh:
            json.dump(nb, fh, indent=1)
        print(f"✓ Fixed: {f}")
        fixed += 1

print(f"\nFixed {fixed} notebooks")
