#!/usr/bin/env python3
"""Upload 4 remaining notebooks via kagglesdk (new API client)."""
import time, sys, os

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"

NOTEBOOKS = [
    ("notebooks/exec_func_crt.ipynb", "AGI Bench: Cognitive Reflection Test"),
    ("notebooks/metacog_canary.ipynb", "AGI Bench: Contamination Canary"),
    ("notebooks/metacog_epistemic_humility.ipynb", "AGI Bench: Epistemic Humility"),
    ("notebooks/social_cog_emotional_prosody.ipynb", "AGI Bench: Emotional Prosody"),
]

DONE_FILE = os.path.join(REPO, "scripts/.kaggle_v3_uploaded.txt")

# Track what's already uploaded
done = set()
if os.path.exists(DONE_FILE):
    with open(DONE_FILE) as f:
        done = {l.strip() for l in f if l.strip()}

from kagglesdk import KaggleClient
from kagglesdk.kernels.types.kernels_api_service import ApiSaveKernelRequest

client = KaggleClient()
ok = 0

for nb_path, title in NOTEBOOKS:
    if nb_path in done:
        print(f"⏭️ Already uploaded: {title}")
        continue

    full = os.path.join(REPO, nb_path)
    with open(full) as f:
        nb_text = f.read()

    req = ApiSaveKernelRequest()
    req.new_title = title
    req.text = nb_text
    req.language = "python"
    req.kernel_type = "notebook"
    req.is_private = False
    req.enable_gpu = False
    req.enable_internet = True
    req.competition_data_sources = ["kaggle-measuring-agi"]

    try:
        resp = client.kernels.kernels_api_client.save_kernel(req)
        print(f"✅ {title}: {resp}")
        with open(DONE_FILE, 'a') as f:
            f.write(f"{nb_path}\n")
        ok += 1
        time.sleep(15)  # Rate limit buffer
    except Exception as e:
        err = str(e)
        if "429" in err:
            print(f"⛔ Rate limited after {ok} uploads. Waiting 60s...")
            time.sleep(60)
            # Retry once
            try:
                resp = client.kernels.kernels_api_client.save_kernel(req)
                print(f"✅ {title} (retry): {resp}")
                with open(DONE_FILE, 'a') as f:
                    f.write(f"{nb_path}\n")
                ok += 1
                time.sleep(15)
            except Exception as e2:
                print(f"❌ {title}: still rate limited. Exiting.")
                sys.exit(1)
        else:
            print(f"❌ {title}: {err[:200]}")

print(f"\n✅ Uploaded {ok} notebooks this run.")
