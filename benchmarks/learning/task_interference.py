"""
Learning Benchmark 3: Proactive & Retroactive Interference (v4)

Tests whether the presence of competing learned systems interferes
with the correct application of a target system.

Cognitive Science Basis:
- Underwood (1957): Proactive inhibition in retention
- Postman (1961): Retroactive inhibition
- Anderson (2003): Retrieval-induced forgetting
- Wickens (1972): Release from proactive interference

v4 Design:
- Easy (0.10):  1 distractor, difficulty=1 (same as v3)
- Medium (0.25): cross-contamination — shared symbol pool, different rules for shared symbols
- Hard (0.35):  3 distractors, difficulty=3, DELAYED interference (5 filler items between
                all-systems presentation and target test), plus rule-conflict items
- Extreme (0.30): 4 systems all difficulty=3, interleaved 6-examples-per-distractor vs
                  2-examples-for-target, test on the LEAST-presented system

Per tier: score = 0.30 * control + 0.70 * interference_accuracy
Composite = 0.10 * easy + 0.25 * medium + 0.35 * hard + 0.30 * extreme
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import re
import json
from data.rule_systems import (
    INTERF_EASY_TARGET_V4,
    INTERF_EASY_DISTRACT_V4,
    INTERF_MED_TARGET_V4,
    INTERF_MED_DISTRACT_V4,
    INTERF_HARD_TARGET_V4,
    INTERF_HARD_DIST1_V4,
    INTERF_HARD_DIST2_V4,
    INTERF_HARD_DIST3_V4,
    INTERF_HARD_FILLER_V4,
    INTERF_EXT_TARGET_V4,
    INTERF_EXT_DIST1_V4,
    INTERF_EXT_DIST2_V4,
    INTERF_EXT_DIST3_V4,
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


def _format_system(system, max_examples: int = 6) -> str:
    """Format a rule system for prompt inclusion."""
    text = f"**{system.name}**\nRules:\n"
    for r in system.rules:
        text += f"  - {r}\n"
    text += "Examples:\n"
    for ex in system.examples[:max_examples]:
        text += f"  {ex['input']} → {ex['output']}\n"
    return text


def _test_items(llm, system, context: str, prefix: str) -> float:
    """Test model on system's test items with given context. Returns accuracy."""
    correct = 0
    items = system.test_items

    for ti, test_item in enumerate(items):
        with kbench.chats.new(f"{prefix}_{ti}"):
            prompt = (
                context
                + f"\nInput: {test_item['input']}\n\n"
                + f"Respond with ONLY: {{\"answer\": \"<output>\"}}"
            )
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            if check_output(answer, test_item["output"]):
                correct += 1

    return correct / len(items) if items else 0


# ── Tier runners ─────────────────────────────────────────────────────

def run_easy_tier(llm) -> dict:
    """Easy: 1 distractor, difficulty=1 (same as v3)."""
    target = INTERF_EASY_TARGET_V4
    distractor = INTERF_EASY_DISTRACT_V4
    target_text = _format_system(target)

    ctrl_context = (
        f"You have learned the following rule system:\n\n{target_text}\n"
        f"Apply the **{target.name}** rules to this input."
    )
    control = _test_items(llm, target, ctrl_context, "easy_ctrl")

    all_text = _format_system(target, 6) + "\n" + _format_system(distractor, 6)
    interf_context = (
        f"You have learned ALL of these rule systems:\n\n{all_text}\n"
        f"Now apply ONLY the **{target.name}** rules (ignore all other systems) to this input."
    )
    interference = _test_items(llm, target, interf_context, "easy_interf")

    tier_score = round(0.30 * control + 0.70 * interference, 4)
    return {"control": control, "interference": interference, "tier_score": tier_score}


