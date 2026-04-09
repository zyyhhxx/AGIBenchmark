#!/usr/bin/env python3
"""
Batch update all 26 already-public notebooks on Kaggle with latest code.

This pushes the latest hardened versions (with structured output fallbacks,
improved parsing, etc.) to replace the existing versions on Kaggle.

Usage: .venv/bin/python3 scripts/kaggle_batch_update_v2.py [--dry-run]
"""
import json, os, subprocess, tempfile, shutil, sys, time
sys.stdout.reconfigure(line_buffering=True)  # Ensure output is flushed

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")

DRY_RUN = "--dry-run" in sys.argv
UPDATED_FILE = os.path.join(REPO, "scripts/.kaggle_updated_v2.txt")

# Track already-updated
updated_set = set()
if os.path.exists(UPDATED_FILE):
    with open(UPDATED_FILE) as f:
        updated_set = {l.strip() for l in f if l.strip()}

# Map slug → notebook file for all public benchmark notebooks
# Slugs verified via `kaggle kernels list --mine` on 2026-04-09
NOTEBOOKS = {
    # Metacognition
    "ianstudy/feeling-of-knowing-fok-benchmark": "notebooks/metacog_fok.ipynb",
    "ianstudy/judgment-of-learning-jol-benchmark": "notebooks/metacog_jol.ipynb",
    "ianstudy/metacognitive-calibration-benchmark": "notebooks/metacog_calibration.ipynb",
    "ianstudy/agi-bench-2026-error-detection-metacog": "notebooks/metacog_error_detection.ipynb",
    "ianstudy/agi-bench-2026-learning-monitoring-task": "notebooks/metacog_learning_monitoring.ipynb",
    "ianstudy/metacog-ctrl-test-apr08": "notebooks/metacog_control.ipynb",
    "ianstudy/epistemic-revision-benchmark-agi-2026a": "notebooks/metacog_epistemic_revision.ipynb",
    # Learning
    "ianstudy/agi-bench-learning-curves": "notebooks/learning_curves.ipynb",
    "ianstudy/agi-bench-near-vs-far-transfer": "notebooks/learning_transfer.ipynb",
    "ianstudy/agi-bench-proactive-retroactive-interference": "notebooks/learning_interference.ipynb",
    "ianstudy/agi-bench-curriculum-sensitivity": "notebooks/learning_curriculum.ipynb",
    # Attention
    "ianstudy/agi-bench-selective-attention": "notebooks/attention_selective.ipynb",
    "ianstudy/agi-bench-2026-vigilance-attention": "notebooks/attention_vigilance.ipynb",
    "ianstudy/divided-attention-benchmark-agi-2026a": "notebooks/attention_divided.ipynb",
    "ianstudy/agi-bench-2026-instruction-update-task": "notebooks/attention_instruction_update.ipynb",
    # Executive Functions
    "ianstudy/wcst-benchmark-agi-2026a": "notebooks/exec_func_wcst.ipynb",
    "ianstudy/agi-bench-2026-tower-of-london-task": "notebooks/exec_func_tol.ipynb",
    "ianstudy/agi-bench-task-switching": "notebooks/exec_func_task_switch.ipynb",
    "ianstudy/agi-bench-n-back": "notebooks/exec_func_nback.ipynb",
    # Social Cognition
    "ianstudy/agi-bench-false-belief-tom": "notebooks/social_cog_false_belief.ipynb",
    "ianstudy/agi-bench-pragmatic-inference": "notebooks/social_cog_pragmatic.ipynb",
    "ianstudy/sarcasm-detection-benchmark-agi-2026a": "notebooks/social_cog_sarcasm.ipynb",
    # Sub-metrics
    "ianstudy/fok-sub-metrics-benchmark": "notebooks/metacog_fok_submetrics.ipynb",
    "ianstudy/jol-sub-metrics-benchmark": "notebooks/metacog_jol_submetrics.ipynb",
    "ianstudy/agi-bench-metacog-error-det-submetrics": "notebooks/metacog_error_detection_submetrics.ipynb",
    # Overview
    "ianstudy/submission-overview-agi-bench-apr08": "notebooks/submission_overview.ipynb",
}

ok = 0
fail = 0
rate_limited = 0

for slug, nb_path in NOTEBOOKS.items():
    if slug in updated_set:
        print(f"⏭️ Already updated: {slug}")
        continue
    full = os.path.join(REPO, nb_path)
    if not os.path.exists(full):
        print(f"⏭️ {slug}: missing {nb_path}")
        continue

    user, kernel = slug.split("/")
    title = kernel  # Use slug as title (will be overridden by existing)

    if DRY_RUN:
        print(f"🔍 Would update: {slug} ← {nb_path}")
        continue

    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copy2(full, os.path.join(tmpdir, os.path.basename(nb_path)))
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

        if r.returncode == 0:
            print(f"✅ {slug}")
            ok += 1
            with open(UPDATED_FILE, 'a') as uf:
                uf.write(f"{slug}\n")
            time.sleep(15)  # 15s between successful pushes
        elif "429" in out:
            rate_limited += 1
            wait = 120 * rate_limited  # Exponential backoff
            print(f"⛔ Rate limited at {slug} (#{ok+1}). Waiting {wait}s...")
            time.sleep(wait)
            # Retry once
            r2 = subprocess.run([KAGGLE, "kernels", "push", "-p", tmpdir],
                              capture_output=True, text=True, timeout=60)
            out2 = (r2.stdout + r2.stderr).strip()
            if r2.returncode == 0:
                print(f"✅ {slug} (retry)")
                ok += 1
                with open(UPDATED_FILE, 'a') as uf:
                    uf.write(f"{slug}\n")
                time.sleep(15)
            else:
                print(f"❌ {slug}: still failing: {out2[:100]}")
                fail += 1
                if rate_limited >= 5:
                    print(f"\n⛔ Too many rate limits ({rate_limited}). Stopping.")
                    break
        else:
            print(f"❌ {slug}: {out[:150]}")
            fail += 1
    finally:
        shutil.rmtree(tmpdir)

print(f"\n{'='*40}")
print(f"Updated: {ok}/{len(NOTEBOOKS)}")
print(f"Failed: {fail}")
print(f"Rate limited: {rate_limited}")
