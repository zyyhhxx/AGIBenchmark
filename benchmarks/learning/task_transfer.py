"""
Learning Benchmark 2: Near vs. Far Transfer (v3)

Tests whether models can genuinely transfer learned structure to novel contexts,
NOT just follow explicit instructions.

Cognitive Science Basis:
- Thorndike & Woodworth (1901): Transfer of practice
- Barnett & Ceci (2002): Taxonomy of far transfer
- Anderson (1987): ACT* theory — procedural vs. declarative transfer

Core Problem Fixed (v1/v2):
Previous versions gave the model all rules in EVERY condition — making it
instruction following, not genuine transfer. v3 forces actual abstraction:
- Near transfer: same domain but INCOMPLETE rules (1 rule omitted)
- Far transfer: different domain, NO rules — only 2 worked examples
- Zero-shot structural: completely different representation, only 1 example

Score = weighted accuracy across 4 conditions.
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.rule_systems import (
    TRANSFER_TRAIN_V3,
    TRANSFER_NEAR_V3,
    TRANSFER_FAR_V3,
    TRANSFER_ZERO_SHOT_V3,
)


def _strip_think(text: str) -> str:
    """Strip <think>...</think> tags from reasoning model output."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def normalize_output(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def check_output(model_output: str, expected: str) -> bool:
    m = normalize_output(model_output)
    e = normalize_output(expected)
    return e in m or m in e


def _extract_answer(raw: str) -> str:
    cleaned = _strip_think(raw)
    cleaned = re.sub(r'//.*', '', cleaned)
    try:
        parsed = json.loads(re.search(r'\{.*\}', cleaned, re.DOTALL).group())
        return str(parsed.get("answer", cleaned))
    except Exception:
        return cleaned


# ── Build training block (full rules + 10 examples) ─────────────────

def _full_system_block(system, max_examples: int = 10) -> str:
    block = f"**Rule System: {system.name}**\n"
    block += f"Description: {system.description}\n\n"
    block += "**Rules:**\n"
    for r in system.rules:
        block += f"  - {r}\n"
    block += "\n**Examples:**\n"
    for ex in system.examples[:max_examples]:
        block += f"  Input: {ex['input']}  →  Output: {ex['output']}\n"
    return block


