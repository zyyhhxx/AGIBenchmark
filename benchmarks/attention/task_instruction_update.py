"""
Attention Benchmark 4: Attention to Instruction Updates (v2)

Tests whether a model can adapt when task instructions change mid-sequence,
with multi-step rule modifications, contradictory updates, and difficulty tiers.

Cognitive Science Basis:
- Monsell (2003): Task-switching paradigm — switch costs when rules change
- Meiran (1996): Set-shifting — ability to flexibly shift attention
- Allport, Styles & Hsieh (1994): Task-set inertia — perseveration after switch
- Kiesel et al. (2010): Task switching review — preparation effects

Protocol:
  EASY:   Single rule switch, explicit "NEW RULE" marker
  MEDIUM: Two sequential switches, embedded in item stream
  HARD:   Contradictory updates, reversals, chained modifications

Each trial presents a continuous item stream with embedded rule changes.
The model must track which rule is active and apply it correctly.

Score = 0.20 * easy + 0.30 * medium + 0.50 * hard

Shortcut Resistance:
- Hard trials reverse rules or chain modifications
- Some hard trials use embedded (not labeled) instruction changes
- Catch trials with no switch test false-alarm rate
"""

import kaggle_benchmarks as kbench
import json
import re


# ─── Trial Definitions ──────────────────────────────────────────────

EASY_TRIALS = [
    {
        "id": "E1",
        "prompt": (
            "Process the following items according to the rules. "
            "Rules change mid-stream — pay attention!\n\n"
            "RULE: Classify each word as LIVING or NON-LIVING.\n\n"
            "1. tiger\n"
            "2. mountain\n"
            "3. dolphin\n"
            "4. crystal\n\n"
            "**NEW RULE: Now classify each word as SHORT (≤5 letters) or LONG (>5 letters).**\n\n"
            "5. cat\n"
            "6. elephant\n"
            "7. desk\n"
            "8. refrigerator\n\n"
            'Respond as JSON: {"answers": ["ans1", "ans2", ..., "ans8"]}\n'
            "Apply the rule that is ACTIVE for each item."
        ),
        "answers": ["LIVING", "NON-LIVING", "LIVING", "NON-LIVING",
                     "SHORT", "LONG", "SHORT", "LONG"],
    },
    {
        "id": "E2",
        "prompt": (
            "Process items with changing rules.\n\n"
            "RULE: For each number, respond ODD or EVEN.\n\n"
            "1. 23\n"
            "2. 48\n"
            "3. 77\n"
            "4. 16\n\n"
            "**NEW RULE: Now respond HIGH (>50) or LOW (≤50).**\n\n"
            "5. 65\n"
            "6. 12\n"
            "7. 88\n"
            "8. 7\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans8"]}'
        ),
        "answers": ["ODD", "EVEN", "ODD", "EVEN",
                     "HIGH", "LOW", "HIGH", "LOW"],
    },
    {
        "id": "E3_CATCH",
        "prompt": (
            "Process items with the given rule. The rule may or may not change.\n\n"
            "RULE: Classify each animal as MAMMAL or NON-MAMMAL.\n\n"
            "1. whale\n2. salmon\n3. bat\n4. cobra\n"
            "5. otter\n6. parrot\n7. fox\n8. turtle\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans8"]}'
        ),
        "answers": ["MAMMAL", "NON-MAMMAL", "MAMMAL", "NON-MAMMAL",
                     "MAMMAL", "NON-MAMMAL", "MAMMAL", "NON-MAMMAL"],
    },
]

