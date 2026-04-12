"""
Attention Benchmark 2: Sustained Attention (Vigilance) — N-back Task

Tests sustained attention via n-back working memory monitoring over
long sequences with near-miss distractors.

Cognitive Science Basis:
- Kirchner (1958): N-back paradigm for working memory / sustained attention
- Mackworth (1948): Clock test — vigilance decrement over time
- Parasuraman & Davies (1977): Vigilance taxonomy and signal detection

Protocol:
1. Present sequence items one segment at a time (10 items per segment)
2. For each item at position i (where i >= n), model decides:
   "Is this letter the SAME as the letter n positions back?"
3. 3-back condition (80 items) + 4-back condition (60 items)
4. Near-miss distractors (confusable letters) increase false alarm rate
5. Target rate decreases over time → vigilance decrement

Scoring (composite):
  0.35 * overall_accuracy (hits + correct rejections)
  0.35 * sensitivity (hit_rate - false_alarm_rate, d' proxy)
  0.15 * vigilance_decrement_resistance (Q1 acc - Q4 acc, inverted)
  0.15 * (1 - false_alarm_rate)

Designed to break ceiling: near-miss distractors + long sequences +
decreasing target rate make perfect scores very unlikely.
"""

import kaggle_benchmarks as kbench
import re
import json
from benchmarks.attention.data.vigilance_stimuli import VIGILANCE_3BACK, VIGILANCE_4BACK


def _parse_responses(raw: str, expected_count: int) -> list:
    """Extract YES/NO responses from model output."""
    # Try JSON array first
    try:
        m = re.search(r'\[.*\]', raw, re.DOTALL)
        if m:
            arr = json.loads(m.group())
            if len(arr) == expected_count:
                return [str(x).strip().upper() for x in arr]
    except Exception:
        pass

    # Try line-by-line or comma-separated
    tokens = re.findall(r'\b(YES|NO|yes|no|Yes|No|Y|N|y|n)\b', raw)
    result = []
    for t in tokens:
        t = t.upper()
        if t in ("Y", "YES"):
            result.append("YES")
        elif t in ("N", "NO"):
            result.append("NO")
    return result[:expected_count]


def run_nback_condition(llm, data: dict, condition_name: str) -> dict:
    """Run one n-back condition and return per-item results."""
    seq = data["sequence"]
    n = data["n_back"]
    segment_size = 10
    all_results = []

    # Build the full letter list for context
    letters = [item["letter"] for item in seq]

    for seg_start in range(0, len(seq), segment_size):
        seg_end = min(seg_start + segment_size, len(seq))
        seg_items = seq[seg_start:seg_end]

        # Only include items where n-back is possible
        eval_items = [item for item in seg_items if item["position"] >= n]
        if not eval_items:
            continue

        # Build the prompt showing the FULL sequence up to this segment
        # so the model has context for n-back lookups
        full_seq_so_far = letters[:seg_end]

        # Format: show positions with letters
        display_lines = []
        for i, letter in enumerate(full_seq_so_far):
            marker = " <-- respond" if seg_start <= i < seg_end and i >= n else ""
            display_lines.append(f"  [{i:2d}] {letter}{marker}")

        positions_to_judge = [item["position"] for item in eval_items]

        with kbench.chats.new(f"{condition_name}_seg{seg_start}"):
            prompt = (
                f"**{n}-Back Vigilance Task — Segment {seg_start // segment_size + 1}**\n\n"
                f"Rule: For each marked position, answer YES if the letter is the SAME as "
                f"the letter exactly {n} positions earlier. Answer NO otherwise.\n\n"
                f"Sequence so far:\n"
                + "\n".join(display_lines) + "\n\n"
                f"For positions {positions_to_judge}, respond with ONLY a JSON array of "
                f"YES/NO strings. Example: [\"YES\", \"NO\", \"NO\", ...]\n"
                f"Give exactly {len(eval_items)} responses."
            )

            raw = llm.prompt(prompt)
            responses = _parse_responses(raw, len(eval_items))

            # Pad if model gave too few
            while len(responses) < len(eval_items):
                responses.append("NO")  # default to NO (conservative)

            for item, resp in zip(eval_items, responses):
                hit = resp == item["correct_response"]
                all_results.append({
                    "position": item["position"],
                    "letter": item["letter"],
                    "type": item["type"],
                    "quartile": item["quartile"],
                    "correct_response": item["correct_response"],
                    "model_response": resp,
                    "correct": hit,
                    "is_false_alarm": (resp == "YES" and item["correct_response"] == "NO"),
                    "is_hit": (resp == "YES" and item["correct_response"] == "YES"),
                    "is_miss": (resp == "NO" and item["correct_response"] == "YES"),
                })

    return all_results


