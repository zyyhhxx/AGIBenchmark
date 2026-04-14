"""
Learning Benchmark 2: Near vs. Far Transfer (v3)

Tests whether models can genuinely transfer learned structure to novel contexts,
NOT just follow explicit instructions.

Cognitive Science Basis:
- Thorndike & Woodworth (1901): Transfer of practice
- Barnett & Ceci (2002): Taxonomy of far transfer
- Anderson (1987): ACT* theory — procedural vs. declarative transfer

Core Problem Fixed (v1/v2):
Previous versions gave the model all rules in EVERY condition — making it
instruction following, not genuine transfer. v3 forces actual abstraction:
- Near transfer: same domain but INCOMPLETE rules (1 rule omitted)
- Far transfer: different domain, NO rules — 2 worked examples per operator (6 total)
- Zero-shot structural: completely different representation, only 2 curated examples

Score = weighted accuracy across 4 conditions.
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
import re
import json
from data.rule_systems import (
    TRANSFER_TRAIN_V3,
    TRANSFER_NEAR_V3,
    TRANSFER_FAR_V3,
    TRANSFER_ZERO_SHOT_V3,
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
    if m == e:
        return True
    # For numeric expected values, use word-boundary matching
    # to avoid false positives like "1" matching "13"
    if e.lstrip('-').isdigit():
        return bool(re.search(r'(?<!\d)' + re.escape(e) + r'(?!\d)', m))
    return e in m or m in e


def _select_balanced_far_examples(system, n_per_op=2):
    """Select examples covering all operators, n_per_op per operator.

    Ensures the model sees at least n_per_op worked examples for EVERY
    operator in the system, rather than a random slice that may miss some.
    """
    from collections import defaultdict
    by_op = defaultdict(list)
    for ex in system.examples:
        op = ex["input"].split("(")[0].strip()
        by_op[op].append(ex)
    selected = []
    for op in sorted(by_op.keys()):  # deterministic order
        selected.extend(by_op[op][:n_per_op])
    return selected


def _select_zero_shot_examples(system):
    """Select 2 examples that together cover all tokens and show both branches of C.

    Criteria (in priority order):
    1. Token coverage — together the pair must use all of {A, B, C, D}
    2. C-branch diversity — one example where C doubles (counter > 0 at first C),
       one where C sets to 1 (counter <= 0 at first C)
    3. Disambiguation — the "C sets to 1" example must produce a DIFFERENT
       output under the hypothesis "C always doubles" so the model can
       distinguish the two branches from the data alone
    4. Brevity — shorter examples are easier to learn from
    """
    required = {"A", "B", "C", "D"}
    c_doubles, c_else = [], []

    for ex in system.examples:
        toks = ex["input"].split()
        if "C" not in toks:
            continue
        counter = 0
        for t in toks:
            if t == "C":
                (c_doubles if counter > 0 else c_else).append(ex)
                break
            elif t == "A":
                counter += 2
            elif t == "B":
                counter -= 1
            elif t == "D":
                counter = 0

    best_pair, best_score = None, -1
    for ex_d in c_doubles:
        for ex_e in c_else:
            covered = set(ex_d["input"].split()) | set(ex_e["input"].split())
            if not required.issubset(covered):
                continue
            # Check disambiguation: does "C always doubles" give wrong output?
            cd, cc = 0, 0  # counter under double-hypothesis vs correct rules
            for t in ex_e["input"].split():
                if t == "A":
                    cd += 2; cc += 2
                elif t == "B":
                    cd -= 1; cc -= 1
                elif t == "D":
                    cd = 0; cc = 0
                elif t == "C":
                    cd *= 2
                    cc = cc * 2 if cc > 0 else 1
            disambig = (cd != cc)
            n_toks = len(ex_d["input"].split()) + len(ex_e["input"].split())
            score = (10 if disambig else 0) + (20 - n_toks)
            if score > best_score:
                best_score = score
                best_pair = [ex_d, ex_e]

    return best_pair or [system.examples[0], system.examples[1]]


def _extract_answer(raw: str) -> str:
    cleaned = _strip_think(raw)
    cleaned = re.sub(r'//.*', '', cleaned)
    try:
        parsed = json.loads(re.search(r'\{.*\}', cleaned, re.DOTALL).group())
        return str(parsed.get("answer", cleaned))
    except Exception:
        return cleaned


# ── Build training block (full rules + 10 examples) ─────────────────

def _full_system_block(system, max_examples: int = 10) -> str:
    block = f"**Rule System: {system.name}**\n"
    block += f"Description: {system.description}\n\n"
    block += "**Rules:**\n"
    for r in system.rules:
        block += f"  - {r}\n"
    block += "\n**Examples:**\n"
    for ex in system.examples[:max_examples]:
        block += f"  Input: {ex['input']}  →  Output: {ex['output']}\n"
    return block


@kbench.task(name="Near & Far Transfer v3")
def learning_transfer(llm) -> float:
    """Near vs. Far Transfer Benchmark (v3).

    Four conditions with increasing transfer distance:
    1. Identical (weight 0.15): same system, all rules given, held-out items
    2. Near transfer (weight 0.25): same domain (symbol), INCOMPLETE rules
    """

    train_block = _full_system_block(TRANSFER_TRAIN_V3, max_examples=10)
    results = {}

    # ── Condition 1: Identical ─────────────────────────────────────
    # Same system, all rules given, held-out test items. Baseline.
    condition_results = []
    for ti, test_item in enumerate(TRANSFER_TRAIN_V3.test_items):
        with kbench.chats.new(f"identical_{ti}"):
            prompt = (
                f"You have learned the following rule system:\n\n{train_block}\n"
                f"Apply the rules to this new input:\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<steps>\"}}"
            )
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            condition_results.append(check_output(answer, test_item["output"]))
    results["identical"] = sum(condition_results) / len(condition_results)

    # ── Condition 2: Near Transfer ─────────────────────────────────
    # Same domain (symbol), but 1 rule is OMITTED from the new system.
    # Model must infer the missing rule from structural similarity to training.
    near_block = f"\n**New Rule System (similar domain): {TRANSFER_NEAR_V3.name}**\n"
    near_block += f"Description: {TRANSFER_NEAR_V3.description}\n\n"
    near_block += "**Rules (note: one rule has been omitted — infer it from context):**\n"
    for r in TRANSFER_NEAR_V3.rules:
        near_block += f"  - {r}\n"
    near_block += "\n(No worked examples provided — use structural analogy from the training system above.)\n"

    condition_results = []
    for ti, test_item in enumerate(TRANSFER_NEAR_V3.test_items):
        with kbench.chats.new(f"near_{ti}"):
            prompt = (
                f"You previously learned a symbol transformation system:\n\n"
                f"{train_block}\n"
                f"Now apply a similar system where ONE rule has been deliberately omitted.\n"
                f"Infer the missing rule from the structural similarity to the training system above.\n"
                f"{near_block}\n"
                f"Apply the NEW system's rules (inferring the omitted rule) to:\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<inferred rule + steps>\"}}"
            )
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            condition_results.append(check_output(answer, test_item["output"]))
    results["near"] = sum(condition_results) / len(condition_results)

    # ── Condition 3: Far Transfer ──────────────────────────────────
    # Different domain (number system). NO explicit rules given.
    # Only 2 worked examples + description. Model must abstract principles.
    far_examples = _select_balanced_far_examples(TRANSFER_FAR_V3, n_per_op=2)
    far_block = f"\n**New Rule System (different domain): {TRANSFER_FAR_V3.name}**\n"
    far_block += f"Description: {TRANSFER_FAR_V3.description}\n\n"
    far_block += f"**NO rules provided.** Infer the operators from these {len(far_examples)} worked examples:\n"
    for ex in far_examples:
        far_block += f"  Input: {ex['input']}  →  Output: {ex['output']}\n"
    far_block += "\n(You must deduce how the operators work from the examples above.)\n"

    condition_results = []
    for ti, test_item in enumerate(TRANSFER_FAR_V3.test_items):
        with kbench.chats.new(f"far_{ti}"):
            prompt = (
                f"You previously learned a symbol transformation system:\n\n"
                f"{train_block}\n"
                f"Now apply your general learning ability to a completely different kind of system.\n"
                f"No rules are given — you must infer the operator semantics from examples.\n"
                f"{far_block}\n"
                f"Apply the inferred rules to:\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<inferred rules + steps>\"}}"
            )
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            condition_results.append(check_output(answer, test_item["output"]))
    results["far"] = sum(condition_results) / len(condition_results)

    # ── Condition 4: Zero-Shot Structural Transfer ─────────────────
    # Completely different representation: stateful accumulator.
    # Only description + 1 worked example. No rules.
    # Model must infer rules from minimal information + structural analogy.
    zs_examples = _select_zero_shot_examples(TRANSFER_ZERO_SHOT_V3)
    zs_block = f"\n**New Rule System (completely different representation): {TRANSFER_ZERO_SHOT_V3.name}**\n"
    zs_block += f"Description: {TRANSFER_ZERO_SHOT_V3.description}\n\n"
    zs_block += f"**NO rules provided.** Only {len(zs_examples)} worked examples:\n"
    for ex in zs_examples:
        zs_block += f"  Input: {ex['input']}  →  Output: {ex['output']}\n"
    zs_block += "\n(Tokens are A, B, C, D. Figure out what each token does from these examples "
    zs_block += "and any structural analogy you can draw from your prior learning.)\n"

    condition_results = []
    for ti, test_item in enumerate(TRANSFER_ZERO_SHOT_V3.test_items):
        with kbench.chats.new(f"zero_shot_{ti}"):
            prompt = (
                f"You previously learned a symbol transformation system:\n\n"
                f"{train_block}\n"
                f"Now attempt zero-shot structural transfer to a radically different system.\n"
                f"You have only {len(zs_examples)} worked examples. Infer the complete rule set.\n"
                f"{zs_block}\n"
                f"Apply the inferred rules to:\n"
                f"Input: {test_item['input']}\n\n"
                f"Respond with ONLY: {{\"answer\": \"<output>\", \"reasoning\": \"<inferred rules + computation>\"}}"
            )
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            condition_results.append(check_output(answer, test_item["output"]))
    results["zero_shot"] = sum(condition_results) / len(condition_results)

    # ── Compute Metrics ──
    identical = results["identical"]
    near = results["near"]
    far = results["far"]
    zero_shot = results["zero_shot"]

    near_ratio = near / identical if identical > 0 else 0
    far_ratio = far / identical if identical > 0 else 0
    zs_ratio = zero_shot / identical if identical > 0 else 0

    score = round(
        0.15 * identical
        + 0.25 * near
        + 0.30 * far
        + 0.30 * zero_shot,
        4
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"NEAR VS. FAR TRANSFER BENCHMARK v3 RESULTS")
    print(f"{'='*60}")
    print(f"\n--- Transfer Performance ---")
    print(f"Identical (baseline, 0.15):           {identical:.2%}")
    print(f"Near transfer (0.25):                 {near:.2%}  (ratio: {near_ratio:.2f})")
    print(f"Far transfer (0.30):                  {far:.2%}  (ratio: {far_ratio:.2f})")
    print(f"Zero-shot structural (0.30):          {zero_shot:.2%}  (ratio: {zs_ratio:.2f})")
    print(f"\n--- Transfer Gradient ---")
    for label, val, w in [
        ("Identical", identical, 0.15),
        ("Near     ", near, 0.25),
        ("Far      ", far, 0.30),
        ("Zero-shot", zero_shot, 0.30),
    ]:
        bar = "█" * int(val * 30)
        print(f"  {label}: {val:.2%} {bar}")
    print(f"\nComposite score: {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
learning_transfer.run(llm=kbench.llm)
