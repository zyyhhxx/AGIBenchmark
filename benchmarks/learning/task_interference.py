"""
Learning Benchmark 3: Proactive & Retroactive Interference

Tests whether learning new material interferes with previously
learned material (retroactive) and whether old knowledge impedes
new learning (proactive).

Cognitive Science Basis:
- Underwood (1957): Proactive inhibition in retention
- Postman (1961): Retroactive inhibition
- Anderson (2003): Retrieval-induced forgetting

Protocol:
1. Learn System A → Test A (baseline A)
2. Learn System B (similar to A) → Test B (baseline B)
3. Re-test A → Measure retroactive interference
4. Compare B learning rate vs. A (proactive interference)

Score: Measures resistance to interference (higher = better).
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.rule_systems import generate_symbol_system


@dataclass
class InterfAnswer:
    answer: str


def normalize_output(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def check_output(model_output: str, expected: str) -> bool:
    m = normalize_output(model_output)
    e = normalize_output(expected)
    return e in m or m in e


def test_system(llm, system, context_prefix: str = "", chat_prefix: str = "test") -> float:
    """Test model on a system's test items. Returns accuracy."""
    correct = 0
    rules_text = f"**{system.name}**\n"
    for r in system.rules:
        rules_text += f"- {r}\n"
    examples_text = "\n**Examples:**\n"
    for ex in system.examples[:8]:
        examples_text += f"  {ex['input']} → {ex['output']}\n"

    for ti, test_item in enumerate(system.test_items):
        with kbench.chats.new(f"{chat_prefix}_{ti}"):
            prompt = (
                context_prefix +
                f"\nApply these rules:\n{rules_text}{examples_text}\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\"}}"
            )
            try:
                result = llm.prompt(prompt, schema=InterfAnswer)
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


# Generate two similar systems that should interfere
SYSTEM_A = generate_symbol_system("interf_alpha_v2", difficulty=2)
SYSTEM_B = generate_symbol_system("interf_beta_v2", difficulty=2)


@kbench.task(name="learning_interference")
def learning_interference(llm) -> float:
    """
    Proactive & Retroactive Interference Benchmark.

    Measures how learning similar systems affects retention and acquisition.

    Protocol:
    1. Learn A → Test A (baseline_A)
    2. Learn B → Test B (baseline_B)
    3. After B: Re-test A (post_interference_A)
    4. Measure interference

    Score = 0.40 * (1 - retroactive_interference)
          + 0.30 * baseline_accuracy_A
          + 0.30 * baseline_accuracy_B

    Where retroactive_interference = max(0, baseline_A - post_interference_A)
    """

    # ── Phase 1: Learn System A, test A ──
    baseline_A = test_system(llm, SYSTEM_A, chat_prefix="phase1_A")

    # ── Phase 2: Learn System B, test B ──
    # Include A context to create potential interference
    a_context = (
        f"You previously learned system {SYSTEM_A.name}. "
        f"Now learn a NEW but similar system.\n"
    )
    baseline_B = test_system(llm, SYSTEM_B, context_prefix=a_context, chat_prefix="phase2_B")

    # ── Phase 3: Re-test A after learning B ──
    b_context = (
        f"You recently learned two similar systems. "
        f"Now I want you to recall the FIRST system ({SYSTEM_A.name}) specifically. "
        f"Ignore the second system you learned.\n"
    )
    post_interf_A = test_system(llm, SYSTEM_A, context_prefix=b_context, chat_prefix="phase3_retest_A")

    # ── Compute Metrics ──
    retroactive = max(0, baseline_A - post_interf_A)
    proactive = max(0, baseline_A - baseline_B)  # If B worse than A, proactive interference

    # Score: higher = better (less interference, higher accuracy)
    score = round(
        0.40 * (1 - retroactive)
        + 0.30 * baseline_A
        + 0.30 * baseline_B,
        4
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"PROACTIVE & RETROACTIVE INTERFERENCE RESULTS")
    print(f"{'='*60}")
    print(f"System A: {SYSTEM_A.name} ({len(SYSTEM_A.rules)} rules)")
    print(f"System B: {SYSTEM_B.name} ({len(SYSTEM_B.rules)} rules)")
    print(f"\n--- Phase Results ---")
    print(f"Baseline A:          {baseline_A:.2%}")
    print(f"Baseline B:          {baseline_B:.2%}")
    print(f"Post-interference A: {post_interf_A:.2%}")
    print(f"\n--- Interference Metrics ---")
    print(f"Retroactive interference: {retroactive:.2%} (A drop after learning B)")
    print(f"Proactive interference:   {proactive:.2%} (B disadvantage vs A)")
    print(f"\nComposite score: {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
learning_interference.run(llm=kbench.llm)
