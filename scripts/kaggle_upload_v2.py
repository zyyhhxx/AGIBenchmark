#!/usr/bin/env python3
"""
Upload the 4 remaining new notebooks to Kaggle.
Uses slug format matching previously successful uploads (e.g., "xxx-benchmark-agi-2026a").
Waits between uploads. Verifies creation.
"""
import json, os, subprocess, tempfile, shutil, sys, time

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")

# Notebooks to upload: (notebook_file, slug, title)
# Using slug patterns that match previously successful uploads
TO_UPLOAD = [
    ("notebooks/exec_func_crt.ipynb", "ianstudy/crt-benchmark-agi-2026a", "CRT Benchmark AGI 2026a"),
    ("notebooks/metacog_canary.ipynb", "ianstudy/canary-benchmark-agi-2026a", "Canary Benchmark AGI 2026a"),
    ("notebooks/metacog_epistemic_humility.ipynb", "ianstudy/epistemic-humility-benchmark-agi-2026a", "Epistemic Humility Benchmark AGI 2026a"),
    ("notebooks/social_cog_emotional_prosody.ipynb", "ianstudy/emotional-prosody-benchmark-agi-2026a", "Emotional Prosody Benchmark AGI 2026a"),
]

# Check which already exist
existing = set()
r = subprocess.run([KAGGLE, "kernels", "list", "--user", "ianstudy", "--page-size", "100"],
                   capture_output=True, text=True, timeout=30)
for line in r.stdout.strip().split('\n'):
    parts = line.split()
    if parts and parts[0].startswith('ianstudy/'):
        existing.add(parts[0])

print(f"Existing public notebooks: {len(existing)}")

remaining = [(f, s, t) for f, s, t in TO_UPLOAD if s not in existing]
print(f"Need to upload: {len(remaining)}")

if not remaining:
    print("🎉 All notebooks are public!")
    sys.exit(0)

uploaded = 0
for nb_file, slug, title in remaining:
    full_path = os.path.join(REPO, nb_file)
    if not os.path.exists(full_path):
        print(f"⏭️ Missing: {nb_file}")
        continue
    
    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copy2(full_path, os.path.join(tmpdir, os.path.basename(nb_file)))
        meta = {
            "id": slug,
            "title": title,
            "code_file": os.path.basename(nb_file),
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
        
        print(f"Pushing {slug}...", end=" ", flush=True)
        r = subprocess.run([KAGGLE, "kernels", "push", "-p", tmpdir],
                          capture_output=True, text=True, timeout=60)
        out = (r.stdout + r.stderr).strip()
        
        if "429" in out:
            print(f"⛔ Rate limited. Uploaded {uploaded}/{len(remaining)}.")
            sys.exit(1)
        elif r.returncode != 0:
            print(f"❌ Error: {out[:200]}")
        else:
            print(f"✅ Push accepted. Output: {out[:100]}")
            uploaded += 1
            # Wait 30s between uploads
            if uploaded < len(remaining):
                print("Waiting 30s...")
                time.sleep(30)
    finally:
        shutil.rmtree(tmpdir)

print(f"\nPushed {uploaded}/{len(remaining)} notebooks.")
if uploaded == len(remaining):
    print("🎉 All done!")
