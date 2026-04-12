"""
Executive Functions Benchmark 1: Wisconsin Card Sort Test (WCST) Analogue

Tests cognitive flexibility / set-shifting — a core executive function.

The model sorts cards by matching a target card to one of 4 reference cards.
The active sorting rule (color, shape, or number) is NOT told to the model —
it must infer it from feedback history. After several correct sorts under one
rule, the rule switches silently. The model sees feedback indicating the old
rule no longer works, plus a few examples of the new rule working. It must
detect the shift, infer the new rule, and adapt.

Batch-prompt design: presents blocks of trials with history context and
feedback, requiring the model to answer ~5-6 test trials per block.

Cognitive Science Basis:
- Wisconsin Card Sort Test (Berg, 1948; Milner, 1963)
- Miyake et al. (2000): set-shifting as a core executive function
- Perseveration errors (continuing old rule after switch) are the key metric
- Frontal lobe patients show elevated perseveration (Milner, 1963)

Score = weighted composite:
  0.25 * accuracy + 0.45 * (1 - perseveration_rate) + 0.30 * categories_norm

Shortcut Resistance:
- Rules are never stated explicitly — model must infer from feedback patterns
- Target cards match different reference cards on different dimensions
- Rule switches are signaled only through feedback, not explicit notification
- Perseveration metric specifically catches models that can't update strategies
- Task never named as "WCST" in prompt (contamination resistance)
- Difficulty varies: easy shifts have more signal, hard shifts have less
"""

import kaggle_benchmarks as kbench
import json as _json
import re
import numpy as np
from data.wcst_stimuli import WCST_BLOCKS, card_str, REFERENCE_CARDS, _correct_ref

def _safe_log(data): print(_json.dumps(data, indent=2, default=str))


def _format_block_prompt(block: dict) -> str:
    """Format a single block into a prompt string."""
    refs = REFERENCE_CARDS
    
    lines = []
    lines.append("You are taking a card sorting test. There are 4 reference cards:")
    for i, r in enumerate(refs, 1):
        lines.append(f"  Card {i}: {card_str(r)}")
    lines.append("")
    lines.append(
        "For each trial, a target card must be matched to one of the 4 reference cards. "
        "The matching rule is based on ONE dimension (color, shape, or number), but "
        "the rule is NOT stated. You must figure it out from the feedback pattern below."
    )
    lines.append("")
    lines.append("IMPORTANT: The sorting rule may change. Pay close attention to when "
                 "responses start getting 'Incorrect' feedback — that means the rule "
                 "has changed and you need to figure out the NEW rule.")
    lines.append("")
    
    # Show history with feedback
    if block["history"]:
        lines.append("=== Previous trials (with responses and feedback) ===")
        for h in block["history"]:
            lines.append(
                f"Target: {card_str(h['target'])} → Response: Card {h['response']} → {h['feedback']}"
            )
        lines.append("")
    
    # Test trials
    n_test = len(block["test_trials"])
    lines.append(f"=== Your turn: sort the next {n_test} cards ===")
    lines.append(f"Based on the feedback pattern above, determine the CURRENT sorting rule "
                 f"and sort each card. Respond with EXACTLY {n_test} numbers (1-4), one per line.")
    lines.append("")
    
    for i, t in enumerate(block["test_trials"], 1):
        lines.append(f"Card {i}: {card_str(t['target'])}")
    
    lines.append("")
    lines.append(f"Your {n_test} answers (one number 1-4 per line):")
    
    return "\n".join(lines)


def _parse_responses(raw: str, n_expected: int) -> list:
    """Parse model response into list of int choices (1-4).
    
    Strategy: Look for the final N standalone numbers (1-4) in the response,
    since models often show reasoning before their actual answers.
    Also try to find lines that are JUST a single digit 1-4.
    """
    # Strategy 1: Find lines that are just a single number 1-4
    line_answers = []
    for line in raw.strip().split('\n'):
        line = line.strip()
        if re.match(r'^[1-4]$', line):
            line_answers.append(int(line))
    
    if len(line_answers) >= n_expected:
        return line_answers[-n_expected:]
    
    # Strategy 2: Find "Card N: ... → N" or similar answer patterns
    # Look for lines like "Card 1: ... 4" at the end
    answer_pattern = re.findall(r'(?:^|\n)\s*(?:Card\s+\d+[:\.].*?)?\s*\b([1-4])\s*$', raw, re.MULTILINE)
    if len(answer_pattern) >= n_expected:
        return [int(x) for x in answer_pattern[-n_expected:]]
    
    # Strategy 3: Take the LAST n_expected standalone digits 1-4
    all_nums = re.findall(r'\b([1-4])\b', raw)
    if len(all_nums) >= n_expected:
        return [int(n) for n in all_nums[-n_expected:]]
    
    # Strategy 4: Take whatever we have and pad
    choices = [int(n) for n in all_nums]
    rng = np.random.RandomState(99)
    while len(choices) < n_expected:
        choices.append(int(rng.randint(1, 5)))
    
    return choices