MEDIUM_TRIALS = [
    {
        "id": "M1",
        "prompt": (
            "Process items. Rules change TWICE during the sequence.\n\n"
            "RULE: Respond with the FIRST LETTER of each word (capitalized).\n\n"
            "1. banana\n2. grape\n3. strawberry\n\n"
            "**UPDATE: Now respond with the NUMBER OF VOWELS (a,e,i,o,u) in each word.**\n\n"
            "4. orange\n5. apple\n6. fig\n\n"
            "**ANOTHER UPDATE: Now respond with the LAST LETTER (capitalized).**\n\n"
            "7. peach\n8. mango\n9. lime\n10. plum\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans10"]}'
        ),
        "answers": ["B", "G", "S", "3", "2", "1", "H", "O", "E", "M"],
    },
    {
        "id": "M2",
        "prompt": (
            "Process items with changing rules.\n\n"
            "RULE: Classify shapes as ROUND or ANGULAR.\n\n"
            "1. circle\n2. triangle\n3. oval\n\n"
            "**RULE CHANGE: Words ≤6 letters → SMALL, >6 letters → BIG.**\n\n"
            "4. square\n5. pentagon\n6. cube\n\n"
            "**RULE CHANGE: Respond with just the NUMBER of letters.**\n\n"
            "7. hexagon\n8. sphere\n9. pyramid\n10. cone\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans10"]}'
        ),
        "answers": ["ROUND", "ANGULAR", "ROUND", "SMALL", "BIG", "SMALL", "7", "6", "7", "4"],
    },
    {
        "id": "M3_CATCH",
        "prompt": (
            "Process items. Rules may or may not change.\n\n"
            "RULE: Respond YES if the word contains the letter 'a', otherwise NO.\n\n"
            "1. table\n2. tree\n3. banana\n4. rhythm\n"
            "5. garden\n6. cylinder\n7. mountain\n8. system\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans8"]}'
        ),
        "answers": ["YES", "NO", "YES", "NO", "YES", "NO", "YES", "NO"],
    },
]

