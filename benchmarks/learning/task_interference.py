"""
Learning Benchmark 3: Proactive & Retroactive Interference (v3)

Tests whether the presence of competing learned systems interferes
with the correct application of a target system.

Cognitive Science Basis:
- Underwood (1957): Proactive inhibition in retention
- Postman (1961): Retroactive inhibition
- Anderson (2003): Retrieval-induced forgetting
- Wickens (1972): Release from proactive interference

Key Design Insight (v3):
Previous versions provided rules in every prompt independently,
making interference impossible (same bug as task_switch v1).
v3 creates interference WITHIN the prompt by presenting multiple
competing rule systems together and testing whether the model
can apply the correct one without confusion.

Protocol per tier:
- Control: Present System A rules alone → test A items
- Interference: Present Systems A + B together → test A items
- Score = control accuracy + interference resistance

Three difficulty tiers with weighted composite.
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import re
import json
from data.rule_systems import generate_symbol_system


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
    items = system.test_items  # 5 items from rule_systems.py
    
    for ti, test_item in enumerate(items):
        with kbench.chats.new(f"{prefix}_{ti}"):
            prompt = (
                context +
                f"\nInput: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\"}}"
            )
            raw = llm.prompt(prompt)
            cleaned = _strip_think(raw)
            cleaned = re.sub(r'//.*', '', cleaned)
            try:
                parsed = json.loads(re.search(r'\{.*\}', cleaned, re.DOTALL).group())
                answer = str(parsed.get("answer", cleaned))
            except Exception:
                answer = cleaned
            
            if check_output(answer, test_item["output"]):
                correct += 1
    
    return correct / len(items) if items else 0


# ── System Definitions (3 tiers) ──

# EASY: Simple substitution rules (difficulty=1), distractor from different seed
EASY_TARGET = generate_symbol_system("v3_easy_target", difficulty=1)
EASY_DISTRACT = generate_symbol_system("v3_easy_distract", difficulty=1)

# MEDIUM: Context-dependent rules (difficulty=2), similar distractor
MED_TARGET = generate_symbol_system("v3_med_target", difficulty=2)
MED_DISTRACT = generate_symbol_system("v3_med_distract", difficulty=2)

# HARD: Multi-pass chained rules (difficulty=3), two distractors
HARD_TARGET = generate_symbol_system("v3_hard_target", difficulty=3)
HARD_DISTRACT1 = generate_symbol_system("v3_hard_dist1", difficulty=3)
HARD_DISTRACT2 = generate_symbol_system("v3_hard_dist2", difficulty=3)


def run_tier(llm, target, distractors: list, prefix: str) -> dict:
    """Run control + interference for one tier."""
    
    target_text = _format_system(target)
    
    # Control: target rules only
    ctrl_context = (
        f"You have learned the following rule system:\n\n{target_text}\n"
        f"Apply the **{target.name}** rules to this input."
    )
    control = _test_items(llm, target, ctrl_context, f"{prefix}_ctrl")
    
    # Interference: target + all distractors, ask for target
    # Use fewer examples when multiple distractors to keep context manageable
    n_ex = 4 if len(distractors) >= 2 else 6
    target_text_short = _format_system(target, max_examples=n_ex)
    all_text = target_text_short
    for d in distractors:
        all_text += "\n" + _format_system(d, max_examples=n_ex)
    
    # Add distractor examples as "previously processed" to create proactive interference
    interleave = ""
    if len(distractors) >= 2:
        interleave = "\nYou recently processed these items from other systems:\n"
        for d in distractors:
            for di in d.test_items[:2]:
                interleave += f"  [{d.name}] {di['input']} → {di['output']}\n"
    
    interf_context = (
        f"You have learned ALL of these rule systems:\n\n{all_text}\n"
        f"{interleave}\n"
        f"Now apply ONLY the **{target.name}** rules "
        f"(ignore all other systems) to this input."
    )
    interference = _test_items(llm, target, interf_context, f"{prefix}_interf")
    
    # Tier score: 0.30 * control + 0.70 * interference_accuracy
    tier_score = 0.30 * control + 0.70 * interference
    
    return {
        "control": control,
        "interference": interference,
        "tier_score": round(tier_score, 4),
    }


@kbench.task(name="Proactive & Retroactive Interference")
def learning_interference(llm) -> float:
    """
    Proactive & Retroactive Interference Benchmark (v3).

    Measures interference resistance: can the model apply rules from a target
    system while competing systems' rules are also present in context?

    Three tiers:
    - Easy (0.15): Simple target + 1 dissimilar distractor (difficulty=1)
    - Medium (0.35): Moderate target + 1 similar distractor (difficulty=2)
    - Hard (0.50): Complex target + 2 similar distractors + interleaved items (difficulty=3)

    Per tier: score = 0.30 * control + 0.70 * interference_accuracy
    Composite = 0.15 * easy + 0.35 * medium + 0.50 * hard
    """

    print("\n" + "=" * 60)
    print("LEARNING INTERFERENCE BENCHMARK v3")
    print("=" * 60)

    # ── Easy Tier ──
    print("\n--- EASY TIER (simple rules, 1 distractor, difficulty=1) ---")
    easy = run_tier(llm, EASY_TARGET, [EASY_DISTRACT], "easy")
    print(f"  Control: {easy['control']:.1%}")
    print(f"  With distractor: {easy['interference']:.1%}")
    print(f"  Tier score: {easy['tier_score']:.4f}")

    # ── Medium Tier ──
    print("\n--- MEDIUM TIER (context-dependent rules, 1 distractor, difficulty=2) ---")
    medium = run_tier(llm, MED_TARGET, [MED_DISTRACT], "med")
    print(f"  Control: {medium['control']:.1%}")
    print(f"  With distractor: {medium['interference']:.1%}")
    print(f"  Tier score: {medium['tier_score']:.4f}")

    # ── Hard Tier ──
    print("\n--- HARD TIER (multi-pass rules, 2 distractors, difficulty=3) ---")
    hard = run_tier(llm, HARD_TARGET, [HARD_DISTRACT1, HARD_DISTRACT2], "hard")
    print(f"  Control: {hard['control']:.1%}")
    print(f"  With 2 distractors: {hard['interference']:.1%}")
    print(f"  Tier score: {hard['tier_score']:.4f}")

    # ── Composite ──
    score = round(
        0.15 * easy["tier_score"]
        + 0.35 * medium["tier_score"]
        + 0.50 * hard["tier_score"],
        4
    )
    score = max(0.0, min(1.0, score))

    print(f"\n{'=' * 60}")
    print(f"COMPOSITE SCORE: {score:.4f}")
    print(f"  Easy:   {easy['tier_score']:.4f} × 0.15 = {0.15 * easy['tier_score']:.4f}")
    print(f"  Medium: {medium['tier_score']:.4f} × 0.35 = {0.35 * medium['tier_score']:.4f}")
    print(f"  Hard:   {hard['tier_score']:.4f} × 0.50 = {0.50 * hard['tier_score']:.4f}")
    print(f"{'=' * 60}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    learning_interference.run(llm=kbench.llm)
