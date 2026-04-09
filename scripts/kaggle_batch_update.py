#!/usr/bin/env python3
"""
Batch update all existing public Kaggle notebooks with latest local versions.
Run this once the API rate limit lifts.
Also attempts to upload the 4 remaining new notebooks.

Usage: .venv/bin/python3 scripts/kaggle_batch_update.py [--dry-run]
"""
import json, os, subprocess, tempfile, shutil, sys, time

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")
DRY_RUN = "--dry-run" in sys.argv

# Mapping: local notebook file -> existing Kaggle slug
# These are notebooks already public on Kaggle that we want to update
EXISTING_NOTEBOOKS = {
    "metacog_fok.ipynb": "ianstudy/agi-bench-feeling-of-knowing-fok",
    "metacog_jol.ipynb": "ianstudy/agi-bench-judgment-of-learning-jol",
    "metacog_calibration.ipynb": "ianstudy/agi-bench-calibration",
    "metacog_error_detection.ipynb": "ianstudy/agi-bench-2026-error-detection-metacog",
    "metacog_learning_monitoring.ipynb": "ianstudy/agi-bench-2026-learning-monitoring-task",
    "metacog_fok_submetrics.ipynb": "ianstudy/agi-bench-fok-sub-metrics",
    "metacog_jol_submetrics.ipynb": "ianstudy/agi-bench-jol-sub-metrics",
    "metacog_error_detection_submetrics.ipynb": "ianstudy/agi-bench-metacog-error-det-submetrics",
    "metacog_control.ipynb": "ianstudy/metacog-ctrl-test-apr08",
    "metacog_epistemic_revision.ipynb": "ianstudy/epistemic-revision-benchmark-agi-2026a",
    "learning_curves.ipynb": "ianstudy/agi-bench-learning-curves",
    "learning_transfer.ipynb": "ianstudy/agi-bench-near-vs-far-transfer",
    "learning_interference.ipynb": "ianstudy/agi-bench-proactive-retroactive-interference",
    "learning_curriculum.ipynb": "ianstudy/agi-bench-curriculum-sensitivity",
    "attention_selective.ipynb": "ianstudy/agi-bench-selective-attention",
    "attention_vigilance.ipynb": "ianstudy/agi-bench-2026-vigilance-attention",
    "attention_divided.ipynb": "ianstudy/divided-attention-benchmark-agi-2026a",
    "attention_instruction_update.ipynb": "ianstudy/agi-bench-2026-instruction-update-task",
    "exec_func_wcst.ipynb": "ianstudy/wcst-benchmark-agi-2026a",
    "exec_func_tol.ipynb": "ianstudy/agi-bench-2026-tower-of-london-task",
    "exec_func_nback.ipynb": "ianstudy/agi-bench-n-back",
    "exec_func_task_switch.ipynb": "ianstudy/agi-bench-task-switching",
    "social_cog_false_belief.ipynb": "ianstudy/agi-bench-false-belief-tom",
    "social_cog_pragmatic.ipynb": "ianstudy/agi-bench-pragmatic-inference",
    "social_cog_sarcasm.ipynb": "ianstudy/sarcasm-detection-benchmark-agi-2026a",
    "submission_overview.ipynb": "ianstudy/submission-overview-agi-bench-apr08",
}

# New notebooks that need uploading (not yet on Kaggle)
NEW_NOTEBOOKS = {
    "exec_func_crt.ipynb": ("ianstudy/agi-bench-cognitive-reflection-test", "AGI Bench: Cognitive Reflection Test"),
    "metacog_canary.ipynb": ("ianstudy/agi-bench-contamination-canary", "AGI Bench: Contamination Canary"),
    "metacog_epistemic_humility.ipynb": ("ianstudy/agi-bench-epistemic-humility", "AGI Bench: Epistemic Humility"),
    "social_cog_emotional_prosody.ipynb": ("ianstudy/agi-bench-emotional-prosody", "AGI Bench: Emotional Prosody"),
}


def push_notebook(notebook_file, slug, title=None):
    """Push a notebook to Kaggle."""
    nb_path = os.path.join(REPO, "notebooks", notebook_file)
    if not os.path.exists(nb_path):
        print(f"  ⚠ Missing: {nb_path}")
        return False

    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copy(nb_path, tmpdir)
        meta = {
            "id": slug,
            "title": title or slug.split("/")[1],
            "code_file": notebook_file,
            "language": "python",
            "kernel_type": "notebook",
            "is_private": False,
            "enable_gpu": False,
            "enable_internet": True,
            "competition_sources": ["kaggle-measuring-agi"],
        }
        with open(os.path.join(tmpdir, "kernel-metadata.json"), "w") as f:
            json.dump(meta, f)

        if DRY_RUN:
            print(f"  [DRY RUN] Would push {notebook_file} → {slug}")
            return True

        r = subprocess.run(
            [KAGGLE, "kernels", "push", "-p", tmpdir],
            capture_output=True, text=True, timeout=60
        )
        if r.returncode == 0:
            print(f"  ✅ {notebook_file} → {slug}")
            return True
        elif "429" in r.stderr or "Too Many Requests" in r.stderr:
            print(f"  ⛔ Rate limited on {notebook_file}")
            return None  # Signal to stop
        else:
            print(f"  ❌ {notebook_file}: {r.stderr.strip()[:100]}")
            return False
    finally:
        shutil.rmtree(tmpdir)


def main():
    print(f"{'[DRY RUN] ' if DRY_RUN else ''}Kaggle Batch Update")
    print(f"{'=' * 60}")

    # First try new notebooks
    print(f"\n📤 New notebooks ({len(NEW_NOTEBOOKS)}):")
    new_ok = 0
    for nb_file, (slug, title) in NEW_NOTEBOOKS.items():
        result = push_notebook(nb_file, slug, title)
        if result is None:
            print("  Rate limited — stopping new uploads.")
            break
        if result:
            new_ok += 1
        time.sleep(5)

    # Then update existing
    print(f"\n🔄 Updating existing notebooks ({len(EXISTING_NOTEBOOKS)}):")
    update_ok = 0
    for nb_file, slug in EXISTING_NOTEBOOKS.items():
        result = push_notebook(nb_file, slug)
        if result is None:
            print("  Rate limited — stopping updates.")
            break
        if result:
            update_ok += 1
        time.sleep(3)

    print(f"\n{'=' * 60}")
    print(f"New: {new_ok}/{len(NEW_NOTEBOOKS)} | Updated: {update_ok}/{len(EXISTING_NOTEBOOKS)}")


if __name__ == "__main__":
    main()
