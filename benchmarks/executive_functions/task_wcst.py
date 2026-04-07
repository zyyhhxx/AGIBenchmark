"""
Executive Functions Benchmark 1: Wisconsin Card Sort Test (WCST) Analogue

Tests cognitive flexibility / set-shifting — a core executive function.

The model sorts cards by matching a target card to one of 4 reference cards.
The active sorting rule (color, shape, or number) is NOT told to the model —
it must infer it from "Correct"/"Incorrect" feedback. After 10 consecutive
correct sorts, the rule switches silently. The model must detect the shift
and adapt.

Cognitive Science Basis:
- Wisconsin Card Sort Test (Berg, 1948; Milner, 1963)
- Miyake et al. (2000): set-shifting as a core executive function
- Perseveration errors (continuing old rule after switch) are the key metric
- Frontal lobe patients show elevated perseveration (Milner, 1963)

Metrics:
- Total accuracy: proportion correct across all trials
- Perseveration rate: proportion of post-switch errors that use the OLD rule
- Set-shifting speed: mean trials to reach 3 consecutive correct after each rule switch
- Categories completed: number of rule episodes with ≥10 correct sorts

Score = weighted composite:
  0.30 * accuracy + 0.40 * (1 - perseveration_rate) + 0.30 * shift_efficiency

Shortcut Resistance:
- Rules are never stated explicitly — model must infer from feedback
- Target cards are constructed so each dimension matches a different reference card
- Rule switches are silent — no hint is given
- Perseveration metric specifically catches models that can't update strategies
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
from data.wcst_stimuli import WCST_STIMULI, card_str


# ─── Structured Output Schema ──────────────────────────────────────

@dataclass
class WCSTResponse:
    """Model's card sort response."""
    choice: int       # 1-4: which reference card the target matches
    reasoning: str    # Brief explanation of why this card was chosen


# ─── Core Scoring Logic ────────────────────────────────────────────

def classify_error(trial: dict, model_choice: int, prev_rule: str) -> str:
    """
    Classify an incorrect response.
    - 'perseverative': model sorted by the PREVIOUS rule
    - 'non_perseverative': model used some other (wrong) strategy
    """
    if model_choice < 1 or model_choice > 4:
        return "invalid"

    target = trial["target_card"]
    refs = trial["reference_cards"]
    chosen_ref = refs[model_choice - 1]

    # Check if the chosen card matches target on the previous rule dimension
    if prev_rule and target.get(prev_rule) == chosen_ref.get(prev_rule):
        return "perseverative"
    return "non_perseverative"


