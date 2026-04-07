#!/usr/bin/env python3
"""Generate self-contained Kaggle notebooks for all 3 Social Cognition benchmarks."""

import json
import sys
import os

def make_notebook(title, description, code_cells):
    cells = [
        {"cell_type": "markdown", "metadata": {}, "source": description}
    ]
    for code in code_cells:
        cells.append({
            "cell_type": "code", "metadata": {},
            "source": code.split("\n"),
            "execution_count": None, "outputs": []
        })
    return {
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.0"},
            "kaggle": {"title": title}
        },
        "nbformat": 4, "nbformat_minor": 5, "cells": cells
    }


def generate_false_belief_notebook():
    with open("benchmarks/social_cognition/data/false_belief_scenarios.py") as f:
        data_code = f.read()
    with open("benchmarks/social_cognition/task_false_belief.py") as f:
        task_code = f.read()
    task_code = task_code.replace(
        "from data.false_belief_scenarios import FALSE_BELIEF_SCENARIOS",
        "# Data defined above"
    )
    desc = [
        "# False-Belief Theory of Mind Benchmark",
        "",
        "Tests 1st-order and 2nd-order belief attribution via Sally-Anne scenarios.",
        "Control questions isolate ToM from comprehension.",
        "",
        "**Cognitive Science**: Wimmer & Perner (1983), Baron-Cohen et al. (1985)",
        "**Human 1st-order**: ~95% (adults), **2nd-order**: ~80%"
    ]
    nb = make_notebook("False-Belief ToM — Social Cognition", desc, [data_code, task_code])
    with open("notebooks/social_cog_false_belief.ipynb", "w") as f:
        json.dump(nb, f, indent=2)
    print("Generated: notebooks/social_cog_false_belief.ipynb")


def generate_pragmatic_notebook():
    with open("benchmarks/social_cognition/data/pragmatic_items.py") as f:
        data_code = f.read()
    with open("benchmarks/social_cognition/task_pragmatic.py") as f:
        task_code = f.read()
    task_code = task_code.replace(
        "from data.pragmatic_items import PRAGMATIC_ITEMS",
        "# Data defined above"
    )
    desc = [
        "# Pragmatic Inference Benchmark",
        "",
        "Tests understanding of speaker intent beyond literal meaning.",
        "Covers scalar implicature, indirect requests, irony, and understatement.",
        "",
        "**Cognitive Science**: Grice (1975), Horn (1984), Searle (1975)",
        "**Human intended accuracy**: ~90-95%"
    ]
    nb = make_notebook("Pragmatic Inference — Social Cognition", desc, [data_code, task_code])
    with open("notebooks/social_cog_pragmatic.ipynb", "w") as f:
        json.dump(nb, f, indent=2)
    print("Generated: notebooks/social_cog_pragmatic.ipynb")


def generate_sarcasm_notebook():
    with open("benchmarks/social_cognition/data/sarcasm_items.py") as f:
        data_code = f.read()
    with open("benchmarks/social_cognition/task_sarcasm.py") as f:
        task_code = f.read()
    task_code = task_code.replace(
        "from data.sarcasm_items import SARCASM_ITEMS",
        "# Data defined above"
    )
    desc = [
        "# Sarcasm Detection in Context Benchmark",
        "",
        "Tests discrimination between sarcastic and sincere utterances.",
        "Matched pairs: same utterance, different context → different intent.",
        "",
        "**Cognitive Science**: Gibbs (1986), Shamay-Tsoory et al. (2005)",
        "**Human AUC**: ~0.95 with context"
    ]
    nb = make_notebook("Sarcasm Detection — Social Cognition", desc, [data_code, task_code])
    with open("notebooks/social_cog_sarcasm.ipynb", "w") as f:
        json.dump(nb, f, indent=2)
    print("Generated: notebooks/social_cog_sarcasm.ipynb")


if __name__ == "__main__":
    generate_false_belief_notebook()
    generate_pragmatic_notebook()
    generate_sarcasm_notebook()
    print("\nAll 3 Social Cognition notebooks generated!")
