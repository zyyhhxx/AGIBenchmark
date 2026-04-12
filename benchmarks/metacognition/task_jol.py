"""
MetaCog Benchmark 3: Judgment-of-Learning (JOL)

Tests whether a model can accurately predict its own future recall
of newly-studied material. Uses NOVEL stimuli (invented words and
rule systems) that cannot be in training data.

Protocol:
1. STUDY: Present novel word-definition pairs and rule systems
2. JOL: For each item, model rates confidence of future recall (0-100)
3. DISTRACTOR: Interpose unrelated conversation to create temporal distance
4. TEST: Test recall of studied items
5. SCORE: Calibration between JOL ratings and actual recall

Cognitive Science Basis:
- Arbuckle & Cuddy (1969): JOL paradigm
- Nelson & Narens (1990): JOL as metacognitive monitoring
- Key finding: Delayed JOLs are more accurate than immediate JOLs
- Human JOL gamma: 0.40–0.90

Shortcut Resistance:
- ALL stimuli are invented (no training data contamination)
- Difficulty varied by imageability and abstractness
- Rule systems require genuine in-context learning
- Distractor phase prevents simple echo/repetition

Score: Weighted composite of gamma, Brier Skill Score, and accuracy bonus.
BSS replaces 1-ECE to fix inverted scoring (always-uncertain scored too high).
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
import random
from data.jol_stimuli import JOL_WORD_PAIRS, JOL_RULE_SYSTEMS, DISTRACTOR_QUESTIONS


@dataclass
class JOLRating:
    """Model's judgment of learning for a studied item."""
    confidence: int  # 0-100: How confident that you'll recall this later?
    reasoning: str   # Brief explanation


@dataclass
class RecallAttempt:
    """Model's recall attempt for a studied word."""
    definition: str  # Recalled definition
    confidence: int  # Post-recall confidence (0-100)


@dataclass
class RuleAnswer:
    """Model's answer to a rule-system test question."""
    answer: str
    reasoning: str


# ─── Helpers ─────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def recall_match(recalled: str, original: str, threshold: float = 0.5) -> bool:
    """
    Check if recalled definition matches original using word overlap.
    Threshold = fraction of content words that must appear.
    """
    stop_words = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "is",
                  "that", "which", "and", "or", "but", "with", "by", "from"}

    orig_words = set(normalize(original).split()) - stop_words
    recall_words = set(normalize(recalled).split()) - stop_words

    if not orig_words:
        return True

    overlap = len(orig_words & recall_words)
    return overlap / len(orig_words) >= threshold


def brier_skill_score(confidences_0_100: list, outcomes_binary: list) -> float:
    """
    Brier Skill Score: BSS = 1 - BS / BS_ref

    Rewards BOTH calibration and resolution (discrimination).
    BS_ref = climatological baseline = base_rate * (1 - base_rate).
    Returns float in (-inf, 1].
    """
    conf = np.array(confidences_0_100) / 100.0
    out = np.array(outcomes_binary, dtype=float)
    BS = float(np.mean((conf - out) ** 2))
    base_rate = float(out.mean())
    BS_ref = base_rate * (1 - base_rate)
    if BS_ref < 1e-10:
        BS_ref = float(np.mean((0.5 - out) ** 2))
    if BS_ref < 1e-10:
        return 0.0
    return 1.0 - BS / BS_ref


def goodman_kruskal_gamma(x: list, y: list) -> float:
    n = len(x)
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            x_diff = x[i] - x[j]
            y_diff = y[i] - y[j]
            product = x_diff * y_diff
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1
    denom = concordant + discordant
    if denom == 0:
        return 0.0
    return (concordant - discordant) / denom


