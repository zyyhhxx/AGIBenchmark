#!/usr/bin/env python3
"""
Submit benchmarks to Kaggle Community Benchmarks platform.
Uses Kaggle API to create CB tasks from our notebooks.

NOTE: This requires notebooks to be PUBLIC first.
Run scripts/kaggle_batch_ops.py first to ensure all notebooks are public.
"""
import json, os, sys

# All benchmark notebooks (excluding overview, dashboard, canary)
BENCHMARK_NOTEBOOKS = {
    # Metacognition
    "metacog_fok": {"slug": "ianstudy/agi-bench-feeling-of-knowing-fok", "track": "metacognition", "name": "Feeling-of-Knowing (FOK)"},
    "metacog_jol": {"slug": "ianstudy/agi-bench-judgment-of-learning-jol", "track": "metacognition", "name": "Judgment-of-Learning (JOL)"},
    "metacog_calibration": {"slug": "ianstudy/agi-bench-calibration", "track": "metacognition", "name": "Retrospective Calibration"},
    "metacog_error_detection": {"slug": "ianstudy/agi-bench-2026-error-detection-metacog", "track": "metacognition", "name": "Error Detection"},
    "metacog_learning_monitoring": {"slug": "ianstudy/agi-bench-2026-learning-monitoring-task", "track": "metacognition", "name": "Learning Monitoring"},
    "metacog_control": {"slug": "ianstudy/metacog-ctrl-test-apr08", "track": "metacognition", "name": "Metacognitive Control"},
    "metacog_epistemic_revision": {"slug": "ianstudy/epistemic-revision-benchmark-agi-2026a", "track": "metacognition", "name": "Epistemic Revision"},
    "metacog_epistemic_humility": {"slug": "ianstudy/agi-bench-2026-epistemic-humility", "track": "metacognition", "name": "Epistemic Humility"},
    
    # Learning
    "learning_curves": {"slug": "ianstudy/agi-bench-learning-curves", "track": "learning", "name": "Learning Curves"},
    "learning_transfer": {"slug": "ianstudy/agi-bench-near-vs-far-transfer", "track": "learning", "name": "Near vs Far Transfer"},
    "learning_interference": {"slug": "ianstudy/agi-bench-proactive-retroactive-interference", "track": "learning", "name": "Interference"},
    "learning_curriculum": {"slug": "ianstudy/agi-bench-curriculum-sensitivity", "track": "learning", "name": "Curriculum Sensitivity"},
    
    # Attention
    "attention_selective": {"slug": "ianstudy/agi-bench-selective-attention", "track": "attention", "name": "Selective Attention"},
    "attention_vigilance": {"slug": "ianstudy/agi-bench-2026-vigilance-attention", "track": "attention", "name": "Vigilance"},
    "attention_divided": {"slug": "ianstudy/divided-attention-benchmark-agi-2026a", "track": "attention", "name": "Divided Attention"},
    "attention_instruction_update": {"slug": "ianstudy/agi-bench-2026-instruction-update-task", "track": "attention", "name": "Instruction Update"},
    
    # Executive Functions
    "exec_func_wcst": {"slug": "ianstudy/wcst-benchmark-agi-2026a", "track": "executive_functions", "name": "WCST"},
    "exec_func_tol": {"slug": "ianstudy/agi-bench-2026-tower-of-london-task", "track": "executive_functions", "name": "Tower of London"},
    "exec_func_task_switch": {"slug": "ianstudy/agi-bench-task-switching", "track": "executive_functions", "name": "Task Switching"},
    "exec_func_nback": {"slug": "ianstudy/agi-bench-n-back", "track": "executive_functions", "name": "N-Back"},
    "exec_func_crt": {"slug": "ianstudy/agi-bench-2026-crt-exec-func", "track": "executive_functions", "name": "Cognitive Reflection Test"},
    
    # Social Cognition
    "social_cog_false_belief": {"slug": "ianstudy/agi-bench-false-belief-tom", "track": "social_cognition", "name": "False Belief ToM"},
    "social_cog_pragmatic": {"slug": "ianstudy/agi-bench-pragmatic-inference", "track": "social_cognition", "name": "Pragmatic Inference"},
    "social_cog_sarcasm": {"slug": "ianstudy/sarcasm-detection-benchmark-agi-2026a", "track": "social_cognition", "name": "Sarcasm Detection"},
    "social_cog_emotional_prosody": {"slug": "ianstudy/agi-bench-2026-emotional-prosody", "track": "social_cognition", "name": "Emotional Prosody"},
}

# Sub-metric notebooks (submit separately)
SUBMETRIC_NOTEBOOKS = {
    "metacog_fok_submetrics": {"slug": "ianstudy/agi-bench-fok-sub-metrics", "track": "metacognition", "name": "FOK Sub-metrics"},
    "metacog_jol_submetrics": {"slug": "ianstudy/agi-bench-jol-sub-metrics", "track": "metacognition", "name": "JOL Sub-metrics"},
    "metacog_error_det_submetrics": {"slug": "ianstudy/agi-bench-metacog-error-det-submetrics", "track": "metacognition", "name": "Error Detection Sub-metrics"},
}

print(f"=== AGI Benchmark Suite — CB Submission Plan ===")
print(f"Total benchmarks: {len(BENCHMARK_NOTEBOOKS)}")
print(f"Total sub-metrics: {len(SUBMETRIC_NOTEBOOKS)}")
print()

# Group by track
tracks = {}
for task_id, info in BENCHMARK_NOTEBOOKS.items():
    track = info["track"]
    if track not in tracks:
        tracks[track] = []
    tracks[track].append((task_id, info))

for track, tasks in sorted(tracks.items()):
    print(f"\n{track.upper()} ({len(tasks)} tasks):")
    for task_id, info in tasks:
        print(f"  {info['name']:35s} → {info['slug']}")

print(f"\n{'='*60}")
print("To submit: go to kaggle.com/benchmarks/tasks/new for each notebook")
print("Or use the Kaggle API (when available) to programmatically create tasks")

# Save as JSON for programmatic use
output = {
    "benchmarks": BENCHMARK_NOTEBOOKS,
    "submetrics": SUBMETRIC_NOTEBOOKS,
    "competition": "kaggle-measuring-agi",
    "suite_name": "Cognitive Abilities Benchmark Suite — Measuring AGI",
}
with open("scripts/cb_submission_plan.json", "w") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved submission plan to scripts/cb_submission_plan.json")
