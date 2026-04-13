#!/usr/bin/env python3
"""Generate self-contained Kaggle notebooks for all 4 Executive Functions benchmarks."""

import json
import sys
import os

# Add benchmarks to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'benchmarks', 'executive_functions'))

def make_notebook(title, description, code_cells):
    """Create a Jupyter notebook dict."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {"trusted": True},
            "source": ["!pip install -q protobuf==5.29.6 kaggle-benchmarks numpy 2>/dev/null\n"],
            "execution_count": None,
            "outputs": []
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": description
        }
    ]
    for code in code_cells:
        cells.append({
            "cell_type": "code",
            "metadata": {},
            "source": code.split("\n"),
            "execution_count": None,
            "outputs": []
        })
    
    return {
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.0"},
            "kaggle": {"title": title}
        },
        "nbformat": 4,
        "nbformat_minor": 5,
        "cells": cells
    }


def generate_wcst_notebook():
    """WCST notebook with inline stimuli and task."""
    # Read source files
    with open("benchmarks/executive_functions/data/wcst_stimuli.py") as f:
        stimuli_code = f.read()
    with open("benchmarks/executive_functions/task_wcst.py") as f:
        task_code = f.read()
    
    # Remove the data import from task code and make it use inline stimuli
    task_code = task_code.replace(
        "from data.wcst_stimuli import WCST_STIMULI, card_str",
        "# Stimuli defined above"
    )
    
    desc = [
        "# Wisconsin Card Sort Test (WCST) Analogue",
        "",
        "Tests cognitive flexibility / set-shifting.",
        "Model infers sorting rule from feedback, adapts when rule silently changes.",
        "",
        "**Cognitive Science**: Berg (1948), Milner (1963), Miyake et al. (2000)",
        "**Key metrics**: Perseveration rate, set-shifting speed",
        "**Human perseveration**: ~10-15% (healthy adults)"
    ]
    
    nb = make_notebook("WCST Analogue — Executive Functions", desc, [stimuli_code, task_code])
    
    with open("notebooks/exec_func_wcst.ipynb", "w") as f:
        json.dump(nb, f, indent=2)
    print("Generated: notebooks/exec_func_wcst.ipynb")


def generate_tol_notebook():
    """Tower of London notebook."""
    with open("benchmarks/executive_functions/data/tol_problems.py") as f:
        stimuli_code = f.read()
    with open("benchmarks/executive_functions/task_tol.py") as f:
        task_code = f.read()
    
    task_code = task_code.replace(
        "from data.tol_problems import TOL_PROBLEMS, state_str, PEG_CAPACITY, apply_move, get_valid_moves, state_to_tuple",
        "# Stimuli and helpers defined above"
    )
    
    desc = [
        "# Tower of London Planning Benchmark",
        "",
        "Tests multi-step planning ability.",
        "Model must find optimal move sequences to rearrange balls on pegs.",
        "",
        "**Cognitive Science**: Shallice (1982), Owen et al. (1990)",
        "**Key metrics**: Optimality ratio, depth scaling",
        "**Human optimality**: ~85% at 3 moves, ~55% at 5 moves"
    ]
    
    nb = make_notebook("Tower of London — Executive Functions", desc, [stimuli_code, task_code])
    
    with open("notebooks/exec_func_tol.ipynb", "w") as f:
        json.dump(nb, f, indent=2)
    print("Generated: notebooks/exec_func_tol.ipynb")


def generate_task_switch_notebook():
    """Task-switching notebook."""
    with open("benchmarks/executive_functions/data/task_switch_stimuli.py") as f:
        stimuli_code = f.read()
    with open("benchmarks/executive_functions/task_switching.py") as f:
        task_code = f.read()
    
    task_code = task_code.replace(
        "from data.task_switch_stimuli import TASK_SWITCH_TRIALS",
        "# Stimuli defined above"
    )
    
    desc = [
        "# Task-Switching Benchmark",
        "",
        "Tests cognitive flexibility via alternating classification rules.",
        "Key metric: switch cost (accuracy drop on switch vs. repeat trials).",
        "",
        "**Cognitive Science**: Rogers & Monsell (1995), Miyake et al. (2000)",
        "**Human switch cost**: ~5-10% accuracy drop on switch trials"
    ]
    
    nb = make_notebook("Task Switching — Executive Functions", desc, [stimuli_code, task_code])
    
    with open("notebooks/exec_func_task_switch.ipynb", "w") as f:
        json.dump(nb, f, indent=2)
    print("Generated: notebooks/exec_func_task_switch.ipynb")


def generate_nback_notebook():
    """N-back notebook."""
    with open("benchmarks/executive_functions/data/nback_stimuli.py") as f:
        stimuli_code = f.read()
    with open("benchmarks/executive_functions/task_nback.py") as f:
        task_code = f.read()
    
    task_code = task_code.replace(
        "from data.nback_stimuli import NBACK_SEQUENCES",
        "# Stimuli defined above"
    )
    
    desc = [
        "# N-back Working Memory Benchmark",
        "",
        "Tests working memory updating across N=1, 2, 3 levels.",
        "Model identifies when current item matches the one N positions back.",
        "",
        "**Cognitive Science**: Kirchner (1958), Owen et al. (2005), Miyake et al. (2000)",
        "**Key metrics**: d-prime per N level",
        "**Human d-prime**: ~3.5 (1-back), ~2.5 (2-back), ~1.5 (3-back)"
    ]
    
    nb = make_notebook("N-back Working Memory — Executive Functions", desc, [stimuli_code, task_code])
    
    with open("notebooks/exec_func_nback.ipynb", "w") as f:
        json.dump(nb, f, indent=2)
    print("Generated: notebooks/exec_func_nback.ipynb")


if __name__ == "__main__":
    generate_wcst_notebook()
    generate_tol_notebook()
    generate_task_switch_notebook()
    generate_nback_notebook()
    print("\nAll 4 Executive Functions notebooks generated!")
