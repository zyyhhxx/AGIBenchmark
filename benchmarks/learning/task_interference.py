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
1. Learn A alone → Test A (control_A: no-interference baseline)
2. Learn A then B → Test B (baseline_B)
3. After learning both: Re-test A (post_interference_A)
4. Compute interference magnitudes relative to control

Scoring redesign (v2):
- Retroactive interference = control_A - post_interference_A (how much A drops after B)
- Proactive interference = control_A - baseline_B (how much worse B is vs A-alone)
- Compartmentalization = post_interference_A / control_A (retention ratio)
- Sub-scores are independent and weighted to discriminate different interference patterns.

Score = 0.25 * retro_magnitude_norm
      + 0.25 * proactive_magnitude_norm
      + 0.25 * compartmentalization
      + 0.25 * control_accuracy

Where magnitudes are normalized to [0,1] and compartmentalization rewards
maintaining A accuracy despite B learning.
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


def compute_interference_score(control_A: float, baseline_B: float,
                                post_interf_A: float) -> dict:
    """
    Compute interference metrics and composite score.

    Args:
        control_A: Accuracy on system A with no interference (A alone)
        baseline_B: Accuracy on system B after learning A
        post_interf_A: Accuracy on A after also learning B

    Returns dict with all sub-metrics and composite score.
    """
    # Retroactive interference: how much A drops after learning B
    # Normalized: magnitude / control (fraction of knowledge lost)
    retro_raw = max(0.0, control_A - post_interf_A)
    retro_norm = retro_raw / control_A if control_A > 0 else 0.0

    # Proactive interference: how much worse B is vs A-alone baseline
    # Normalized: magnitude / control
    proactive_raw = max(0.0, control_A - baseline_B)
    proactive_norm = proactive_raw / control_A if control_A > 0 else 0.0

    # Compartmentalization: how well model retains A after B
    # 1.0 = perfect retention, 0.0 = total forgetting
    compartment = post_interf_A / control_A if control_A > 0 else 0.0
    compartment = min(1.0, compartment)  # Cap at 1 (improvement is possible)

    # Composite: balanced across 4 independent dimensions
    # Higher retro/proactive magnitude = more interference detected (interesting)
    # Higher compartmentalization = better resistance
    # Higher control = model can actually do the task
    score = round(
        0.25 * retro_norm
        + 0.25 * proactive_norm
        + 0.25 * compartment
        + 0.25 * control_A,
        4
    )

    return {
        "control_A": control_A,
        "baseline_B": baseline_B,
        "post_interf_A": post_interf_A,
        "retro_raw": retro_raw,
        "retro_norm": retro_norm,
        "proactive_raw": proactive_raw,
        "proactive_norm": proactive_norm,
        "compartmentalization": compartment,
        "composite_score": max(0.0, min(1.0, score)),
    }


@kbench.task(name="learning_interference")
def learning_interference(llm) -> float:
    """
    Proactive & Retroactive Interference Benchmark (v2).

    Measures how learning similar systems affects retention and acquisition.
    Uses a no-interference control baseline for proper normalization.

    Protocol:
    1. Learn A alone → Test A (control_A: no-interference baseline)
    2. Learn A, then B → Test B (baseline_B)
    3. After both: Re-test A (post_interference_A)
    4. Compute interference magnitudes relative to control

    Score = 0.25 * retro_magnitude_norm + 0.25 * proactive_magnitude_norm
          + 0.25 * compartmentalization + 0.25 * control_accuracy
    """

    # ── Phase 1: Control — Learn System A alone, test A (no interference) ──
    control_A = test_system(llm, SYSTEM_A, chat_prefix="control_A")

    # ── Phase 2: Learn System B after A context ──
    a_context = (
        f"You previously learned system {SYSTEM_A.name}. "
        f"Now learn a NEW but similar system.\n"
    )
    baseline_B = test_system(llm, SYSTEM_B, context_prefix=a_context, chat_prefix="phase2_B")

    # ── Phase 3: Re-test A after learning B (retroactive interference) ──
    b_context = (
        f"You recently learned two similar systems: "
        f"{SYSTEM_A.name} and {SYSTEM_B.name}. "
        f"Now I want you to recall the FIRST system ({SYSTEM_A.name}) specifically. "
        f"Ignore the second system you learned.\n"
    )
    post_interf_A = test_system(llm, SYSTEM_A, context_prefix=b_context,
                                 chat_prefix="phase3_retest_A")

    # ── Compute Metrics ──
    metrics = compute_interference_score(control_A, baseline_B, post_interf_A)
    score = metrics["composite_score"]

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"PROACTIVE & RETROACTIVE INTERFERENCE RESULTS (v2)")
    print(f"{'='*60}")
    print(f"System A: {SYSTEM_A.name} ({len(SYSTEM_A.rules)} rules)")
    print(f"System B: {SYSTEM_B.name} ({len(SYSTEM_B.rules)} rules)")
    print(f"\n--- Phase Results ---")
    print(f"Control A (no interference): {control_A:.2%}")
    print(f"Baseline B (after A):        {baseline_B:.2%}")
    print(f"Post-interference A:         {post_interf_A:.2%}")
    print(f"\n--- Interference Metrics ---")
    print(f"Retroactive (raw):          {metrics['retro_raw']:.2%}")
    print(f"Retroactive (normalized):   {metrics['retro_norm']:.4f}")
    print(f"Proactive (raw):            {metrics['proactive_raw']:.2%}")
    print(f"Proactive (normalized):     {metrics['proactive_norm']:.4f}")
    print(f"Compartmentalization:       {metrics['compartmentalization']:.4f}")
    print(f"\nComposite score: {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    learning_interference.run(llm=kbench.llm)
