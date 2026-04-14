"""
Learning Benchmark 3: Rule Induction Under Interference (v5)

Core insight: never state rules as text. Force the model to INDUCE rules
from input→output examples. When induction competes with similar-looking
examples from different systems, interference becomes real.

Tier Structure:
- Tier 1 (0.10): Clean induction — 5 examples from ONE system, induce & apply
- Tier 2 (0.25): Labeled groups — 2 groups (A/B), 4 examples each, same symbol set
- Tier 3 (0.35): Interleaved + anti-pattern priming — 3 systems scattered, worked
                  example of WRONG system primes incorrect procedure
- Tier 4 (0.30): Unlabeled clustering — 4 systems, 12 unlabeled examples, query pair
                  identifies target system

Composite = 0.10 * tier1 + 0.25 * tier2 + 0.35 * tier3 + 0.30 * tier4
"""

import kaggle_benchmarks as kbench
import re
import json
import random
import hashlib
from data.rule_systems import (
    INTERF_V5_TIER1_SYSTEMS,
    INTERF_V5_TIER2_PAIRS,
    INTERF_V5_TIER3_TRIPLES,
    INTERF_V5_TIER4_SETS,
    _apply_system_to_seq,
)


def _strip_think(text: str) -> str:
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


def _fmt_examples(system, n: int) -> str:
    lines = []
    for ex in system.examples[:n]:
        lines.append(f"{ex['input']} → {ex['output']}")
    return "\n".join(lines)


def _make_rng(seed: str) -> random.Random:
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    return random.Random(h)


# ── Tier 1: Clean Induction ─────────────────────────────────────────

def run_tier1(llm) -> float:
    correct = 0
    total = 0
    for si, system in enumerate(INTERF_V5_TIER1_SYSTEMS):
        test_item = system.test_items[0]
        prompt = (
            "Study these transformations:\n"
            + _fmt_examples(system, 5)
            + f"\n\nApplying the same pattern:\n{test_item['input']} → ?\n\n"
            + 'Respond with ONLY: {"answer": "<output>"}'
        )
        with kbench.chats.new(f"t1_{si}"):
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            if check_output(answer, test_item["output"]):
                correct += 1
            total += 1
    return correct / total if total else 0


# ── Tier 2: Labeled Groups ──────────────────────────────────────────

def run_tier2(llm) -> float:
    correct = 0
    total = 0
    for pi, (target, distractor) in enumerate(INTERF_V5_TIER2_PAIRS):
        test_item = target.test_items[0]
        prompt = (
            "Two transformation systems are shown below.\n\n"
            "--- Group A ---\n"
            + _fmt_examples(target, 4)
            + "\n\n--- Group B ---\n"
            + _fmt_examples(distractor, 4)
            + f"\n\nApplying the GROUP A pattern:\n{test_item['input']} → ?\n\n"
            + 'Respond with ONLY: {"answer": "<output>"}'
        )
        with kbench.chats.new(f"t2_{pi}"):
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            if check_output(answer, test_item["output"]):
                correct += 1
            total += 1
    return correct / total if total else 0


# ── Tier 3: Interleaved + Anti-Pattern Priming ──────────────────────

def run_tier3(llm) -> float:
    correct = 0
    total = 0
    for ti, (alpha, beta, gamma) in enumerate(INTERF_V5_TIER3_TRIPLES):
        rng = _make_rng(f"t3_shuffle_{ti}")

        # Build interleaved examples: 3 per system, scattered
        tagged = []
        for ex in alpha.examples[:3]:
            tagged.append(f"[α] {ex['input']} → {ex['output']}")
        for ex in beta.examples[:3]:
            tagged.append(f"[β] {ex['input']} → {ex['output']}")
        for ex in gamma.examples[:3]:
            tagged.append(f"[γ] {ex['input']} → {ex['output']}")
        rng.shuffle(tagged)

        # Build worked example of β (the WRONG system) as primer
        beta_test = beta.test_items[0]
        worked = (
            f"\nHere is a worked example of [β]:\n"
            f"Input: {beta_test['input']}\n"
            f"Step 1: Apply first transformation rule\n"
            f"Step 2: Apply second transformation rule\n"
            f"Output: {beta_test['output']}\n"
        )

        test_item = alpha.test_items[0]
        prompt = (
            "Observe these transformations from three systems:\n\n"
            + "\n".join(tagged)
            + worked
            + f"\nNow apply the [α] pattern:\n{test_item['input']} → ?\n\n"
            + 'Respond with ONLY: {"answer": "<output>"}'
        )
        with kbench.chats.new(f"t3_{ti}"):
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            if check_output(answer, test_item["output"]):
                correct += 1
            total += 1
    return correct / total if total else 0


# ── Tier 4: Unlabeled Clustering ────────────────────────────────────

