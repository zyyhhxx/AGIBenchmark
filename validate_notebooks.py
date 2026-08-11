#!/usr/bin/env python3
"""Validate all Kaggle benchmark notebooks for required elements."""
import json
import glob
import os

issues = []
for nb_path in sorted(glob.glob('notebooks/*.ipynb')):
    f = open(nb_path)
    nb = json.load(f)
    f.close()
    cells = nb.get('cells', [])
    sources = [''.join(c.get('source', [])) for c in cells]
    all_src = '\n'.join(sources)
    name = os.path.basename(nb_path)
    if '%choose' not in all_src:
        issues.append(f'{name}: MISSING %choose')
    if 'kaggle_benchmarks' not in all_src and 'kbench' not in all_src:
        issues.append(f'{name}: MISSING kaggle_benchmarks import')
    if '@kbench.task' not in all_src and '@kb.task' not in all_src:
        issues.append(f'{name}: MISSING @kbench.task decorator')

nb_count = len(glob.glob('notebooks/*.ipynb'))
if issues:
    print(f'ISSUES FOUND ({len(issues)}):')
    for i in issues:
        print(f'  - {i}')
else:
    print(f'All {nb_count} notebooks pass basic validation.')
print(f'Total notebooks checked: {nb_count}')