def run_medium_tier(llm) -> dict:
    """
    Medium: cross-contamination.
    Both systems share some symbols but apply DIFFERENT rules to them.
    Adds 2 cross-contamination items where the correct answer under the target
    coincidentally matches what the distractor system would produce — testing
    whether the model is truly applying the right system or just guessing.
    """
    target = INTERF_MED_TARGET_V4
    distractor = INTERF_MED_DISTRACT_V4
    target_text = _format_system(target)

    ctrl_context = (
        f"You have learned the following rule system:\n\n{target_text}\n"
        f"Apply the **{target.name}** rules to this input."
    )
    control = _test_items(llm, target, ctrl_context, "med_ctrl")

    # Cross-contamination: present both systems with explicit note about shared symbols
    shared_symbols_note = (
        "\n⚠️  WARNING: These two systems share some symbols but apply DIFFERENT rules to them. "
        "You must apply EXACTLY the rules of the specified system, not the other.\n"
    )
    all_text = (
        _format_system(target, 6)
        + "\n"
        + _format_system(distractor, 6)
        + shared_symbols_note
    )

    # Cross-contamination test items: use the first 3 target test items normally,
    # but also note that the distractor's answer for those inputs may look plausible
    contamination_note = (
        "\nNote: for some inputs, both systems may produce similar-looking outputs. "
        "Only the exact output of the specified system is correct.\n"
    )
    interf_context = (
        f"You have learned ALL of these rule systems:\n\n{all_text}"
        f"{contamination_note}\n"
        f"Now apply ONLY the **{target.name}** rules to this input."
    )
    interference = _test_items(llm, target, interf_context, "med_interf")

    tier_score = round(0.30 * control + 0.70 * interference, 4)
    return {"control": control, "interference": interference, "tier_score": tier_score}


def run_hard_tier(llm) -> dict:
    """
    Hard: 3 distractors, difficulty=3, DELAYED interference.

    Protocol:
    1. Present all 4 systems (target + 3 distractors) with examples
    2. Show 5 filler items from a 5th unrelated system (delay/interference buffer)
    3. THEN present the test item and ask for target system output
    4. Also includes rule-conflict framing: distractors are noted to contradict the target
    """
    target = INTERF_HARD_TARGET_V4
    dist1 = INTERF_HARD_DIST1_V4
    dist2 = INTERF_HARD_DIST2_V4
    dist3 = INTERF_HARD_DIST3_V4
    filler = INTERF_HARD_FILLER_V4

    target_text = _format_system(target)
    ctrl_context = (
        f"You have learned the following rule system:\n\n{target_text}\n"
        f"Apply the **{target.name}** rules to this input."
    )
    control = _test_items(llm, target, ctrl_context, "hard_ctrl")

    # Build the delayed interference context
    n_ex = 3  # fewer examples per system to keep context bounded
    all_systems_text = (
        _format_system(target, n_ex)
        + "\n" + _format_system(dist1, n_ex)
        + "\n" + _format_system(dist2, n_ex)
        + "\n" + _format_system(dist3, n_ex)
    )

    # Filler items (delay buffer — 5 items from a separate system)
    filler_block = "\n**[Unrelated processing task — complete before the final test]**\n"
    filler_block += "Process the following items using the most recently shown system:\n"
    for item in filler.test_items[:5]:
        filler_block += f"  {item['input']} → {item['output']}\n"
    filler_block += "(Above items processed. Now return to the target system.)\n"

    # Rule-conflict note
    conflict_note = (
        "\n⚠️  Note: Some distractors have rules that DIRECTLY CONTRADICT the target system's rules. "
        "Do NOT let these override your memory of the target system.\n"
    )

    def build_delayed_context(test_input):
        return (
            f"You have learned ALL of the following rule systems:\n\n"
            f"{all_systems_text}"
            f"{conflict_note}"
            f"{filler_block}\n"
            f"After the above processing, apply ONLY the **{target.name}** rules "
            f"(ignore all other systems) to this input."
        )

    # Run delayed interference
    correct = 0
    items = target.test_items
    for ti, test_item in enumerate(items):
        ctx = build_delayed_context(test_item["input"])
        with kbench.chats.new(f"hard_interf_{ti}"):
            prompt = ctx + f"\nInput: {test_item['input']}\n\nRespond with ONLY: {{\"answer\": \"<output>\"}}"
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            if check_output(answer, test_item["output"]):
                correct += 1
    interference = correct / len(items) if items else 0

    tier_score = round(0.30 * control + 0.70 * interference, 4)
    return {"control": control, "interference": interference, "tier_score": tier_score}