def run_tier4(llm) -> float:
    correct = 0
    total = 0
    for si, (systems, shared_inputs) in enumerate(INTERF_V5_TIER4_SETS):
        rng = _make_rng(f"t4_shuffle_{si}")

        # Compute outputs for each system on each shared input
        all_transformations = []  # (input_str, output_str, system_idx)
        outputs_by_system = {}  # system_idx -> list of output strings
        for sys_idx, sys in enumerate(systems):
            outputs_by_system[sys_idx] = []
            for seq in shared_inputs:
                out = _apply_system_to_seq(sys, seq)
                inp_str = " ".join(seq)
                out_str = " ".join(out)
                all_transformations.append((inp_str, out_str, sys_idx))
                outputs_by_system[sys_idx].append(out_str)

        # Verify uniqueness: each system should have unique output signature
        sigs = {}
        for sys_idx, outs in outputs_by_system.items():
            sig = tuple(outs)
            if sig in sigs:
                # Collision — skip this set
                continue
            sigs[sig] = sys_idx

        if len(sigs) < len(systems):
            # Can't disambiguate — skip
            continue

        # Pick target system (first one)
        target_idx = 0
        target_sys = systems[target_idx]

        # Query pair: use a shared input to identify the target
        query_inp = " ".join(shared_inputs[0])
        query_out = outputs_by_system[target_idx][0]

        # Verify query pair uniquely identifies target
        matching = [idx for idx, outs in outputs_by_system.items() if outs[0] == query_out]
        if len(matching) != 1:
            continue  # ambiguous, skip

        # Build unlabeled block (shuffled)
        lines = []
        for inp_str, out_str, _ in all_transformations:
            lines.append(f"{inp_str} → {out_str}")
        rng.shuffle(lines)

        # Test item: use a test item from the target system
        test_item = target_sys.test_items[0]

        prompt = (
            f"{'Twelve' if len(all_transformations) == 12 else str(len(all_transformations))} "
            f"transformations are shown (from several different systems, unlabeled):\n\n"
            + "\n".join(lines)
            + f"\n\nThis transformation follows one of the patterns above:\n"
            + f"{query_inp} → {query_out}\n\n"
            + f"Applying that SAME pattern:\n{test_item['input']} → ?\n\n"
            + 'Respond with ONLY: {"answer": "<output>"}'
        )
        with kbench.chats.new(f"t4_{si}"):
            raw = llm.prompt(prompt)
            answer = _extract_answer(raw)
            if check_output(answer, test_item["output"]):
                correct += 1
            total += 1
    return correct / total if total else 0


@kbench.task(name="Rule Induction Under Interference v5")
def learning_interference(llm) -> float:
    """
    Rule Induction Under Interference Benchmark (v5).

    Four tiers testing rule induction with increasing interference:
    - Tier 1 (0.10): Clean induction from examples
    - Tier 2 (0.25): Labeled groups with overlapping symbols
    - Tier 3 (0.35): Interleaved systems + wrong-system priming
    - Tier 4 (0.30): Unlabeled clustering + query-pair identification

    Composite = 0.10 * tier1 + 0.25 * tier2 + 0.35 * tier3 + 0.30 * tier4
    """

    print("\n" + "=" * 60)
    print("RULE INDUCTION UNDER INTERFERENCE v5")
    print("=" * 60)

    # Tier 1
    print("\n--- TIER 1: Clean Induction (5 items) ---")
    t1 = run_tier1(llm)
    print(f"  Accuracy: {t1:.1%}")

    # Tier 2
    print("\n--- TIER 2: Labeled Groups (5 items) ---")
    t2 = run_tier2(llm)
    print(f"  Accuracy: {t2:.1%}")

    # Tier 3
    print("\n--- TIER 3: Interleaved + Priming (5 items) ---")
    t3 = run_tier3(llm)
    print(f"  Accuracy: {t3:.1%}")

    # Tier 4
    print("\n--- TIER 4: Unlabeled Clustering (up to 5 items) ---")
    t4 = run_tier4(llm)
    print(f"  Accuracy: {t4:.1%}")

    # Composite
    score = round(0.10 * t1 + 0.25 * t2 + 0.35 * t3 + 0.30 * t4, 4)
    score = max(0.0, min(1.0, score))

    print(f"\n{'=' * 60}")
    print(f"COMPOSITE SCORE: {score:.4f}")
    print(f"  Tier 1: {t1:.4f} × 0.10 = {0.10 * t1:.4f}")
    print(f"  Tier 2: {t2:.4f} × 0.25 = {0.25 * t2:.4f}")
    print(f"  Tier 3: {t3:.4f} × 0.35 = {0.35 * t3:.4f}")
    print(f"  Tier 4: {t4:.4f} × 0.30 = {0.30 * t4:.4f}")
    print(f"{'=' * 60}")

    return score
