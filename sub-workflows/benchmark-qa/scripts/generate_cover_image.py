#!/usr/bin/env python3
"""Generate metacognition cover image: grouped bar chart showing three-tier pattern across models."""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Load data
df = pd.read_csv("/home/ubuntu/.openclaw/workspace-agi-bench/repo/results/metacog_final_scores.csv")
df = df[df['error'].isna() | (df['error'] == '')]

# Define tiers and benchmark display names
tiers = {
    'External Monitoring': ['metacog_canary', 'metacog_epistemic_humility', 'metacog_error_detection'],
    'Self-Monitoring': ['metacog_epistemic_revision', 'metacog_learning_monitoring', 'metacog_control'],
    'Prospective\nSelf-Assessment': ['metacog_fok', 'metacog_jol', 'metacog_calibration'],
}

bench_labels = {
    'metacog_canary': 'Canary\nDetection',
    'metacog_epistemic_humility': 'Epistemic\nHumility',
    'metacog_error_detection': 'Error\nDetection',
    'metacog_epistemic_revision': 'Epistemic\nRevision',
    'metacog_learning_monitoring': 'Learning\nMonitoring',
    'metacog_control': 'Metacog\nControl',
    'metacog_fok': 'Feeling of\nKnowing',
    'metacog_jol': 'Judgment of\nLearning',
    'metacog_calibration': 'Confidence\nCalibration',
}

# Pick 5 interesting models (frontier + mid + weak)
selected_models = ['Claude Opus 4.6', 'Claude Sonnet 4.6', 'Nova Pro', 'Llama 3.3 70B', 'Ministral 3B']
colors = ['#2563eb', '#60a5fa', '#f59e0b', '#10b981', '#ef4444']

# Build ordered benchmark list
benchmarks = []
for tier_benchmarks in tiers.values():
    benchmarks.extend(tier_benchmarks)

# Pivot to get scores
pivot = df.pivot_table(index='benchmark', columns='model', values='score')

# Setup figure
fig, ax = plt.subplots(figsize=(12, 8))
fig.set_facecolor('white')

n_benchmarks = len(benchmarks)
n_models = len(selected_models)
bar_width = 0.15
x = np.arange(n_benchmarks)

# Plot bars
for i, (model, color) in enumerate(zip(selected_models, colors)):
    scores = []
    for b in benchmarks:
        try:
            s = pivot.loc[b, model]
            scores.append(s if not pd.isna(s) else 0)
        except KeyError:
            scores.append(0)
    offset = (i - n_models/2 + 0.5) * bar_width
    ax.bar(x + offset, scores, bar_width, label=model, color=color, edgecolor='white', linewidth=0.5, zorder=3)

# Tier backgrounds and labels
tier_starts = [0, 3, 6]
tier_ends = [3, 6, 9]
tier_colors_bg = ['#dbeafe', '#fef3c7', '#fce7f3']
tier_names = list(tiers.keys())

for start, end, bg_color, name in zip(tier_starts, tier_ends, tier_colors_bg, tier_names):
    ax.axvspan(start - 0.5, end - 0.5, alpha=0.3, color=bg_color, zorder=0)
    ax.text((start + end - 1) / 2, 1.08, name, ha='center', va='bottom',
            fontsize=11, fontweight='bold', color='#374151')

# Tier separators
for sep in [2.5, 5.5]:
    ax.axvline(sep, color='#9ca3af', linestyle='--', linewidth=0.8, alpha=0.7, zorder=1)

# Human baseline band (approximate)
ax.axhspan(0.60, 0.85, alpha=0.08, color='green', zorder=0)
ax.text(8.4, 0.87, 'Human\nBaseline', fontsize=8, color='#166534', ha='center', va='bottom', style='italic')

# Formatting
ax.set_xticks(x)
ax.set_xticklabels([bench_labels[b] for b in benchmarks], fontsize=8.5)
ax.set_ylabel('Score', fontsize=12, fontweight='bold')
ax.set_ylim(0, 1.18)
ax.set_xlim(-0.6, n_benchmarks - 0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3, zorder=0)
ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

ax.set_title('Metacognition Benchmark Suite: Three-Tier Cognitive Profile\nacross 10 AI Models',
             fontsize=14, fontweight='bold', pad=25)

plt.tight_layout()
out_path = '/home/ubuntu/.openclaw/workspace-agi-bench/repo/assets/metacognition_cover.png'
import os
os.makedirs(os.path.dirname(out_path), exist_ok=True)
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved to {out_path}")
print(f"File size: {os.path.getsize(out_path)} bytes")
plt.close()
