#!/usr/bin/env python3
"""
Incremental Kaggle notebook updater. Pushes 2 notebooks, then exits.
Designed to be called by a cron job every 15 minutes.

Usage: .venv/bin/python3 scripts/kaggle_incremental_push.py
"""
import json, os, subprocess, tempfile, shutil, sys, time
sys.stdout.reconfigure(line_buffering=True)

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")
UPDATED_FILE = os.path.join(REPO, "scripts/.kaggle_updated_v2.txt")
MAX_PER_RUN = 2

NOTEBOOKS = {
    "ianstudy/feeling-of-knowing-fok-benchmark": "notebooks/metacog_fok.ipynb",
    "ianstudy/judgment-of-learning-jol-benchmark": "notebooks/metacog_jol.ipynb",
    "ianstudy/metacognitive-calibration-benchmark": "notebooks/metacog_calibration.ipynb",
    "ianstudy/agi-bench-2026-error-detection-metacog": "notebooks/metacog_error_detection.ipynb",
    "ianstudy/agi-bench-2026-learning-monitoring-task": "notebooks/metacog_learning_monitoring.ipynb",
    "ianstudy/metacog-ctrl-test-apr08": "notebooks/metacog_control.ipynb",
    "ianstudy/epistemic-revision-benchmark-agi-2026a": "notebooks/metacog_epistemic_revision.ipynb",
    "ianstudy/agi-bench-learning-curves": "notebooks/learning_curves.ipynb",
    "ianstudy/agi-bench-near-vs-far-transfer": "notebooks/learning_transfer.ipynb",
    "ianstudy/agi-bench-proactive-retroactive-interference": "notebooks/learning_interference.ipynb",
    "ianstudy/agi-bench-curriculum-sensitivity": "notebooks/learning_curriculum.ipynb",
    "ianstudy/agi-bench-selective-attention": "notebooks/attention_selective.ipynb",
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
print(f"Remaining: {len(remaining)} / {len(NOTEBOOKS)}")

if not remaining:
    print("✅ All notebooks updated!")
    sys.exit(0)

pushed = 0
for slug, nb_path in remaining[:MAX_PER_RUN]:
    full = os.path.join(REPO, nb_path)
    if not os.path.exists(full):
        print(f"⏭️ Missing: {nb_path}")
        continue

    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copy2(full, os.path.join(tmpdir, os.path.basename(nb_path)))
        user, kernel = slug.split("/")
        meta = {
            "id": slug,
            "title": kernel,
            "code_file": os.path.basename(nb_path),
            "language": "python",
            "kernel_type": "notebook",
            "is_private": False,
            "enable_gpu": False,
            "enable_tpu": False,
            "enable_internet": True,
            "competition_sources": ["kaggle-measuring-agi"],
        }
        with open(os.path.join(tmpdir, "kernel-metadata.json"), "w") as f:
            json.dump(meta, f, indent=2)

        r = subprocess.run([KAGGLE, "kernels", "push", "-p", tmpdir],
                          capture_output=True, text=True, timeout=60)
        out = (r.stdout + r.stderr).strip()

        if r.returncode == 0 and "successfully pushed" in out.lower():
            print(f"✅ {slug}")
            with open(UPDATED_FILE, 'a') as uf:
                uf.write(f"{slug}\n")
            pushed += 1
            if pushed < MAX_PER_RUN:
                time.sleep(10)
        elif "429" in out:
            print(f"⛔ Rate limited at {slug}. Will retry next run.")
            break
        else:
            print(f"❌ {slug}: {out[:200]}")
    finally:
        shutil.rmtree(tmpdir)

print(f"\nPushed {pushed} this run. {len(remaining) - pushed} remaining.")
