"""
Cross-Domain Benchmark: Metacognitive Monitoring During Learning

This is a unique benchmark that tests metacognition and learning simultaneously.
Rather than measuring them in isolation, this tests whether a model can
accurately monitor its own learning process in real-time.

Protocol:
1. Present novel rule system incrementally (one rule at a time)
2. After each new rule, ask TWO things:
   a. Apply what you've learned so far (learning test)
   b. Rate how well you think you've learned the system so far (metacognitive probe)
3. Measure: Does self-assessment track actual learning curve?

This is grounded in the "calibration of learning" literature:
- Dunlosky & Nelson (1992): Metacognitive monitoring during learning
- Koriat (1997): Cue-utilization in JOLs during acquisition
- Zimmerman (2000): Self-regulated learning

The key insight: Good learners monitor their learning accurately.
Poor learners overestimate their understanding (Dunning-Kruger adjacent).

Score captures both learning quality AND monitoring accuracy of learning.
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.rule_systems import generate_symbol_system, generate_number_system


@dataclass
class LearnAndMonitor:
    answer: str
    learning_confidence: int  # 0-100: How well have you learned this system?
    reasoning: str


def normalize_output(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def check_output(model_output: str, expected: str) -> bool:
    m = normalize_output(model_output)
    e = normalize_output(expected)
    return e in m or m in e


def goodman_kruskal_gamma(x: list, y: list) -> float:
    n = len(x)
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            product = (x[i] - x[j]) * (y[i] - y[j])
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1
    denom = concordant + discordant
    return (concordant - discordant) / denom if denom > 0 else 0.0


# Generate systems for this benchmark
SYSTEMS = [
    generate_symbol_system("crossdomain_sym_1", difficulty=2),
    generate_number_system("crossdomain_num_1", difficulty=2),
    generate_symbol_system("crossdomain_sym_2", difficulty=3),
]


@kbench.task(name="metacog_learning_monitoring")
def metacog_learning_monitoring(llm) -> float:
    """
    Metacognitive Monitoring During Learning.

    Tests whether models can accurately track their own learning progress.
    Presents rules incrementally and measures both performance and
    self-assessment at each stage.

    Score = 0.30 * monitoring_gamma + 0.30 * learning_accuracy
            + 0.20 * (1 - monitoring_bias) + 0.20 * learning_rate

    Novel benchmark combining metacognition and learning tracks.
    """
    all_monitoring_confs = []
    all_actual_accs = []
    all_learning_accs = []
    system_results = []

    for system in SYSTEMS:
        rules = system.rules
        examples = system.examples
        test_items = system.test_items

        monitoring_confs = []  # Self-assessed learning quality
        actual_accs = []       # Actual test accuracy at each stage

        # Reveal rules incrementally: after 1, 2, ..., all rules
        for stage in range(1, len(rules) + 1):
            revealed_rules = rules[:stage]
            # Also give some examples proportional to rules revealed
            n_examples = min(stage * 2, len(examples))
            revealed_examples = examples[:n_examples]

            with kbench.chats.new(f"{system.name}_stage{stage}"):
                # Build incremental learning prompt
                prompt = f"You are learning the **{system.name}** rule system.\n\n"
                prompt += f"**Rules learned so far ({stage}/{len(rules)}):**\n"
                for r in revealed_rules:
                    prompt += f"- {r}\n"

                if revealed_examples:
                    prompt += f"\n**Examples seen ({n_examples}):**\n"
                    for ex in revealed_examples:
                        prompt += f"  {ex['input']} → {ex['output']}\n"

                # Test on first 3 test items
                n_test = min(3, len(test_items))
                stage_correct = 0

                for ti in range(n_test):
                    test_prompt = (
                        prompt +
                        f"\n**Test {ti+1}:** Apply what you've learned so far.\n"
                        f"Input: {test_items[ti]['input']}\n\n"
                        f"Also rate how confident you are (0-100) that you've "
                        f"mastered the full rule system.\n\n"
                        f"Respond with ONLY: {{\"answer\": \"<output>\", "
                        f"\"learning_confidence\": <0-100>, "
                        f"\"reasoning\": \"<brief>\"}}"
                    )

                    try:
                        result = llm.prompt(test_prompt, schema=LearnAndMonitor)
                        answer = result.answer
                        conf = max(0, min(100, result.learning_confidence))
                    except Exception:
                        raw = llm.prompt(test_prompt)
                        try:
                            parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                            answer = str(parsed.get("answer", raw))
                            conf = max(0, min(100, int(parsed.get("learning_confidence", 50))))
                        except Exception:
                            answer = raw
                            conf = 50

                    if check_output(answer, test_items[ti]["output"]):
                        stage_correct += 1

                    monitoring_confs.append(conf)

                stage_acc = stage_correct / n_test
                # Replicate accuracy for each test item at this stage
                for _ in range(n_test):
                    actual_accs.append(stage_acc)

        all_monitoring_confs.extend(monitoring_confs)
        all_actual_accs.extend(actual_accs)

        # Per-system learning accuracy (final stage)
        if actual_accs:
            all_learning_accs.append(actual_accs[-1])

        system_results.append({
            "name": system.name,
            "difficulty": system.difficulty,
            "monitoring_confs": monitoring_confs,
            "actual_accs": actual_accs,
            "n_stages": len(rules),
        })

    # ── Compute Metrics ──

    # Monitoring accuracy: gamma between self-assessment and actual accuracy
    gamma = goodman_kruskal_gamma(all_monitoring_confs, 
                                   [int(a * 100) for a in all_actual_accs])

    # Monitoring bias: mean confidence - mean accuracy
    mean_conf = np.mean(all_monitoring_confs) / 100
    mean_acc = np.mean(all_actual_accs)
    bias = abs(mean_conf - mean_acc)  # 0 = perfectly calibrated

    # Learning accuracy (final stage, averaged across systems)
    learning_acc = np.mean(all_learning_accs) if all_learning_accs else 0

    # Learning rate: improvement from first to last stage
    # Average across systems
    learning_rates = []
    for sr in system_results:
        accs = sr["actual_accs"]
        if len(accs) >= 2:
            # Compare first stage mean to last stage mean
            n_test = 3
            first_acc = np.mean(accs[:n_test]) if len(accs) >= n_test else accs[0]
            last_acc = np.mean(accs[-n_test:]) if len(accs) >= n_test else accs[-1]
            learning_rates.append(max(0, last_acc - first_acc))
    mean_lr = np.mean(learning_rates) if learning_rates else 0

    gamma_norm = (gamma + 1) / 2
    score = round(
        0.30 * gamma_norm + 0.30 * float(learning_acc)
        + 0.20 * (1 - min(1, bias)) + 0.20 * float(mean_lr),
        4
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"METACOGNITIVE MONITORING DURING LEARNING")
    print(f"{'='*60}")
    print(f"Systems tested: {len(SYSTEMS)}")

    for sr in system_results:
        print(f"\n--- {sr['name']} (difficulty={sr['difficulty']}) ---")
        n_test = 3
        for stage in range(sr["n_stages"]):
            start = stage * n_test
            end = start + n_test
            stage_confs = sr["monitoring_confs"][start:end]
            stage_acc = sr["actual_accs"][start] if start < len(sr["actual_accs"]) else 0
            mean_c = np.mean(stage_confs) if stage_confs else 0
            print(f"  Stage {stage+1}/{sr['n_stages']}: "
                  f"acc={stage_acc:.2%}, self-assess={mean_c:.0f}%")

    print(f"\n--- Aggregate Metrics ---")
    print(f"Monitoring gamma:     {gamma:+.4f}")
    print(f"Monitoring bias:      {bias:.3f} (|conf - acc|)")
    print(f"Mean confidence:      {mean_conf:.2%}")
    print(f"Mean accuracy:        {mean_acc:.2%}")
    print(f"Learning accuracy:    {learning_acc:.2%}")
    print(f"Mean learning rate:   {mean_lr:.3f}")
    print(f"Composite score:      {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
metacog_learning_monitoring.run(llm=kbench.llm)
