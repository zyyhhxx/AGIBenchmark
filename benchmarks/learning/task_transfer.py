"""
Learning Benchmark 2: Near vs. Far Transfer

Tests whether models can generalize learned rules to novel contexts.
Near transfer: same structure, different surface features.
Far transfer: same principle, completely different domain.

Cognitive Science Basis:
- Thorndike & Woodworth (1901): Transfer of practice
- Barnett & Ceci (2002): Taxonomy of far transfer
- Genuine learning should show some transfer; pure memorization shows none.

Score: Weighted transfer performance across distances.
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.rule_systems import (
    generate_symbol_system, generate_number_system
)


@dataclass
class TransferAnswer:
    answer: str
    reasoning: str


def normalize_output(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def check_output(model_output: str, expected: str) -> bool:
    m = normalize_output(model_output)
    e = normalize_output(expected)
    return e in m or m in e


# ── Transfer Test Sets ──
# Training system: symbol transform (difficulty 2)
# Near transfer: same type (symbol) with different symbols
# Far transfer: number system with structurally analogous rules

TRAIN_SYSTEM = generate_symbol_system("transfer_train_v2", difficulty=2)
NEAR_SYSTEM = generate_symbol_system("transfer_near_v2", difficulty=2)

# For far transfer: we teach the symbol system, then test on number
# system that has analogous structure but different domain
FAR_SYSTEM = generate_number_system("transfer_far_v2", difficulty=2)


@kbench.task(name="Near & Far Transfer")
def learning_transfer(llm) -> float:
    """
    Near vs. Far Transfer Benchmark.

    Train on one rule system, then test transfer to:
    1. Identical: same system, new test items (baseline)
    2. Near: same domain, different surface features
    3. Far: different domain, structurally similar rules

    Score = 0.30 * identical_acc + 0.35 * near_acc + 0.35 * far_acc

    Transfer ratio = far_acc / identical_acc measures genuine generalization.
    """

    # Build training prompt (10 examples from training system)
    training_examples = TRAIN_SYSTEM.examples[:10]
    train_block = f"**Rule System: {TRAIN_SYSTEM.name}**\n\n"
    train_block += f"Description: {TRAIN_SYSTEM.description}\n\n"
    train_block += "**Rules:**\n"
    for r in TRAIN_SYSTEM.rules:
        train_block += f"- {r}\n"
    train_block += "\n**Examples:**\n"
    for ex in training_examples:
        train_block += f"  Input: {ex['input']}  →  Output: {ex['output']}\n"

    results = {}

    # ── Condition 1: Identical (same system, held-out test items) ──
    condition_results = []
    for ti, test_item in enumerate(TRAIN_SYSTEM.test_items):
        with kbench.chats.new(f"identical_{ti}"):
            prompt = (
                train_block +
                f"\nApply the rules to this new input:\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<steps>\"}}"
            )
            try:
                result = llm.prompt(prompt, schema=TransferAnswer)
                answer = result.answer
            except Exception:
                raw = llm.prompt(prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    answer = str(parsed.get("answer", raw))
                except Exception:
                    answer = raw

            condition_results.append(check_output(answer, test_item["output"]))
    results["identical"] = sum(condition_results) / len(condition_results)

    # ── Condition 2: Near Transfer (same domain, different specifics) ──
    # Show training system, then test on NEAR system items with NEAR rules revealed
    near_block = f"\n\n**New Rule System: {NEAR_SYSTEM.name}**\n"
    near_block += f"Description: {NEAR_SYSTEM.description}\n\n"
    near_block += "**Rules:**\n"
    for r in NEAR_SYSTEM.rules:
        near_block += f"- {r}\n"
    near_block += "\n(No examples provided — use your understanding from the previous system.)\n"

    condition_results = []
    for ti, test_item in enumerate(NEAR_SYSTEM.test_items):
        with kbench.chats.new(f"near_{ti}"):
            prompt = (
                f"You previously learned a rule system. Now apply a similar but different system.\n\n"
                f"**Previous system for reference:**\n{train_block}\n"
                f"{near_block}\n"
                f"Apply the NEW rules to:\nInput: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<steps>\"}}"
            )
            try:
                result = llm.prompt(prompt, schema=TransferAnswer)
                answer = result.answer
            except Exception:
                raw = llm.prompt(prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    answer = str(parsed.get("answer", raw))
                except Exception:
                    answer = raw

            condition_results.append(check_output(answer, test_item["output"]))
    results["near"] = sum(condition_results) / len(condition_results)

    # ── Condition 3: Far Transfer (different domain) ──
    far_block = f"\n\n**New Rule System: {FAR_SYSTEM.name}**\n"
    far_block += f"Description: {FAR_SYSTEM.description}\n\n"
    far_block += "**Rules:**\n"
    for r in FAR_SYSTEM.rules:
        far_block += f"- {r}\n"
    far_block += "\n(No examples provided — use your general learning ability.)\n"

    condition_results = []
    for ti, test_item in enumerate(FAR_SYSTEM.test_items):
        with kbench.chats.new(f"far_{ti}"):
            prompt = (
                f"You previously learned a symbol transformation system. "
                f"Now apply a completely different kind of rule system.\n\n"
                f"{far_block}\n"
                f"Apply the rules to:\nInput: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<steps>\"}}"
            )
            try:
                result = llm.prompt(prompt, schema=TransferAnswer)
                answer = result.answer
            except Exception:
                raw = llm.prompt(prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    answer = str(parsed.get("answer", raw))
                except Exception:
                    answer = raw

            condition_results.append(check_output(answer, test_item["output"]))
    results["far"] = sum(condition_results) / len(condition_results)

    # ── Compute Metrics ──
    identical = results["identical"]
    near = results["near"]
    far = results["far"]

    # Transfer ratios
    near_ratio = near / identical if identical > 0 else 0
    far_ratio = far / identical if identical > 0 else 0

    score = round(0.30 * identical + 0.35 * near + 0.35 * far, 4)

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"NEAR VS. FAR TRANSFER BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"\n--- Transfer Performance ---")
    print(f"Identical (baseline): {identical:.2%}")
    print(f"Near transfer:        {near:.2%}  (ratio: {near_ratio:.2f})")
    print(f"Far transfer:         {far:.2%}  (ratio: {far_ratio:.2f})")
    print(f"\n--- Transfer Gradient ---")
    gradient = [identical, near, far]
    for i, (label, val) in enumerate(zip(["Identical", "Near", "Far"], gradient)):
        bar = "█" * int(val * 30)
        print(f"  {label:10s}: {val:.2%} {bar}")
    print(f"\nComposite score: {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
learning_transfer.run(llm=kbench.llm)
