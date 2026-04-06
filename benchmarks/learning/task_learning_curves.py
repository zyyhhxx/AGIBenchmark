"""
Learning Benchmark 1: Novel Rule System Learning Curves

Measures how model performance improves with increasing numbers of
training examples — the fundamental learning curve.

Protocol:
1. Present a novel rule system description (rules only, no examples)
2. Incrementally provide training examples: 0, 2, 4, 8, 12 examples
3. At each step, test on held-out problems
4. Plot accuracy vs. number of training examples
5. Measure learning curve shape and efficiency

Cognitive Science Basis:
- Power Law of Practice (Newell & Rosenbloom, 1981)
- Learning curves (Bryan & Harter, 1897)
- Sample efficiency as a measure of learning ability

Key Innovation:
- Rule systems are procedurally generated → not in training data
- Tests genuine in-context learning, not memorization
- Multiple difficulty levels test learning capacity

Score: Composite of learning rate, asymptotic accuracy, and sample efficiency.
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.rule_systems import LEARNING_CURVE_SYSTEMS


@dataclass
class RuleAnswer:
    answer: str
    reasoning: str


# Test checkpoints: how many examples to show before each test
CHECKPOINTS = [0, 2, 4, 8, 12]


def normalize_output(text: str) -> str:
    """Normalize output for comparison."""
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def check_output(model_output: str, expected: str) -> bool:
    """Check if model output matches expected."""
    m = normalize_output(model_output)
    e = normalize_output(expected)
    # Exact match or containment
    return e in m or m in e


def fit_power_law(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """
    Fit y = a * x^b + c (power law of practice).
    Returns (a, b, c) or best-effort approximation.
    """
    # Simple: use log-linear regression on non-zero x
    mask = x > 0
    if mask.sum() < 2:
        return (0.0, 0.0, float(y[0]) if len(y) > 0 else 0.0)

    log_x = np.log(x[mask])
    # Subtract baseline (zero-shot)
    baseline = y[0] if len(y) > 0 else 0
    y_adj = y[mask] - baseline
    y_adj = np.maximum(y_adj, 0.001)  # Avoid log(0)
    log_y = np.log(y_adj)

    # Linear regression in log space
    try:
        b, log_a = np.polyfit(log_x, log_y, 1)
        a = np.exp(log_a)
        return (float(a), float(b), float(baseline))
    except Exception:
        return (0.0, 0.0, float(baseline))


@kbench.task(name="learning_curves")
def learning_curves(llm) -> float:
    """
    Learning Curves Benchmark.

    Tests how model performance improves with training examples
    for novel rule systems that cannot be in training data.

    Score = weighted average of:
      0.30 * mean_asymptotic_accuracy
      0.30 * mean_learning_rate (normalized)
      0.20 * mean_sample_efficiency (normalized)
      0.20 * curve_quality (does it show genuine learning?)
    """
    all_curves = []
    results_log = []

    for system in LEARNING_CURVE_SYSTEMS:
        curve = {"system": system.name, "difficulty": system.difficulty, "checkpoints": []}

        for n_examples in CHECKPOINTS:
            # Only use up to n_examples from the pool
            n_examples_actual = min(n_examples, len(system.examples))

            with kbench.chats.new(f"{system.name}_n{n_examples}"):
                # Build prompt with rules + n examples
                prompt_parts = [
                    f"You are learning the rule system: **{system.name}**\n",
                    f"Description: {system.description}\n",
                    "\n**Rules:**",
                ]
                for rule in system.rules:
                    prompt_parts.append(f"- {rule}")

                if n_examples_actual > 0:
                    prompt_parts.append(f"\n**Training examples ({n_examples_actual}):**")
                    for ex in system.examples[:n_examples_actual]:
                        prompt_parts.append(f"  Input: {ex['input']}  →  Output: {ex['output']}")

                # Test on held-out items
                n_correct = 0
                for ti, test_item in enumerate(system.test_items):
                    test_prompt = "\n".join(prompt_parts) + (
                        f"\n\nNow apply the rules to this new input:\n"
                        f"Input: {test_item['input']}\n\n"
                        f"Respond with ONLY a JSON object:\n"
                        f'{{"answer": "<output after applying rules>", "reasoning": "<your steps>"}}'
                    )

                    try:
                        result = llm.prompt(test_prompt, schema=RuleAnswer)
                        answer = result.answer
                    except Exception:
                        raw = llm.prompt(test_prompt)
                        try:
                            parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                            answer = str(parsed.get("answer", raw))
                        except Exception:
                            answer = raw

                    if check_output(answer, test_item["output"]):
                        n_correct += 1

                accuracy = n_correct / len(system.test_items) if system.test_items else 0
                curve["checkpoints"].append({
                    "n_examples": n_examples,
                    "accuracy": accuracy,
                    "n_correct": n_correct,
                    "n_total": len(system.test_items),
                })

        all_curves.append(curve)

    # ── Compute Metrics ──
    asymptotic_accs = []
    learning_rates = []
    sample_efficiencies = []
    curve_qualities = []

    for curve in all_curves:
        checkpoints = curve["checkpoints"]
        x = np.array([c["n_examples"] for c in checkpoints], dtype=float)
        y = np.array([c["accuracy"] for c in checkpoints], dtype=float)

        # Asymptotic accuracy (last checkpoint)
        asymptotic = float(y[-1])
        asymptotic_accs.append(asymptotic)

        # Learning rate: improvement from 0 to max examples
        learning_rate = float(y[-1] - y[0]) if len(y) > 1 else 0
        learning_rates.append(max(0, learning_rate))

        # Sample efficiency: first checkpoint where accuracy >= 0.8 (lower = better)
        efficiency = len(CHECKPOINTS)  # Default: never reached
        for i, c in enumerate(checkpoints):
            if c["accuracy"] >= 0.8:
                efficiency = i
                break
        # Normalize: 0 = worst (never), 1 = best (zero-shot)
        sample_efficiencies.append(1 - efficiency / len(CHECKPOINTS))

        # Curve quality: is there monotonic improvement? (genuine learning)
        if len(y) > 1:
            improvements = np.diff(y)
            # Fraction of steps that show improvement or maintenance
            quality = np.mean(improvements >= -0.05)  # Allow tiny dips
        else:
            quality = 0.5
        curve_qualities.append(float(quality))

    # Overall score
    mean_asymptotic = np.mean(asymptotic_accs)
    mean_lr = np.mean(learning_rates)
    mean_se = np.mean(sample_efficiencies)
    mean_cq = np.mean(curve_qualities)

    score = round(
        0.30 * mean_asymptotic + 0.30 * mean_lr + 0.20 * mean_se + 0.20 * mean_cq,
        4
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"LEARNING CURVES BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Systems tested: {len(LEARNING_CURVE_SYSTEMS)}")
    print(f"Checkpoints: {CHECKPOINTS}")

    for curve in all_curves:
        print(f"\n--- {curve['system']} (difficulty={curve['difficulty']}) ---")
        for cp in curve["checkpoints"]:
            bar = "█" * int(cp["accuracy"] * 20)
            print(f"  n={cp['n_examples']:2d}: {cp['accuracy']:.2%} ({cp['n_correct']}/{cp['n_total']}) {bar}")

    print(f"\n--- Aggregate Metrics ---")
    print(f"Mean asymptotic accuracy: {mean_asymptotic:.3f}")
    print(f"Mean learning rate:       {mean_lr:.3f}")
    print(f"Mean sample efficiency:   {mean_se:.3f}")
    print(f"Mean curve quality:       {mean_cq:.3f}")
    print(f"Composite score:          {score:.4f}")

    # Per-system summary
    print(f"\n--- Per-System Summary ---")
    for i, curve in enumerate(all_curves):
        print(f"  {curve['system']}: asym={asymptotic_accs[i]:.2f}, "
              f"lr={learning_rates[i]:.2f}, se={sample_efficiencies[i]:.2f}, "
              f"cq={curve_qualities[i]:.2f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
learning_curves.run(llm=kbench.llm)
