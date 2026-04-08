#!/usr/bin/env python3
"""Upload CRT and canary notebooks to Kaggle. Run when rate limit lifts."""
import json, os, subprocess, tempfile, shutil, time, sys

KERNELS = {
    "ianstudy/agi-bench-2026-crt-exec-func": "notebooks/exec_func_crt.ipynb",
    "ianstudy/agi-bench-2026-metacog-canary": "notebooks/metacog_canary.ipynb",
    "ianstudy/agi-bench-2026-epistemic-humility": "notebooks/metacog_epistemic_humility.ipynb",
    "ianstudy/agi-bench-2026-emotional-prosody": "notebooks/social_cog_emotional_prosody.ipynb",
}

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")

for slug, nb_path in KERNELS.items():
    full_nb = os.path.join(REPO, nb_path)
    if not os.path.exists(full_nb):
        print(f"SKIP {slug}: {nb_path} not found")
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

        result = subprocess.run(
            [KAGGLE, "kernels", "push", "-p", tmpdir],
            capture_output=True, text=True, timeout=60
        )
        out = result.stdout.strip() or result.stderr.strip()
        if result.returncode == 0:
            print(f"✅ {slug}: {out}")
        else:
            print(f"❌ {slug}: {out}")
    finally:
        shutil.rmtree(tmpdir)
    time.sleep(15)
