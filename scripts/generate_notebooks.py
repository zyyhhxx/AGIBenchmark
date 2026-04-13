#!/usr/bin/env python3
"""
Generate Kaggle notebook JSON files from our benchmark task scripts.

Each notebook is self-contained: all data and code are inlined.
This allows direct upload to Kaggle without external dependencies
(beyond kaggle-benchmarks SDK which is pre-installed).
"""

import json
import os
import sys


def make_cell(source: str, cell_type: str = "code") -> dict:
    """Create a Jupyter notebook cell."""
    cell = {
        "cell_type": cell_type,
        "metadata": {},
        "source": source.split("\n"),
    }
    if cell_type == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
    return cell


def make_notebook(cells: list[dict], title: str) -> dict:
    """Create a Jupyter notebook structure with pip install cell."""
    pip_cell = make_cell("!pip install -q protobuf==5.29.6 kaggle-benchmarks numpy 2>/dev/null\n")
    return {
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.10.0",
            },
            "kaggle": {
                "title": title,
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
        "cells": [pip_cell] + cells,
    }


def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def generate_metacog_calibration():
    """Generate the calibration benchmark notebook."""
    cells = [
        make_cell(
            "# Metacognitive Calibration Benchmark\n\n"
            "Tests whether a model's stated confidence matches actual accuracy.\n"
            "Grounded in Nelson & Narens (1990) metamemory monitoring framework.\n\n"
            "**Cognitive Science Basis**: Retrospective confidence judgment.\n"
            "**Human baseline ECE**: 0.10–0.20\n"
            "**Score**: 1 - ECE (higher = better calibrated)",
            "markdown"
        ),
        make_cell(read_file("benchmarks/metacognition/task_calibration.py")),
    ]
    return make_notebook(cells, "Metacognitive Calibration Benchmark")


def generate_metacog_fok():
    """Generate the FOK benchmark notebook."""
    fok_data = read_file("benchmarks/metacognition/data/fok_questions.py")
    fok_task = read_file("benchmarks/metacognition/task_fok.py")

    # Replace the import with inline data
    fok_task = fok_task.replace(
        "from data.fok_questions import FOK_QUESTIONS",
        "# FOK_QUESTIONS is defined above"
    )

    cells = [
        make_cell(
            "# Feeling-of-Knowing (FOK) Benchmark\n\n"
            "Two-phase prospective metacognitive monitoring benchmark.\n"
            "Phase 1: Rate confidence BEFORE answering.\n"
            "Phase 2: Actually answer.\n\n"
            "**Cognitive Science**: Hart (1965), Nelson & Narens (1990)\n"
            "**Human FOK gamma**: 0.25–0.55\n"
            "**Key innovation**: Two-phase protocol prevents post-hoc rationalization",
            "markdown"
        ),
        make_cell(fok_data),
        make_cell(fok_task),
    ]
    return make_notebook(cells, "Feeling-of-Knowing (FOK) Benchmark")


def generate_metacog_jol():
    """Generate the JOL benchmark notebook."""
    jol_data = read_file("benchmarks/metacognition/data/jol_stimuli.py")
    jol_task = read_file("benchmarks/metacognition/task_jol.py")

    jol_task = jol_task.replace(
        "from data.jol_stimuli import JOL_WORD_PAIRS, JOL_RULE_SYSTEMS, DISTRACTOR_QUESTIONS",
        "# JOL data defined above"
    )

    cells = [
        make_cell(
            "# Judgment-of-Learning (JOL) Benchmark\n\n"
            "Tests prediction of future recall for novel material.\n"
            "Uses invented stimuli that CANNOT be in training data.\n\n"
            "**Cognitive Science**: Arbuckle & Cuddy (1969), Nelson & Narens (1990)\n"
            "**Human JOL gamma**: 0.40–0.90\n"
            "**Key innovation**: All stimuli are invented (no data contamination)",
            "markdown"
        ),
        make_cell(jol_data),
        make_cell(jol_task),
    ]
    return make_notebook(cells, "Judgment-of-Learning (JOL) Benchmark")


