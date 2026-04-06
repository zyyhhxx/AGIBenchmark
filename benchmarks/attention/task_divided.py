"""
Attention Benchmark 3: Divided Attention (Dual-Task)

Tests the cost of performing two cognitive tasks simultaneously.

Cognitive Science Basis:
- Pashler (1994): Dual-task interference and the central bottleneck
- Kahneman (1973): Attention as a limited resource
- Wickens (2002): Multiple Resource Theory

Protocol:
1. Perform Task A alone (baseline)
2. Perform Task B alone (baseline)
3. Perform both A and B simultaneously
4. Measure dual-task cost: accuracy drop from single to dual

Score: Performance maintenance under dual-task conditions.
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.attention_stimuli import DUAL_TASK_ITEMS


@dataclass
class SingleTaskAnswer:
    answer: str


@dataclass
class DualTaskAnswer:
    task_a_answer: str
    task_b_answer: str


def normalize(text: str) -> str:
    return text.strip().lower()


def check_answer(model_answer: str, correct: str) -> bool:
    m = normalize(model_answer)
    c = normalize(correct)
    return c in m or m in c


@kbench.task(name="attention_divided")
def attention_divided(llm) -> float:
    """
    Divided Attention (Dual-Task) Benchmark.

    Measures performance cost when doing two tasks simultaneously.

    Score = 0.25 * single_A_acc + 0.25 * single_B_acc
            + 0.25 * dual_A_acc + 0.25 * dual_B_acc

    Human dual-task cost: 10-30% accuracy drop
    """
    single_a_results = []
    single_b_results = []
    dual_a_results = []
    dual_b_results = []

    for item in DUAL_TASK_ITEMS:
        # ── Single Task A ──
        with kbench.chats.new(f"single_a_{item['id']}"):
            prompt_a = (
                f"**Task:** {item['task_a']['instruction']}\n\n"
                f"{item['task_a']['problem']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<your answer>\"}}"
            )
            try:
                result = llm.prompt(prompt_a, schema=SingleTaskAnswer)
                answer_a = result.answer
            except Exception:
                raw = llm.prompt(prompt_a)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    answer_a = str(parsed.get("answer", raw))
                except Exception:
                    answer_a = raw

            single_a_results.append(check_answer(answer_a, item["task_a"]["answer"]))

        # ── Single Task B ──
        with kbench.chats.new(f"single_b_{item['id']}"):
            prompt_b = (
                f"**Task:** {item['task_b']['instruction']}: {item['task_b']['word']}\n\n"
                f"(Do some other thinking...)\n\n"
                f"Now: {item['task_b']['recall_prompt']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<your answer>\"}}"
            )
            try:
                result = llm.prompt(prompt_b, schema=SingleTaskAnswer)
                answer_b = result.answer
            except Exception:
                raw = llm.prompt(prompt_b)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    answer_b = str(parsed.get("answer", raw))
                except Exception:
                    answer_b = raw

            single_b_results.append(check_answer(answer_b, item["task_b"]["word"]))

        # ── Dual Task (both simultaneously) ──
        with kbench.chats.new(f"dual_{item['id']}"):
            dual_prompt = (
                f"You must do TWO tasks at once.\n\n"
                f"**Task A:** {item['task_a']['instruction']}: {item['task_a']['problem']}\n\n"
                f"**Task B:** {item['task_b']['instruction']}: {item['task_b']['word']}\n\n"
                f"First, complete Task A. Then recall the answer for Task B.\n\n"
                f"Respond with ONLY: {{\"task_a_answer\": \"<answer for A>\", \"task_b_answer\": \"<answer for B>\"}}"
            )
            try:
                result = llm.prompt(dual_prompt, schema=DualTaskAnswer)
                dual_a = result.task_a_answer
                dual_b = result.task_b_answer
            except Exception:
                raw = llm.prompt(dual_prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    dual_a = str(parsed.get("task_a_answer", ""))
                    dual_b = str(parsed.get("task_b_answer", ""))
                except Exception:
                    dual_a = raw
                    dual_b = raw

            dual_a_results.append(check_answer(dual_a, item["task_a"]["answer"]))
            dual_b_results.append(check_answer(dual_b, item["task_b"]["word"]))

    # Compute accuracies
    n = len(DUAL_TASK_ITEMS)
    single_a_acc = sum(single_a_results) / n
    single_b_acc = sum(single_b_results) / n
    dual_a_acc = sum(dual_a_results) / n
    dual_b_acc = sum(dual_b_results) / n

    # Dual-task costs
    cost_a = max(0, single_a_acc - dual_a_acc)
    cost_b = max(0, single_b_acc - dual_b_acc)
    mean_cost = (cost_a + cost_b) / 2

    score = round(
        0.25 * single_a_acc + 0.25 * single_b_acc
        + 0.25 * dual_a_acc + 0.25 * dual_b_acc,
        4
    )

    # Logging
    print(f"\n{'='*60}")
    print(f"DIVIDED ATTENTION (DUAL-TASK) RESULTS")
    print(f"{'='*60}")
    print(f"Items: {n}")
    print(f"\n--- Single Task Performance ---")
    print(f"Task A (problem-solving): {single_a_acc:.2%}")
    print(f"Task B (memory):          {single_b_acc:.2%}")
    print(f"\n--- Dual Task Performance ---")
    print(f"Task A (dual):    {dual_a_acc:.2%}  (cost: {cost_a:.2%})")
    print(f"Task B (dual):    {dual_b_acc:.2%}  (cost: {cost_b:.2%})")
    print(f"Mean dual cost:   {mean_cost:.2%}")
    print(f"\nComposite score:  {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
attention_divided.run(llm=kbench.llm)
