#!/usr/bin/env python3
"""Pre-submission audit: check all benchmark task files."""
import os, re, ast, sys

BENCH_DIR = os.path.join(os.path.dirname(__file__), 'benchmarks')
tracks = ['metacognition', 'learning', 'attention', 'executive_functions', 'social_cognition']
issues = []
total = 0

for track in tracks:
    track_dir = os.path.join(BENCH_DIR, track)
    for fn in sorted(os.listdir(track_dir)):
        if not fn.startswith('task_') or not fn.endswith('.py'):
            continue
        total += 1
        fpath = os.path.join(track_dir, fn)
        with open(fpath) as f:
            src = f.read()
        
        tag = f"{track}/{fn}"
        
        # Check docstring
        try:
            tree = ast.parse(src)
            mod_doc = ast.get_docstring(tree)
            if not mod_doc:
                issues.append(f"[WARN] {tag}: no module docstring")
        except SyntaxError as e:
            issues.append(f"[ERROR] {tag}: syntax error: {e}")
            continue
        
        # Check for @kbench.task or @register_task or similar decorator
        has_decorator = bool(re.search(r'@kbench\.(task|register)', src) or 
                           re.search(r'def\s+(task_|run_benchmark|evaluate)', src))
        if not has_decorator:
            issues.append(f"[WARN] {tag}: no task function found")
        
        # Check score range assertions or clamp
        if 'max(0' in src or 'min(1' in src or 'clip' in src or 'clamp' in src:
            pass  # has clamping
        elif 'assert' in src and ('0' in src and '1' in src):
            pass
        # Not a hard error, just note
        
        print(f"  ✓ {tag}")

print(f"\nAudited {total} task files across {len(tracks)} tracks")
if issues:
    print(f"\n{len(issues)} issues found:")
    for iss in issues:
        print(f"  {iss}")
else:
    print("No issues found!")

# Check notebooks
NB_DIR = os.path.join(os.path.dirname(__file__), 'notebooks')
nb_count = len([f for f in os.listdir(NB_DIR) if f.endswith('.ipynb')])
print(f"\n{nb_count} notebooks in notebooks/")

# Check for DESIGN.md in each track
for track in tracks:
    design = os.path.join(BENCH_DIR, track, 'DESIGN.md')
    if os.path.exists(design):
        print(f"  ✓ {track}/DESIGN.md")
    else:
        print(f"  ✗ {track}/DESIGN.md MISSING")