def generate_metacog_error():
    """Generate the error detection benchmark notebook."""
    err_data = read_file("benchmarks/metacognition/data/error_detection_chains.py")
    err_task = read_file("benchmarks/metacognition/task_error_detection.py")

    err_task = err_task.replace(
        "from data.error_detection_chains import REASONING_CHAINS",
        "# REASONING_CHAINS defined above"
    )

    cells = [
        make_cell(
            "# Error Detection Benchmark\n\n"
            "Tests ability to detect and localize errors in reasoning chains.\n\n"
            "**Cognitive Science**: Yeung & Summerfield (2012)\n"
            "**Human d'**: 1.5–3.0\n"
            "**Score**: F1 + localization + confidence calibration",
            "markdown"
        ),
        make_cell(err_data),
        make_cell(err_task),
    ]
    return make_notebook(cells, "Error Detection Benchmark")


def generate_learning_curves():
    """Generate the learning curves benchmark notebook."""
    rules_data = read_file("benchmarks/learning/data/rule_systems.py")
    lc_task = read_file("benchmarks/learning/task_learning_curves.py")

    lc_task = lc_task.replace(
        "from data.rule_systems import LEARNING_CURVE_SYSTEMS",
        "# LEARNING_CURVE_SYSTEMS defined above"
    )

    cells = [
        make_cell(
            "# Learning Curves Benchmark\n\n"
            "Tests how performance improves with increasing training examples.\n"
            "Uses procedurally generated rule systems.\n\n"
            "**Cognitive Science**: Power Law of Practice (Newell & Rosenbloom, 1981)\n"
            "**Key innovation**: Novel rule systems that cannot be in training data",
            "markdown"
        ),
        make_cell(rules_data),
        make_cell(lc_task),
    ]
    return make_notebook(cells, "Learning Curves Benchmark")


def generate_learning_transfer():
    """Generate the transfer benchmark notebook."""
    rules_data = read_file("benchmarks/learning/data/rule_systems.py")
    task = read_file("benchmarks/learning/task_transfer.py")
    task = task.replace(
        "from data.rule_systems import (\n    generate_symbol_system, generate_number_system\n)",
        "# Rule system generators defined above"
    )
    cells = [
        make_cell(
            "# Near vs. Far Transfer Benchmark\n\n"
            "Tests generalization across similarity distances.\n\n"
            "**Cognitive Science**: Thorndike & Woodworth (1901), Barnett & Ceci (2002)",
            "markdown"
        ),
        make_cell(rules_data),
        make_cell(task),
    ]
    return make_notebook(cells, "Near vs Far Transfer Benchmark")


def generate_learning_interference():
    rules_data = read_file("benchmarks/learning/data/rule_systems.py")
    task = read_file("benchmarks/learning/task_interference.py")
    task = task.replace(
        "from data.rule_systems import generate_symbol_system",
        "# generate_symbol_system defined above"
    )
    cells = [
        make_cell(
            "# Proactive & Retroactive Interference Benchmark\n\n"
            "**Cognitive Science**: Underwood (1957), Anderson (2003)",
            "markdown"
        ),
        make_cell(rules_data),
        make_cell(task),
    ]
    return make_notebook(cells, "Interference Benchmark")


def generate_learning_curriculum():
    rules_data = read_file("benchmarks/learning/data/rule_systems.py")
    task = read_file("benchmarks/learning/task_curriculum.py")
    task = task.replace(
        "from data.rule_systems import generate_symbol_system",
        "# generate_symbol_system defined above"
    )
    cells = [
        make_cell(
            "# Curriculum Sensitivity Benchmark\n\n"
            "Tests whether example ordering affects learning.\n\n"
            "**Cognitive Science**: Rohrer & Taylor (2007), Bengio et al. (2009)",
            "markdown"
        ),
        make_cell(rules_data),
        make_cell(task),
    ]
    return make_notebook(cells, "Curriculum Sensitivity Benchmark")


