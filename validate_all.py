"""Validate all benchmark task files and notebooks."""
import ast
import json
import os


def validate_task_files():
    """Check all task .py files for syntax errors."""
    tracks = [
        'metacognition', 'attention', 'executive_functions',
        'learning', 'social_cognition'
    ]
    all_ok = True
    total = 0
    for track in tracks:
        task_dir = f'benchmarks/{track}'
        if not os.path.isdir(task_dir):
            continue
        for fname in sorted(os.listdir(task_dir)):
            if fname.startswith('task_') and fname.endswith('.py'):
                total += 1
                path = os.path.join(task_dir, fname)
                try:
                    source = open(path).read()
                    ast.parse(source)
                except SyntaxError as err:
                    print(f'  SYNTAX ERROR: {path}: {err}')
                    all_ok = False
    if all_ok:
        print(f'All {total} task files parse OK')
    return all_ok


def validate_notebooks():
    """Check all notebooks have percent-choose and @kbench.task."""
    notebooks_dir = 'notebooks'
    if not os.path.isdir(notebooks_dir):
        print('  No notebooks/ directory found')
        return False
    issues = []
    count = 0
    for nb in sorted(os.listdir(notebooks_dir)):
        if not nb.endswith('.ipynb'):
            continue
        count += 1
        filepath = os.path.join(notebooks_dir, nb)
        fobj = open(filepath)
        content = json.load(fobj)
        fobj.close()
        cells = content.get('cells', [])
        has_choose = any(
            '%choose' in ''.join(c.get('source', []))
            for c in cells
        )
        has_task_decorator = any(
            '@kbench.task' in ''.join(c.get('source', []))
            for c in cells
        )
        if not has_choose:
            issues.append(f'{nb}: missing %choose')
        if not has_task_decorator:
            issues.append(f'{nb}: missing @kbench.task')
    if issues:
        print('  Notebook issues:')
        for i in issues:
            print(f'    - {i}')
        return False
    print(f'All {count} notebooks validated: have %choose and @kbench.task')
    return True


if __name__ == '__main__':
    print('=== Task File Validation ===')
    t_ok = validate_task_files()
    print()
    print('=== Notebook Validation ===')
    n_ok = validate_notebooks()
    print()
    if t_ok and n_ok:
        print('All validations passed!')
    else:
        print('Some validations FAILED')
        exit(1)