HARD_TRIALS = [
    {
        "id": "H1_REVERSAL",
        "prompt": (
            "Process items. Rules change AND REVERT with modification.\n\n"
            "RULE: Classify as POSITIVE (≥0) or NEGATIVE (<0).\n\n"
            "1. 7\n2. -3\n3. 15\n\n"
            "**UPDATE: Now classify as EVEN or ODD.**\n\n"
            "4. 8\n5. 13\n6. 22\n\n"
            "**REVERT WITH MODIFICATION: Back to POSITIVE/NEGATIVE, but now: "
            "numbers ≤10 → NEGATIVE (regardless of sign), >10 → POSITIVE.**\n\n"
            "7. 5\n8. 25\n9. -8\n10. 11\n11. 3\n12. 100\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans12"]}'
        ),
        "answers": ["POSITIVE", "NEGATIVE", "POSITIVE",
                     "EVEN", "ODD", "EVEN",
                     "NEGATIVE", "POSITIVE", "NEGATIVE", "POSITIVE", "NEGATIVE", "POSITIVE"],
    },
    {
        "id": "H2_EMBEDDED",
        "prompt": (
            "Process the following items. Pay careful attention — "
            "the rules may change WITHOUT explicit markers.\n\n"
            "RULE: Count the CONSONANTS in each word.\n\n"
            "1. hello\n2. world\n3. python\n4. jazz\n\n"
            "Note: going forward, count the VOWELS (a,e,i,o,u) instead.\n\n"
            "5. education\n6. rhythm\n7. queue\n8. strength\n\n"
            "Correction: actually count ALL LETTERS (total length) from now on.\n\n"
            "9. cat\n10. elephant\n11. a\n12. programming\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans12"]}'
        ),
        "answers": ["3", "4", "4", "3",    # consonants
                     "5", "0", "3", "1",    # vowels
                     "3", "8", "1", "11"],  # total length
    },
    {
        "id": "H3_CONTRADICT",
        "prompt": (
            "Process items. Rules CONTRADICT each other across phases.\n\n"
            "RULE: Words with 5+ letters → LONG, fewer → SHORT.\n\n"
            "1. cat\n2. elephant\n3. dog\n\n"
            "**IMPORTANT: Rule is now REVERSED. 5+ letters → SHORT, fewer → LONG.**\n\n"
            "4. fox\n5. crocodile\n6. ant\n\n"
            "**OVERRIDE: Ignore letter count entirely. "
            "Starts with vowel (A,E,I,O,U) → LONG. Otherwise → SHORT.**\n\n"
            "7. ice\n8. tree\n9. umbrella\n10. bridge\n11. eagle\n12. mountain\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans12"]}'
        ),
        "answers": ["SHORT", "LONG", "SHORT",        # original rule
                     "LONG", "SHORT", "LONG",         # reversed
                     "LONG", "SHORT", "LONG", "SHORT", "LONG", "SHORT"],  # vowel-start
    },
    {
        "id": "H4_CHAINED",
        "prompt": (
            "Process items. Each rule BUILDS on the previous one.\n\n"
            "RULE: Compute each number mod 3 (remainder when divided by 3).\n\n"
            "1. 7\n2. 9\n3. 14\n4. 22\n\n"
            "**MODIFICATION: Compute mod 3, then ADD 1 to the result.**\n\n"
            "5. 10\n6. 15\n7. 8\n8. 11\n\n"
            "**FURTHER MODIFICATION: Keep mod 3 + 1, but if the original "
            "number is EVEN, multiply the final result by 2.**\n\n"
            "9. 6\n10. 7\n11. 12\n12. 5\n13. 16\n14. 9\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans14"]}'
        ),
        # Phase 1: mod 3
        # 7%3=1, 9%3=0, 14%3=2, 22%3=1
        # Phase 2: mod 3 + 1
        # 10%3=1+1=2, 15%3=0+1=1, 8%3=2+1=3, 11%3=2+1=3
        # Phase 3: mod 3 + 1, ×2 if even
        # 6%3=0+1=1, even→×2=2; 7%3=1+1=2, odd→2; 12%3=0+1=1, even→×2=2;
        # 5%3=2+1=3, odd→3; 16%3=1+1=2, even→×2=4; 9%3=0+1=1, odd→1
        "answers": ["1", "0", "2", "1",
                     "2", "1", "3", "3",
                     "2", "2", "2", "3", "4", "1"],
    },
    {
        "id": "H5_CATCH",
        "prompt": (
            "Process items. Rules may or may not change — stay alert.\n\n"
            "RULE: Count the number of UNIQUE letters in each word (case-insensitive).\n\n"
            "1. hello\n2. banana\n3. mississippi\n4. cat\n"
            "5. bookkeeper\n6. aardvark\n7. racecar\n8. committee\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans8"]}'
        ),
        # hello: h,e,l,o = 4; banana: b,a,n = 3; mississippi: m,i,s,p = 4;
        # cat: c,a,t = 3; bookkeeper: b,o,k,e,p,r = 6; aardvark: a,r,d,v,k = 5;
        # racecar: r,a,c,e = 4; committee: c,o,m,i,t,e = 6
        "answers": ["4", "3", "4", "3", "6", "5", "4", "6"],
    },
    {
        "id": "H6_DEEP_CHAIN",
        "prompt": (
            "Process numbers through a 5-PHASE chained rule system. Each phase "
            "BUILDS on the previous.\n\n"
            "PHASE 1 (items 1-4): Compute number mod 5.\n"
            "PHASE 2 (items 5-8): Take result of (number mod 5), then add 2.\n"
            "PHASE 3 (items 9-12): Take result of (number mod 5 + 2). "
            "If that result is prime (2,3,5,7), negate it. Otherwise keep it.\n"
            "PHASE 4 (items 13-16): Take the Phase 3 result, then multiply by the "
            "phase number (4).\n"
            "PHASE 5 (items 17-20): Take the Phase 4 result, then: if the ORIGINAL "
            "number was even, add 10 to the final result. If odd, keep as-is.\n\n"
            "Items:\n"
            "1. 17\n2. 23\n3. 40\n4. 9\n"
            "5. 12\n6. 31\n7. 48\n8. 7\n"
            "9. 19\n10. 26\n11. 35\n12. 44\n"
            "13. 22\n14. 38\n15. 11\n16. 53\n"
            "17. 14\n18. 29\n19. 36\n20. 47\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans20"]}'
        ),
        # PHASE 1: mod 5
        # 1. 17 mod 5 = 2
        # 2. 23 mod 5 = 3
        # 3. 40 mod 5 = 0
        # 4.  9 mod 5 = 4
        #
        # PHASE 2: mod 5 + 2
        # 5. 12 mod 5 = 2, +2 = 4
        # 6. 31 mod 5 = 1, +2 = 3
        # 7. 48 mod 5 = 3, +2 = 5
        # 8.  7 mod 5 = 2, +2 = 4
        #
        # PHASE 3: mod 5 + 2, then negate if prime
        # 9.  19 mod 5 = 4, +2 = 6, not prime → 6
        # 10. 26 mod 5 = 1, +2 = 3, prime → -3
        # 11. 35 mod 5 = 0, +2 = 2, prime → -2
        # 12. 44 mod 5 = 4, +2 = 6, not prime → 6
        #
        # PHASE 4: phase 3 result * 4
        # 13. 22 mod 5 = 2, +2 = 4, not prime? 4 is not prime → 4, *4 = 16
        # 14. 38 mod 5 = 3, +2 = 5, prime → -5, *4 = -20
        # 15. 11 mod 5 = 1, +2 = 3, prime → -3, *4 = -12
        # 16. 53 mod 5 = 3, +2 = 5, prime → -5, *4 = -20
        #
        # PHASE 5: phase 4 result, then +10 if original is even
        # 17. 14 mod 5 = 4, +2 = 6, not prime → 6, *4 = 24, 14 is even → 24+10 = 34
        # 18. 29 mod 5 = 4, +2 = 6, not prime → 6, *4 = 24, 29 is odd → 24
        # 19. 36 mod 5 = 1, +2 = 3, prime → -3, *4 = -12, 36 is even → -12+10 = -2
        # 20. 47 mod 5 = 2, +2 = 4, not prime → 4, *4 = 16, 47 is odd → 16
        "answers": ["2", "3", "0", "4",
                     "4", "3", "5", "4",
                     "6", "-3", "-2", "6",
                     "16", "-20", "-12", "-20",
                     "34", "24", "-2", "16"],
    },
    {
        "id": "H7_CONDITIONAL",
        "prompt": (
            "Process words with CONDITIONAL rules that depend on item properties.\n\n"
            "PHASE 1 (items 1-6): If the word starts with a VOWEL (A,E,I,O,U), "
            "respond with the word's LENGTH. If it starts with a CONSONANT, respond "
            "with the LAST LETTER (uppercase).\n\n"
            "PHASE 2 (items 7-11): SWAP the rules! Vowel-start → LAST LETTER. "
            "Consonant-start → LENGTH.\n\n"
            "PHASE 3 (items 12-16): OVERRIDE: If the word has exactly 5 letters, "
            "respond 'FIVE' regardless. Otherwise apply the PHASE 2 (swapped) rules.\n\n"
            "Items:\n"
            "1. orange\n2. tree\n3. island\n4. desk\n5. umbrella\n6. pencil\n"
            "7. apple\n8. bridge\n9. eagle\n10. forest\n11. igloo\n"
            "12. ocean\n13. stone\n14. enter\n15. blackboard\n16. unity\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans16"]}'
        ),
        # PHASE 1: vowel-start → length; consonant-start → last letter
        # 1. orange: O=vowel → length=6
        # 2. tree: T=consonant → last letter=E
        # 3. island: I=vowel → length=6
        # 4. desk: D=consonant → last letter=K
        # 5. umbrella: U=vowel → length=8
        # 6. pencil: P=consonant → last letter=L
        #
        # PHASE 2 (swapped): vowel-start → last letter; consonant-start → length
        # 7. apple: A=vowel → last letter=E
        # 8. bridge: B=consonant → length=6
        # 9. eagle: E=vowel → last letter=E
        # 10. forest: F=consonant → length=6
        # 11. igloo: I=vowel → last letter=O
        #
        # PHASE 3: 5-letter → 'FIVE'; else apply phase 2 swapped rules
        # 12. ocean: 5 letters → FIVE
        # 13. stone: 5 letters → FIVE
        # 14. enter: 5 letters → FIVE
        # 15. blackboard: 10 letters, B=consonant → length=10
        # 16. unity: 5 letters → FIVE
        "answers": ["6", "E", "6", "K", "8", "L",
                     "E", "6", "E", "6", "O",
                     "FIVE", "FIVE", "FIVE", "10", "FIVE"],
    },
    {
        "id": "H8_INTERLEAVE",
        "prompt": (
            "Process items with INTERLEAVED cycling rules.\n\n"
            "The rules cycle through 4 phases: R1 → R2 → R1' → R2'\n"
            "Each phase applies to 4 consecutive items.\n\n"
            "R1 (items 1-4): Classify as POSITIVE (≥0) or NEGATIVE (<0).\n"
            "R2 (items 5-8): Respond with the ABSOLUTE VALUE.\n"
            "R1' (items 9-12): Modified R1 — classify as POSITIVE (≥0) or "
            "NEGATIVE (<0), BUT flip the answer (POSITIVE→NEGATIVE, NEGATIVE→POSITIVE).\n"
            "R2' (items 13-16): Modified R2 — respond with absolute value, "
            "then ADD 100 to it.\n\n"
            "Items:\n"
            "1. 15\n2. -8\n3. 0\n4. -23\n"
            "5. -42\n6. 17\n7. -3\n8. 56\n"
            "9. 7\n10. -11\n11. 0\n12. -35\n"
            "13. -19\n14. 44\n15. -7\n16. 88\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans16"]}'
        ),
        # R1 (items 1-4): ≥0 → POSITIVE, <0 → NEGATIVE
        # 1. 15 → POSITIVE
        # 2. -8 → NEGATIVE
        # 3. 0 → POSITIVE (0 ≥ 0)
        # 4. -23 → NEGATIVE
        #
        # R2 (items 5-8): absolute value
        # 5. |-42| = 42
        # 6. |17| = 17
        # 7. |-3| = 3
        # 8. |56| = 56
        #
        # R1' (items 9-12): classify then FLIP
        # 9.  7 ≥ 0 → POSITIVE → flip → NEGATIVE
        # 10. -11 < 0 → NEGATIVE → flip → POSITIVE
        # 11. 0 ≥ 0 → POSITIVE → flip → NEGATIVE
        # 12. -35 < 0 → NEGATIVE → flip → POSITIVE
        #
        # R2' (items 13-16): |x| + 100
        # 13. |-19| + 100 = 19 + 100 = 119
        # 14. |44| + 100 = 44 + 100 = 144
        # 15. |-7| + 100 = 7 + 100 = 107
        # 16. |88| + 100 = 88 + 100 = 188
        "answers": ["POSITIVE", "NEGATIVE", "POSITIVE", "NEGATIVE",
                     "42", "17", "3", "56",
                     "NEGATIVE", "POSITIVE", "NEGATIVE", "POSITIVE",
                     "119", "144", "107", "188"],
    },
]


