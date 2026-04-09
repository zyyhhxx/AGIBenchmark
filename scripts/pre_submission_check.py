#!/usr/bin/env python3
"""
Final pre-submission checklist validation.
Checks all competition requirements are met.
"""
import json, os, glob, ast

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check(name, condition, detail=""):
    status = "✓" if condition else "✗"
    print(f"  {status} {name}{': ' + detail if detail else ''}")
    return condition

def main():
    print("=" * 60)
    print("AGI BENCHMARK — PRE-SUBMISSION CHECKLIST")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # 1. All 5 tracks covered
    print("\n[1] Track Coverage")
    tracks = ["metacognition", "learning", "attention", "executive_functions", "social_cognition"]
    for track in tracks:
        exists = os.path.isdir(os.path.join(REPO, "benchmarks", track))
        design = os.path.isfile(os.path.join(REPO, "benchmarks", track, "DESIGN.md"))
        if check(f"Track: {track}", exists and design, f"dir={exists}, DESIGN.md={design}"):
            passed += 1
        else:
            failed += 1
    
    # 2. Benchmark count
    print("\n[2] Benchmark Count")
    task_files = glob.glob(os.path.join(REPO, "benchmarks/*/task_*.py"))
    task_files = [f for f in task_files if "__pycache__" not in f]
    if check(f"Task files", len(task_files) >= 26, f"{len(task_files)} files"):
        passed += 1
    else:
        failed += 1
    
    # 3. Notebooks
    print("\n[3] Notebook Quality")
    notebooks = sorted(glob.glob(os.path.join(REPO, "notebooks/*.ipynb")))
    if check(f"Notebook count", len(notebooks) >= 30, f"{len(notebooks)} notebooks"):
        passed += 1
    else:
        failed += 1
    
    pip_count = 0
    run_count = 0
    task_count = 0
    for nb_path in notebooks:
        with open(nb_path) as f:
            nb = json.load(f)
        all_src = ''.join(''.join(c['source']) for c in nb['cells'])
        if 'pip install' in all_src: pip_count += 1
        if '.run(' in all_src: run_count += 1
        if '@kbench.task' in all_src: task_count += 1
    
    if check(f"Pip install cells", pip_count == len(notebooks), f"{pip_count}/{len(notebooks)}"):
        passed += 1
    else:
        failed += 1
    
    # 4. Documentation
    print("\n[4] Documentation")
    docs = [
        "SUBMISSION_NARRATIVE.md",
        "KAGGLE_DISCUSSION_DRAFT.md",
        "KAGGLE_SUBMISSION_PLAYBOOK.md",
        "QUICKSTART.md",
        "IAN_TODO.md",
        "STATUS.md",
        "benchmarks/METHODOLOGY.md",
        "benchmarks/COGNITIVE_RATIONALE.md",
        "benchmarks/HUMAN_BASELINES.md",
    ]
    for doc in docs:
        exists = os.path.isfile(os.path.join(REPO, doc))
        if check(f"Doc: {doc}", exists):
            passed += 1
        else:
            failed += 1
    
    # 5. Psychometric validation
    print("\n[5] Validation Artifacts")
    validations = [
        "results/mock_validation.json",
        "results/correlation_analysis.json",
        "results/reliability_analysis.json",
        "results/stratified_calibration.json",
    ]
    for v in validations:
        exists = os.path.isfile(os.path.join(REPO, v))
        if check(f"Validation: {v}", exists):
            passed += 1
        else:
            failed += 1
    
    # 6. Git status
    print("\n[6] Git Status")
    import subprocess
    r = subprocess.run(["git", "-C", REPO, "status", "--porcelain"], capture_output=True, text=True)
    uncommitted = len([l for l in r.stdout.strip().split('\n') if l.strip()])
    if check(f"Uncommitted files", uncommitted <= 2, f"{uncommitted} files"):
        passed += 1
    else:
        failed += 1
    
    # Summary
    total = passed + failed
    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed}/{total} checks passed")
    if failed > 0:
        print(f"⚠ {failed} checks FAILED")
    else:
        print("✅ ALL CHECKS PASSED — Ready for submission!")
    print(f"{'=' * 60}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
