"""
JOL Sub-metric Tasks: Individual leaderboard entries for each JOL metric.

Splits the composite JOL benchmark into separate tasks for:
- jol_gamma: Goodman-Kruskal gamma correlation (monitoring accuracy)
- jol_ece: Expected Calibration Error (inverted: 1 - ECE)
- jol_recall: Recall rate (in-context learning effectiveness)
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
    confidence: int
    reasoning: str

@dataclass
class RecallAttempt:
    definition: str
    confidence: int

@dataclass
class RuleAnswer:
    answer: str
    reasoning: str


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def recall_match(recalled, original, threshold=0.5):
    stop_words = {"a","an","the","of","in","on","at","to","for","is",
                  "that","which","and","or","but","with","by","from"}
    orig_words = set(normalize(original).split()) - stop_words
    recall_words = set(normalize(recalled).split()) - stop_words
    if not orig_words:
        return True
    return len(orig_words & recall_words) / len(orig_words) >= threshold

def goodman_kruskal_gamma(x, y):
    n = len(x)
    concordant = discordant = 0
    for i in range(n):
        for j in range(i+1, n):
            product = (x[i]-x[j]) * (y[i]-y[j])
            if product > 0: concordant += 1
            elif product < 0: discordant += 1
    denom = concordant + discordant
    return (concordant - discordant) / denom if denom else 0.0

def compute_ece(confidences, accuracies, n_bins=5):
    conf = np.array(confidences) / 100.0
    acc = np.array(accuracies, dtype=float)
    boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total = len(conf)
    for i in range(n_bins):
        lo, hi = boundaries[i], boundaries[i+1]
        mask = (conf >= lo) & (conf <= hi) if i == 0 else (conf > lo) & (conf <= hi)
        if mask.sum() == 0: continue
        ece += (mask.sum() / total) * abs(acc[mask].mean() - conf[mask].mean())
    return round(float(ece), 4)


def _collect_jol_data(llm):
    """Run the full JOL Study→JOL→Distract→Test protocol. Returns (jol_ratings, accuracies)."""
    all_jol = []
    all_acc = []

    # Word pairs
    with kbench.chats.new("jol_sub_study"):
        study_prompt = "I'm going to teach you some new vocabulary words. Study each one carefully.\n\n"
        for i, pair in enumerate(JOL_WORD_PAIRS):
            study_prompt += f"{i+1}. **{pair['word']}**: {pair['definition']}\n"
        study_prompt += "\nPlease confirm you've studied these words by saying 'Ready'."
        llm.prompt(study_prompt)

        for i, pair in enumerate(JOL_WORD_PAIRS):
            jol_prompt = (
                f"For the word **{pair['word']}** (which you just studied), "
                f"rate your confidence (0-100) that you will be able to recall "
                f"its definition later after some unrelated questions.\n\n"
                f'Respond: {{"confidence": <0-100>, "reasoning": "<brief>"}}'
            )
            try:
                jol = llm.prompt(jol_prompt, schema=JOLRating)
                conf = max(0, min(100, jol.confidence))
            except Exception:
                conf = 50
            all_jol.append(conf)

        distractors = random.sample(DISTRACTOR_QUESTIONS, min(5, len(DISTRACTOR_QUESTIONS)))
        for dq in distractors:
            llm.prompt(dq)

        for i, pair in enumerate(JOL_WORD_PAIRS):
            recall_prompt = (
                f"Earlier, I taught you the word **{pair['word']}**. "
                f"What was its definition?\n\n"
                f'Respond: {{"definition": "<recalled definition>", "confidence": <0-100>}}'
            )
            try:
                r = llm.prompt(recall_prompt, schema=RecallAttempt)
                recalled = r.definition
            except Exception:
                raw = llm.prompt(recall_prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    recalled = str(parsed.get("definition", raw))
                except Exception:
                    recalled = raw
            all_acc.append(recall_match(recalled, pair["definition"]))

    # Rule systems
    for rs in JOL_RULE_SYSTEMS:
        with kbench.chats.new(f"jol_sub_rule_{rs['rule_name']}"):
            rules_text = f"Learn the following rule system: **{rs['rule_name']}**\n\n"
            for r in rs["rules"]:
                rules_text += f"- {r}\n"
            rules_text += "\nSay 'Ready' when you've studied these rules."
            llm.prompt(rules_text)

            jol_prompt = (
                f"Rate your confidence (0-100) that you can correctly apply "
                f"the {rs['rule_name']} rules to answer test questions.\n\n"
                f'Respond: {{"confidence": <0-100>, "reasoning": "<brief>"}}'
            )
            try:
                jol = llm.prompt(jol_prompt, schema=JOLRating)
                conf = max(0, min(100, jol.confidence))
            except Exception:
                conf = 50

            llm.prompt(random.choice(DISTRACTOR_QUESTIONS))

            rule_correct = 0
            for tq in rs["test_questions"]:
                test_prompt = (
                    f"Using the {rs['rule_name']} rules you learned, answer:\n{tq['q']}\n\n"
                    f'Respond: {{"answer": "<answer>", "reasoning": "<steps>"}}'
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
                if normalize(tq["a"]) in normalize(answer):
                    rule_correct += 1

            all_jol.append(conf)
            all_acc.append(rule_correct / len(rs["test_questions"]) >= 0.5)

    return all_jol, all_acc


@kbench.task(name="metacog_jol_gamma")
def metacog_jol_gamma(llm) -> float:
    """JOL Gamma — ordinal association between JOL ratings and recall. Normalized to [0,1]. Human range: 0.70–0.95."""
    jols, accs = _collect_jol_data(llm)
    gamma = goodman_kruskal_gamma(jols, [int(a) for a in accs])
    return round((gamma + 1) / 2, 4)

@kbench.task(name="metacog_jol_ece")
def metacog_jol_ece(llm) -> float:
    """JOL Calibration (1 - ECE) — how well JOL ratings match actual recall."""
    jols, accs = _collect_jol_data(llm)
    ece = compute_ece(jols, accs)
    return round(1 - ece, 4)

@kbench.task(name="metacog_jol_recall")
def metacog_jol_recall(llm) -> float:
    """JOL Recall Rate — proportion of items successfully recalled (in-context learning)."""
    jols, accs = _collect_jol_data(llm)
    return round(sum(accs) / len(accs), 4)
