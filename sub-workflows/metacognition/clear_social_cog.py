#!/usr/bin/env python3
"""Clear social_cog_emotional_prosody scores from all model result files so they get re-run."""
import json, os, glob

RESULTS_DIR = "/home/ubuntu/.openclaw/workspace-agi-bench/repo/results"
BENCH = "social_cog_emotional_prosody"

for f in glob.glob(os.path.join(RESULTS_DIR, "*.json")):
    try:
        with open(f) as fh:
            d = json.load(fh)
        if "scores" in d and BENCH in d["scores"]:
            del d["scores"][BENCH]
            with open(f, "w") as fh:
                json.dump(d, fh, indent=2)
            print(f"Cleared {BENCH} from {os.path.basename(f)}")
    except Exception as e:
        pass
