#!/usr/bin/env python3
"""
Push all metacognition notebooks to Kaggle with rate-limit handling.
Run: /home/ubuntu/.openclaw/workspace-agi-bench/repo/.venv/bin/python3 push_metacog_notebooks.py
"""
from kaggle.api.kaggle_api_extended import KaggleApi
import os, time, glob, json, sys

api = KaggleApi()
api.authenticate()

push_dir = "/home/ubuntu/.openclaw/workspace-agi-bench/repo/kaggle_push"
folders = sorted(glob.glob(f"{push_dir}/metacog_*"))

print(f"Pushing {len(folders)} notebooks to Kaggle...")
successes = []
failures = []

for i, folder in enumerate(folders):
    name = os.path.basename(folder)
    
    if i > 0:
        print(f"  Waiting 20s between pushes...", flush=True)
        time.sleep(20)
    
    for attempt in range(5):
        try:
            result = api.kernels_push(folder)
            print(f"✓ [{i+1}/{len(folders)}] {name}: pushed", flush=True)
            successes.append(name)
            break
        except Exception as e:
            if "429" in str(e):
                wait = 60 * (attempt + 1)
                print(f"  ⏳ Rate limited, waiting {wait}s (attempt {attempt+1}/5)...", flush=True)
                time.sleep(wait)
            else:
                print(f"✗ [{i+1}/{len(folders)}] {name}: {e}", flush=True)
                failures.append((name, str(e)))
                break
    else:
        failures.append((name, "rate limited after 5 attempts"))
        print(f"✗ [{i+1}/{len(folders)}] {name}: gave up after 5 attempts", flush=True)

print(f"\n=== Results ===")
print(f"Pushed: {len(successes)}/{len(folders)}")
for s in successes:
    print(f"  ✓ {s}")
for name, err in failures:
    print(f"  ✗ {name}: {err}")