def compute_shift_speed(trial_results: list, switch_points: list) -> float:
    """
    Compute mean trials to reach 3 consecutive correct after each rule switch.
    Lower = better shifting. Returns normalized score in [0, 1].
    """
    if not switch_points:
        return 0.5

    shift_speeds = []
    for sp in switch_points:
        consecutive = 0
        trials_needed = 0
        for i in range(sp, len(trial_results)):
            trials_needed += 1
            if trial_results[i]["correct"]:
                consecutive += 1
                if consecutive >= 3:
                    break
            else:
                consecutive = 0
        else:
            # Never reached 3 consecutive — max penalty
            trials_needed = len(trial_results) - sp

        shift_speeds.append(trials_needed)

    if not shift_speeds:
        return 0.5

    mean_speed = np.mean(shift_speeds)
    # Normalize: 3 trials (instant adapt) = 1.0, 10+ trials = 0.0
    efficiency = max(0.0, 1.0 - (mean_speed - 3) / 7.0)
    return round(float(efficiency), 4)


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="exec_func_wcst")
def exec_func_wcst(llm) -> float:
    """
    Wisconsin Card Sort Test Analogue.

    Tests cognitive flexibility through rule inference and set-shifting.
    Model sorts cards by inferring the active rule from feedback,
    then must adapt when the rule silently changes.

    Score = 0.30 * accuracy + 0.40 * (1 - perseveration_rate) + 0.30 * shift_efficiency

    Cognitive Science Basis: Berg (1948), Milner (1963), Miyake et al. (2000).
    Human perseveration rate: ~10-15% (healthy adults).
    """
    stim = WCST_STIMULI
    refs = stim["reference_cards"]
    trials = stim["trials"]

    # Build reference card description (shown every trial)
    ref_desc = "Reference Cards:\n"
    for i, r in enumerate(refs, 1):
        ref_desc += f"  Card {i}: {card_str(r)}\n"

    trial_results = []
    prev_rule = None
    current_episode = 0
    switch_points = []  # trial indices where rule switched

    # Use a single persistent chat for the entire task (feedback-dependent)
    with kbench.chats.new("wcst_session") as chat:
        # Initial instructions
        system_msg = (
            "You are taking a card sorting test. On each trial, you'll see a target card "
            "and 4 reference cards. Your job is to match the target to the correct reference card.\n\n"
            "The sorting rule is based on ONE dimension: color, shape, or number. "
            "You must figure out which dimension is active by paying attention to the feedback "
            "(Correct/Incorrect) after each response.\n\n"
            "IMPORTANT: The sorting rule may change without warning. If you start getting "
            "'Incorrect' feedback, the rule has probably changed — adapt your strategy.\n\n"
            f"{ref_desc}\n"
            "For each trial, respond with ONLY your card choice (1, 2, 3, or 4) "
            "and a brief reason. Format:\n"
            "Choice: [number]\nReason: [brief explanation]"
        )

        # We'll send trials in conversation, accumulating feedback
        history = system_msg + "\n\n"

        for t_idx, trial in enumerate(trials):
            # Detect rule switches
            if trial["rule_episode"] != current_episode:
                switch_points.append(t_idx)
                prev_rule_at_switch = trials[t_idx - 1]["active_rule"] if t_idx > 0 else None
                current_episode = trial["rule_episode"]
            else:
                prev_rule_at_switch = None

            target = trial["target_card"]
            trial_prompt = (
                f"--- Trial {trial['trial_num']} ---\n"
                f"Target card: {card_str(target)}\n"
                f"Which reference card does it match? (1-4)"
            )

            # Build full prompt with history for context
            full_prompt = history + trial_prompt

            response = llm(
                full_prompt,
                response_format=WCSTResponse
            )

            # Parse choice
            choice = response.choice
            if choice < 1 or choice > 4:
                choice = 1  # default on parse failure

            correct = (choice == trial["correct_answer"])

            # Classify error if incorrect
            error_type = None
            if not correct and prev_rule is not None:
                error_type = classify_error(trial, choice, prev_rule)

            # Generate feedback
            feedback = "✓ Correct!" if correct else "✗ Incorrect."

            trial_results.append({
                "trial_num": trial["trial_num"],
                "active_rule": trial["active_rule"],
                "rule_episode": trial["rule_episode"],
                "correct_answer": trial["correct_answer"],
                "model_choice": choice,
                "correct": correct,
                "error_type": error_type,
                "is_switch_trial": t_idx in switch_points,
            })

            # Update history with this trial + feedback
            history += trial_prompt + f"\nYour answer: Card {choice}\n{feedback}\n\n"

            # Track previous rule for perseveration detection
            prev_rule = trial["active_rule"]

    # ── Compute Metrics ──

    n_trials = len(trial_results)
    n_correct = sum(1 for r in trial_results if r["correct"])
    accuracy = n_correct / n_trials if n_trials > 0 else 0

    # Perseveration rate: among post-switch errors, proportion that are perseverative
    post_switch_errors = [
        r for r in trial_results
        if not r["correct"] and r["error_type"] in ("perseverative", "non_perseverative")
    ]
    perseverative_errors = [r for r in post_switch_errors if r["error_type"] == "perseverative"]
    perseveration_rate = (
        len(perseverative_errors) / len(post_switch_errors)
        if post_switch_errors else 0.0
    )

    # Shift efficiency
    shift_efficiency = compute_shift_speed(trial_results, switch_points)

    # Categories completed (episodes where model got ≥10 correct)
    episode_correct = {}
    for r in trial_results:
        ep = r["rule_episode"]
        if ep not in episode_correct:
            episode_correct[ep] = 0
        if r["correct"]:
            episode_correct[ep] += 1
    categories_completed = sum(1 for v in episode_correct.values() if v >= 7)

    # ── Composite Score ──
    score = (
        0.30 * accuracy +
        0.40 * (1.0 - perseveration_rate) +
        0.30 * shift_efficiency
    )
    score = round(float(np.clip(score, 0, 1)), 4)

    # ── Log detailed results ──
    kbench.log({
        "benchmark": "WCST",
        "n_trials": n_trials,
        "accuracy": round(accuracy, 4),
        "perseveration_rate": round(perseveration_rate, 4),
        "perseverative_errors": len(perseverative_errors),
        "total_post_switch_errors": len(post_switch_errors),
        "shift_efficiency": shift_efficiency,
        "categories_completed": categories_completed,
        "total_episodes": len(episode_correct),
        "switch_points": switch_points,
        "composite_score": score,
        "score_breakdown": {
            "accuracy_component": round(0.30 * accuracy, 4),
            "perseveration_component": round(0.40 * (1 - perseveration_rate), 4),
            "shift_component": round(0.30 * shift_efficiency, 4),
        },
        "per_episode": {
            str(ep): {
                "correct": episode_correct.get(ep, 0),
                "rule": trials[min(i for i, t in enumerate(trials) if t["rule_episode"] == ep)]["active_rule"]
            }
            for ep in sorted(episode_correct.keys())
        },
    })

    return score
