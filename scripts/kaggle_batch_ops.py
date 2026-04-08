#!/usr/bin/env python3
"""
All-in-one Kaggle notebook management script.
Handles: upload new notebooks, make existing private ones public, standardize titles.
Uses exponential backoff. Safe to re-run (idempotent).
Run: python3 scripts/kaggle_batch_ops.py [--dry-run]
"""
import json, os, subprocess, tempfile, shutil, time, sys

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")
DRY_RUN = "--dry-run" in sys.argv

# ─── Desired state: slug → (notebook_path, desired_title) ─────
# These should all be PUBLIC with standardized titles.
DESIRED_STATE = {
    # Metacognition (11)
    "ianstudy/agi-bench-feeling-of-knowing-fok": ("notebooks/metacog_fok.ipynb", "AGI Bench: Feeling-of-Knowing (FOK)"),
    "ianstudy/agi-bench-judgment-of-learning-jol": ("notebooks/metacog_jol.ipynb", "AGI Bench: Judgment-of-Learning (JOL)"),
    "ianstudy/agi-bench-calibration": ("notebooks/metacog_calibration.ipynb", "AGI Bench: Metacognitive Calibration"),
    "ianstudy/agi-bench-2026-error-detection-metacog": ("notebooks/metacog_error_detection.ipynb", "AGI Bench: Error Detection"),
    "ianstudy/agi-bench-2026-learning-monitoring-task": ("notebooks/metacog_learning_monitoring.ipynb", "AGI Bench: Learning Monitoring"),
    "ianstudy/metacog-ctrl-test-apr08": ("notebooks/metacog_control.ipynb", "AGI Bench: Metacognitive Control"),
    "ianstudy/epistemic-revision-benchmark-agi-2026a": ("notebooks/metacog_epistemic_revision.ipynb", "AGI Bench: Epistemic Revision"),
    "ianstudy/agi-bench-2026-epistemic-humility": ("notebooks/metacog_epistemic_humility.ipynb", "AGI Bench: Epistemic Humility"),
    "ianstudy/agi-bench-2026-metacog-canary": ("notebooks/metacog_canary.ipynb", "AGI Bench: Contamination Canary"),
    "ianstudy/agi-bench-fok-sub-metrics": ("notebooks/metacog_fok_submetrics.ipynb", "AGI Bench: FOK Sub-metrics"),
    "ianstudy/agi-bench-jol-sub-metrics": ("notebooks/metacog_jol_submetrics.ipynb", "AGI Bench: JOL Sub-metrics"),
    "ianstudy/agi-bench-metacog-error-det-submetrics": ("notebooks/metacog_error_detection_submetrics.ipynb", "AGI Bench: Error Detection Sub-metrics"),
    # Learning (4)
    "ianstudy/agi-bench-learning-curves": ("notebooks/learning_curves.ipynb", "AGI Bench: Learning Curves"),
    "ianstudy/agi-bench-near-vs-far-transfer": ("notebooks/learning_transfer.ipynb", "AGI Bench: Near vs Far Transfer"),
    "ianstudy/agi-bench-proactive-retroactive-interference": ("notebooks/learning_interference.ipynb", "AGI Bench: Proactive/Retroactive Interference"),
    "ianstudy/agi-bench-curriculum-sensitivity": ("notebooks/learning_curriculum.ipynb", "AGI Bench: Curriculum Sensitivity"),
    # Attention (4)
    "ianstudy/agi-bench-selective-attention": ("notebooks/attention_selective.ipynb", "AGI Bench: Selective Attention"),
    "ianstudy/agi-bench-2026-vigilance-attention": ("notebooks/attention_vigilance.ipynb", "AGI Bench: Sustained Attention (Vigilance)"),
    "ianstudy/divided-attention-benchmark-agi-2026a": ("notebooks/attention_divided.ipynb", "AGI Bench: Divided Attention"),
    "ianstudy/agi-bench-2026-instruction-update-task": ("notebooks/attention_instruction_update.ipynb", "AGI Bench: Instruction Update"),
    # Executive Functions (5)
    "ianstudy/wcst-benchmark-agi-2026a": ("notebooks/exec_func_wcst.ipynb", "AGI Bench: WCST"),
    "ianstudy/agi-bench-2026-tower-of-london-task": ("notebooks/exec_func_tol.ipynb", "AGI Bench: Tower of London"),
    "ianstudy/agi-bench-task-switching": ("notebooks/exec_func_task_switch.ipynb", "AGI Bench: Task Switching"),
    "ianstudy/agi-bench-n-back": ("notebooks/exec_func_nback.ipynb", "AGI Bench: N-Back"),
    "ianstudy/agi-bench-2026-crt-exec-func": ("notebooks/exec_func_crt.ipynb", "AGI Bench: Cognitive Reflection Test"),
    # Social Cognition (3)
    "ianstudy/agi-bench-false-belief-tom": ("notebooks/social_cog_false_belief.ipynb", "AGI Bench: False Belief ToM"),
    "ianstudy/agi-bench-pragmatic-inference": ("notebooks/social_cog_pragmatic.ipynb", "AGI Bench: Pragmatic Inference"),
    "ianstudy/sarcasm-detection-benchmark-agi-2026a": ("notebooks/social_cog_sarcasm.ipynb", "AGI Bench: Sarcasm Detection"),
    "ianstudy/agi-bench-2026-emotional-prosody": ("notebooks/social_cog_emotional_prosody.ipynb", "AGI Bench: Emotional Prosody"),
    # Overview
    "ianstudy/submission-overview-agi-bench-apr08": ("notebooks/submission_overview.ipynb", "AGI Bench: Submission Overview"),
}