@kbench.task(name="Near & Far Transfer v3")
def learning_transfer(llm) -> float:
    """
    Near vs. Far Transfer Benchmark (v3).

    Four conditions with increasing transfer distance:
    1. Identical (weight 0.15): same system, all rules given, held-out items
    2. Near transfer (weight 0.25): same domain (symbol), INCOMPLETE rules (1 omitted)
    3. Far transfer (weight 0.30): different domain (number), NO rules — 2 worked examples only
    4. Zero-shot structural (weight 0.30): stateful system, NO rules — 1 worked example only

    Score = 0.15 * identical + 0.25 * near + 0.30 * far + 0.30 * zero_shot
    """

    train_block = _full_system_block(TRANSFER_TRAIN_V3, max_examples=10)
    results = {}

    # ── Condition 1: Identical ─────────────────────────────────────
    # Same system, all rules given, held-out test items. Baseline.
    condition_results = []
    for ti, test_item in enumerate(TRANSFER_TRAIN_V3.test_items):
        with kbench.chats.new(f"identical_{ti}"):
            prompt = (
                f"You have learned the following rule system:\n\n{train_block}\n"
                f"Apply the rules to this new input:\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<steps>\"}}"
            )
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            condition_results.append(check_output(answer, test_item["output"]))
    results["identical"] = sum(condition_results) / len(condition_results)

    # ── Condition 2: Near Transfer ─────────────────────────────────
    # Same domain (symbol), but 1 rule is OMITTED from the new system.
    # Model must infer the missing rule from structural similarity to training.
    near_block = f"\n**New Rule System (similar domain): {TRANSFER_NEAR_V3.name}**\n"
    near_block += f"Description: {TRANSFER_NEAR_V3.description}\n\n"
    near_block += "**Rules (note: one rule has been omitted — infer it from context):**\n"
    for r in TRANSFER_NEAR_V3.rules:
        near_block += f"  - {r}\n"
    near_block += "\n(No worked examples provided — use structural analogy from the training system above.)\n"

    condition_results = []
    for ti, test_item in enumerate(TRANSFER_NEAR_V3.test_items):
        with kbench.chats.new(f"near_{ti}"):
            prompt = (
                f"You previously learned a symbol transformation system:\n\n"
                f"{train_block}\n"
                f"Now apply a similar system where ONE rule has been deliberately omitted.\n"
                f"Infer the missing rule from the structural similarity to the training system above.\n"
                f"{near_block}\n"
                f"Apply the NEW system's rules (inferring the omitted rule) to:\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<inferred rule + steps>\"}}"
            )
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            condition_results.append(check_output(answer, test_item["output"]))
    results["near"] = sum(condition_results) / len(condition_results)

    # ── Condition 3: Far Transfer ──────────────────────────────────
    # Different domain (number system). NO explicit rules given.
    # Only 2 worked examples + description. Model must abstract principles.
    far_block = f"\n**New Rule System (different domain): {TRANSFER_FAR_V3.name}**\n"
    far_block += f"Description: {TRANSFER_FAR_V3.description}\n\n"
    far_block += "**NO rules provided.** Infer the operators from these 2 worked examples:\n"
    for ex in TRANSFER_FAR_V3.examples[:2]:
        far_block += f"  Input: {ex['input']}  →  Output: {ex['output']}\n"
    far_block += "\n(You must deduce how the operators work from the examples above.)\n"

    condition_results = []
    for ti, test_item in enumerate(TRANSFER_FAR_V3.test_items):
        with kbench.chats.new(f"far_{ti}"):
            prompt = (
                f"You previously learned a symbol transformation system:\n\n"
                f"{train_block}\n"
                f"Now apply your general learning ability to a completely different kind of system.\n"
                f"No rules are given — you must infer the operator semantics from examples.\n"
                f"{far_block}\n"
                f"Apply the inferred rules to:\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<inferred rules + steps>\"}}"
            )
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            condition_results.append(check_output(answer, test_item["output"]))
    results["far"] = sum(condition_results) / len(condition_results)

    # ── Condition 4: Zero-Shot Structural Transfer ─────────────────
    # Completely different representation: stateful accumulator.
    # Only description + 1 worked example. No rules.
    # Model must infer rules from minimal information + structural analogy.
    zs_ex = TRANSFER_ZERO_SHOT_V3.examples[0]
    zs_block = f"\n**New Rule System (completely different representation): {TRANSFER_ZERO_SHOT_V3.name}**\n"
    zs_block += f"Description: {TRANSFER_ZERO_SHOT_V3.description}\n\n"
    zs_block += "**NO rules provided.** Only one worked example:\n"
    zs_block += f"  Input: {zs_ex['input']}  →  Output: {zs_ex['output']}\n"
    zs_block += "\n(Tokens are A, B, C, D. Figure out what each token does from this single example "
    zs_block += "and any structural analogy you can draw from your prior learning.)\n"

    condition_results = []
    for ti, test_item in enumerate(TRANSFER_ZERO_SHOT_V3.test_items):
        with kbench.chats.new(f"zero_shot_{ti}"):
            prompt = (
                f"You previously learned a symbol transformation system:\n\n"
                f"{train_block}\n"
                f"Now attempt zero-shot structural transfer to a radically different system.\n"
                f"You have only ONE worked example. Infer the complete rule set.\n"
                f"{zs_block}\n"
                f"Apply the inferred rules to:\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<inferred rules + computation>\"}}"
            )
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            condition_results.append(check_output(answer, test_item["output"]))
    results["zero_shot"] = sum(condition_results) / len(condition_results)

    # ── Compute Metrics ──
    identical = results["identical"]
    near = results["near"]
    far = results["far"]
    zero_shot = results["zero_shot"]

    near_ratio = near / identical if identical > 0 else 0
    far_ratio = far / identical if identical > 0 else 0
    zs_ratio = zero_shot / identical if identical > 0 else 0

    score = round(
        0.15 * identical
        + 0.25 * near
        + 0.30 * far
        + 0.30 * zero_shot,
        4
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"NEAR VS. FAR TRANSFER BENCHMARK v3 RESULTS")
    print(f"{'='*60}")
    print(f"\n--- Transfer Performance ---")
    print(f"Identical (baseline, 0.15):           {identical:.2%}")
    print(f"Near transfer (0.25):                 {near:.2%}  (ratio: {near_ratio:.2f})")
    print(f"Far transfer (0.30):                  {far:.2%}  (ratio: {far_ratio:.2f})")
    print(f"Zero-shot structural (0.30):          {zero_shot:.2%}  (ratio: {zs_ratio:.2f})")
    print(f"\n--- Transfer Gradient ---")
    for label, val, w in [
        ("Identical", identical, 0.15),
        ("Near     ", near, 0.25),
        ("Far      ", far, 0.30),
        ("Zero-shot", zero_shot, 0.30),
    ]:
        bar = "█" * int(val * 30)
        print(f"  {label}: {val:.2%} {bar}")
    print(f"\nComposite score: {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
learning_transfer.run(llm=kbench.llm)
