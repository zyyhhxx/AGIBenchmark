"""
Learning Benchmark 1: Novel Rule System Learning Curves (v2)

Measures how model performance improves with increasing training examples,
including far-transfer and steep learning conditions.

Three conditions:
  A) Standard learning curves (0.25 weight) — original 8 systems, checkpoints 0-12
  B) Far-transfer (0.50 weight) — train on base system, test on abstract reskin
  C) Steep/hard (0.25 weight) — only 3 training examples before test on difficulty-3 systems

Cognitive Science Basis:
- Power Law of Practice (Newell & Rosenbloom, 1981)
- Transfer of learning (Thorndike & Woodworth, 1901)
- Sample efficiency as a measure of learning ability

Score: 0.20*standard + 0.50*far_transfer + 0.30*steep
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.rule_systems import (
    LEARNING_CURVE_SYSTEMS, FAR_TRANSFER_PAIRS, HARD_LEARNING_SYSTEMS,
)


def _strip_think(text: str) -> str:
    """Strip <think>...</think> tags from reasoning model output."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


CHECKPOINTS = [0, 2, 4, 8, 12]
HARD_CHECKPOINTS = [0, 3]  # Only 0 and 3 examples for steep condition


def normalize_output(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def check_output(model_output: str, expected: str) -> bool:
    m = normalize_output(model_output)
    e = normalize_output(expected)
    return e in m or m in e


def _eval_system(llm, system, n_examples, test_items, chat_label):
    """Evaluate a system with n_examples training, return accuracy on test_items."""
    n_actual = min(n_examples, len(system.examples))
    with kbench.chats.new(chat_label):
        prompt_parts = [
            f"You are learning the rule system: **{system.name}**\n",
            f"Description: {system.description}\n",
            "\n**Rules:**",
        ]
        for rule in system.rules:
            prompt_parts.append(f"- {rule}")

        if n_actual > 0:
            prompt_parts.append(f"\n**Training examples ({n_actual}):**")
            for ex in system.examples[:n_actual]:
                prompt_parts.append(f"  Input: {ex['input']}  →  Output: {ex['output']}")

        n_correct = 0
        for test_item in test_items:
            test_prompt = "\n".join(prompt_parts) + (
                f"\n\nNow apply the rules to this new input:\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY a JSON object:\n"
                f'{{"answer": "<output after applying rules>", "reasoning": "<your steps>"}}'
            )
            raw = llm.prompt(test_prompt)
            cleaned = _strip_think(raw)
            cleaned = re.sub(r'//.*', '', cleaned)
            try:
                parsed = json.loads(re.search(r'\{.*\}', cleaned, re.DOTALL).group())
                answer = str(parsed.get("answer", cleaned))
            except Exception:
                answer = cleaned
            if check_output(answer, test_item["output"]):
                n_correct += 1

        return n_correct / len(test_items) if test_items else 0


@kbench.task(name="Learning Curves")
def learning_curves(llm) -> float:
    """
    Learning Curves Benchmark v2.

    Score = 0.20*standard + 0.50*far_transfer + 0.30*steep
    """

    # ═══ CONDITION A: Standard Learning Curves (0.25) ═══
    all_curves = []
    for system in LEARNING_CURVE_SYSTEMS:
        curve = {"system": system.name, "difficulty": system.difficulty, "checkpoints": []}
        for n_ex in CHECKPOINTS:
            acc = _eval_system(llm, system, n_ex, system.test_items,
                               f"{system.name}_n{n_ex}")
            curve["checkpoints"].append({"n_examples": n_ex, "accuracy": acc})
        all_curves.append(curve)

    # Compute standard score (same as v1)
    asymptotic_accs = []
    learning_rates = []
    sample_efficiencies = []
    curve_qualities = []

    for curve in all_curves:
        y = np.array([c["accuracy"] for c in curve["checkpoints"]])
        asymptotic_accs.append(float(y[-1]))
        learning_rates.append(max(0, float(y[-1] - y[0])))
        eff = len(CHECKPOINTS)
        for i, c in enumerate(curve["checkpoints"]):
            if c["accuracy"] >= 0.8:
                eff = i
                break
        sample_efficiencies.append(1 - eff / len(CHECKPOINTS))
        if len(y) > 1:
            curve_qualities.append(float(np.mean(np.diff(y) >= -0.05)))
        else:
            curve_qualities.append(0.5)

    dw = [c["difficulty"] ** 1.5 for c in all_curves]
    tw = sum(dw)
    std_score = (
        0.30 * sum(a*w for a,w in zip(asymptotic_accs, dw)) / tw +
        0.30 * sum(a*w for a,w in zip(learning_rates, dw)) / tw +
        0.20 * sum(a*w for a,w in zip(sample_efficiencies, dw)) / tw +
        0.20 * sum(a*w for a,w in zip(curve_qualities, dw)) / tw
    )

    # ═══ CONDITION B: Far-Transfer (0.50) ═══
    # Train on base system (rules + examples), then test on transfer system
    # with different representation. Only base rules/examples + 2 transfer
    # examples provided — model must infer the structural mapping.
    transfer_scores = []
    for i, pair in enumerate(FAR_TRANSFER_PAIRS):
        base = pair["base"]
        transfer = pair["transfer"]

        with kbench.chats.new(f"far_transfer_{i}"):
            n_correct = 0
            for test_item in transfer.test_items:
                prompt_parts = [
                    f"You learned the rule system: **{base.name}**\n",
                    f"Description: {base.description}\n",
                    "\n**Rules:**",
                ]
                for rule in base.rules:
                    prompt_parts.append(f"- {rule}")
                prompt_parts.append(f"\n**Training examples ({min(8, len(base.examples))}):**")
                for ex in base.examples[:8]:
                    prompt_parts.append(f"  Input: {ex['input']}  →  Output: {ex['output']}")

                prompt_parts.append(f"\n\n--- NOW: TRANSFER TO A NEW REPRESENTATION ---")
                prompt_parts.append(f"The same underlying rules apply, but inputs/outputs use a different format.")
                prompt_parts.append(f"New system: **{transfer.name}**")
                prompt_parts.append(f"Description: {transfer.description}\n")

                # Provide only 2 worked examples — model must figure out mapping
                if transfer.examples:
                    prompt_parts.append("**Worked examples in the new format:**")
                    for ex in transfer.examples[:2]:
                        prompt_parts.append(f"  Input: {ex['input']}  →  Output: {ex['output']}")
                prompt_parts.append("\nFigure out how the new representation maps to the original rules, then apply them.")

                test_prompt = "\n".join(prompt_parts) + (
                    f"\n\nApply the rules to this new-format input:\n"
                    f"Input: {test_item['input']}\n\n"
                    f"Respond with ONLY a JSON object:\n"
                    f'{{"answer": "<output in the new format>", "reasoning": "<your steps>"}}'
                )
                raw = llm.prompt(test_prompt)
                cleaned = _strip_think(raw)
                cleaned = re.sub(r'//.*', '', cleaned)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', cleaned, re.DOTALL).group())
                    answer = str(parsed.get("answer", cleaned))
                except Exception:
                    answer = cleaned
                if check_output(answer, test_item["output"]):
                    n_correct += 1

            acc = n_correct / len(transfer.test_items) if transfer.test_items else 0
            transfer_scores.append(acc)
            print(f"  Far-transfer {i} ({base.name} → {transfer.name}): {acc:.2%}")  

    far_transfer_score = np.mean(transfer_scores) if transfer_scores else 0

    # ═══ CONDITION C: Steep/Hard (0.25) ═══
    # Only 3 training examples on difficulty-3 systems
    steep_scores = []
    for system in HARD_LEARNING_SYSTEMS:
        acc_0 = _eval_system(llm, system, 0, system.test_items,
                             f"steep_{system.name}_n0")
        acc_3 = _eval_system(llm, system, 3, system.test_items,
                             f"steep_{system.name}_n3")
        # Score = how much learned from just 3 examples × accuracy
        steep_score = 0.40 * acc_3 + 0.60 * max(0, acc_3 - acc_0)
        steep_scores.append(steep_score)
        print(f"  Steep {system.name}: 0-shot={acc_0:.2%}, 3-shot={acc_3:.2%}, score={steep_score:.3f}")

    steep_score = np.mean(steep_scores) if steep_scores else 0

    # ═══ COMPOSITE ═══
    score = round(0.20 * std_score + 0.50 * far_transfer_score + 0.30 * steep_score, 4)

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"LEARNING CURVES BENCHMARK v2 RESULTS")
    print(f"{'='*60}")
    print(f"\nCondition A (Standard): {std_score:.4f}")
    print(f"Condition B (Far-Transfer): {far_transfer_score:.4f}")
    print(f"Condition C (Steep/Hard): {steep_score:.4f}")
    print(f"\nComposite (0.25*A + 0.50*B + 0.25*C): {score:.4f}")

    for curve in all_curves:
        print(f"\n--- {curve['system']} (difficulty={curve['difficulty']}) ---")
        for cp in curve["checkpoints"]:
            bar = "█" * int(cp["accuracy"] * 20)
            print(f"  n={cp['n_examples']:2d}: {cp['accuracy']:.2%} {bar}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    learning_curves.run(llm=kbench.llm)