@kbench.task(name="Wisconsin Card Sorting")
def exec_func_wcst(llm) -> float:
    """
    Wisconsin Card Sort Test Analogue (batch-prompt version).

    Tests cognitive flexibility through rule inference and set-shifting.
    Model sorts cards by inferring the active rule from feedback history,
    then must adapt when the rule silently changes.

    Score = 0.25 * accuracy + 0.45 * (1 - perseveration_rate) + 0.30 * categories_norm

    Cognitive Science Basis: Berg (1948), Milner (1963), Miyake et al. (2000).
    Human perseveration rate: ~10-15% (healthy adults).
    """
    blocks = WCST_BLOCKS["blocks"]
    
    all_results = []
    
    for block in blocks:
        prompt = _format_block_prompt(block)
        
        try:
            raw = llm.prompt(prompt)
        except Exception:
            raw = ""
        
        n_test = len(block["test_trials"])
        choices = _parse_responses(raw, n_test)
        
        for trial, choice in zip(block["test_trials"], choices):
            correct = (choice == trial["correct_answer"])
            
            # Classify errors for post-shift trials
            error_type = None
            if not correct and trial["is_post_shift"] and trial["prev_rule"]:
                old_rule_answer = _correct_ref(trial["target"], trial["prev_rule"])
                if choice == old_rule_answer:
                    error_type = "perseverative"
                else:
                    error_type = "non_perseverative"
            elif not correct:
                error_type = "non_perseverative"
            
            all_results.append({
                "block_id": block["block_id"],
                "correct": correct,
                "choice": choice,
                "expected": trial["correct_answer"],
                "is_post_shift": trial["is_post_shift"],
                "error_type": error_type,
                "active_rule": trial["active_rule"],
            })
    
    # === Compute metrics ===
    
    n_total = len(all_results)
    n_correct = sum(1 for r in all_results if r["correct"])
    accuracy = n_correct / n_total if n_total > 0 else 0
    
    # Perseveration rate: among post-shift trials (not just errors),
    # what fraction of responses match the OLD rule?
    # This is more discriminating than only counting among errors.
    post_shift_trials = [r for r in all_results if r["is_post_shift"]]
    perseverative_responses = [
        r for r in post_shift_trials
        if not r["correct"] and r["error_type"] == "perseverative"
    ]
    
    if post_shift_trials:
        # Rate relative to ALL post-shift trials (not just errors)
        perseveration_rate = len(perseverative_responses) / len(post_shift_trials)
    else:
        perseveration_rate = 0.0
    
    # Categories completed: blocks where model got >= 66% correct on test trials
    block_results = {}
    for r in all_results:
        bid = r["block_id"]
        if bid not in block_results:
            block_results[bid] = {"correct": 0, "total": 0}
        block_results[bid]["total"] += 1
        if r["correct"]:
            block_results[bid]["correct"] += 1
    
    categories_completed = sum(
        1 for v in block_results.values()
        if v["total"] > 0 and v["correct"] / v["total"] >= 0.66
    )
    total_blocks = len(block_results)
    categories_norm = categories_completed / total_blocks if total_blocks > 0 else 0
    
    # === Composite score ===
    # Higher perseveration weight (0.45) since that's the key cognitive construct
    score = (
        0.25 * accuracy +
        0.45 * (1.0 - perseveration_rate) +
        0.30 * categories_norm
    )
    score = round(float(np.clip(score, 0, 1)), 4)
    
    _safe_log({
        "benchmark": "WCST_v2",
        "n_blocks": len(blocks),
        "n_test_trials": n_total,
        "accuracy": round(accuracy, 4),
        "perseveration_rate": round(perseveration_rate, 4),
        "perseverative_responses": len(perseverative_responses),
        "total_post_shift_trials": len(post_shift_trials),
        "categories_completed": categories_completed,
        "total_blocks": total_blocks,
        "categories_norm": round(categories_norm, 4),
        "composite_score": score,
        "score_breakdown": {
            "accuracy_component": round(0.25 * accuracy, 4),
            "perseveration_component": round(0.45 * (1 - perseveration_rate), 4),
            "categories_component": round(0.30 * categories_norm, 4),
        },
        "per_block": {
            str(bid): {
                "correct": v["correct"],
                "total": v["total"],
                "pct": round(v["correct"] / v["total"], 2) if v["total"] > 0 else 0,
            }
            for bid, v in sorted(block_results.items())
        },
    })
    
    return score

exec_func_wcst.run(llm=kbench.llm)