def generate_metacog_learning_monitoring():
    rules_data = read_file("benchmarks/metacognition/data/rule_systems.py")
    task = read_file("benchmarks/metacognition/task_learning_monitoring.py")
    task = task.replace(
        "from data.rule_systems import generate_symbol_system, generate_number_system",
        "# Rule system generators defined above"
    )
    cells = [
        make_cell(
            "# Metacognitive Monitoring During Learning\n\n"
            "Cross-domain benchmark testing metacognition while learning.\n\n"
            "**Cognitive Science**: Dunlosky & Nelson (1992), Zimmerman (2000)",
            "markdown"
        ),
        make_cell(rules_data),
        make_cell(task),
    ]
    return make_notebook(cells, "Metacognitive Monitoring During Learning")


def generate_attention_selective():
    data = read_file("benchmarks/attention/data/attention_stimuli.py")
    task = read_file("benchmarks/attention/task_selective.py")
    task = task.replace(
        "from data.attention_stimuli import STROOP_ITEMS",
        "# STROOP_ITEMS defined above"
    )
    cells = [
        make_cell(
            "# Selective Attention (Stroop Analogue) Benchmark\n\n"
            "**Cognitive Science**: Stroop (1935)\n"
            "Tests ability to focus on relevant info while ignoring distractors",
            "markdown"
        ),
        make_cell(data),
        make_cell(task),
    ]
    return make_notebook(cells, "Selective Attention Benchmark")


def generate_attention_vigilance():
    data = read_file("benchmarks/attention/data/attention_stimuli.py")
    task = read_file("benchmarks/attention/task_vigilance.py")
    task = task.replace(
        "from data.attention_stimuli import VIGILANCE_SEQUENCE",
        "# VIGILANCE_SEQUENCE defined above"
    )
    cells = [
        make_cell(
            "# Sustained Attention (Vigilance) Benchmark\n\n"
            "**Cognitive Science**: Mackworth (1948)\n"
            "Tests whether performance degrades over long monitoring tasks",
            "markdown"
        ),
        make_cell(data),
        make_cell(task),
    ]
    return make_notebook(cells, "Sustained Attention Benchmark")


def generate_attention_divided():
    data = read_file("benchmarks/attention/data/attention_stimuli.py")
    task = read_file("benchmarks/attention/task_divided.py")
    task = task.replace(
        "from data.attention_stimuli import DUAL_TASK_ITEMS",
        "# DUAL_TASK_ITEMS defined above"
    )
    cells = [
        make_cell(
            "# Divided Attention (Dual-Task) Benchmark\n\n"
            "**Cognitive Science**: Pashler (1994), Kahneman (1973)\n"
            "Tests performance cost of simultaneous task execution",
            "markdown"
        ),
        make_cell(data),
        make_cell(task),
    ]
    return make_notebook(cells, "Divided Attention Benchmark")


def main():
    os.makedirs("notebooks", exist_ok=True)

    notebooks = {
        # Metacognition track
        "metacog_calibration": generate_metacog_calibration,
        "metacog_fok": generate_metacog_fok,
        "metacog_jol": generate_metacog_jol,
        "metacog_error_detection": generate_metacog_error,
        "metacog_learning_monitoring": generate_metacog_learning_monitoring,
        # Learning track
        "learning_curves": generate_learning_curves,
        "learning_transfer": generate_learning_transfer,
        "learning_interference": generate_learning_interference,
        "learning_curriculum": generate_learning_curriculum,
        # Attention track
        "attention_selective": generate_attention_selective,
        "attention_vigilance": generate_attention_vigilance,
        "attention_divided": generate_attention_divided,
    }

    for name, generator in notebooks.items():
        nb = generator()
        path = f"notebooks/{name}.ipynb"
        with open(path, "w") as f:
            json.dump(nb, f, indent=2)
        n_cells = len(nb["cells"])
        print(f"Generated {path} ({n_cells} cells)")


if __name__ == "__main__":
    main()