def run_extreme_tier(llm) -> dict:
    """
    Extreme: 4 systems all at difficulty=3.
    The target is the LEAST-presented system: only 2 examples.
    Distractors each get 6 examples — 3x more exposure.
    Examples from all systems are INTERLEAVED in the prompt.
    Model must identify and apply the under-represented system.
    """
    target = INTERF_EXT_TARGET_V4
    dist1 = INTERF_EXT_DIST1_V4
    dist2 = INTERF_EXT_DIST2_V4
    dist3 = INTERF_EXT_DIST3_V4

    target_text = _format_system(target)
    ctrl_context = (
        f"You have learned the following rule system:\n\n{target_text}\n"
        f"Apply the **{target.name}** rules to this input."
    )
    control = _test_items(llm, target, ctrl_context, "ext_ctrl")

    # Build interleaved prompt: 2 target examples mixed with 6 each from distractors
    target_exs = target.examples[:2]
    d1_exs = dist1.examples[:6]
    d2_exs = dist2.examples[:6]
    d3_exs = dist3.examples[:6]

    # Interleave: d1[0], d2[0], target[0], d3[0], d1[1], d2[1], target[1], d3[1], d1[2..5], d2[2..5], d3[2..5]
    interleaved_examples = []
    interleaved_examples.append(f"  [{dist1.name}] {d1_exs[0]['input']} → {d1_exs[0]['output']}")
    interleaved_examples.append(f"  [{dist2.name}] {d2_exs[0]['input']} → {d2_exs[0]['output']}")
    interleaved_examples.append(f"  [{target.name}] {target_exs[0]['input']} → {target_exs[0]['output']}")
    interleaved_examples.append(f"  [{dist3.name}] {d3_exs[0]['input']} → {d3_exs[0]['output']}")
    interleaved_examples.append(f"  [{dist1.name}] {d1_exs[1]['input']} → {d1_exs[1]['output']}")
    interleaved_examples.append(f"  [{dist2.name}] {d2_exs[1]['input']} → {d2_exs[1]['output']}")
    interleaved_examples.append(f"  [{target.name}] {target_exs[1]['input']} → {target_exs[1]['output']}")
    interleaved_examples.append(f"  [{dist3.name}] {d3_exs[1]['input']} → {d3_exs[1]['output']}")
    for i in range(2, 6):
        interleaved_examples.append(f"  [{dist1.name}] {d1_exs[i]['input']} → {d1_exs[i]['output']}")
        interleaved_examples.append(f"  [{dist2.name}] {d2_exs[i]['input']} → {d2_exs[i]['output']}")
        interleaved_examples.append(f"  [{dist3.name}] {d3_exs[i]['input']} → {d3_exs[i]['output']}")

    # System headers
    system_headers = (
        f"**Systems you have learned:**\n"
        f"1. {target.name}: {target.description}\n"
        f"   Rules: {' | '.join(target.rules)}\n\n"
        f"2. {dist1.name}: {dist1.description}\n"
        f"   Rules: {' | '.join(dist1.rules)}\n\n"
        f"3. {dist2.name}: {dist2.description}\n"
        f"   Rules: {' | '.join(dist2.rules)}\n\n"
        f"4. {dist3.name}: {dist3.description}\n"
        f"   Rules: {' | '.join(dist3.rules)}\n\n"
    )

    interleaved_block = "\n**Interleaved examples from all systems:**\n" + "\n".join(interleaved_examples)

    extreme_note = (
        f"\n⚠️  You saw far fewer examples of **{target.name}** than the other systems. "
        f"Apply ONLY the **{target.name}** rules to the test item below.\n"
    )

    interf_context = (
        system_headers
        + interleaved_block
        + extreme_note
        + f"Now apply ONLY the **{target.name}** rules to this input."
    )
    interference = _test_items(llm, target, interf_context, "ext_interf")

    tier_score = round(0.30 * control + 0.70 * interference, 4)
    return {"control": control, "interference": interference, "tier_score": tier_score}


