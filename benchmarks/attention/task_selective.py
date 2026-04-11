"""
Attention Benchmark 1: Selective Attention (Stroop Analogue)

Tests the ability to focus on relevant information while ignoring
conflicting or misleading distractors.

Cognitive Science Basis:
- Stroop (1935): Color-word interference effect
- Posner & Snyder (1975): Inhibition of return
- Selective attention as cognitive filtering

Protocol:
1. Present instructions + text with potential conflicts
2. Three conditions: congruent, incongruent, neutral
3. Measure accuracy across conditions
4. Stroop interference = performance(congruent) - performance(incongruent)

Score: Weighted accuracy with interference resistance bonus.
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.attention_stimuli import STROOP_ITEMS


@dataclass
class StroopAnswer:
    answer: str


def normalize(text: str) -> str:
    return text.strip().lower()


def check_answer(model_answer: str, correct: str) -> bool:
    m = normalize(model_answer)
    c = normalize(correct)
    return c in m or m in c


@kbench.task(name="attention_selective")
def attention_selective(llm) -> float:
    """
    Selective Attention (Stroop Analogue) Benchmark.

    Tests ability to follow precise instructions while ignoring
    conflicting or misleading information in the context.

    Score = 0.30 * congruent_acc + 0.40 * incongruent_acc
            + 0.15 * neutral_acc + 0.15 * (1 - interference)

    Stroop interference = congruent_acc - incongruent_acc
    Human Stroop interference: ~10-20% accuracy difference
    """
    results = {"congruent": [], "incongruent": [], "neutral": [], "adversarial": [], "extreme": []}

    for item in STROOP_ITEMS:
        with kbench.chats.new(f"stroop_{item['id']}"):
            prompt = (
                f"Follow this instruction EXACTLY.\n\n"
                f"**Instruction:** {item['instruction']}\n\n"
                f"**Text:** {item['text']}\n\n"
                f"Respond with ONLY a JSON object: {{\"answer\": \"<your answer>\"}}"
            )

            try:
                result = llm.prompt(prompt, schema=StroopAnswer)
                answer = result.answer
            except Exception:
                raw = llm.prompt(prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    answer = str(parsed.get("answer", raw))
                except Exception:
                    answer = raw

            correct = check_answer(answer, item["correct"])
            results[item["condition"]].append({
                "id": item["id"],
                "correct": correct,
                "answer": answer[:50],
                "expected": item["correct"],
            })

    # Compute condition accuracies
    accs = {}
    for cond in ["congruent", "incongruent", "neutral", "adversarial", "extreme"]:
        items = results[cond]
        accs[cond] = sum(1 for r in items if r["correct"]) / len(items) if items else 0

    # Stroop interference
    interference = max(0, accs["congruent"] - accs["incongruent"])

    # Adversarial resistance (how well it handles shortcut-exploiting items)
    adv_resistance = accs.get("adversarial", 0)

    # Extreme items — multi-step reasoning under heavy interference
    extreme_resistance = accs.get("extreme", 0)

    # Composite score — extreme items weighted heavily to spread scores
    score = round(
        0.10 * accs["congruent"]
        + 0.15 * accs["incongruent"]
        + 0.05 * accs["neutral"]
        + 0.05 * (1 - interference)
        + 0.25 * adv_resistance
        + 0.40 * extreme_resistance,
        4
    )

    # Logging
    print(f"\n{'='*60}")
    print(f"SELECTIVE ATTENTION (STROOP ANALOGUE) RESULTS")
    print(f"{'='*60}")

    for cond in ["congruent", "incongruent", "neutral", "adversarial", "extreme"]:
        items = results[cond]
        acc = accs[cond]
        print(f"\n--- {cond.upper()} (n={len(items)}, acc={acc:.2%}) ---")
        for r in items:
            status = "✓" if r["correct"] else "✗"
            print(f"  {status} {r['id']}: got '{r['answer'][:30]}', expected '{r['expected']}'")

    print(f"\n--- Summary ---")
    print(f"Congruent accuracy:   {accs['congruent']:.2%}")
    print(f"Incongruent accuracy: {accs['incongruent']:.2%}")
    print(f"Neutral accuracy:     {accs['neutral']:.2%}")
    print(f"Adversarial accuracy:  {accs.get('adversarial', 0):.2%}")
    print(f"Extreme accuracy:      {accs.get('extreme', 0):.2%}")
    print(f"Stroop interference:  {interference:.2%}")
    print(f"Composite score:      {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
attention_selective.run(llm=kbench.llm)
