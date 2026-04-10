#!/usr/bin/env python3
"""
Push ALL remaining notebooks to Kaggle in one run.
Waits 30s between each push to stay under rate limits.
Run: .venv/bin/python3 scripts/kaggle_push_all.py
"""
import json, os, subprocess, tempfile, shutil, sys, time
sys.stdout.reconfigure(line_buffering=True)

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")
UPDATED_FILE = os.path.join(REPO, "scripts/.kaggle_updated_v2.txt")
DELAY = 30  # seconds between pushes

NOTEBOOKS = {
    "ianstudy/agi-bench-2026-error-detection-metacog": "notebooks/metacog_error_detection.ipynb",
    "ianstudy/agi-bench-2026-learning-monitoring-task": "notebooks/metacog_learning_monitoring.ipynb",
    "ianstudy/metacog-ctrl-test-apr08": "notebooks/metacog_control.ipynb",
    "ianstudy/epistemic-revision-benchmark-agi-2026a": "notebooks/metacog_epistemic_revision.ipynb",
    "ianstudy/agi-bench-2026-vigilance-attention": "notebooks/attention_vigilance.ipynb",
    "ianstudy/divided-attention-benchmark-agi-2026a": "notebooks/attention_divided.ipynb",
    "ianstudy/agi-bench-2026-instruction-update-task": "notebooks/attention_instruction_update.ipynb",
    "ianstudy/wcst-benchmark-agi-2026a": "notebooks/exec_func_wcst.ipynb",
    "ianstudy/agi-bench-2026-tower-of-london-task": "notebooks/exec_func_tol.ipynb",
    "ianstudy/agi-bench-task-switching": "notebooks/exec_func_task_switch.ipynb",
    "ianstudy/agi-bench-n-back": "notebooks/exec_func_nback.ipynb",
    "ianstudy/agi-bench-false-belief-tom": "notebooks/social_cog_false_belief.ipynb",
    "ianstudy/agi-bench-pragmatic-inference": "notebooks/social_cog_pragmatic.ipynb",
    "ianstudy/sarcasm-detection-benchmark-agi-2026a": "notebooks/social_cog_sarcasm.ipynb",
    "ianstudy/fok-sub-metrics-benchmark": "notebooks/metacog_fok_submetrics.ipynb",
    "ianstudy/jol-sub-metrics-benchmark": "notebooks/metacog_jol_submetrics.ipynb",
    "ianstudy/agi-bench-metacog-error-det-submetrics": "notebooks/metacog_error_detection_submetrics.ipynb",
#    "ianstudy/submission-overview-agi-bench-apr08": "notebooks/submission_overview.ipynb",  # REMOVED: merged into SUBMISSION_NARRATIVE.md
}

updated = set()
if os.path.exists(UPDATED_FILE):
    with open(UPDATED_FILE) as f:
        updated = {l.strip() for l in f if l.strip()}

remaining = [(s, p) for s, p in NOTEBOOKS.items() if s not in updated]
print(f"📦 {len(remaining)} notebooks to push ({len(updated)} already done)")

pushed = 0
for i, (slug, nb_rel) in enumerate(remaining):
    nb_file = os.path.basename(nb_rel)
    full = os.path.join(REPO, nb_rel)
    if not os.path.exists(full):
        print(f"  ⚠ {nb_file} not found, skipping")
        continue

    tmpdir = tempfile.mkdtemp()
    shutil.copy(full, os.path.join(tmpdir, nb_file))
    title = "AGI Bench: " + slug.split("/")[-1].replace("-", " ").title()
    meta = {
        "id": slug, "title": title,
        "code_file": nb_file, "language": "python",
        "kernel_type": "notebook", "is_private": "false",
        "enable_gpu": "false", "enable_internet": "true",
        "keywords": ["agi-benchmark"],
        "competition_sources": ["kaggle-measuring-agi"]
    }
    with open(os.path.join(tmpdir, "kernel-metadata.json"), "w") as f:
        json.dump(meta, f)

    r = subprocess.run([KAGGLE, "kernels", "push", "-p", tmpdir],
                       capture_output=True, text=True, timeout=60)
    shutil.rmtree(tmpdir)

    if r.returncode == 0:
        pushed += 1
        print(f"  ✓ [{pushed}/{len(remaining)}] {slug}")
        with open(UPDATED_FILE, "a") as f:
            f.write(slug + "\n")
    elif "429" in r.stdout or "429" in r.stderr:
        print(f"  ⛔ Rate limited at {slug}. Pushed {pushed} this run.")
        print(f"     Wait and re-run, or use the backoff cron.")
        break
    else:
        print(f"  ✗ {slug}: {r.stdout.strip()[:100]}")

    if i < len(remaining) - 1:
        print(f"     Waiting {DELAY}s...")
        time.sleep(DELAY)

print(f"\n{'='*40}")
print(f"Pushed: {pushed} | Remaining: {len(remaining) - pushed}")