@kbench.task(name="Sustained Vigilance")
def attention_vigilance(llm) -> float:
    """
    N-Back Sustained Attention (Vigilance) Benchmark.

    Runs 3-back (80 items) and 4-back (60 items) conditions.

    Score = 0.35 * overall_accuracy + 0.35 * sensitivity (hit_rate - FA_rate)
            + 0.15 * vigilance_decrement_resistance + 0.15 * (1 - false_alarm_rate)
    """
    conditions = [
        ("3-back", VIGILANCE_3BACK, 0.55),  # weight
        ("4-back", VIGILANCE_4BACK, 0.45),
    ]

    condition_scores = []

    for cond_name, cond_data, weight in conditions:
        results = run_nback_condition(llm, cond_data, cond_name)

        if not results:
            condition_scores.append(0.0)
            continue

        # Overall accuracy
        overall_acc = sum(1 for r in results if r["correct"]) / len(results)

        # Quartile accuracies for vigilance decrement
        q_accs = {}
        for q in range(4):
            q_items = [r for r in results if r["quartile"] == q]
            if q_items:
                q_accs[q] = sum(1 for r in q_items if r["correct"]) / len(q_items)
            else:
                q_accs[q] = 0.0

        # Vigilance decrement = Q1 acc - Q4 acc (positive = decrement occurred)
        vig_decrement = max(0, q_accs.get(0, 0) - q_accs.get(3, 0))
        vig_resistance = 1.0 - vig_decrement

        # False alarm rate (said YES when should be NO)
        non_targets = [r for r in results if r["correct_response"] == "NO"]
        false_alarm_rate = (
            sum(1 for r in non_targets if r["is_false_alarm"]) / len(non_targets)
            if non_targets else 0.0
        )

        # d-prime proxy: hit_rate - false_alarm_rate (signal detection sensitivity)
        targets_list = [r for r in results if r["correct_response"] == "YES"]
        hit_rate_val = sum(1 for r in targets_list if r["is_hit"]) / len(targets_list) if targets_list else 0
        sensitivity = max(0, hit_rate_val - false_alarm_rate)

        cond_score = round(
            0.35 * overall_acc
            + 0.35 * sensitivity
            + 0.15 * vig_resistance
            + 0.15 * (1.0 - false_alarm_rate),
            4
        )

        condition_scores.append(cond_score * weight)

        # Logging
        n = cond_data["n_back"]
        targets = [r for r in results if r["correct_response"] == "YES"]
        hit_rate = sum(1 for r in targets if r["is_hit"]) / len(targets) if targets else 0
        miss_rate = sum(1 for r in targets if r["is_miss"]) / len(targets) if targets else 0

        print(f"\n{'='*60}")
        print(f"{cond_name.upper()} CONDITION RESULTS")
        print(f"{'='*60}")
        print(f"Items evaluated: {len(results)}")
        print(f"Overall accuracy: {overall_acc:.3f}")
        print(f"Hit rate (targets): {hit_rate:.3f}")
        print(f"Miss rate: {miss_rate:.3f}")
        print(f"False alarm rate: {false_alarm_rate:.3f}")
        print(f"Quartile accuracies: Q1={q_accs[0]:.3f} Q2={q_accs[1]:.3f} Q3={q_accs[2]:.3f} Q4={q_accs[3]:.3f}")
        print(f"Vigilance decrement: {vig_decrement:.3f}")
        print(f"Condition score: {cond_score:.4f} (weight={weight})")

    final_score = round(sum(condition_scores), 4)

    print(f"\n{'='*60}")
    print(f"FINAL VIGILANCE SCORE: {final_score:.4f}")
    print(f"{'='*60}")

    return min(1.0, max(0.0, final_score))


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    attention_vigilance.run(llm=kbench.llm)
