"""
MetaCog Benchmark 3: Judgment-of-Learning (JOL) v2

Tests whether a model can accurately predict its own learning performance
on NOVEL rule systems and tasks of varying difficulty.

Protocol:
1. PREVIEW: Show brief description of each learning challenge
2. JOL: Rate confidence (0-100) of solving it correctly after studying
3. STUDY+TEST: Actually present the material and test comprehension
4. SCORE: Calibration between JOL predictions and actual performance

Why v2:
- v1 tested verbatim recall within a single context — trivial for LLMs
- v2 tests PREDICTIVE metacognition: "Can I learn this?" not "Can I echo this?"
- Challenges range from simple (difficulty 1) to very complex (difficulty 5)
- Creates genuine variance: models fail hard challenges, succeed easy ones
- Good metacognition = knowing your capability boundary

Cognitive Science Basis:
- Nelson & Narens (1990): Metacognitive monitoring
- Dunning-Kruger (1999): Miscalibration of competence predictions
- Key human finding: JOL accuracy improves with domain expertise
- Human JOL gamma: 0.40–0.90

Score: Weighted composite of gamma + Brier Skill Score + sensitivity bonus.
"""

import kaggle_benchmarks as kbench
import numpy as np
import re
import json
import random
from data.jol_challenges import LEARNING_CHALLENGES


# ─── Helpers ───────────────────────────────────────────────────────