MAX_RETRIES = 5
BASE_DELAY = 30
SUCCESS_DELAY = 15

def push_kernel(slug, nb_path, title):
    full_nb = os.path.join(REPO, nb_path)
    if not os.path.exists(full_nb):
        return "skip", f"file not found: {nb_path}"
    
    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copy2(full_nb, os.path.join(tmpdir, os.path.basename(nb_path)))
        # Kaggle requires title to resolve to the slug, so use slug's name part
        slug_title = slug.split('/')[1]
        meta = {
            "id": slug,
            "title": slug_title,
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
        
        if DRY_RUN:
            return "dry_run", f"would push {slug} as '{title}'"
        
        for attempt in range(MAX_RETRIES):
            result = subprocess.run(
                [KAGGLE, "kernels", "push", "-p", tmpdir],
                capture_output=True, text=True, timeout=60
            )
            out = result.stdout.strip() + result.stderr.strip()
            if result.returncode == 0:
                return "success", out
            elif "429" in out:
                delay = BASE_DELAY * (2 ** attempt)
                print(f"  ⏳ 429 rate limited, retry in {delay}s ({attempt+1}/{MAX_RETRIES})")
                time.sleep(delay)
            else:
                return "error", out
        return "error", "exhausted retries (429)"
    finally:
        shutil.rmtree(tmpdir)


# ─── Skip already-pushed ─────
SKIP_FILE = os.path.join(REPO, "scripts/.kaggle_pushed_public.txt")
already_pushed = set()
if os.path.exists(SKIP_FILE):
    with open(SKIP_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                already_pushed.add(line)

# ─── Main ─────
print(f"{'='*60}")
print(f"Kaggle Batch Operations {'(DRY RUN)' if DRY_RUN else ''}")
print(f"{'='*60}")
print(f"Total notebooks to manage: {len(DESIRED_STATE)}")
print(f"Already pushed: {len(already_pushed)}")

success, failed, skipped = [], [], []

for slug, (nb_path, title) in DESIRED_STATE.items():
    if slug in already_pushed:
        print(f"⏭️ {title} (already pushed)")
        skipped.append((slug, "already pushed"))
        continue
    status, msg = push_kernel(slug, nb_path, title)
    if status == "success":
        print(f"✅ {title}")
        success.append(slug)
        # Track successful push
        with open(SKIP_FILE, 'a') as f:
            f.write(f"{slug}\n")
        time.sleep(SUCCESS_DELAY)
    elif status == "skip":
        print(f"⏭️ {slug}: {msg}")
        skipped.append((slug, msg))
    elif status == "dry_run":
        print(f"🔍 {msg}")
    else:
        print(f"❌ {slug}: {msg}")
        failed.append((slug, msg))
        if "429" in msg:
            print(f"\n⛔ Rate limited. {len(success)} pushed so far. Re-run later for remaining.")
            break

print(f"\n--- Summary ---")
print(f"Success: {len(success)}/{len(DESIRED_STATE)}")
print(f"Failed: {len(failed)}, Skipped: {len(skipped)}")
if failed:
    print("\nFailed:")
    for s, e in failed:
        print(f"  {s}: {e[:80]}")
