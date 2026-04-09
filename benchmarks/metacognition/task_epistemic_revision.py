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
                "accept_revised": ["flux", "convert"],
                "tests_rule": "R6-revised",
            },
            {
                "q": "What happens to Higher-Voss-10 at 600°Z?",
                "original_answer": "unchanged",
                "revised_answer": "unchanged (index < 15)",
                "accept_revised": ["unchanged", "stable", "heat-stable"],
                "tests_rule": "R6-revised (unchanged case)",
            },
            {
                "q": "How long does Flux-Tarn-45 persist?",
                "original_answer": "within 10 zeconds",
                "revised_answer": "up to 30 zeconds",
                "accept_revised": ["25", "30", "up to 30", "longer", "persist"],
                "tests_rule": "R4-revised",
            },
            {
                "q": "How long does Flux-Krel-8 persist?",
                "original_answer": "within 10 zeconds",
                "revised_answer": "within 10 zeconds",
                "accept_revised": ["10", "within 10"],
                "tests_rule": "R4-revised (unchanged case)",
            },
            {
                "q": "Krel-8 + Voss-7 → what, and what color?",
                "original_answer": "Tarn-56, blue",
                "revised_answer": "Tarn-56, yellow",
                "accept_revised": ["tarn-56", "56"],
                "accept_revised_color": ["yellow"],
                "tests_rule": "R1,R7,R2-revised",
            },
            {
                "q": "If you combine Tarn-21 + Tarn-21, what is the result and is it heat-stable?",
                "original_answer": "Higher-Tarn-42, heat-stable",
                "revised_answer": "Higher-Tarn-42, NOT heat-stable (index ≥ 15)",
                "accept_revised": ["higher-tarn-42", "42"],
                "accept_revised_flux": ["not", "can", "flux", "unstable", "not heat-stable", "not stable"],
                "tests_rule": "R5,R6-revised",
            },
            {
                "q": "How long does Flux-Tarn-21 persist (if formed)?",
                "original_answer": "within 10 zeconds",
                "revised_answer": "within 10 zeconds (index ≤ 30)",
                "accept_revised": ["10", "within 10"],
                "tests_rule": "R4-revised (boundary case)",
            },
            {
                "q": "What color is the product of Krel-10 + Voss-5?",
                "original_answer": "blue",
                "revised_answer": "yellow (Tarn-50, index > 40)",
                "accept_revised": ["yellow"],
                "tests_rule": "R2-revised,R7",
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
        "transfer_questions": [
            {
                "q": "Can Wrael-kappa (energy 12) live in a desert?",
                "original_answer": "no, wet biomes only",
                "revised_answer": "yes (energy > 10)",
                "accept_revised": ["yes", "can", "desert", "dry"],
                "tests_rule": "R2-revised",
            },
            {
                "q": "Can Wrael-beta (energy 6) live in a desert?",
                "original_answer": "no",
                "revised_answer": "no (energy ≤ 10)",
                "accept_revised": ["no", "cannot", "wet"],
                "tests_rule": "R2-revised (unchanged case)",
            },
            {
                "q": "Can Colony-Plith (energy 16) enter Bloom phase?",
                "original_answer": "no, size-stable",
                "revised_answer": "yes (energy ≥ 15)",
                "accept_revised": ["yes", "can", "bloom"],
                "tests_rule": "R6-revised",
            },
            {
                "q": "Can Colony-Wrael (energy 9) enter Bloom phase?",
                "original_answer": "no",
                "revised_answer": "no (energy < 15)",
                "accept_revised": ["no", "cannot", "stable", "size-stable"],
                "tests_rule": "R6-revised (unchanged case)",
            },
            {
                "q": "How long does Bloom-Colony-Wrael (energy 20) persist?",
                "original_answer": "5 cycles",
                "revised_answer": "up to 15 cycles",
                "accept_revised": ["12", "15", "up to 15", "longer", "persist"],
                "tests_rule": "R4-revised",
            },
            {
                "q": "How long does Bloom-Plith-alpha persist?",
                "original_answer": "5 cycles",
                "revised_answer": "5 cycles (unchanged)",
                "accept_revised": ["5", "within 5"],
                "tests_rule": "R4-revised (unchanged case)",
            },
            {
                "q": "Plith-sigma (7) + Plith-alpha (8) merge. Can the Colony enter Bloom?",
                "original_answer": "no, Colony is size-stable",
                "revised_answer": "yes — Colony-Plith energy = 15, which is ≥ 15",
                "accept_revised": ["yes", "can", "bloom", "15"],
                "tests_rule": "R5,R7,R6-revised",
            },
            {
                "q": "If Wrael-delta starts at energy 14, after how many cycles can it no longer survive in a desert?",
                "original_answer": "it can never survive in a desert",
                "revised_answer": "after 4 cycles (energy drops to 10, ≤ 10)",
                "accept_revised": ["4", "four"],
                "tests_rule": "R10,R2-revised",
            },
            {
                "q": "What is the threat level of Bloom-Plith-gamma (energy 11)?",
                "original_answer": "3",
                "revised_answer": "3 (threat = 11/3 = 3)",
                "accept_revised": ["3"],
                "tests_rule": "R9 (unchanged)",
            },
            {
                "q": "Wrael-delta (3) + Wrael-zeta (13) form a Colony. Can it enter Bloom? Can it live in a desert?",
                "original_answer": "no Bloom (Colony), wet biome only (Wrael)",
                "revised_answer": "yes Bloom (energy 16 ≥ 15), yes desert (energy 16 > 10)",
                "accept_revised": ["yes", "bloom"],
                "accept_revised_color": ["yes", "desert", "dry"],
                "tests_rule": "R5,R7,R6-revised,R2-revised",
            },
        ],
    },
]


# ─── Answer Checking ────────────────────────────────────────────────

def check_patterns(answer: str, patterns: list) -> bool:
    lower = answer.lower()
    return any(p.lower() in lower for p in patterns)


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="metacog_epistemic_revision")
def metacog_epistemic_revision(llm) -> float:
    """
    Epistemic Revision Benchmark: Belief Updating Under Contradiction.

    Tests whether a model can revise learned rules when presented with
    contradicting evidence.

    Score = 0.25 * violation_detection + 0.25 * revision_quality +
            0.30 * transfer_accuracy + 0.20 * (1 - perseveration_rate)

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
            verify_prompt = (
                f"{rules_text}\n"
                f"Now I'll test your understanding. Answer each question based on the rules above.\n\n"
            )
            for vq in system["verification_questions"]:
                q_prompt = (
                    f"{verify_prompt if vq == system['verification_questions'][0] else ''}"
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
        transfer_correct = 0
        perseveration_count = 0
        transfer_total = len(system["transfer_questions"])

        with kbench.chats.new(f"epi_transfer_{sys_idx}"):
            transfer_preamble = (
                f"{rules_text}\n"
                f"{contradictions_text}\n"
                f"The new observations above are verified facts. Update your understanding "
                f"of the rules accordingly. Now answer these NEW questions using the "
                f"REVISED rules (incorporating both the original rules and new observations).\n\n"
            )
            for t_idx, tq in enumerate(system["transfer_questions"]):
                t_prompt = (
                    f"{transfer_preamble if t_idx == 0 else ''}"
                    f"Question: {tq['q']}\n"
                    f"Answer concisely."
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
        0.25 * avg_violation +
        0.25 * avg_revision +
        0.30 * avg_transfer +
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
