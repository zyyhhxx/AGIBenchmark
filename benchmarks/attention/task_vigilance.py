"""
Attention Benchmark 2: Sustained Attention (Vigilance)

Tests whether model performance degrades over long sequences,
analogous to human vigilance decrements.

Cognitive Science Basis:
- Mackworth (1948): Clock test — performance on monotonous
  monitoring tasks decreases over time
- Parasuraman & Davies (1977): Vigilance taxonomy

Protocol:
1. Present a long sequence of symbols
2. Model must detect rare target symbols (★) among distractors
3. Target frequency decreases across the sequence
4. Measure detection rate in early, middle, and late thirds

Score: Accuracy with bonus for resistance to vigilance decrement.
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.attention_stimuli import VIGILANCE_SEQUENCE


@dataclass
class VigilanceCount:
    count: int
    positions: str  # Comma-separated positions where targets were spotted


def check_count(model_count: int, actual_count: int, tolerance: int = 1) -> bool:
    return abs(model_count - actual_count) <= tolerance


@kbench.task(name="attention_vigilance")
def attention_vigilance(llm) -> float:
    """
    Sustained Attention (Vigilance) Benchmark.

    Present a long sequence of symbols. Model must count target
    occurrences in chunks and track running total.

    Score = 0.40 * overall_accuracy + 0.30 * late_accuracy
            + 0.30 * (1 - vigilance_decrement)

    Human vigilance decrement: 10-30% drop in detection over time.
    """
    seq = VIGILANCE_SEQUENCE
    symbols = [item["symbol"] for item in seq["sequence"]]
    target = seq["target"]

    # Split into chunks of 20 for manageable monitoring
    chunk_size = 20
    n_chunks = len(symbols) // chunk_size
    chunk_results = []

    for ci in range(n_chunks):
        start = ci * chunk_size
        end = start + chunk_size
        chunk_symbols = symbols[start:end]
        chunk_items = seq["sequence"][start:end]
        actual_targets = sum(1 for item in chunk_items if item["is_target"])

        with kbench.chats.new(f"vigilance_chunk_{ci}"):
            seq_display = " ".join(chunk_symbols)
            prompt = (
                f"**Vigilance Monitoring Task — Segment {ci+1}/{n_chunks}**\n\n"
                f"Target symbol: {target}\n"
                f"Count how many times '{target}' appears in this sequence:\n\n"
                f"{seq_display}\n\n"
                f"Respond with ONLY: {{\"count\": <number>, \"positions\": \"<comma-separated 0-indexed positions>\"}}"
            )

            try:
                result = llm.prompt(prompt, schema=VigilanceCount)
                model_count = result.count
            except Exception:
                raw = llm.prompt(prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    model_count = int(parsed.get("count", 0))
                except Exception:
                    # Try to extract a number
                    nums = re.findall(r'\d+', raw)
                    model_count = int(nums[0]) if nums else 0

            correct = check_count(model_count, actual_targets)
            third = "early" if ci < n_chunks // 3 else ("middle" if ci < 2 * n_chunks // 3 else "late")

            chunk_results.append({
                "chunk": ci,
                "third": third,
                "actual_targets": actual_targets,
                "model_count": model_count,
                "correct": correct,
            })

    # Compute metrics by third
    third_accs = {}
    for third in ["early", "middle", "late"]:
        items = [r for r in chunk_results if r["third"] == third]
        if items:
            third_accs[third] = sum(1 for r in items if r["correct"]) / len(items)
        else:
            third_accs[third] = 0

    overall_acc = sum(1 for r in chunk_results if r["correct"]) / len(chunk_results)
    vigilance_decrement = max(0, third_accs.get("early", 0) - third_accs.get("late", 0))

    score = round(
        0.40 * overall_acc
        + 0.30 * third_accs.get("late", 0)
        + 0.30 * (1 - vigilance_decrement),
        4
    )

    # Logging
    print(f"\n{'='*60}")
    print(f"SUSTAINED ATTENTION (VIGILANCE) RESULTS")
    print(f"{'='*60}")
    print(f"Sequence length: {len(symbols)}")
    print(f"Target: {target}")
    print(f"Chunks: {n_chunks} (size {chunk_size})")

    for third in ["early", "middle", "late"]:
        items = [r for r in chunk_results if r["third"] == third]
        if items:
            print(f"\n  {third.upper()}: accuracy={third_accs[third]:.2%}")
            for r in items:
                status = "✓" if r["correct"] else "✗"
                print(f"    {status} Chunk {r['chunk']}: actual={r['actual_targets']}, model={r['model_count']}")

    print(f"\n--- Summary ---")
    print(f"Overall accuracy:      {overall_acc:.2%}")
    print(f"Early accuracy:        {third_accs.get('early', 0):.2%}")
    print(f"Late accuracy:         {third_accs.get('late', 0):.2%}")
    print(f"Vigilance decrement:   {vigilance_decrement:.2%}")
    print(f"Composite score:       {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
attention_vigilance.run(llm=kbench.llm)
