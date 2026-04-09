"""
Attention Benchmark 4: Attention to Instruction Updates

Tests whether a model can adapt when task instructions change mid-sequence,
measuring adaptation speed and perseveration (failure to switch).

Cognitive Science Basis:
- Task-switching paradigm (Monsell, 2003): switch costs when rules change
- Set-shifting (Meiran, 1996): ability to flexibly shift attention
- Cognitive flexibility as component of executive attention
- Perseveration: continued application of now-invalid rules

Protocol:
1. Present initial instructions (e.g., "classify words by category")
2. Model processes items under those instructions
3. Mid-sequence, instructions update subtly (e.g., "now classify by length")
4. Measure: pre-switch accuracy, post-switch accuracy, adaptation speed,
   perseveration rate

Score: Composite of pre-switch accuracy, post-switch accuracy,
       adaptation speed, and low perseveration.

Shortcut Resistance:
- Instructions are embedded in a continuous stream (not a separate prompt)
- Updates are subtle — not "STOP! New rules!" but woven into the sequence
- Some trials have NO switch (catch trials) to test false alarm rate
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import json
import re


# ─── Stimulus Data ──────────────────────────────────────────────────

TRIALS = [
    {
        "id": "T1",
        "initial_instruction": "Classify each word as LIVING or NON-LIVING.",
        "switch_instruction": "NEW RULE: Now classify each word as SHORT (≤5 letters) or LONG (>5 letters).",
        "switch_after_item": 8,  # Switch happens after item 8
        "items": [
            # Pre-switch items (classify as LIVING/NON-LIVING)
            {"word": "tiger", "pre_answer": "LIVING", "post_answer": "SHORT"},
            {"word": "mountain", "pre_answer": "NON-LIVING", "post_answer": "LONG"},
            {"word": "dolphin", "pre_answer": "LIVING", "post_answer": "LONG"},
            {"word": "crystal", "pre_answer": "NON-LIVING", "post_answer": "LONG"},
            {"word": "mushroom", "pre_answer": "LIVING", "post_answer": "LONG"},
            {"word": "hammer", "pre_answer": "NON-LIVING", "post_answer": "LONG"},
            {"word": "fern", "pre_answer": "LIVING", "post_answer": "SHORT"},
            {"word": "bridge", "pre_answer": "NON-LIVING", "post_answer": "LONG"},
            # Post-switch items (classify as SHORT/LONG)
            {"word": "cat", "pre_answer": "LIVING", "post_answer": "SHORT"},
            {"word": "elephant", "pre_answer": "LIVING", "post_answer": "LONG"},
            {"word": "desk", "pre_answer": "NON-LIVING", "post_answer": "SHORT"},
            {"word": "refrigerator", "pre_answer": "NON-LIVING", "post_answer": "LONG"},
            {"word": "owl", "pre_answer": "LIVING", "post_answer": "SHORT"},
            {"word": "microphone", "pre_answer": "NON-LIVING", "post_answer": "LONG"},
            {"word": "bee", "pre_answer": "LIVING", "post_answer": "SHORT"},
            {"word": "lamp", "pre_answer": "NON-LIVING", "post_answer": "SHORT"},
        ],
    },
    {
        "id": "T2",
        "initial_instruction": "For each number, respond ODD or EVEN.",
        "switch_instruction": "NEW RULE: Now respond HIGH (>50) or LOW (≤50) instead.",
        "switch_after_item": 6,
        "items": [
            {"word": "23", "pre_answer": "ODD", "post_answer": "LOW"},
            {"word": "48", "pre_answer": "EVEN", "post_answer": "LOW"},
            {"word": "77", "pre_answer": "ODD", "post_answer": "HIGH"},
            {"word": "16", "pre_answer": "EVEN", "post_answer": "LOW"},
            {"word": "91", "pre_answer": "ODD", "post_answer": "HIGH"},
            {"word": "34", "pre_answer": "EVEN", "post_answer": "LOW"},
            # Post-switch
            {"word": "65", "pre_answer": "ODD", "post_answer": "HIGH"},
            {"word": "12", "pre_answer": "EVEN", "post_answer": "LOW"},
            {"word": "88", "pre_answer": "EVEN", "post_answer": "HIGH"},
            {"word": "7", "pre_answer": "ODD", "post_answer": "LOW"},
            {"word": "52", "pre_answer": "EVEN", "post_answer": "HIGH"},
            {"word": "39", "pre_answer": "ODD", "post_answer": "LOW"},
        ],
    },
    {
        "id": "T3",
        "initial_instruction": "Classify each shape description as ROUND or ANGULAR.",
        "switch_instruction": "NEW RULE: Now classify as LARGE (mentioned size > 10cm) or SMALL (≤10cm).",
        "switch_after_item": 7,
        "items": [
            {"word": "A 15cm circle", "pre_answer": "ROUND", "post_answer": "LARGE"},
            {"word": "A 5cm triangle", "pre_answer": "ANGULAR", "post_answer": "SMALL"},
            {"word": "A 20cm oval", "pre_answer": "ROUND", "post_answer": "LARGE"},
            {"word": "A 8cm square", "pre_answer": "ANGULAR", "post_answer": "SMALL"},
            {"word": "A 3cm sphere", "pre_answer": "ROUND", "post_answer": "SMALL"},
            {"word": "A 12cm pentagon", "pre_answer": "ANGULAR", "post_answer": "LARGE"},
            {"word": "A 7cm disc", "pre_answer": "ROUND", "post_answer": "SMALL"},
            # Post-switch
            {"word": "A 25cm hexagon", "pre_answer": "ANGULAR", "post_answer": "LARGE"},
            {"word": "A 4cm ellipse", "pre_answer": "ROUND", "post_answer": "SMALL"},
            {"word": "A 18cm diamond", "pre_answer": "ANGULAR", "post_answer": "LARGE"},
            {"word": "A 2cm ring", "pre_answer": "ROUND", "post_answer": "SMALL"},
            {"word": "A 30cm rectangle", "pre_answer": "ANGULAR", "post_answer": "LARGE"},
            {"word": "A 9cm globe", "pre_answer": "ROUND", "post_answer": "SMALL"},
        ],
    },
    {
        # Catch trial — NO switch happens
        "id": "T4_CATCH",
        "initial_instruction": "Classify each animal as MAMMAL or NON-MAMMAL.",
        "switch_instruction": None,  # No switch!
        "switch_after_item": 99,  # Never switches
        "items": [
            {"word": "whale", "pre_answer": "MAMMAL", "post_answer": "MAMMAL"},
            {"word": "salmon", "pre_answer": "NON-MAMMAL", "post_answer": "NON-MAMMAL"},
            {"word": "bat", "pre_answer": "MAMMAL", "post_answer": "MAMMAL"},
            {"word": "cobra", "pre_answer": "NON-MAMMAL", "post_answer": "NON-MAMMAL"},
            {"word": "otter", "pre_answer": "MAMMAL", "post_answer": "MAMMAL"},
            {"word": "parrot", "pre_answer": "NON-MAMMAL", "post_answer": "NON-MAMMAL"},
            {"word": "fox", "pre_answer": "MAMMAL", "post_answer": "MAMMAL"},
            {"word": "turtle", "pre_answer": "NON-MAMMAL", "post_answer": "NON-MAMMAL"},
            {"word": "rabbit", "pre_answer": "MAMMAL", "post_answer": "MAMMAL"},
            {"word": "eagle", "pre_answer": "NON-MAMMAL", "post_answer": "NON-MAMMAL"},
        ],
    },
    {
        "id": "T5",
        "initial_instruction": "For each word, respond with its FIRST LETTER (capitalized).",
        "switch_instruction": "NEW RULE: Now respond with the NUMBER OF VOWELS in each word.",
        "switch_after_item": 6,
        "items": [
            {"word": "banana", "pre_answer": "B", "post_answer": "3"},
            {"word": "grape", "pre_answer": "G", "post_answer": "2"},
            {"word": "strawberry", "pre_answer": "S", "post_answer": "2"},
            {"word": "kiwi", "pre_answer": "K", "post_answer": "2"},
            {"word": "mango", "pre_answer": "M", "post_answer": "2"},
            {"word": "plum", "pre_answer": "P", "post_answer": "1"},
            # Post-switch
            {"word": "orange", "pre_answer": "O", "post_answer": "3"},
            {"word": "apple", "pre_answer": "A", "post_answer": "2"},
            {"word": "peach", "pre_answer": "P", "post_answer": "2"},
            {"word": "fig", "pre_answer": "F", "post_answer": "1"},
            {"word": "avocado", "pre_answer": "A", "post_answer": "4"},
            {"word": "lime", "pre_answer": "L", "post_answer": "2"},
        ],
    },
]


@dataclass
class Classification:
    answer: str


def normalize_answer(text):
    return text.strip().upper().replace(".", "").replace(",", "")


def check_answer(model_answer, expected):
    model_norm = normalize_answer(model_answer)
    expected_norm = normalize_answer(expected)
    return expected_norm in model_norm or model_norm == expected_norm


@kbench.task(name="attention_instruction_update")
def attention_instruction_update(llm) -> float:
    """
    Attention to Instruction Updates Benchmark.

    Tests whether a model can adapt when task instructions change mid-sequence.

    Score = 0.25 * pre_switch_accuracy + 0.35 * post_switch_accuracy
            + 0.25 * adaptation_speed + 0.15 * (1 - false_switch_rate)

    Cognitive Science Basis: Monsell (2003) task-switching, Meiran (1996) set-shifting.
    """
    pre_correct = 0
    pre_total = 0
    post_correct = 0
    post_total = 0
    # Track adaptation: how quickly does model switch after instruction change?
    # Items immediately after switch that are still answered with OLD rule
    post_switch_perseveration = []
    catch_trial_switches = 0  # False switches on catch trials
    catch_trial_items = 0

    results_log = []

    for trial in TRIALS:
        is_catch = trial["switch_instruction"] is None
        switch_idx = trial["switch_after_item"]

        with kbench.chats.new(f"instupd_{trial['id']}"):
            # Present instructions and process items as a stream
            instruction_text = trial["initial_instruction"]

            for i, item in enumerate(trial["items"]):
                is_post_switch = i >= switch_idx and not is_catch

                # Build prompt — include switch instruction when it's time
                if i == switch_idx and not is_catch:
                    # Insert the instruction update
                    prompt = (
                        f"{trial['switch_instruction']}\n\n"
                        f"Item: {item['word']}\n"
                        f"Your classification:"
                    )
                elif i == 0:
                    prompt = (
                        f"Task: {instruction_text}\n\n"
                        f"For each item I give you, respond with ONLY your classification "
                        f"(one or two words, no explanation).\n\n"
                        f"Item: {item['word']}\n"
                        f"Your classification:"
                    )
                else:
                    prompt = f"Item: {item['word']}\nYour classification:"

                try:
                    ans = llm.prompt(prompt, schema=Classification)
                    answer = ans.answer
                except Exception:
                    answer = llm.prompt(prompt)

                expected = item["post_answer"] if is_post_switch else item["pre_answer"]
                correct = check_answer(answer, expected)

                if is_post_switch:
                    post_correct += int(correct)
                    post_total += 1
                    # Check if perseverating (using old rule answer)
                    using_old_rule = check_answer(answer, item["pre_answer"]) and not correct
                    post_switch_perseveration.append(using_old_rule)
                elif is_catch:
                    # On catch trials, check if model falsely switches
                    correct_catch = check_answer(answer, item["pre_answer"])
                    pre_correct += int(correct_catch)
                    pre_total += 1
                    # Detect false switch: model gives an answer that doesn't match the rule
                    if not correct_catch:
                        catch_trial_switches += 1
                    catch_trial_items += 1
                else:
                    pre_correct += int(correct)
                    pre_total += 1

                results_log.append({
                    "trial": trial["id"],
                    "item": item["word"],
                    "phase": "post-switch" if is_post_switch else ("catch" if is_catch else "pre-switch"),
                    "expected": expected,
                    "answer": answer[:30],
                    "correct": correct if not is_catch else correct_catch if is_catch else correct,
                })

    # ── Compute Metrics ──
    pre_acc = pre_correct / pre_total if pre_total else 0
    post_acc = post_correct / post_total if post_total else 0

    # Adaptation speed: proportion of post-switch items where model
    # adapted (not perseverating). Higher = faster adaptation.
    if post_switch_perseveration:
        perseveration_rate = sum(post_switch_perseveration) / len(post_switch_perseveration)
        adaptation_speed = 1 - perseveration_rate
    else:
        adaptation_speed = 1.0
        perseveration_rate = 0.0

    # False switch rate on catch trials
    false_switch_rate = catch_trial_switches / catch_trial_items if catch_trial_items else 0

    score = round(
        0.25 * pre_acc +
        0.35 * post_acc +
        0.25 * adaptation_speed +
        0.15 * (1 - false_switch_rate),
        4,
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"ATTENTION TO INSTRUCTION UPDATES BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Trials: {len(TRIALS)} ({sum(1 for t in TRIALS if t['switch_instruction'] is None)} catch)")
    print(f"\n--- Metrics ---")
    print(f"Pre-switch accuracy:  {pre_acc:.3f} (n={pre_total})")
    print(f"Post-switch accuracy: {post_acc:.3f} (n={post_total})")
    print(f"Adaptation speed:     {adaptation_speed:.3f}")
    print(f"Perseveration rate:   {perseveration_rate:.3f}")
    print(f"False switch rate:    {false_switch_rate:.3f} (n={catch_trial_items})")
    print(f"Composite score:      {score:.4f}")

    print(f"\n--- Per-Item Results ---")
    for r in results_log:
        status = "✓" if r["correct"] else "✗"
        print(f"  {status} [{r['trial']:10s}] [{r['phase']:11s}] "
              f"{r['item']:15s} → {r['answer']:10s} (expected: {r['expected']})")

    return score


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    attention_instruction_update.run(llm=kbench.llm)
