#!/usr/bin/env python3
"""
Lightweight Kaggle push retry — tries notebooks one at a time.
If 429, exits immediately. Designed for cron retry.

Usage: python3 scripts/kaggle_push_retry.py
"""
import json, os, subprocess, tempfile, shutil, sys, time

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")
SKIP_FILE = os.path.join(REPO, "scripts/.kaggle_pushed_public.txt")

# Full desired state: slug → (notebook_path, title)
DESIRED = {
    "ianstudy/agi-bench-2026-error-detection-metacog": ("notebooks/metacog_error_detection.ipynb", "AGI Bench: Error Detection"),
    "ianstudy/agi-bench-2026-learning-monitoring-task": ("notebooks/metacog_learning_monitoring.ipynb", "AGI Bench: Learning Monitoring"),
    "ianstudy/metacog-ctrl-test-apr08": ("notebooks/metacog_control.ipynb", "AGI Bench: Metacognitive Control"),
    "ianstudy/epistemic-revision-benchmark-agi-2026a": ("notebooks/metacog_epistemic_revision.ipynb", "AGI Bench: Epistemic Revision"),
    "ianstudy/agi-bench-2026-epistemic-humility": ("notebooks/metacog_epistemic_humility.ipynb", "AGI Bench: Epistemic Humility"),
    "ianstudy/agi-bench-2026-metacog-canary": ("notebooks/metacog_canary.ipynb", "AGI Bench: Contamination Canary"),
    "ianstudy/agi-bench-metacog-error-det-submetrics": ("notebooks/metacog_error_detection_submetrics.ipynb", "AGI Bench: Error Detection Sub-metrics"),
    "ianstudy/agi-bench-2026-vigilance-attention": ("notebooks/attention_vigilance.ipynb", "AGI Bench: Vigilance"),
    "ianstudy/divided-attention-benchmark-agi-2026a": ("notebooks/attention_divided.ipynb", "AGI Bench: Divided Attention"),
    "ianstudy/agi-bench-2026-instruction-update-task": ("notebooks/attention_instruction_update.ipynb", "AGI Bench: Instruction Update"),
    "ianstudy/wcst-benchmark-agi-2026a": ("notebooks/exec_func_wcst.ipynb", "AGI Bench: WCST"),
    "ianstudy/agi-bench-2026-tower-of-london-task": ("notebooks/exec_func_tol.ipynb", "AGI Bench: Tower of London"),
    "ianstudy/agi-bench-task-switching": ("notebooks/exec_func_task_switch.ipynb", "AGI Bench: Task Switching"),
    "ianstudy/agi-bench-n-back": ("notebooks/exec_func_nback.ipynb", "AGI Bench: N-Back"),
    "ianstudy/agi-bench-2026-crt-exec-func": ("notebooks/exec_func_crt.ipynb", "AGI Bench: Cognitive Reflection Test"),
    "ianstudy/agi-bench-false-belief-tom": ("notebooks/social_cog_false_belief.ipynb", "AGI Bench: False Belief ToM"),
    "ianstudy/agi-bench-pragmatic-inference": ("notebooks/social_cog_pragmatic.ipynb", "AGI Bench: Pragmatic Inference"),
    "ianstudy/sarcasm-detection-benchmark-agi-2026a": ("notebooks/social_cog_sarcasm.ipynb", "AGI Bench: Sarcasm Detection"),
    "ianstudy/agi-bench-2026-emotional-prosody": ("notebooks/social_cog_emotional_prosody.ipynb", "AGI Bench: Emotional Prosody"),
    "ianstudy/submission-overview-agi-bench-apr08": ("notebooks/submission_overview.ipynb", "AGI Bench: Submission Overview"),
}

pushed = set()
if os.path.exists(SKIP_FILE):
    with open(SKIP_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                pushed.add(line)

remaining = [(s, nb, t) for s, (nb, t) in DESIRED.items() if s not in pushed]
print(f"Remaining: {len(remaining)} / {len(DESIRED)} notebooks to push")

if not remaining:
    print("✅ All done!")
    sys.exit(0)

ok = 0
for slug, nb_path, title in remaining:
    full = os.path.join(REPO, nb_path)
    if not os.path.exists(full):
        print(f"⏭️ {slug}: missing {nb_path}")
        continue
    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copy2(full, os.path.join(tmpdir, os.path.basename(nb_path)))
        meta = {"id": slug, "title": slug.split('/')[1], "code_file": os.path.basename(nb_path),
                "language": "python", "kernel_type": "notebook", "is_private": False,
                "enable_gpu": False, "enable_tpu": False, "enable_internet": True,
                "competition_sources": ["kaggle-measuring-agi"]}
        with open(os.path.join(tmpdir, "kernel-metadata.json"), "w") as f:
            json.dump(meta, f, indent=2)
        r = subprocess.run([KAGGLE, "kernels", "push", "-p", tmpdir], capture_output=True, text=True, timeout=60)
        out = (r.stdout + r.stderr).strip()
        if r.returncode == 0:
            print(f"✅ {title}")
            with open(SKIP_FILE, 'a') as f:
                f.write(f"{slug}\n")
            ok += 1
            time.sleep(10)
        elif "429" in out:
            print(f"⛔ Rate limited after {ok} pushes. {len(remaining)-ok} remain.")
            sys.exit(1)
        else:
            print(f"❌ {slug}: {out[:120]}")
    finally:
        shutil.rmtree(tmpdir)

print(f"\n✅ Pushed {ok} notebooks.")
