#!/usr/bin/env python3
"""Upload the canary notebook to Kaggle."""
import json, os, subprocess, tempfile, shutil

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")

tmpdir = tempfile.mkdtemp()
try:
    shutil.copy2(os.path.join(REPO, "notebooks/metacog_canary.ipynb"), tmpdir)
    meta = {
        "id": "ianstudy/agi-bench-contamination-canary",
        "title": "AGI Bench: Contamination Canary",
        "code_file": "metacog_canary.ipynb",
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

    result = subprocess.run(
        [KAGGLE, "kernels", "push", "-p", tmpdir],
        capture_output=True, text=True, timeout=60
    )
    print(result.stdout.strip())
    if result.returncode != 0:
        print(f"ERROR: {result.stderr.strip()}")
finally:
    shutil.rmtree(tmpdir)
