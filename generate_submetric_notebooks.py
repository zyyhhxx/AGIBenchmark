#!/usr/bin/env python3
"""Generate notebooks for sub-metric benchmarks."""
import json, os

def read_file(path):
    with open(path) as f:
        return f.read()

def make_cell(source, cell_type="code"):
    cell = {"cell_type": cell_type, "metadata": {}, "source": source.split("\n")}
    if cell_type == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
    return cell

def make_notebook(cells, title):
    pip_cell = {"cell_type": "code", "metadata": {"trusted": True},
                "source": ["!pip install -q protobuf==5.29.6 kaggle-benchmarks numpy 2>/dev/null\n"],
                "execution_count": None, "outputs": []}
    return {
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.0"},
            "kaggle": {"title": title}
        },
        "nbformat": 4, "nbformat_minor": 5, "cells": [pip_cell] + cells
    }

os.chdir(os.path.dirname(__file__))

# JOL submetrics
jol_data = read_file("benchmarks/metacognition/data/jol_stimuli.py")
jol_task = read_file("benchmarks/metacognition/task_jol_submetrics.py")
jol_task = jol_task.replace(
    "from data.jol_stimuli import JOL_WORD_PAIRS, JOL_RULE_SYSTEMS, DISTRACTOR_QUESTIONS",
    "# JOL data defined above"
)
nb = make_notebook([
    make_cell("# JOL Sub-metrics Benchmark\n\nIndividual JOL metrics: gamma, ECE, recall.\n\n**Cognitive Science**: Nelson & Dunlosky (1991)", "markdown"),
    make_cell(jol_data),
    make_cell(jol_task),
], "JOL Sub-metrics Benchmark")
with open("notebooks/metacog_jol_submetrics.ipynb", "w") as f:
    json.dump(nb, f, indent=2)
print("Generated metacog_jol_submetrics.ipynb")

# FOK submetrics
fok_data = read_file("benchmarks/metacognition/data/fok_questions.py")
fok_task = read_file("benchmarks/metacognition/task_fok_submetrics.py")
fok_task = fok_task.replace(
    "from data.fok_questions import FOK_QUESTIONS",
    "# FOK_QUESTIONS defined above"
)
nb = make_notebook([
    make_cell("# FOK Sub-metrics Benchmark\n\nIndividual FOK metrics.\n\n**Cognitive Science**: Hart (1965)", "markdown"),
    make_cell(fok_data),
    make_cell(fok_task),
], "FOK Sub-metrics Benchmark")
with open("notebooks/metacog_fok_submetrics.ipynb", "w") as f:
    json.dump(nb, f, indent=2)
print("Generated metacog_fok_submetrics.ipynb")

# Error detection submetrics
err_data = read_file("benchmarks/metacognition/data/error_detection_chains.py")
err_task = read_file("benchmarks/metacognition/task_error_detection_submetrics.py")
err_task = err_task.replace(
    "from data.error_detection_chains import REASONING_CHAINS",
    "# REASONING_CHAINS defined above"
)
nb = make_notebook([
    make_cell("# Error Detection Sub-metrics Benchmark\n\nIndividual error detection metrics: F1, localization, ECE, gamma.\n\n**Cognitive Science**: Yeung & Summerfield (2012)", "markdown"),
    make_cell(err_data),
    make_cell(err_task),
], "Error Detection Sub-metrics Benchmark")
with open("notebooks/metacog_error_detection_submetrics.ipynb", "w") as f:
    json.dump(nb, f, indent=2)
print("Generated metacog_error_detection_submetrics.ipynb")
