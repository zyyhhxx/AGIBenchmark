#!/usr/bin/env python3
"""Regenerate all 5 track cover images from score_matrix_all_tracks.csv."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import csv
import os
from PIL import Image

OUTPUT_DIR = '/home/ubuntu/.openclaw/workspace-agi-bench/repo/assets'
CSV_PATH = '/home/ubuntu/.openclaw/workspace-agi-bench/repo/results/score_matrix_all_tracks.csv'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load scores from CSV
scores_data = {}
with open(CSV_PATH) as f:
    reader = csv.DictReader(f)
    for row in reader:
        bench = row['benchmark']
        scores_data[bench] = {}
        for k, v in row.items():
            if k not in ('benchmark', 'track'):
                scores_data[bench][k] = float(v) if v and v != 'N/A' else None

MODELS = ['Claude Opus 4.6', 'Claude Sonnet 4.6', 'Nova Pro', 'Llama 3.3 70B', 'Ministral 3B']
MODEL_COLORS = ['#2563eb', '#60a5fa', '#f59e0b', '#10b981', '#ef4444']

TRACKS = {
    'attention': {
        'title': 'Attention Benchmark Suite: Cognitive Profile\nacross 10 AI Models',
        'benchmarks': ['attention_divided', 'attention_instruction_update', 'attention_selective', 'attention_vigilance'],
        'bench_labels': ['Divided\nAttention', 'Instruction\nUpdate', 'Selective\nAttention', 'Vigilance\n(N-back)'],
        'groups': [('Multi-Stream\nProcessing', 0, 2), ('Sustained\nMonitoring', 2, 4)],
        'group_colors': ['#E8F0FE', '#FEF7E0'],
    },
    'learning': {
        'title': 'Learning Benchmark Suite: Cognitive Profile\nacross 10 AI Models',
        'benchmarks': ['learning_transfer', 'learning_interference', 'learning_curriculum', 'learning_curves'],
        'bench_labels': ['Transfer', 'Interference', 'Curriculum', 'Learning\nCurves'],
        'groups': [('Knowledge\nApplication', 0, 2), ('Acquisition\nProcess', 2, 4)],
        'group_colors': ['#E8F0FE', '#E6F4EA'],
    },
    'executive_functions': {
        'title': 'Executive Functions Benchmark Suite: Cognitive Profile\nacross 10 AI Models',
        'benchmarks': ['exec_func_crt', 'exec_func_nback', 'exec_func_task_switch', 'exec_func_tol', 'exec_func_wcst'],
        'bench_labels': ['CRT\n(Inhibition)', 'N-back\n(Updating)', 'Task Switch\n(Shifting)', 'Tower of\nLondon', 'WCST\n(Set Shift)'],
        'groups': [('Inhibition &\nUpdating', 0, 2), ('Flexibility', 2, 3), ('Planning &\nSet Shifting', 3, 5)],
        'group_colors': ['#E8F0FE', '#FEF7E0', '#FCE8E6'],
    },
    'social_cognition': {
        'title': 'Social Cognition Benchmark Suite: Cognitive Profile\nacross 10 AI Models',
        'benchmarks': ['social_cog_false_belief', 'social_cog_pragmatic', 'social_cog_sarcasm', 'social_cog_emotional_prosody'],
        'bench_labels': ['False Belief\n(ToM)', 'Pragmatic\nInference', 'Sarcasm\nDetection', 'Emotional\nProsody'],
        'groups': [('Mentalizing', 0, 2), ('Social Language', 2, 4)],
        'group_colors': ['#E8F0FE', '#F3E8FD'],
    },
    'metacognition': {
        'title': 'Metacognition Benchmark Suite: Three-Tier Cognitive Profile\nacross 10 AI Models',
        'benchmarks': ['metacog_canary', 'metacog_epistemic_humility', 'metacog_error_detection',
                       'metacog_epistemic_revision', 'metacog_learning_monitoring', 'metacog_control',
                       'metacog_fok', 'metacog_jol', 'metacog_calibration'],
        'bench_labels': ['Canary\nDetection', 'Epistemic\nHumility', 'Error\nDetection',
                         'Epistemic\nRevision', 'Learning\nMonitoring', 'Metacog\nControl',
                         'Feeling of\nKnowing', 'Judgment of\nLearning', 'Confidence\nCalibration'],
        'groups': [('External Monitoring', 0, 3), ('Self-Monitoring', 3, 6), ('Prospective\nSelf-Assessment', 6, 9)],
        'group_colors': ['#dbeafe', '#fef3c7', '#fce7f3'],
    },
}

for track_name, track in TRACKS.items():
    benchmarks = track['benchmarks']
    n_benchmarks = len(benchmarks)
    n_models = len(MODELS)

    fig, ax = plt.subplots(figsize=(max(12, n_benchmarks * 1.8), 8))
    fig.set_facecolor('white')

    # Background groups
    for idx, (label, start, end) in enumerate(track['groups']):
        color = track['group_colors'][idx]
        ax.axvspan(start - 0.5, end - 0.5, alpha=0.3, color=color, zorder=0)
        mid = (start + end - 1) / 2
        ax.text(mid, 1.08 if track_name == 'metacognition' else 1.02, label,
                ha='center', va='bottom', fontsize=10 if track_name != 'metacognition' else 11,
                fontstyle='italic' if track_name != 'metacognition' else 'normal',
                fontweight='bold' if track_name == 'metacognition' else 'normal',
                color='#374151',
                transform=ax.get_xaxis_transform() if track_name != 'metacognition' else None)

    # Group dividers
    for idx, (label, start, end) in enumerate(track['groups']):
        if start > 0:
            ax.axvline(x=start - 0.5, color='#9ca3af', linestyle='--', linewidth=0.8, alpha=0.7, zorder=1)

    # Bars
    bar_width = 0.15
    x = np.arange(n_benchmarks)
    for i, (model, color) in enumerate(zip(MODELS, MODEL_COLORS)):
        scores = []
        for b in benchmarks:
            val = scores_data.get(b, {}).get(model, None)
            scores.append(val if val is not None else 0)
        offset = (i - n_models / 2 + 0.5) * bar_width
        ax.bar(x + offset, scores, bar_width, label=model, color=color,
               edgecolor='white', linewidth=0.5, zorder=3)

    # Human baseline band
    ax.axhspan(0.60, 0.85, alpha=0.10, color='#34A853', zorder=0)
    text_x = n_benchmarks - 0.6 if track_name != 'metacognition' else n_benchmarks - 0.6
    ax.text(text_x, 0.87, 'Human\nBaseline', fontsize=8, fontstyle='italic',
            color='#166534', ha='right' if track_name != 'metacognition' else 'center', va='bottom')

    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(track['bench_labels'], fontsize=8.5 if n_benchmarks > 5 else 10)
    ax.set_ylim(0, 1.18 if track_name == 'metacognition' else 1.05)
    ax.set_xlim(-0.6, n_benchmarks - 0.4)
    ax.set_title(track['title'], fontsize=14, fontweight='bold', pad=30)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, f'{track_name}_cover.png')
    fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    # Verify
    img = Image.open(out_path)
    w, h = img.size
    fsize = os.path.getsize(out_path)
    print(f'Saved: {out_path}  |  {w}x{h}px  |  {fsize/1024:.0f} KB  |  {"OK" if w >= 1000 else "WARN: width < 1000"}')

print('\nAll 5 cover images regenerated from final 10-model scores.')
