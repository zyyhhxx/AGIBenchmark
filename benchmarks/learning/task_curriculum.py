"""
Learning Benchmark 4: Curriculum Sensitivity

Tests whether the ORDER of training examples affects learning outcomes.
This is a key finding from educational psychology — curriculum design
matters for human learning, and any genuine learning system should
show sensitivity to example ordering.

Cognitive Science Basis:
- Rohrer & Taylor (2007): Interleaving vs. blocking practice
- Elio & Anderson (1981): Effects of category generality on learning
- Curriculum Learning (Bengio et al., 2009): Easy-to-hard ordering

Protocol:
1. Present the same rule system under different orderings:
   a. RANDOM: Examples in random order
   b. EASY-HARD: Sorted from simple to complex
   c. HARD-EASY: Sorted from complex to simple
   d. BLOCKED: Grouped by sub-rule (e.g., all rule-1 examples, then rule-2)
   e. INTERLEAVED: Alternating between sub-rules
2. After each curriculum, test on the same held-out items
3. Measure: Does ordering matter? Which ordering works best?

Score: Captures both sensitivity to ordering and optimal ordering selection.
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
import random
from data.rule_systems import generate_symbol_system


@dataclass
class CurriculumAnswer:
    answer: str


def normalize_output(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def check_output(model_output: str, expected: str) -> bool:
    m = normalize_output(model_output)
    e = normalize_output(expected)
    return e in m or m in e


# Use a medium-difficulty system with enough examples to order meaningfully
CURRICULUM_SYSTEM = generate_symbol_system("curriculum_v2", difficulty=2)


def sort_by_complexity(examples: list) -> list:
    """Sort examples by input length (proxy for complexity)."""
    return sorted(examples, key=lambda x: len(x["input"]))


def run_curriculum(llm, system, examples: list, label: str) -> float:
    """Run a single curriculum ordering and return test accuracy."""
    correct = 0

    for ti, test_item in enumerate(system.test_items):
        with kbench.chats.new(f"curriculum_{label}_{ti}"):
            prompt = f"**Rule System: {system.name}**\n\n"
            prompt += "**Rules:**\n"
            for r in system.rules:
                prompt += f"- {r}\n"
            prompt += f"\n**Training examples ({len(examples)}):**\n"
            for ex in examples:
                prompt += f"  {ex['input']} → {ex['output']}\n"
            prompt += (
                f"\nApply the rules to:\nInput: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\"}}"
            )

            try:
                result = llm.prompt(prompt, schema=CurriculumAnswer)
                answer = result.answer
            except Exception:
                raw = llm.prompt(prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    answer = str(parsed.get("answer", raw))
                except Exception:
                    answer = raw

            if check_output(answer, test_item["output"]):
                correct += 1

    return correct / len(system.test_items) if system.test_items else 0


@kbench.task(name="learning_curriculum")
def learning_curriculum(llm) -> float:
    """
    Curriculum Sensitivity Benchmark.

    Tests whether example ordering affects learning.
    Genuine learning systems should show curriculum effects.

    Score = 0.40 * max_accuracy + 0.30 * sensitivity + 0.30 * optimal_ordering_bonus

    Where:
    - max_accuracy: best accuracy across orderings
    - sensitivity: range of accuracies (higher = more sensitive to ordering)
    - optimal_ordering_bonus: whether easy→hard beats random
    """
    system = CURRICULUM_SYSTEM
    examples = system.examples[:10]  # Use 10 examples

    rng = random.Random(42)

    # Create curriculum orderings
    orderings = {}

    # Random
    random_examples = list(examples)
    rng.shuffle(random_examples)
    orderings["random"] = random_examples

    # Easy → Hard (short inputs first)
    orderings["easy_hard"] = sort_by_complexity(examples)

    # Hard → Easy (long inputs first)
    orderings["hard_easy"] = sort_by_complexity(examples)[::-1]

    # Interleaved (alternating short and long)
    sorted_ex = sort_by_complexity(examples)
    interleaved = []
    left, right = 0, len(sorted_ex) - 1
    while left <= right:
        interleaved.append(sorted_ex[left])
        if left != right:
            interleaved.append(sorted_ex[right])
        left += 1
        right -= 1
    orderings["interleaved"] = interleaved

    # Run each curriculum
    results = {}
    for label, ordered_examples in orderings.items():
        acc = run_curriculum(llm, system, ordered_examples, label)
        results[label] = acc

    # ── Compute Metrics ──
    accuracies = list(results.values())
    max_acc = max(accuracies)
    min_acc = min(accuracies)
    sensitivity = max_acc - min_acc  # Range of performance

    # Optimal ordering bonus: easy→hard should beat random
    optimal_bonus = 0.0
    if results.get("easy_hard", 0) > results.get("random", 0):
        optimal_bonus = 0.5
    if results.get("easy_hard", 0) >= max_acc:
        optimal_bonus = 1.0

    score = round(
        0.40 * max_acc + 0.30 * sensitivity + 0.30 * optimal_bonus,
        4
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"CURRICULUM SENSITIVITY BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"System: {system.name}")
    print(f"Training examples: {len(examples)}")
    print(f"Test items: {len(system.test_items)}")

    print(f"\n--- Accuracy by Ordering ---")
    for label, acc in sorted(results.items(), key=lambda x: -x[1]):
        bar = "█" * int(acc * 30)
        marker = " ← best" if acc == max_acc else ""
        print(f"  {label:15s}: {acc:.2%} {bar}{marker}")

    print(f"\n--- Metrics ---")
    print(f"Max accuracy:        {max_acc:.2%}")
    print(f"Sensitivity (range): {sensitivity:.2%}")
    print(f"Optimal ordering:    {optimal_bonus:.1f}")
    print(f"Composite score:     {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
learning_curriculum.run(llm=kbench.llm)
