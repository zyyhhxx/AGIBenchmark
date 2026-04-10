#!/usr/bin/env python3
"""
Kaggle notebook push with exponential backoff.
Pushes 1 notebook per run, increases wait on 429.
Run from cron every 30 min.
"""
import json, os, subprocess, tempfile, shutil, sys, time
sys.stdout.reconfigure(line_buffering=True)

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")
UPDATED_FILE = os.path.join(REPO, "scripts/.kaggle_updated_v2.txt")
STATE_FILE = os.path.join(REPO, "scripts/.kaggle_push_state.json")

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

# Load state
state = {"last_429": 0, "consecutive_429": 0}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        state = json.load(f)

# Check backoff
now = time.time()
backoff_sec = min(3600 * 4, 1800 * (2 ** state.get("consecutive_429", 0)))
if now - state.get("last_429", 0) < backoff_sec:
    wait_min = int((backoff_sec - (now - state["last_429"])) / 60)
    print(f"⏳ Backing off. {wait_min}min remaining (429 streak: {state['consecutive_429']})")
    sys.exit(0)

# Load updated
updated = set()
if os.path.exists(UPDATED_FILE):
    with open(UPDATED_FILE) as f:
        updated = {l.strip() for l in f if l.strip()}

remaining = [(s, p) for s, p in NOTEBOOKS.items() if s not in updated]
print(f"Remaining: {len(remaining)}/{len(NOTEBOOKS)}")

if not remaining:
    print("✅ All notebooks updated!")
    sys.exit(0)

slug, nb_rel = remaining[0]
nb_file = os.path.basename(nb_rel)
full = os.path.join(REPO, nb_rel)

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
    print(f"✓ Pushed {slug}")
    with open(UPDATED_FILE, "a") as f:
        f.write(slug + "\n")
    state["consecutive_429"] = 0
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
elif "429" in r.stdout or "429" in r.stderr:
    state["last_429"] = now
    state["consecutive_429"] = state.get("consecutive_429", 0) + 1
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
    print(f"⛔ Rate limited (streak: {state['consecutive_429']}). Backoff: {backoff_sec/60:.0f}min")
else:
    print(f"✗ Error: {r.stdout} {r.stderr}")
