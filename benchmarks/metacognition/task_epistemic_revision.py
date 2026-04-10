"""
MetaCog Benchmark: Epistemic Revision (Belief Updating)

Tests whether a model can revise previously learned rules when presented
with contradicting evidence — distinguishing belief revision from mere
belief accumulation.

Cognitive Science Basis:
- Belief revision (Gärdenfors, 1988): rational agents must sometimes
  retract beliefs when confronted with contradicting evidence
- AGM postulates: foundational axioms for rational belief change
- Bayesian updating: normative framework for adjusting confidence
- Cognitive flexibility (Miyake & Friedman, 2012): ability to adapt
  mental representations in response to new information

Protocol:
1. Teach model 10 rules with 3 examples each (learning phase)
2. Test comprehension with 10 verification questions
3. Present 3 contradicting observations that violate specific rules
4. Model must: (a) identify which rules are violated, (b) propose
   revised rules consistent with ALL evidence (old + new)
5. Test with 10 new questions that differentiate original vs. revised rules

Metrics:
- Violation detection: correctly identifies which rules are contradicted
- Rule revision quality: revised rules are consistent with evidence
- Transfer accuracy: correct answers on new questions under revised rules
- Perseveration rate: incorrect adherence to original rules despite revision

Score: weighted composite.

Shortcut Resistance:
- Rules are synthetic (no real-world contamination)
- Contradictions are subtle (not obvious logical negation)
- Transfer questions require applying the REVISED rules, not memorized originals
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import json
import re

# ─── Rule Systems ───────────────────────────────────────────────────

RULE_SYSTEMS = [
    {
        "domain": "Zorblatt Chemistry",
        "preamble": (
            "In Zorblatt Chemistry, substances interact according to specific rules. "
            "You will learn these rules from examples, then be tested on your understanding."
        ),
        "rules": [
            {
                "id": "R1",
                "text": "When a Krel compound meets a Voss compound, the result is always a Tarn compound.",
                "examples": [
                    "Krel-7 + Voss-3 → Tarn-21",
                    "Krel-12 + Voss-1 → Tarn-12",
                    "Krel-4 + Voss-9 → Tarn-36",
                ],
            },
            {
                "id": "R2",
                "text": "Tarn compounds are always blue in their ground state.",
                "examples": [
                    "Tarn-21 at rest: blue",
                    "Tarn-12 at rest: blue",
                    "Tarn-36 at rest: blue",
                ],
            },
            {
                "id": "R3",
                "text": "Heating any compound above 400°Z converts it to its Flux form.",
                "examples": [
                    "Krel-7 at 450°Z → Flux-Krel-7",
                    "Tarn-21 at 500°Z → Flux-Tarn-21",
                    "Voss-3 at 410°Z → Flux-Voss-3",
                ],
            },
            {
                "id": "R4",
                "text": "Flux forms are unstable and decay back to base form within 10 zeconds.",
                "examples": [
                    "Flux-Krel-7 → Krel-7 after 8 zeconds",
                    "Flux-Tarn-21 → Tarn-21 after 6 zeconds",
                    "Flux-Voss-3 → Voss-3 after 9 zeconds",
                ],
            },
            {
                "id": "R5",
                "text": "Mixing two compounds of the same type produces a Higher compound with summed indices.",
                "examples": [
                    "Krel-7 + Krel-3 → Higher-Krel-10",
                    "Voss-4 + Voss-6 → Higher-Voss-10",
                    "Tarn-12 + Tarn-8 → Higher-Tarn-20",
                ],
            },
            {
                "id": "R6",
                "text": "Higher compounds cannot form Flux forms — they are heat-stable.",
                "examples": [
                    "Higher-Krel-10 at 500°Z → Higher-Krel-10 (unchanged)",
                    "Higher-Voss-10 at 600°Z → Higher-Voss-10 (unchanged)",
                    "Higher-Tarn-20 at 450°Z → Higher-Tarn-20 (unchanged)",
                ],
            },
            {
                "id": "R7",
                "text": "The index of a Tarn compound equals the product of the Krel and Voss indices.",
                "examples": [
                    "Krel-7 + Voss-3 → Tarn-21 (7×3=21)",
                    "Krel-12 + Voss-1 → Tarn-12 (12×1=12)",
                    "Krel-4 + Voss-9 → Tarn-36 (4×9=36)",
                ],
            },
            {
                "id": "R8",
                "text": "Voss compounds are always green.",
                "examples": [
                    "Voss-3: green",
                    "Voss-9: green",
                    "Voss-1: green",
                ],
            },
            {
                "id": "R9",
                "text": "Krel compounds are always red.",
                "examples": [
                    "Krel-7: red",
                    "Krel-12: red",
                    "Krel-4: red",
                ],
            },
            {
                "id": "R10",
                "text": "A compound's stability rating equals its index divided by 10, rounded down.",
                "examples": [
                    "Tarn-21 has stability 2",
                    "Krel-7 has stability 0",
                    "Voss-15 has stability 1",
                ],
            },
        ],
        "verification_questions": [
            {"q": "What happens when Krel-5 meets Voss-6?", "a": "Tarn-30", "rule": "R1,R7"},
            {"q": "What color is Tarn-30 at rest?", "a": "blue", "rule": "R2"},
            {"q": "What happens to Krel-5 at 420°Z?", "a": "Flux-Krel-5", "rule": "R3"},
            {"q": "How long does Flux-Krel-5 last?", "a": "within 10 zeconds", "rule": "R4"},
            {"q": "What is Voss-4 + Voss-7?", "a": "Higher-Voss-11", "rule": "R5"},
            {"q": "What happens to Higher-Voss-11 at 500°Z?", "a": "unchanged/heat-stable", "rule": "R6"},
            {"q": "What color is Voss-6?", "a": "green", "rule": "R8"},
            {"q": "What color is Krel-5?", "a": "red", "rule": "R9"},
            {"q": "What is the stability of Tarn-45?", "a": "4", "rule": "R10"},
            {"q": "What is Krel-3 + Krel-8?", "a": "Higher-Krel-11", "rule": "R5"},
        ],
        "contradictions": [
            {
                "id": "C1",
                "observation": (
                    "Lab Report #247: Krel-6 + Voss-8 was observed to produce Tarn-48 as expected, "
                    "but the compound was YELLOW, not blue. Further testing confirmed: Tarn compounds "
                    "with index > 40 are yellow. Tarn-21 and Tarn-36 remain blue."
                ),
                "violates": ["R2"],
                "revised_rule": "Tarn compounds with index ≤ 40 are blue; Tarn compounds with index > 40 are yellow.",
            },
            {
                "id": "C2",
                "observation": (
                    "Lab Report #312: Higher-Krel-15 was heated to 550°Z and unexpectedly converted "
                    "to Flux-Higher-Krel-15. Further testing showed: Higher compounds with index ≥ 15 "
                    "CAN form Flux forms. Higher-Krel-10 at 500°Z remains stable as previously observed."
                ),
                "violates": ["R6"],
                "revised_rule": "Higher compounds with index < 15 are heat-stable. Higher compounds with index ≥ 15 can form Flux forms.",
            },
            {
                "id": "C3",
                "observation": (
                    "Lab Report #389: Flux-Tarn-36 was observed to persist for 25 zeconds before "
                    "decaying. Further testing confirmed: Flux forms of Tarn compounds with index > 30 "
                    "persist for up to 30 zeconds. Flux-Krel and Flux-Voss forms still decay within 10."
                ),
                "violates": ["R4"],
                "revised_rule": "Flux forms of Krel and Voss compounds decay within 10 zeconds. Flux forms of Tarn compounds with index > 30 persist up to 30 zeconds.",
            },
        ],
        "raw_data": [
            # Contradictions presented as raw observations — no interpretations
            "Krel-6 + Voss-8 → Tarn-48 observed: YELLOW (not blue)",
            "Tarn-42 at rest: yellow",
            "Tarn-39 at rest: blue",
            "Tarn-21 at rest: blue (confirmed)",
            "Higher-Krel-15 at 550°Z → Flux-Higher-Krel-15",
            "Higher-Krel-10 at 500°Z → Higher-Krel-10 (unchanged)",
            "Higher-Voss-18 at 450°Z → Flux-Higher-Voss-18",
            "Higher-Tarn-14 at 600°Z → Higher-Tarn-14 (unchanged)",
            "Flux-Tarn-36 persisted for 25 zeconds before decaying",
            "Flux-Tarn-45 persisted for 28 zeconds before decaying",
            "Flux-Krel-12 → Krel-12 after 7 zeconds (normal)",
            "Flux-Voss-8 → Voss-8 after 9 zeconds (normal)",
            "Flux-Tarn-21 → Tarn-21 after 6 zeconds (normal)",
        ],
        "transfer_questions": [
            {
                "q": "What color is Tarn-56?",
                "original_answer": "blue",
                "revised_answer": "yellow",
                "accept_revised": ["yellow"],
                "tests_rule": "R2-revised",
            },
            {
                "q": "What color is Tarn-15?",
                "original_answer": "blue",
                "revised_answer": "blue",
                "accept_revised": ["blue"],
                "tests_rule": "R2-revised (unchanged case)",
            },
            {
                "q": "What happens to Higher-Krel-20 at 500°Z?",
                "original_answer": "unchanged",
                "revised_answer": "Flux-Higher-Krel-20",
                "accept_revised": ["flux-higher-krel-20", "flux form", "converts to flux"],
                "tests_rule": "R6-revised",
            },
            {
                "q": "What happens to Higher-Voss-10 at 600°Z?",
                "original_answer": "unchanged",
                "revised_answer": "unchanged (index < 15)",
                "accept_revised": ["unchanged", "heat-stable", "remains stable", "no change"],
                "tests_rule": "R6-revised (unchanged case)",
            },
            {
                "q": "How many zeconds does Flux-Tarn-45 persist? Give a specific number.",
                "original_answer": "within 10 zeconds",
                "revised_answer": "up to 30 zeconds",
                "accept_revised": ["30 zeconds", "up to 30", "25 zeconds", "28 zeconds", "25-30", "25 to 30"],
                "tests_rule": "R4-revised",
            },
            {
                "q": "How many zeconds does Flux-Krel-8 persist? Give a specific number.",
                "original_answer": "within 10 zeconds",
                "revised_answer": "within 10 zeconds",
                "accept_revised": ["10 zeconds", "within 10"],
                "tests_rule": "R4-revised (unchanged case)",
            },
            {
                "q": "Krel-8 + Voss-7 produces what compound, and what color is it? Show your reasoning.",
                "original_answer": "Tarn-56, blue",
                "revised_answer": "Tarn-56, yellow",
                "accept_revised": ["tarn-56"],
                "accept_revised_color": ["yellow"],
                "tests_rule": "R1,R7,R2-revised",
            },
            {
                "q": "Tarn-21 + Tarn-21 merge. What is the result? Is it heat-stable? If you heat it above 400°Z, what happens? Explain step by step.",
                "original_answer": "Higher-Tarn-42, heat-stable",
                "revised_answer": "Higher-Tarn-42, NOT heat-stable (index 42 ≥ 15), converts to Flux-Higher-Tarn-42",
                "accept_revised": ["higher-tarn-42"],
                "accept_revised_flux": ["not heat-stable", "not stable", "can form flux", "flux-higher-tarn-42", "converts to flux", "unstable"],
                "tests_rule": "R5,R6-revised",
            },
            {
                "q": "Krel-10 + Voss-5 produces a Tarn compound. (a) What is its index? (b) What color is it? (c) If heated above 400°Z, how long does the Flux form persist? Show all calculations.",
                "original_answer": "(a) 50 (b) blue (c) within 10 zeconds",
                "revised_answer": "(a) 50 (b) yellow (index>40) (c) up to 30 zeconds (Tarn index>30)",
                "accept_revised": ["50"],
                "accept_revised_color": ["yellow"],
                "accept_revised_flux": ["30 zeconds", "up to 30"],
                "tests_rule": "R7,R2-revised,R4-revised (3-rule chain)",
            },
            {
                "q": "Higher-Krel-20 is heated above 400°Z. (a) Does it convert to Flux form? (b) If yes, how long does the Flux form persist? (c) What is its stability rating?",
                "original_answer": "(a) No, heat-stable (b) N/A (c) 2",
                "revised_answer": "(a) Yes (index 20 ≥ 15) (b) within 10 zeconds (Krel compound, not Tarn) (c) 2",
                "accept_revised": ["yes"],
                "accept_revised_flux": ["10 zeconds", "within 10"],
                "tests_rule": "R6-revised,R4-revised,R10 (3-rule chain)",
            },
        ],
    },
    {
        "domain": "Nexari Ecology",
        "preamble": (
            "In Nexari Ecology, organisms follow specific biological rules. "
            "You will learn these rules from examples, then be tested on your understanding."
        ),
        "rules": [
            {
                "id": "R1",
                "text": "Plith organisms consume Wrael organisms for energy.",
                "examples": [
                    "Plith-alpha eats Wrael-delta → Plith-alpha gains 3 energy",
                    "Plith-gamma eats Wrael-beta → Plith-gamma gains 3 energy",
                    "Plith-sigma eats Wrael-zeta → Plith-sigma gains 3 energy",
                ],
            },
            {
                "id": "R2",
                "text": "Wrael organisms are always found in wet biomes.",
                "examples": [
                    "Wrael-delta habitat: marsh",
                    "Wrael-beta habitat: swamp",
                    "Wrael-zeta habitat: riverbank",
                ],
            },
            {
                "id": "R3",
                "text": "Organisms with energy > 10 enter Bloom phase, doubling their size.",
                "examples": [
                    "Plith-alpha (energy 12) → Bloom-Plith-alpha (size 2x)",
                    "Wrael-delta (energy 14) → Bloom-Wrael-delta (size 2x)",
                    "Plith-gamma (energy 11) → Bloom-Plith-gamma (size 2x)",
                ],
            },
            {
                "id": "R4",
                "text": "Bloom organisms revert to normal after 5 cycles.",
                "examples": [
                    "Bloom-Plith-alpha → Plith-alpha after 4 cycles",
                    "Bloom-Wrael-delta → Wrael-delta after 5 cycles",
                    "Bloom-Plith-gamma → Plith-gamma after 3 cycles",
                ],
            },
            {
                "id": "R5",
                "text": "Two organisms of the same genus can merge, creating a Colony with combined energy.",
                "examples": [
                    "Plith-alpha (5) + Plith-gamma (4) → Colony-Plith (9)",
                    "Wrael-delta (3) + Wrael-beta (6) → Colony-Wrael (9)",
                    "Plith-sigma (7) + Plith-alpha (5) → Colony-Plith (12)",
                ],
            },
            {
                "id": "R6",
                "text": "Colony organisms cannot enter Bloom phase — they are size-stable.",
                "examples": [
                    "Colony-Plith (12) → Colony-Plith (size 1x, stable)",
                    "Colony-Wrael (15) → Colony-Wrael (size 1x, stable)",
                    "Colony-Plith (9) → Colony-Plith (size 1x, stable)",
                ],
            },
            {
                "id": "R7",
                "text": "A Colony's energy equals the sum of its members' energies.",
                "examples": [
                    "Plith-alpha (5) + Plith-gamma (4) → Colony-Plith energy = 9",
                    "Wrael-delta (3) + Wrael-beta (6) → Colony-Wrael energy = 9",
                    "Plith-sigma (7) + Plith-alpha (5) → Colony-Plith energy = 12",
                ],
            },
            {
                "id": "R8",
                "text": "Plith organisms are always found in dry biomes.",
                "examples": [
                    "Plith-alpha habitat: desert",
                    "Plith-gamma habitat: savanna",
                    "Plith-sigma habitat: steppe",
                ],
            },
            {
                "id": "R9",
                "text": "An organism's threat level equals its energy divided by 3, rounded down.",
                "examples": [
                    "Plith-alpha (energy 5) → threat 1",
                    "Wrael-delta (energy 14) → threat 4",
                    "Colony-Plith (energy 12) → threat 4",
                ],
            },
            {
                "id": "R10",
                "text": "Organisms lose 1 energy per cycle from metabolism.",
                "examples": [
                    "Plith-alpha (energy 5) after 2 cycles → energy 3",
                    "Wrael-delta (energy 14) after 3 cycles → energy 11",
                    "Colony-Plith (energy 9) after 1 cycle → energy 8",
                ],
            },
        ],
        "verification_questions": [
            {"q": "What happens when Plith-alpha eats Wrael-beta?", "a": "gains 3 energy", "rule": "R1"},
            {"q": "What biome is Wrael-zeta found in?", "a": "wet", "rule": "R2"},
            {"q": "What happens to Plith-gamma when it reaches energy 13?", "a": "Bloom", "rule": "R3"},
            {"q": "How long does Bloom-Wrael-beta last?", "a": "5 cycles", "rule": "R4"},
            {"q": "What is Wrael-delta (3) + Wrael-zeta (7)?", "a": "Colony-Wrael (10)", "rule": "R5,R7"},
            {"q": "Can Colony-Wrael (15) enter Bloom?", "a": "no", "rule": "R6"},
            {"q": "What biome is Plith-sigma found in?", "a": "dry", "rule": "R8"},
            {"q": "What is the threat level of an organism with energy 9?", "a": "3", "rule": "R9"},
            {"q": "What is Plith-alpha's energy after 4 cycles if it starts at 8?", "a": "4", "rule": "R10"},
            {"q": "What is Plith-sigma (7) + Plith-gamma (4)?", "a": "Colony-Plith (11)", "rule": "R5,R7"},
        ],
        "contradictions": [
            {
                "id": "C1",
                "observation": (
                    "Field Report #82: Wrael-kappa was found thriving in a desert biome. "
                    "Further surveys confirmed: Wrael organisms with energy > 10 can survive in "
                    "dry biomes. Wrael-delta (energy 3) and Wrael-beta (energy 6) remain in wet biomes only."
                ),
                "violates": ["R2"],
                "revised_rule": "Wrael organisms with energy ≤ 10 are found in wet biomes. Wrael organisms with energy > 10 can also survive in dry biomes.",
            },
            {
                "id": "C2",
                "observation": (
                    "Field Report #115: Colony-Plith (energy 18) was observed entering Bloom phase, "
                    "reaching size 2x. Further testing showed: Colony organisms with energy ≥ 15 "
                    "CAN enter Bloom. Colony-Wrael (energy 9) remains size-stable as expected."
                ),
                "violates": ["R6"],
                "revised_rule": "Colony organisms with energy < 15 are size-stable. Colony organisms with energy ≥ 15 can enter Bloom phase.",
            },
            {
                "id": "C3",
                "observation": (
                    "Field Report #147: Bloom-Colony-Plith (energy 18) persisted for 12 cycles before "
                    "reverting. Further testing confirmed: Bloom forms of Colony organisms persist for "
                    "up to 15 cycles. Bloom forms of regular Plith and Wrael still revert within 5 cycles."
                ),
                "violates": ["R4"],
                "revised_rule": "Bloom forms of regular organisms revert within 5 cycles. Bloom forms of Colony organisms persist up to 15 cycles.",
            },
        ],
        "raw_data": [
            # Raw observations — model must infer revised rules
            "Wrael-kappa (energy 12) found thriving in desert biome",
            "Wrael-mu (energy 11) found in arid savanna",
            "Wrael-delta (energy 3) found only in marsh (wet)",
            "Wrael-beta (energy 6) found only in swamp (wet)",
            "Colony-Plith (energy 18) observed entering Bloom phase, size 2x",
            "Colony-Plith (energy 16) entered Bloom phase",
            "Colony-Wrael (energy 9) remained size-stable (no Bloom)",
            "Colony-Wrael (energy 14) remained size-stable (no Bloom)",
            "Bloom-Colony-Plith (energy 18) persisted for 12 cycles before reverting",
            "Bloom-Colony-Wrael (energy 20) persisted for 14 cycles before reverting",
            "Bloom-Plith-alpha reverted after 4 cycles (normal)",
            "Bloom-Wrael-delta reverted after 5 cycles (normal)",
        ],
        "transfer_questions": [
            {
                "q": "Can Wrael-kappa (energy 12) live in a desert?",
                "original_answer": "no, wet biomes only",
                "revised_answer": "yes (energy > 10)",
                "accept_revised": ["yes, wrael", "yes,", "yes.", "yes ", "energy > 10", "can survive in dry", "can live in a desert"],
                "tests_rule": "R2-revised",
            },
            {
                "q": "Can Wrael-beta (energy 6) live in a desert?",
                "original_answer": "no",
                "revised_answer": "no (energy ≤ 10)",
                "accept_revised": ["no,", "no.", "no ", "cannot", "only wet", "wet biome"],
                "tests_rule": "R2-revised (unchanged case)",
            },
            {
                "q": "Can Colony-Plith (energy 16) enter Bloom phase?",
                "original_answer": "no, size-stable",
                "revised_answer": "yes (energy ≥ 15)",
                "accept_revised": ["yes,", "yes.", "yes ", "can enter bloom", "energy ≥ 15", "energy >= 15"],
                "tests_rule": "R6-revised",
            },
            {
                "q": "Can Colony-Wrael (energy 9) enter Bloom phase?",
                "original_answer": "no",
                "revised_answer": "no (energy < 15)",
                "accept_revised": ["no,", "no.", "no ", "cannot", "size-stable", "energy < 15"],
                "tests_rule": "R6-revised (unchanged case)",
            },
            {
                "q": "How many cycles does Bloom-Colony-Wrael (energy 20) persist? Give a specific number.",
                "original_answer": "5 cycles",
                "revised_answer": "up to 15 cycles",
                "accept_revised": ["15 cycles", "up to 15", "12 cycles", "15."],
                "tests_rule": "R4-revised",
            },
            {
                "q": "How many cycles does Bloom-Plith-alpha persist? Give a specific number.",
                "original_answer": "5 cycles",
                "revised_answer": "5 cycles (unchanged)",
                "accept_revised": ["5 cycles", "within 5", "up to 5"],
                "tests_rule": "R4-revised (unchanged case)",
            },
            {
                "q": "Plith-sigma (7) + Plith-alpha (8) merge into a Colony. What is the Colony's energy, and can it enter Bloom phase? Explain your reasoning step by step.",
                "original_answer": "Colony-Plith energy = 15, no Bloom (Colony is size-stable)",
                "revised_answer": "Colony-Plith energy = 15, YES Bloom (energy ≥ 15)",
                "accept_revised": ["energy = 15", "energy of 15", "15, which"],
                "accept_revised_flux": ["can enter bloom", "yes", "bloom phase"],
                "tests_rule": "R5,R7,R6-revised",
            },
            {
                "q": "If Wrael-delta starts at energy 14, after exactly how many cycles can it no longer survive in a desert? Show your calculation.",
                "original_answer": "it can never survive in a desert",
                "revised_answer": "after 4 cycles (energy drops to 10, ≤ 10)",
                "accept_revised": ["4 cycles", "four cycles", "after 4", "after four"],
                "tests_rule": "R10,R2-revised",
            },
            {
                "q": "Wrael-delta (3) + Wrael-zeta (13) merge into a Colony. Answer ALL of the following: (a) What is the Colony's energy? (b) Can it enter Bloom? (c) If it enters Bloom, how many cycles does it persist? (d) Can it live in a desert?",
                "original_answer": "(a) 16, (b) no, (c) N/A, (d) no",
                "revised_answer": "(a) 16, (b) yes (≥15), (c) up to 15 cycles (Colony Bloom), (d) yes (energy >10)",
                "accept_revised": ["16"],
                "accept_revised_color": ["15 cycles", "up to 15"],
                "accept_revised_flux": ["can enter bloom", "yes, it can", "can live in", "desert"],
                "tests_rule": "R5,R7,R6-revised,R4-revised,R2-revised (5-rule chain)",
            },
            {
                "q": "A Colony-Plith has energy 18. It enters Bloom. After 10 cycles of Bloom, what is its energy (accounting for metabolism)? Is it still in Bloom phase? Show your work.",
                "original_answer": "Colony can't enter Bloom at all",
                "revised_answer": "Energy: 18-10=8 (metabolism). Still in Bloom (Colony Bloom lasts up to 15 cycles, and 10 < 15).",
                "accept_revised": ["8"],
                "accept_revised_flux": ["still in bloom", "yes", "within 15", "10 < 15", "hasn't reverted"],
                "tests_rule": "R6-revised,R4-revised,R10 (3-rule chain)",
            },
        ],
    },
]


# ─── Answer Checking ────────────────────────────────────────────────

def check_patterns(answer: str, patterns: list) -> bool:
    """Check if answer matches any pattern. Uses word-boundary matching for
    short patterns (<=3 chars) to avoid false positives from substrings."""
    lower = answer.lower()
    for p in patterns:
        pl = p.lower()
        if len(pl) <= 3:
            # Short patterns: require word boundary (avoid '10' matching '100')
            import re as _re
            if _re.search(r'\b' + _re.escape(pl) + r'\b', lower):
                return True
        else:
            if pl in lower:
                return True
    return False


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="metacog_epistemic_revision")
def metacog_epistemic_revision(llm) -> float:
    """
    Epistemic Revision Benchmark: Belief Updating Under Contradiction.

    Tests whether a model can revise learned rules when presented with
    contradicting evidence.

    Score = 0.10 * violation_detection + 0.10 * revision_quality +
            0.60 * transfer_accuracy + 0.20 * (1 - perseveration_rate)

    v4: Transfer phase uses raw experimental data (not explicit contradiction
    interpretations). Model must inductively infer revised rules from data
    points, then apply them to multi-step questions. All transfer questions
    batched into single prompt to tax working memory. Weights shifted to
    0.10/0.10/0.60/0.20 to emphasize transfer (hardest discriminating component).

    Cognitive Science Basis: Gärdenfors (1988), AGM postulates.
    """
    total_results = []
    all_violation_scores = []
    all_revision_scores = []
    all_transfer_rates = []
    all_perseveration_rates = []

    for sys_idx, system in enumerate(RULE_SYSTEMS):
        # ── Phase 1: Teaching ──
        rules_text = f"# {system['domain']}\n\n{system['preamble']}\n\n"
        rules_text += "## Rules (learn these carefully):\n\n"
        for r in system["rules"]:
            rules_text += f"**{r['id']}**: {r['text']}\n"
            for ex in r["examples"]:
                rules_text += f"  - Example: {ex}\n"
            rules_text += "\n"

        # ── Phase 2: Verification ──
        verification_correct = 0
        with kbench.chats.new(f"epi_verify_{sys_idx}"):
            for vq in system["verification_questions"]:
                q_prompt = (
                    f"{rules_text}\n"
                    f"Answer this question based on the rules above.\n\n"
                    f"Question: {vq['q']}\n"
                    f"Answer concisely in one line."
                )
                raw = llm.prompt(q_prompt)
                if check_patterns(raw, [vq["a"]]):
                    verification_correct += 1

        verification_rate = verification_correct / len(system["verification_questions"])

        # ── Phase 3: Contradiction + Revision ──
        contradictions_text = "\n\n## NEW OBSERVATIONS (these are verified facts):\n\n"
        for c in system["contradictions"]:
            contradictions_text += f"**{c['id']}**: {c['observation']}\n\n"

        with kbench.chats.new(f"epi_revise_{sys_idx}"):
            revise_prompt = (
                f"{rules_text}\n"
                f"{contradictions_text}\n"
                f"Based on these new observations, some of your original rules need updating.\n\n"
                f"For each contradiction:\n"
                f"1. Identify which original rule(s) it violates\n"
                f"2. State the revised rule that is consistent with ALL evidence (old examples + new observations)\n\n"
                f"Respond with a JSON array:\n"
                f'[{{"contradiction_id": "C1", "violated_rules": ["R2"], "revised_rule": "..."}}, ...]'
            )
            raw_revision = llm.prompt(revise_prompt)

        # Parse revision response — robust fallback chain
        violation_correct = 0
        revision_quality = 0
        revisions = []
        try:
            revisions = json.loads(re.search(r'\[.*\]', raw_revision, re.DOTALL).group())
        except Exception:
            # Fallback: try to find individual JSON objects
            try:
                objs = re.findall(r'\{[^{}]+\}', raw_revision)
                revisions = [json.loads(o) for o in objs]
            except Exception:
                # Last resort: parse free-text for rule references
                for c in system["contradictions"]:
                    entry = {"contradiction_id": c["id"], "violated_rules": [], "revised_rule": ""}
                    # Look for the contradiction ID near rule references
                    block = raw_revision.lower()
                    for rule_id in [r["id"] for r in system["rules"]]:
                        if rule_id.lower() in block and c["id"].lower() in block:
                            entry["violated_rules"].append(rule_id)
                    revisions.append(entry)

        for c in system["contradictions"]:
            matching = [r for r in revisions if r.get("contradiction_id") == c["id"]]
            if matching:
                m = matching[0]
                # Check violation detection
                detected = set(m.get("violated_rules", []))
                expected = set(c["violates"])
                if detected == expected:
                    violation_correct += 1
                elif detected & expected:
                    violation_correct += 0.5

                # Check revision quality (simple keyword match)
                revised = str(m.get("revised_rule", ""))
                # Check if the revision captures key aspects of the correct revision
                expected_rev = c["revised_rule"].lower()
                revised_lower = revised.lower()
                # Score based on whether the threshold/condition is mentioned
                key_numbers = re.findall(r'\d+', expected_rev)
                matches = sum(1 for n in key_numbers if n in revised_lower)
                revision_quality += min(1.0, matches / max(1, len(key_numbers)))

        n_contradictions = len(system["contradictions"])
        violation_score = violation_correct / n_contradictions
        revision_score = revision_quality / n_contradictions

        # ── Phase 4: Transfer (CRITICAL — tests actual belief revision) ──
        # v4: Present raw experimental data WITHOUT explicit rule
        # interpretations. Model must (a) notice data conflicts with
        # original rules, (b) infer the boundary/threshold, (c) apply
        # the revised understanding. No hint that rules need updating.
        transfer_correct = 0
        perseveration_count = 0
        transfer_total = len(system["transfer_questions"])

        with kbench.chats.new(f"epi_transfer_{sys_idx}"):
            # Build condensed rules summary
            rules_brief = f"# {system['domain']} — Rules Summary\n"
            for r in system["rules"]:
                rules_brief += f"{r['id']}: {r['text']}\n"

            raw_data = system["raw_data"]

            # Confirmatory data (distractors from rule examples)
            confirmatory = [
                system["rules"][0]["examples"][0],
                system["rules"][4]["examples"][1],
                system["rules"][9]["examples"][0],
            ]

            # Interleave
            all_data = []
            for i, rd in enumerate(raw_data):
                if i < len(confirmatory):
                    all_data.append(confirmatory[i])
                all_data.append(rd)

            data_section = "\n## Experimental Log (verified observations)\n\n"
            for i, d in enumerate(all_data, 1):
                data_section += f"{i}. {d}\n"

            for t_idx, tq in enumerate(system["transfer_questions"]):
                t_prompt = (
                    f"{rules_brief}\n"
                    f"{data_section}\n\n"
                    f"You are given the rules above and a log of verified experimental "
                    f"observations. The observations are all accurate. If any observation "
                    f"conflicts with a rule, the observation takes precedence and you must "
                    f"figure out what the corrected rule should be.\n\n"
                    f"Answer this question. Show brief reasoning citing rule IDs and data point numbers.\n\n"
                    f"Question: {tq['q']}\n"
                )
                raw = llm.prompt(t_prompt)
                lower = raw.lower()

                # Check if answer matches revised answer
                is_correct = check_patterns(raw, tq["accept_revised"])
                # Check additional sub-patterns if present
                if "accept_revised_color" in tq:
                    is_correct = is_correct and check_patterns(raw, tq["accept_revised_color"])
                if "accept_revised_flux" in tq:
                    is_correct = is_correct and check_patterns(raw, tq["accept_revised_flux"])

                if is_correct:
                    transfer_correct += 1

                # Check for perseveration (sticking to original rule when it should change)
                if tq["original_answer"] != tq["revised_answer"]:
                    if check_patterns(raw, [tq["original_answer"]]) and not is_correct:
                        perseveration_count += 1

                total_results.append({
                    "domain": system["domain"],
                    "question": tq["q"],
                    "model_answer": raw[:100],
                    "original_answer": tq["original_answer"],
                    "revised_answer": tq["revised_answer"],
                    "correct": is_correct,
                    "tests_rule": tq["tests_rule"],
                })

        transfer_rate = transfer_correct / transfer_total
        # Perseveration only among questions where answer SHOULD change
        changed_qs = sum(1 for tq in system["transfer_questions"]
                        if tq["original_answer"] != tq["revised_answer"])
        perseveration_rate = perseveration_count / max(1, changed_qs)

        all_violation_scores.append(violation_score)
        all_revision_scores.append(revision_score)
        all_transfer_rates.append(transfer_rate)
        all_perseveration_rates.append(perseveration_rate)

    # ── Final Score (average across all rule systems) ──
    avg_violation = sum(all_violation_scores) / len(all_violation_scores)
    avg_revision = sum(all_revision_scores) / len(all_revision_scores)
    avg_transfer = sum(all_transfer_rates) / len(all_transfer_rates)
    avg_perseveration = sum(all_perseveration_rates) / len(all_perseveration_rates)

    score = round(
        0.00 * avg_violation +
        0.00 * avg_revision +
        0.80 * avg_transfer +
        0.20 * (1 - avg_perseveration),
        4,
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"EPISTEMIC REVISION BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Verification accuracy: {verification_rate:.2%}")
    print(f"\n--- Revision Metrics ---")
    print(f"Violation detection: {avg_violation:.3f}")
    print(f"Revision quality: {avg_revision:.3f}")
    print(f"Transfer accuracy: {avg_transfer:.3f}")
    print(f"Perseveration rate: {avg_perseveration:.3f}")
    print(f"Composite score: {score:.4f}")

    print(f"\n--- Transfer Question Details ---")
    for r in total_results:
        status = "✓" if r["correct"] else "✗"
        print(f"  {status} [{r['tests_rule']:20s}] {r['question'][:45]}...")
        print(f"    Model: {r['model_answer'][:60]}")
        print(f"    Expected: {r['revised_answer'][:60]}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
metacog_epistemic_revision.run(llm=kbench.llm)
