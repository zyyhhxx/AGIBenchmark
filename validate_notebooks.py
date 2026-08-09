import json, os

notebooks_dir = 'notebooks'
issues = []
for nb in sorted(os.listdir(notebooks_dir)):
    if not nb.endswith('.ipynb'):
        continue
    with open(os.path.join(notebooks_dir, nb)) as f:\n        content = json.load(f)\n    cells = content.get('cells', [])\n    has_choose = any('%choose' in ''.join(c.get('source', [])) for c in cells)\n    has_task_decorator = any('@kbench.task' in ''.join(c.get('source', [])) for c in cells)
    if not has_choose:
        issues.append(f'{nb}: missing %choose')
    if not has_task_decorator:
        issues.append(f'{nb}: missing @kbench.task')

if issues:
    print('Issues found:')
    for i in issues:
        print(f'  - {i}')
else:
    count = len([f for f in os.listdir(notebooks_dir) if f.endswith('.ipynb')])
    print(f'All {count} notebooks validated OK: have %choose and @kbench.task')