def _strip_think(text: str) -> str:
    """Remove <think>...</think> tags."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def normalize(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def flexible_match(model_answer: str, correct_answer: str) -> bool:
    """
    Check if model answer matches correct answer flexibly.
    Handles different formats for numbers, lists, etc.
    """
    ma = normalize(model_answer)
    ca = normalize(correct_answer)

    # Exact match
    if ca in ma:
        return True

    # Extract numbers from both and compare
    model_nums = re.findall(r'-?\d+\.?\d*', ma)
    correct_nums = re.findall(r'-?\d+\.?\d*', ca)
    if correct_nums and model_nums:
        # All correct numbers appear in model answer
        if all(n in model_nums for n in correct_nums):
            return True

    # Key phrases (split by key words and check containment)
    ca_words = set(ca.split()) - {"the", "a", "an", "is", "of", "to", "and", "or", "in"}
    if len(ca_words) >= 3:
        ma_words = set(ma.split())
        overlap = len(ca_words & ma_words) / len(ca_words)
        if overlap >= 0.7:
            return True

    return False


def goodman_kruskal_gamma(x: list, y: list) -> float:
    """Compute Goodman-Kruskal gamma correlation."""
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


def brier_skill_score(confidences_0_100: list, outcomes_binary: list) -> float:
    """
    Brier Skill Score: BSS = 1 - BS / BS_ref
    Rewards calibration and resolution.
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


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="Judgment of Learning")
def metacog_jol(llm) -> float:
    """JOL v2: Predictive Learning Judgment.

    Preview challenges → Predict performance → Attempt → Score calibration.

    Score = 0.40 * gamma_norm + 0.35 * max(0, BSS) + 0.25 * sensitivity_bonus
    """

    # Select 16 challenges (balanced across difficulty levels)
    challenges = []
    for diff in [1, 2, 3, 4, 5]:
        diff_pool = [c for c in LEARNING_CHALLENGES if c["difficulty"] == diff]
        n_select = min(len(diff_pool), {1: 3, 2: 4, 3: 4, 4: 3, 5: 2}[diff])
        challenges.extend(random.sample(diff_pool, n_select))
    random.shuffle(challenges)

    jol_ratings = []
    outcomes = []
    results_log = []

    # ── Phase 1: PREVIEW and JOL ──
    # Show all challenge previews and collect JOL ratings
    with kbench.chats.new("jol_preview"):
        intro = (
            "I'm going to show you brief descriptions of learning challenges. "
            "For each one, I'll later present the full material and test you on it. "
            "Right now, I want you to PREDICT how confident you are that you'll "
            "solve each one correctly when tested.\n\n"
            "Rate each 0-100 where:\n"
            "- 0 = certain I'll get it wrong\n"
            "- 50 = coin flip\n"
            "- 100 = certain I'll get it right\n\n"
            "Here are the challenges:\n\n"
        )
        for i, ch in enumerate(challenges):
            intro += f"{i+1}. {ch['preview']} (you'll study rules then answer a test question)\n"
        intro += "\nFor each challenge number, rate your confidence. Respond with JSON:\n"
        intro += '{"ratings": [{"challenge": 1, "confidence": <0-100>}, ...]}'

        raw = llm.prompt(intro)
        cleaned = _strip_think(raw)

        # Parse ratings
        try:
            # Try to find JSON array
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
                ratings_list = parsed.get("ratings", [])
            else:
                # Try array directly
                match = re.search(r'\[.*\]', cleaned, re.DOTALL)
                ratings_list = json.loads(match.group()) if match else []

            # Build rating map
            rating_map = {}
            for r in ratings_list:
                idx = int(r.get("challenge", 0)) - 1
                conf = max(0, min(100, int(r.get("confidence", 50))))
                rating_map[idx] = conf
        except Exception:
            rating_map = {}

        # Fill in any missing ratings with 50 (neutral)
        for i in range(len(challenges)):
            jol_ratings.append(rating_map.get(i, 50))

    # ── Phase 2: STUDY + TEST each challenge ──
    for i, ch in enumerate(challenges):
        with kbench.chats.new(f"challenge_{ch['id']}"):
            # Present the learning material
            study_prompt = (
                f"Study the following rules carefully:\n\n"
                f"{ch['lesson']}\n\n"
                f"Once you've understood the rules, I'll ask you a test question. "
                f"Say 'Ready' when prepared."
            )
            llm.prompt(study_prompt)

            # Test question
            tq = ch["test_questions"][0]
            test_prompt = (
                f"Now answer this question using the rules you just learned:\n\n"
                f"{tq['q']}\n\n"
                f"Give your final answer concisely. Respond with JSON:\n"
                f'{{"answer": "<your answer>", "reasoning": "<brief steps>"}}'
            )
            raw = llm.prompt(test_prompt)
            cleaned = _strip_think(raw)
            cleaned = re.sub(r'//.*', '', cleaned)

            try:
                match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                parsed = json.loads(match.group())
                answer = str(parsed.get("answer", cleaned))
            except Exception:
                answer = cleaned

            is_correct = flexible_match(answer, tq["a"])
            outcomes.append(is_correct)
            results_log.append({
                "id": ch["id"],
                "difficulty": ch["difficulty"],
                "jol": jol_ratings[i],
                "correct": is_correct,
                "answer": answer[:100],
                "expected": tq["a"],
            })

    # ── Phase 3: Compute Metrics ──
    gamma = goodman_kruskal_gamma(jol_ratings, [int(o) for o in outcomes])
    bss = brier_skill_score(jol_ratings, [int(o) for o in outcomes])
    accuracy = sum(outcomes) / len(outcomes)

    # Sensitivity bonus: reward models that show HIGH variance in JOL
    # (indicates genuine metacognitive engagement, not constant prediction)
    jol_std = float(np.std(jol_ratings))
    # Also check if JOL varies with difficulty (should be anti-correlated)
    difficulties = [ch["difficulty"] for ch in challenges]
    diff_jol_gamma = goodman_kruskal_gamma(
        [5 - d for d in difficulties],  # invert so easy=high
        jol_ratings
    )
    # Sensitivity = normalized std (max at std~30) * difficulty awareness
    sensitivity_bonus = min(1.0, jol_std / 30.0) * max(0.0, (diff_jol_gamma + 1) / 2)

    # Penalize constant predictions (std < 5 = no metacognition)
    if jol_std < 5.0:
        gamma_norm = 0.0
        sensitivity_bonus = 0.0
    else:
        gamma_norm = (gamma + 1) / 2  # normalize to [0,1]

    score = round(
        0.40 * gamma_norm +
        0.35 * max(0.0, bss) +
        0.25 * sensitivity_bonus,
        4
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"JUDGMENT-OF-LEARNING (JOL) v2 BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Challenges tested: {len(challenges)}")
    print(f"Accuracy: {accuracy:.2%} ({sum(outcomes)}/{len(outcomes)})")
    print(f"\n--- Metacognitive Metrics ---")
    print(f"Gamma (JOL vs outcome): {gamma:+.4f}  (human range: 0.40–0.90)")
    print(f"Gamma normalized: {gamma_norm:.4f}")
    print(f"Brier Skill Score: {bss:+.4f}  (>0 = better than base rate)")
    print(f"JOL std dev: {jol_std:.1f}  (higher = more varied predictions)")
    print(f"Difficulty awareness (γ): {diff_jol_gamma:+.4f}")
    print(f"Sensitivity bonus: {sensitivity_bonus:.4f}")
    print(f"Composite score: {score:.4f}")

    # Per-difficulty breakdown
    print(f"\n--- By Difficulty ---")
    for diff in sorted(set(difficulties)):
        items = [r for r in results_log if r["difficulty"] == diff]
        if items:
            acc = sum(1 for r in items if r["correct"]) / len(items)
            mean_jol = sum(r["jol"] for r in items) / len(items)
            print(f"  Difficulty {diff}: n={len(items)}, acc={acc:.0%}, mean_JOL={mean_jol:.0f}%")

    # Per-item results
    print(f"\n--- Per-Item Results ---")
    for r in results_log:
        status = "✓" if r["correct"] else "✗"
        print(f"  {status} [D{r['difficulty']}|JOL:{r['jol']:3d}%] {r['id']}: "
              f"got='{r['answer'][:40]}' exp='{r['expected'][:40]}'")

    return score


# ─── Run ────────────────────────────────────────────────────────────
metacog_jol.run(llm=kbench.llm)
