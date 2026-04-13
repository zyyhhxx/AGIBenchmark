#!/usr/bin/env python3
"""Generate cover images for all 4 non-metacognition tracks."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUTPUT_DIR = '/home/ubuntu/.openclaw/workspace-agi-bench/repo/assets'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 5 representative models for bar charts (matching metacognition cover style)
MODELS = ['Claude Opus 4.6', 'Claude Sonnet 4.6', 'Nova Pro', 'Llama 3.3 70B', 'Ministral 3B']
MODEL_COLORS = ['#4285F4', '#7BAAF7', '#F4A623', '#34A853', '#EA4335']

TRACKS = {
    'attention': {
        'title': 'Attention Benchmark Suite: Cognitive Profile\nacross 10 AI Models',
        'benchmarks': ['Divided\nAttention', 'Instruction\nUpdate', 'Selective\nAttention', 'Vigilance\n(N-back)'],
        'scores': {
            'Claude Opus 4.6':    [0.9306, 0.9833, 0.8950, 0.8559],
            'Claude Sonnet 4.6':  [0.9167, 0.9833, 0.8950, 0.8647],
            'Nova Pro':           [0.6894, 0.6121, 0.8200, 0.5857],
            'Llama 3.3 70B':      [0.8264, 0.9525, 0.8700, 0.5803],
            'Ministral 3B':       [0.4139, 0.2992, 0.7750, 0.5677],
        },
        'groups': [
            ('Multi-Stream\nProcessing', 0, 2),
            ('Sustained\nMonitoring', 2, 4),
        ],
        'group_colors': ['#E8F0FE', '#FEF7E0'],
    },
    'learning': {
        'title': 'Learning Benchmark Suite: Cognitive Profile\nacross 10 AI Models',
        'benchmarks': ['Transfer', 'Interference', 'Curriculum', 'Learning\nCurves'],
        'scores': {
            'Claude Opus 4.6':    [1.0000, 0.1200, 0.7000, 0.7267],
            'Claude Sonnet 4.6':  [1.0000, 1.0000, 0.7000, 0.7167],
            'Nova Pro':           [0.5500, 0.7830, 0.4600, 0.6550],
            'Llama 3.3 70B':      [0.5200, 0.4000, 0.7600, 0.5467],
            'Ministral 3B':       [0.2800, 0.4410, 0.6800, 0.5617],
        },
        'groups': [
            ('Knowledge\nApplication', 0, 2),
            ('Acquisition\nProcess', 2, 4),
        ],
        'group_colors': ['#E8F0FE', '#E6F4EA'],
    },
    'executive_functions': {
        'title': 'Executive Functions Benchmark Suite: Cognitive Profile\nacross 10 AI Models',
        'benchmarks': ['CRT\n(Inhibition)', 'N-back\n(Updating)', 'Task Switch\n(Shifting)', 'Tower of\nLondon', 'WCST\n(Set Shift)'],
        'scores': {
            'Claude Opus 4.6':    [0.9142, 1.0000, 1.0000, 0.8000, 1.0000],
            'Claude Sonnet 4.6':  [0.8000, 1.0000, 0.9005, 0.0000, 0.6985],
            'Nova Pro':           [0.5126, 0.8060, 0.7125, 0.2800, 0.5264],
            'Llama 3.3 70B':      [0.6116, 1.0000, 0.7225, 0.1533, 0.4792],
            'Ministral 3B':       [0.4542, 0.5136, 0.7750, 0.1600, 0.2607],
        },
        'groups': [
            ('Inhibition &\nUpdating', 0, 2),
            ('Flexibility', 2, 3),
            ('Planning &\nSet Shifting', 3, 5),
        ],
        'group_colors': ['#E8F0FE', '#FEF7E0', '#FCE8E6'],
    },
    'social_cognition': {
        'title': 'Social Cognition Benchmark Suite: Cognitive Profile\nacross 10 AI Models',
        'benchmarks': ['False Belief\n(ToM)', 'Pragmatic\nInference', 'Sarcasm\nDetection', 'Emotional\nProsody'],
        'scores': {
            'Claude Opus 4.6':    [0.5833, 0.8674, 0.9261, 0.8022],
            'Claude Sonnet 4.6':  [0.7937, 0.7774, 0.8147, 0.8356],
            'Nova Pro':           [0.6375, 0.3041, 0.8536, 0.8300],
            'Llama 3.3 70B':      [0.8625, 0.8680, 0.9239, 0.8383],
            'Ministral 3B':       [0.6823, 0.4757, 0.7972, 0.6856],
        },
        'groups': [
            ('Mentalizing', 0, 2),
            ('Social Language', 2, 4),
        ],
        'group_colors': ['#E8F0FE', '#F3E8FD'],
    },
}

for track_name, track in TRACKS.items():
    benchmarks = track['benchmarks']
    n_benchmarks = len(benchmarks)
    n_models = len(MODELS)
    
    fig, ax = plt.subplots(figsize=(max(12, n_benchmarks * 2.5), 8), dpi=150)
    
    # Background groups
    for label, start, end in track['groups']:
        color = track['group_colors'][track['groups'].index((label, start, end))]
        ax.axvspan(start - 0.5, end - 0.5, alpha=0.3, color=color, zorder=0)
        mid = (start + end) / 2 - 0.5
        ax.text(mid, 1.02, label, ha='center', va='bottom', fontsize=10, fontstyle='italic',
                transform=ax.get_xaxis_transform())
    
    # Bars
    bar_width = 0.15
    x = np.arange(n_benchmarks)
    for i, model in enumerate(MODELS):
        scores = track['scores'][model]
        offset = (i - n_models/2 + 0.5) * bar_width
        ax.bar(x + offset, scores, bar_width, label=model, color=MODEL_COLORS[i], zorder=3)
    
    # Human baseline band
    ax.axhspan(0.60, 0.85, alpha=0.12, color='#34A853', zorder=1)
    ax.text(n_benchmarks - 0.6, 0.83, 'Human\nBaseline', fontsize=9, fontstyle='italic',
            color='#34A853', ha='right', va='top')
    
    ax.set_ylabel('Score', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks, fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.set_title(track['title'], fontsize=14, fontweight='bold', pad=30)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, zorder=0)
    
    # Group dividers
    for label, start, end in track['groups']:
        if start > 0:
            ax.axvline(x=start - 0.5, color='gray', linestyle='--', alpha=0.4, zorder=2)
    
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, f'{track_name}_cover.png')
    fig.savefig(out_path, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {out_path}')

print('All 4 cover images generated.')