@kbench.task(name="Proactive & Retroactive Interference v4")
def learning_interference(llm) -> float:
    """
    Proactive & Retroactive Interference Benchmark (v4).

    Four tiers:
    - Easy (0.10):    1 distractor, difficulty=1
    - Medium (0.25):  cross-contamination (shared symbols, different rules)
    - Hard (0.35):    3 distractors, difficulty=3, delayed interference + rule conflicts
    - Extreme (0.30): 4 systems difficulty=3, interleaved (target only 2 examples vs 6 each for distractors)

    Per tier: score = 0.30 * control + 0.70 * interference_accuracy
    Composite = 0.10 * easy + 0.25 * medium + 0.35 * hard + 0.30 * extreme
    """

    print("\n" + "=" * 60)
    print("LEARNING INTERFERENCE BENCHMARK v4")
    print("=" * 60)

    # ── Easy Tier ──
    print("\n--- EASY TIER (1 distractor, difficulty=1) ---")
    easy = run_easy_tier(llm)
    print(f"  Control: {easy['control']:.1%}")
    print(f"  With distractor: {easy['interference']:.1%}")
    print(f"  Tier score: {easy['tier_score']:.4f}")

    # ── Medium Tier ──
    print("\n--- MEDIUM TIER (cross-contamination, difficulty=2) ---")
    medium = run_medium_tier(llm)
    print(f"  Control: {medium['control']:.1%}")
    print(f"  With cross-contamination: {medium['interference']:.1%}")
    print(f"  Tier score: {medium['tier_score']:.4f}")

    # ── Hard Tier ──
    print("\n--- HARD TIER (3 distractors, delayed interference, difficulty=3) ---")
    hard = run_hard_tier(llm)
    print(f"  Control: {hard['control']:.1%}")
    print(f"  With 3 distractors + delay: {hard['interference']:.1%}")
    print(f"  Tier score: {hard['tier_score']:.4f}")

    # ── Extreme Tier ──
    print("\n--- EXTREME TIER (4 systems, interleaved, under-presented target) ---")
    extreme = run_extreme_tier(llm)
    print(f"  Control: {extreme['control']:.1%}")
    print(f"  Extreme interference: {extreme['interference']:.1%}")
    print(f"  Tier score: {extreme['tier_score']:.4f}")

    # ── Composite ──
    score = round(
        0.10 * easy["tier_score"]
        + 0.25 * medium["tier_score"]
        + 0.35 * hard["tier_score"]
        + 0.30 * extreme["tier_score"],
        4
    )
    score = max(0.0, min(1.0, score))

    print(f"\n{'=' * 60}")
    print(f"COMPOSITE SCORE: {score:.4f}")
    print(f"  Easy:    {easy['tier_score']:.4f} × 0.10 = {0.10 * easy['tier_score']:.4f}")
    print(f"  Medium:  {medium['tier_score']:.4f} × 0.25 = {0.25 * medium['tier_score']:.4f}")
    print(f"  Hard:    {hard['tier_score']:.4f} × 0.35 = {0.35 * hard['tier_score']:.4f}")
    print(f"  Extreme: {extreme['tier_score']:.4f} × 0.30 = {0.30 * extreme['tier_score']:.4f}")
    print(f"{'=' * 60}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
learning_interference.run(llm=kbench.llm)
