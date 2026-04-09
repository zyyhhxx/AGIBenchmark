#!/usr/bin/env python3
"""
Upload remaining NEW notebooks to Kaggle (CRT, canary, epistemic humility, emotional prosody).
These were never uploaded at all — they need kernels push to create them.

Usage: python3 scripts/kaggle_upload_remaining.py
"""
import json, os, subprocess, tempfile, shutil, sys, time

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")
SKIP_FILE = os.path.join(REPO, "scripts/.kaggle_pushed_public.txt")

# Only the 4 notebooks that were never uploaded
TO_UPLOAD = {
    "ianstudy/agi-bench-2026-crt-exec-func": ("notebooks/exec_func_crt.ipynb", "AGI Bench: Cognitive Reflection Test"),
    "ianstudy/agi-bench-2026-emotional-prosody": ("notebooks/social_cog_emotional_prosody.ipynb", "AGI Bench: Emotional Prosody"),
    "ianstudy/agi-bench-2026-epistemic-humility": ("notebooks/metacog_epistemic_humility.ipynb", "AGI Bench: Epistemic Humility"),
    "ianstudy/agi-bench-2026-metacog-canary": ("notebooks/metacog_canary.ipynb", "AGI Bench: Contamination Canary"),
}

# Check what's already pushed
pushed = set()
if os.path.exists(SKIP_FILE):
    with open(SKIP_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                pushed.add(line)

remaining = {s: v for s, v in TO_UPLOAD.items() if s not in pushed}
print(f"Remaining to upload: {len(remaining)}")

if not remaining:
    print("✅ All uploaded!")
    sys.exit(0)

ok = 0
for slug, (nb_path, title) in remaining.items():
    full = os.path.join(REPO, nb_path)
    if not os.path.exists(full):
        print(f"⏭️ {slug}: missing {nb_path}")
        continue
    
    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copy2(full, os.path.join(tmpdir, os.path.basename(nb_path)))
        meta = {
            "id": slug,
            "title": slug.split('/')[1],
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
            print(f"✅ {title}")
            with open(SKIP_FILE, 'a') as f:
                f.write(f"{slug}\n")
            ok += 1
            time.sleep(10)
        elif "429" in out:
            print(f"⛔ Rate limited after {ok} uploads. {len(remaining)-ok} remain.")
            sys.exit(1)
        else:
            print(f"❌ {slug}: {out[:150]}")
    finally:
        shutil.rmtree(tmpdir)

print(f"\n✅ Uploaded {ok}/{len(remaining)} notebooks.")