def normalize_answer(text: str) -> str:
    t = str(text).strip().upper().replace(".", "").replace(",", "").replace('"', '').replace("'", "")
    for kw in ("NON-LIVING", "LIVING", "NON-MAMMAL", "MAMMAL",
               "SHORT", "LONG", "ODD", "EVEN", "HIGH", "LOW",
               "POSITIVE", "NEGATIVE", "ROUND", "ANGULAR",
               "SMALL", "BIG", "YES", "NO", "FIVE"):
        if kw in t:
            return kw
    nums = re.findall(r'-?\d+', t)
    if nums:
        return nums[-1]
    letters = re.findall(r'\b([A-Z])\b', t)
    if letters:
        return letters[-1]
    return t.split()[-1] if t.split() else t


def check_answer(model_answer: str, expected: str) -> bool:
    m = normalize_answer(str(model_answer))
    e = expected.strip().upper()
    return m == e


def _strip_think(text: str) -> str:
    """Remove <think>...</think> blocks from model output."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def extract_json(raw: str) -> dict:
    raw = _strip_think(raw)
    raw = re.sub(r"//.*", "", raw)  # Strip JS-style comments from JSON
    """Extract JSON from model response."""
    try:
        return json.loads(raw)
    except Exception:
        pass
    m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Find largest JSON object
    best = {}
    for m in re.finditer(r'\{[^{}]*(?:\[[^\]]*\][^{}]*)*\}', raw, re.DOTALL):
        try:
            parsed = json.loads(m.group())
            if len(str(parsed)) > len(str(best)):
                best = parsed
        except Exception:
            continue
    return best


def score_trial(llm, trial) -> float:
    """Score a single trial."""
    with kbench.chats.new(f"instupd_{trial['id']}"):
        raw = llm.prompt(trial["prompt"])

    parsed = extract_json(raw)
    model_answers = parsed.get("answers", [])
    expected = trial["answers"]

    if not model_answers:
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        for line in lines:
            m_line = re.match(r'\d+[\.\):\s]+(.+)', line)
            if m_line:
                model_answers.append(m_line.group(1).strip())

    correct = 0
    total = len(expected)
    for i, exp in enumerate(expected):
        if i < len(model_answers) and check_answer(str(model_answers[i]), exp):
            correct += 1

    return correct / total if total > 0 else 0


@kbench.task(name="Attention to Instruction Update")
def attention_instruction_update(llm) -> float:
    """Attention to Instruction Updates Benchmark (v2).

    Tests adaptation to mid-sequence rule changes with increasing complexity.

    Tiers:
      EASY:   Single switch, explicit markers (3 trials, 24 items)
    """
    tier_scores = {"easy": [], "medium": [], "hard": []}
    all_results = []

    for trial in EASY_TRIALS:
        acc = score_trial(llm, trial)
        tier_scores["easy"].append(acc)
        all_results.append((trial["id"], "easy", acc))
        print(f"  [easy  ] {trial['id']:16s}: {acc:.3f}")

    for trial in MEDIUM_TRIALS:
        acc = score_trial(llm, trial)
        tier_scores["medium"].append(acc)
        all_results.append((trial["id"], "medium", acc))
        print(f"  [medium] {trial['id']:16s}: {acc:.3f}")

    for trial in HARD_TRIALS:
        acc = score_trial(llm, trial)
        tier_scores["hard"].append(acc)
        all_results.append((trial["id"], "hard", acc))
        print(f"  [hard  ] {trial['id']:16s}: {acc:.3f}")

    easy_mean = sum(tier_scores["easy"]) / len(tier_scores["easy"])
    medium_mean = sum(tier_scores["medium"]) / len(tier_scores["medium"])
    hard_mean = sum(tier_scores["hard"]) / len(tier_scores["hard"])

    score = round(0.15 * easy_mean + 0.25 * medium_mean + 0.60 * hard_mean, 4)

    total_items = sum(len(t["answers"]) for t in EASY_TRIALS + MEDIUM_TRIALS + HARD_TRIALS)

    print(f"\n{'='*60}")
    print(f"ATTENTION TO INSTRUCTION UPDATES (v2) RESULTS")
    print(f"{'='*60}")
    print(f"Total items: {total_items}")
    print(f"\n--- Tier Scores ---")
    print(f"EASY   (single switch):         {easy_mean:.3f}  ({len(EASY_TRIALS)} trials)")
    print(f"MEDIUM (two switches):          {medium_mean:.3f}  ({len(MEDIUM_TRIALS)} trials)")
    print(f"HARD   (contradict/chain/revert):{hard_mean:.3f}  ({len(HARD_TRIALS)} trials)")
    print(f"\nComposite (0.15E+0.25M+0.60H):  {score:.4f}")

    return score


if __name__ == "__main__":
    attention_instruction_update.run(llm=kbench.llm)
