#!/usr/bin/env python3
"""Make all private Kaggle notebooks public by re-pushing with is_private=false.
Uses exponential backoff on 429 errors. Safe to re-run."""
import json, os, subprocess, tempfile, shutil, time, sys

KERNELS = {
    "ianstudy/agi-bench-2026-error-detection-metacog": "notebooks/metacog_error_detection.ipynb",
    "ianstudy/agi-bench-metacog-error-det-submetrics": "notebooks/metacog_error_detection_submetrics.ipynb",
    "ianstudy/agi-bench-2026-learning-monitoring-task": "notebooks/metacog_learning_monitoring.ipynb",
    "ianstudy/metacog-ctrl-test-apr08": "notebooks/metacog_control.ipynb",
    "ianstudy/epistemic-revision-benchmark-agi-2026a": "notebooks/metacog_epistemic_revision.ipynb",
    "ianstudy/agi-bench-2026-vigilance-attention": "notebooks/attention_vigilance.ipynb",
    "ianstudy/divided-attention-benchmark-agi-2026a": "notebooks/attention_divided.ipynb",
    "ianstudy/agi-bench-2026-instruction-update-task": "notebooks/attention_instruction_update.ipynb",
    "ianstudy/agi-bench-task-switching": "notebooks/exec_func_task_switch.ipynb",
    "ianstudy/agi-bench-n-back": "notebooks/exec_func_nback.ipynb",
    "ianstudy/wcst-benchmark-agi-2026a": "notebooks/exec_func_wcst.ipynb",
    "ianstudy/agi-bench-2026-tower-of-london-task": "notebooks/exec_func_tol.ipynb",
    "ianstudy/agi-bench-false-belief-tom": "notebooks/social_cog_false_belief.ipynb",
    "ianstudy/agi-bench-pragmatic-inference": "notebooks/social_cog_pragmatic.ipynb",
    "ianstudy/sarcasm-detection-benchmark-agi-2026a": "notebooks/social_cog_sarcasm.ipynb",
    "ianstudy/submission-overview-agi-bench-apr08": "notebooks/submission_overview.ipynb",
}

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")
MAX_RETRIES = 5
BASE_DELAY = 30  # seconds

success, failed, skipped = [], [], []

for slug, nb_path in KERNELS.items():
    full_nb = os.path.join(REPO, nb_path)
    if not os.path.exists(full_nb):
        skipped.append((slug, "file not found"))
        continue

    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copy2(full_nb, os.path.join(tmpdir, os.path.basename(nb_path)))
        meta = {
            "id": slug,
            "title": slug.split("/")[1],
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

        pushed = False
        for attempt in range(MAX_RETRIES):
            result = subprocess.run(
                [KAGGLE, "kernels", "push", "-p", tmpdir],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                print(f"✅ {slug}")
                success.append(slug)
                pushed = True
                time.sleep(15)  # delay between successes to avoid rate limit
                break
            elif "429" in result.stderr or "429" in result.stdout:
                delay = BASE_DELAY * (2 ** attempt)
                print(f"⏳ {slug}: 429 rate limited, retry in {delay}s (attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(delay)
            else:
                err = result.stderr.strip() or result.stdout.strip()
                print(f"❌ {slug}: {err}")
                failed.append((slug, err))
                break
        else:
            if not pushed:
                print(f"❌ {slug}: exhausted retries")
                failed.append((slug, "exhausted retries after 429s"))
    finally:
        shutil.rmtree(tmpdir)

print(f"\n--- Summary ---")
print(f"Success: {len(success)}/{len(KERNELS)}")
print(f"Failed: {len(failed)}, Skipped: {len(skipped)}")
for s, e in failed + skipped:
    print(f"  {s}: {e}")
