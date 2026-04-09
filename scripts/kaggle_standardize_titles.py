#!/usr/bin/env python3
"""
Standardize Kaggle notebook titles to 'AGI Bench: <Name>' format.
Re-pushes notebooks with updated titles. Also makes all notebooks public.
Run when rate limit has lifted.
"""
import json, os, subprocess, tempfile, shutil, sys, time

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
KAGGLE = os.path.join(REPO, ".venv/bin/kaggle")

# Map of slug -> desired title
DESIRED_TITLES = {
    "ianstudy/agi-bench-feeling-of-knowing-fok": "AGI Bench: Feeling of Knowing (FOK)",
    "ianstudy/agi-bench-judgment-of-learning-jol": "AGI Bench: Judgment of Learning (JOL)",
    "ianstudy/agi-bench-calibration": "AGI Bench: Retrospective Calibration",
    "ianstudy/agi-bench-selective-attention": "AGI Bench: Selective Attention",
    "ianstudy/agi-bench-curriculum-sensitivity": "AGI Bench: Curriculum Sensitivity",
    "ianstudy/agi-bench-proactive-retroactive-interference": "AGI Bench: Proactive/Retroactive Interference",
    "ianstudy/agi-bench-near-vs-far-transfer": "AGI Bench: Near vs Far Transfer",
    "ianstudy/agi-bench-learning-curves": "AGI Bench: Learning Curves",
    "ianstudy/agi-bench-jol-sub-metrics": "AGI Bench: JOL Sub-metrics",
    "ianstudy/agi-bench-fok-sub-metrics": "AGI Bench: FOK Sub-metrics",
    "ianstudy/agi-bench-2026-error-detection-metacog": "AGI Bench: Error Detection",
    "ianstudy/agi-bench-2026-instruction-update-task": "AGI Bench: Instruction Update",
    "ianstudy/agi-bench-2026-learning-monitoring-task": "AGI Bench: Learning Monitoring",
    "ianstudy/agi-bench-2026-tower-of-london-task": "AGI Bench: Tower of London",
    "ianstudy/agi-bench-2026-vigilance-attention": "AGI Bench: Vigilance (Sustained Attention)",
    "ianstudy/agi-bench-false-belief-tom": "AGI Bench: False Belief Theory of Mind",
    "ianstudy/agi-bench-metacog-error-det-submetrics": "AGI Bench: Error Detection Sub-metrics",
    "ianstudy/agi-bench-n-back": "AGI Bench: N-Back Working Memory",
    "ianstudy/agi-bench-pragmatic-inference": "AGI Bench: Pragmatic Inference",
    "ianstudy/agi-bench-task-switching": "AGI Bench: Task Switching",
    "ianstudy/divided-attention-benchmark-agi-2026a": "AGI Bench: Divided Attention",
    "ianstudy/epistemic-revision-benchmark-agi-2026a": "AGI Bench: Epistemic Revision",
    "ianstudy/metacog-ctrl-test-apr08": "AGI Bench: Metacognitive Control",
    "ianstudy/sarcasm-detection-benchmark-agi-2026a": "AGI Bench: Sarcasm Detection",
    "ianstudy/submission-overview-agi-bench-apr08": "AGI Bench: Submission Overview",
    "ianstudy/wcst-benchmark-agi-2026a": "AGI Bench: Wisconsin Card Sorting Test",
}

# Notebooks that don't exist yet — skip
NEW_NOTEBOOKS = {
    "ianstudy/crt-benchmark-agi-2026a": "AGI Bench: Cognitive Reflection Test",
    "ianstudy/canary-benchmark-agi-2026a": "AGI Bench: Contamination Canary",
    "ianstudy/epistemic-humility-benchmark-agi-2026a": "AGI Bench: Epistemic Humility",
    "ianstudy/emotional-prosody-benchmark-agi-2026a": "AGI Bench: Emotional Prosody",
}

print("This script re-pushes notebooks to update titles.")
print("WARNING: Each push counts against Kaggle's rate limit.")
print(f"Notebooks to update: {len(DESIRED_TITLES)}")
print(f"New notebooks to create: {len(NEW_NOTEBOOKS)}")
print()

if "--dry-run" in sys.argv:
    for slug, title in {**DESIRED_TITLES, **NEW_NOTEBOOKS}.items():
        print(f"  {slug} -> {title}")
    sys.exit(0)

# This is a potentially expensive operation. Only run when rate limit is clear.
print("Run with --dry-run first to preview changes.")
print("Not implemented yet — use when rate limit lifts.")