def compute_ece(confidences: list, accuracies: list, n_bins: int = 5) -> float:
    """Compute ECE. Using 5 bins due to smaller sample size."""
    conf = np.array(confidences) / 100.0
    acc = np.array(accuracies, dtype=float)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total = len(conf)
    for i in range(n_bins):
        lo, hi = bin_boundaries[i], bin_boundaries[i + 1]
        if i == 0:
            mask = (conf >= lo) & (conf <= hi)
        else:
            mask = (conf > lo) & (conf <= hi)
        if mask.sum() == 0:
            continue
        ece += (mask.sum() / total) * abs(acc[mask].mean() - conf[mask].mean())
    return round(float(ece), 4)


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="Judgment of Learning")
def metacog_jol(llm) -> float:
    """
    Judgment-of-Learning (JOL) Benchmark.

    Study → JOL → Distract → Test protocol with novel stimuli.

    Score = 0.40 * gamma_norm + 0.30 * max(0, BSS) + 0.30 * recall_rate

    BSS (Brier Skill Score) replaces the old 1-ECE component to properly
    reward resolution alongside calibration.

    Cognitive Science Basis: Arbuckle & Cuddy (1969), Nelson & Narens (1990).
    Scoring: Brier (1950), Murphy (1973) skill score decomposition.
    Human JOL gamma: 0.40–0.90.
    """

    all_jol_ratings = []
    all_accuracies = []
    results_log = []

    # ── Phase 1: STUDY — Present all word-definition pairs ──
    with kbench.chats.new("study_session"):
        study_prompt = "I'm going to teach you some new vocabulary words. Study each one carefully.\n\n"
        for i, pair in enumerate(JOL_WORD_PAIRS):
            study_prompt += f"{i+1}. **{pair['word']}**: {pair['definition']}\n"
        study_prompt += "\nPlease confirm you've studied these words by saying 'Ready'."
        llm.prompt(study_prompt)

        # ── Phase 2: JOL — Rate confidence for each item ──
        for i, pair in enumerate(JOL_WORD_PAIRS):
            jol_prompt = (
                f"For the word **{pair['word']}** (which you just studied), "
                f"rate your confidence (0-100) that you will be able to recall "
                f"its definition if I ask you later in this conversation, "
                f"after some unrelated questions.\n\n"
                f"Respond with ONLY a JSON object:\n"
                f'{{"confidence": <0-100>, "reasoning": "<brief>"}}'
            )

            try:
                jol = llm.prompt(jol_prompt, schema=JOLRating)
                jol_conf = max(0, min(100, jol.confidence))
            except Exception:
                raw = llm.prompt(jol_prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    jol_conf = max(0, min(100, int(parsed.get("confidence", 50))))
                except Exception:
                    jol_conf = 50

            all_jol_ratings.append(jol_conf)
            results_log.append({
                "word": pair["word"],
                "definition": pair["definition"],
                "difficulty": pair["difficulty"],
                "jol": jol_conf,
            })

        # ── Phase 3: DISTRACTOR — Unrelated questions ──
        distractors = random.sample(DISTRACTOR_QUESTIONS, min(5, len(DISTRACTOR_QUESTIONS)))
        for dq in distractors:
            llm.prompt(dq)

        # ── Phase 4: TEST — Recall definitions ──
        for i, pair in enumerate(JOL_WORD_PAIRS):
            recall_prompt = (
                f"Earlier, I taught you the word **{pair['word']}**. "
                f"What was its definition? Try to recall it as accurately as possible.\n\n"
                f"Respond with ONLY a JSON object:\n"
                f'{{"definition": "<recalled definition>", "confidence": <0-100>}}'
            )

            try:
                recall = llm.prompt(recall_prompt, schema=RecallAttempt)
                recalled_def = recall.definition
            except Exception:
                raw = llm.prompt(recall_prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    recalled_def = str(parsed.get("definition", raw))
                except Exception:
                    recalled_def = raw

            is_correct = recall_match(recalled_def, pair["definition"])
            all_accuracies.append(is_correct)
            results_log[i]["recalled"] = recalled_def[:100]
            results_log[i]["is_correct"] = is_correct

    # ── Phase 5: Rule System Test ──
    rule_jols = []
    rule_accs = []

    for rs in JOL_RULE_SYSTEMS:
        with kbench.chats.new(f"rule_{rs['rule_name']}"):
            # Study rules
            rules_text = f"Learn the following rule system: **{rs['rule_name']}**\n\n"
            for r in rs["rules"]:
                rules_text += f"- {r}\n"
            rules_text += "\nSay 'Ready' when you've studied these rules."
            llm.prompt(rules_text)

            # JOL for rule system
            jol_prompt = (
                f"Rate your confidence (0-100) that you can correctly apply "
                f"the {rs['rule_name']} rules to answer test questions.\n\n"
                f"Respond with ONLY: {{\"confidence\": <0-100>, \"reasoning\": \"<brief>\"}}"
            )
            try:
                jol = llm.prompt(jol_prompt, schema=JOLRating)
                jol_conf = max(0, min(100, jol.confidence))
            except Exception:
                jol_conf = 50

            # Distractor
            llm.prompt(random.choice(DISTRACTOR_QUESTIONS))

            # Test questions
            rule_correct = 0
            for tq in rs["test_questions"]:
                test_prompt = (
                    f"Using the {rs['rule_name']} rules you learned, answer:\n"
                    f"{tq['q']}\n\n"
                    f"Respond with ONLY: {{\"answer\": \"<answer>\", \"reasoning\": \"<steps>\"}}"
                )
                try:
                    ans = llm.prompt(test_prompt, schema=RuleAnswer)
                    answer = ans.answer
                except Exception:
                    raw = llm.prompt(test_prompt)
                    try:
                        parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                        answer = str(parsed.get("answer", raw))
                    except Exception:
                        answer = raw

                correct = normalize(tq["a"]) in normalize(answer)
                if correct:
                    rule_correct += 1

            rule_acc = rule_correct / len(rs["test_questions"])
            # Each rule system contributes one JOL-accuracy pair
            rule_jols.append(jol_conf)
            rule_accs.append(rule_acc >= 0.5)  # Binarize: majority correct
            all_jol_ratings.append(jol_conf)
            all_accuracies.append(rule_acc >= 0.5)

    # ── Compute Metrics ──
    gamma = goodman_kruskal_gamma(all_jol_ratings, [int(a) for a in all_accuracies])
    ece = compute_ece(all_jol_ratings, all_accuracies)
    recall_rate = sum(all_accuracies) / len(all_accuracies)
    bss_raw = brier_skill_score(all_jol_ratings, [int(a) for a in all_accuracies])

    gamma_norm = (gamma + 1) / 2
    score = round(0.40 * gamma_norm + 0.30 * max(0.0, bss_raw) + 0.30 * recall_rate, 4)

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"JUDGMENT-OF-LEARNING (JOL) BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Word pairs tested: {len(JOL_WORD_PAIRS)}")
    print(f"Rule systems tested: {len(JOL_RULE_SYSTEMS)}")
    print(f"Total items: {len(all_jol_ratings)}")
    print(f"\n--- Metacognitive Metrics ---")
    print(f"Gamma correlation: {gamma:+.4f}  (human range: 0.40–0.90)")
    print(f"Brier Skill Score: {bss_raw:+.4f}  (>0 = better than base rate)")
    print(f"ECE (diagnostic): {ece:.4f}")
    print(f"Recall rate: {recall_rate:.2%}")
    print(f"Composite score: {score:.4f}")

    # Per-difficulty breakdown
    print(f"\n--- Word Pairs by Difficulty ---")
    for diff in [1, 2, 3]:
        items = [r for r in results_log if r["difficulty"] == diff]
        if items:
            acc = sum(1 for r in items if r.get("is_correct", False)) / len(items)
            mean_jol = sum(r["jol"] for r in items) / len(items)
            print(f"  Difficulty {diff}: n={len(items)}, acc={acc:.2%}, mean_jol={mean_jol:.0f}%")

    # Per-item results
    print(f"\n--- Per-Item Results ---")
    for r in results_log:
        status = "✓" if r.get("is_correct", False) else "✗"
        recalled = r.get("recalled", "N/A")
        print(f"  {status} [JOL:{r['jol']:3d}%] {r['word']}: {recalled[:50]}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
metacog_jol.run(llm=kbench.llm)
