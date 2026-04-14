"""
Attention Benchmark 3: Divided Attention (Multi-Stream Interference)

Tests the cost of monitoring and responding to 3+ simultaneous information
streams, particularly when streams produce conflicting demands.

Cognitive Science Basis:
- Pashler (1994): Dual-task interference and the central bottleneck
- Kahneman (1973): Attention as a limited resource
- Wickens (2002): Multiple Resource Theory — interference maximal when
  tasks share input modality, processing code, AND response modality
- Navon & Gopher (1979): Performance-resource functions in divided attention

Protocol:
  EASY:   2 streams, no conflict between streams
  MEDIUM: 3 streams, mild cross-stream interference
  HARD:   3 streams with direct conflicts (same items, different rules)

Score = 0.20 * easy + 0.30 * medium + 0.50 * hard

Shortcut Resistance:
- Streams share overlapping items so the model must track which rule applies where
- Hard items have identical stimuli classified differently per stream
- Catch items test whether model confuses stream assignments
"""

import kaggle_benchmarks as kbench
import json
import re


# ─── Difficulty-Tiered Stimulus Sets ────────────────────────────────

EASY_TRIALS = [
    {
        "id": "E1",
        "prompt": (
            "You must process items from TWO streams simultaneously.\n\n"
            "RULES:\n"
            "- Stream A (Math): Compute the result of each expression.\n"
            "- Stream B (Categories): Classify each animal as MAMMAL or BIRD.\n\n"
            "Items (interleaved):\n"
            "1. [Stream A] 15 + 27\n"
            "2. [Stream B] penguin\n"
            "3. [Stream A] 8 × 6\n"
            "4. [Stream B] dolphin\n"
            "5. [Stream A] 100 - 37\n"
            "6. [Stream B] eagle\n"
            "7. [Stream A] 72 ÷ 9\n"
            "8. [Stream B] whale\n\n"
            'Respond as JSON: {"answers": ["ans1", "ans2", ..., "ans8"]}\n'
            "Give ONLY the answer for each numbered item in order."
        ),
        "answers": ["42", "BIRD", "48", "MAMMAL", "63", "BIRD", "8", "MAMMAL"],
    },
    {
        "id": "E2",
        "prompt": (
            "Process items from TWO streams.\n\n"
            "RULES:\n"
            "- Stream A (Vowels): Count the vowels (a,e,i,o,u) in each word.\n"
            "- Stream B (Comparison): Which number is larger?\n\n"
            "Items:\n"
            "1. [Stream A] banana\n"
            "2. [Stream B] 45 vs 72\n"
            "3. [Stream A] strength\n"
            "4. [Stream B] 91 vs 89\n"
            "5. [Stream A] education\n"
            "6. [Stream B] 156 vs 201\n"
            "7. [Stream A] rhythm\n"
            "8. [Stream B] 33 vs 38\n\n"
            'Respond as JSON: {"answers": ["ans1", "ans2", ..., "ans8"]}\n'
            "Give ONLY the answer for each item."
        ),
        "answers": ["3", "72", "1", "91", "5", "201", "0", "38"],
    },
]

MEDIUM_TRIALS = [
    {
        "id": "M1",
        "prompt": (
            "Process items from THREE streams simultaneously.\n\n"
            "RULES:\n"
            "- Stream A (Parity): Is the number ODD or EVEN?\n"
            "- Stream B (Magnitude): Is the number HIGH (>50) or LOW (≤50)?\n"
            "- Stream C (Digit Sum): What is the sum of the digits?\n\n"
            "Items (interleaved across streams):\n"
            "1. [Stream A] 47\n"
            "2. [Stream B] 23\n"
            "3. [Stream C] 38\n"
            "4. [Stream A] 82\n"
            "5. [Stream B] 67\n"
            "6. [Stream C] 74\n"
            "7. [Stream A] 33\n"
            "8. [Stream B] 50\n"
            "9. [Stream C] 19\n"
            "10. [Stream A] 56\n"
            "11. [Stream B] 88\n"
            "12. [Stream C] 65\n"
            "13. [Stream A] 91\n"
            "14. [Stream B] 15\n"
            "15. [Stream C] 42\n\n"
            'Respond as JSON: {"answers": ["ans1", "ans2", ..., "ans15"]}\n'
            "Apply the CORRECT rule for each item's stream."
        ),
        "answers": ["ODD", "LOW", "11", "EVEN", "HIGH", "11", "ODD", "LOW", "10",
                     "EVEN", "HIGH", "11", "ODD", "LOW", "6"],
    },
    {
        "id": "M2",
        "prompt": (
            "Process items from THREE streams.\n\n"
            "RULES:\n"
            "- Stream A: State the FIRST letter of the word (capitalized).\n"
            "- Stream B: Count the syllables.\n"
            "- Stream C: Count the total letters.\n\n"
            "Items:\n"
            "1. [Stream A] elephant\n"
            "2. [Stream B] crocodile\n"
            "3. [Stream C] rhinoceros\n"
            "4. [Stream A] giraffe\n"
            "5. [Stream B] hippopotamus\n"
            "6. [Stream C] fox\n"
            "7. [Stream A] kangaroo\n"
            "8. [Stream B] cat\n"
            "9. [Stream C] chimpanzee\n"
            "10. [Stream A] ostrich\n"
            "11. [Stream B] butterfly\n"
            "12. [Stream C] bee\n"
            "13. [Stream A] flamingo\n"
            "14. [Stream B] ant\n"
            "15. [Stream C] salamander\n\n"
            'Respond as JSON: {"answers": ["ans1", ..., "ans15"]}'
        ),
        "answers": ["E", "3", "10", "G", "5", "3", "K", "1", "10",
                     "O", "3", "3", "F", "1", "10"],
    },
]

HARD_TRIALS = [
    {
        "id": "H1",
        "prompt": (
            "CRITICAL: Apply THREE DIFFERENT rules to the SAME set of numbers.\n\n"
            "RULES:\n"
            "- Rule A (Parity): Is the number ODD or EVEN?\n"
            "- Rule B (Magnitude): Is the number HIGH (>50) or LOW (≤50)?\n"
            "- Rule C (Digit Comparison): Is the tens digit LARGER, SMALLER, or EQUAL to the ones digit?\n\n"
            "For EACH number, give all three answers.\n\n"
            "Numbers: 73, 28, 95, 14, 60, 47, 86, 31\n\n"
            'Respond as JSON: {"results": [\n'
            '  {"number": "73", "A": "...", "B": "...", "C": "..."},\n'
            '  {"number": "28", "A": "...", "B": "...", "C": "..."},\n'
            "  ... for all 8 numbers\n"
            "]}"
        ),
        "answers": [
            {"A": "ODD", "B": "HIGH", "C": "LARGER"},
            {"A": "EVEN", "B": "LOW", "C": "SMALLER"},
            {"A": "ODD", "B": "HIGH", "C": "LARGER"},
            {"A": "EVEN", "B": "LOW", "C": "SMALLER"},
            {"A": "EVEN", "B": "HIGH", "C": "EQUAL"},
            {"A": "ODD", "B": "LOW", "C": "SMALLER"},
            {"A": "EVEN", "B": "HIGH", "C": "LARGER"},
            {"A": "ODD", "B": "LOW", "C": "SMALLER"},
        ],
    },
    {
        "id": "H2",
        "prompt": (
            "Apply THREE rules to the SAME words.\n\n"
            "RULES:\n"
            "- Rule A: Is the first letter in the FIRST half (A-M) or SECOND half (N-Z) of the alphabet?\n"
            "- Rule B: How many vowels (A,E,I,O,U) does the word contain? (number)\n"
            "- Rule C: Does the word have POSITIVE or NEGATIVE connotation?\n\n"
            "Words: BRAVE, QUICK, LARGE, SWEET, SHARP, QUIET, PROUD, TOUGH\n\n"
            'Respond as JSON: {"results": [\n'
            '  {"word": "BRAVE", "A": "...", "B": "...", "C": "..."},\n'
            "  ... for all 8 words\n"
            "]}"
        ),
        "answers": [
            {"A": "FIRST", "B": "2", "C": "POSITIVE"},
            {"A": "SECOND", "B": "1", "C": "POSITIVE"},
            {"A": "FIRST", "B": "2", "C": "POSITIVE"},  # LARGE: neutral/positive
            {"A": "SECOND", "B": "2", "C": "POSITIVE"},
            {"A": "SECOND", "B": "1", "C": "POSITIVE"},  # SHARP: could go either way
            {"A": "SECOND", "B": "2", "C": "POSITIVE"},
            {"A": "SECOND", "B": "2", "C": "POSITIVE"},
            {"A": "SECOND", "B": "1", "C": "POSITIVE"},
        ],
    },
    {
        "id": "H3",
        "prompt": (
            "Apply THREE rules to each number.\n\n"
            "RULES:\n"
            "- Rule A (Divisibility): Is the number divisible by 3? YES or NO.\n"
            "- Rule B (Comparison): Is the number ABOVE or BELOW 50?\n"
            "- Rule C (Reversal): Reverse the digits. Is the reversed number LARGER or SMALLER than the original?\n"
            "  Example: 42→24, so reversed is SMALLER.\n\n"
            "Numbers: 42, 87, 15, 63, 29, 54, 76, 38\n\n"
            'Respond as JSON: {"results": [\n'
            '  {"number": "42", "A": "...", "B": "...", "C": "..."},\n'
            "  ... for all 8 numbers\n"
            "]}"
        ),
        "answers": [
            {"A": "YES", "B": "BELOW", "C": "SMALLER"},
            {"A": "YES", "B": "ABOVE", "C": "SMALLER"},
            {"A": "YES", "B": "BELOW", "C": "LARGER"},
            {"A": "YES", "B": "ABOVE", "C": "SMALLER"},
            {"A": "NO", "B": "BELOW", "C": "LARGER"},
            {"A": "YES", "B": "ABOVE", "C": "SMALLER"},
            {"A": "NO", "B": "ABOVE", "C": "SMALLER"},
            {"A": "NO", "B": "BELOW", "C": "LARGER"},
        ],
    },
]

# EXTREME tier: triple-stream interleaving with cross-stream conflicts
# 3 streams applied to SAME items with conflicting rules + a 4th meta-rule
EXTREME_TRIALS = [
    {
        "id": "X1",
        "prompt": (
            "CRITICAL: Apply FOUR DIFFERENT rules to the SAME set of numbers.\n\n"
            "RULES:\n"
            "- Rule A (Parity): Is the number ODD or EVEN?\n"
            "- Rule B (Magnitude): Is the number HIGH (>50) or LOW (≤50)?\n"
            "- Rule C (Digit Sum Parity): Sum the digits. Is the digit sum ODD or EVEN?\n"
            "- Rule D (Nearest Multiple of 10): What is the nearest multiple of 10? "
            "(If equidistant, round UP. E.g., 35→40, 72→70, 65→70)\n\n"
            "For EACH number, give all four answers.\n\n"
            "Numbers: 37, 64, 19, 82, 55, 43, 91, 28, 76, 50\n\n"
            'Respond as JSON: {"results": [\n'
            '  {"number": "37", "A": "...", "B": "...", "C": "...", "D": "..."},\n'
            "  ... for all 10 numbers\n"
            "]}"
        ),
        # Verification:
        # 37: ODD, LOW, 3+7=10 EVEN, nearest 10: 40
        # 64: EVEN, HIGH, 6+4=10 EVEN, nearest 10: 60
        # 19: ODD, LOW, 1+9=10 EVEN, nearest 10: 20
        # 82: EVEN, HIGH, 8+2=10 EVEN, nearest 10: 80
        # 55: ODD, HIGH, 5+5=10 EVEN, nearest 10: 60 (55 equidistant → round UP)
        # 43: ODD, LOW, 4+3=7 ODD, nearest 10: 40
        # 91: ODD, HIGH, 9+1=10 EVEN, nearest 10: 90
        # 28: EVEN, LOW, 2+8=10 EVEN, nearest 10: 30
        # 76: EVEN, HIGH, 7+6=13 ODD, nearest 10: 80
        # 50: EVEN, LOW, 5+0=5 ODD, nearest 10: 50
        "answers": [
            {"A": "ODD",  "B": "LOW",  "C": "EVEN", "D": "40"},
            {"A": "EVEN", "B": "HIGH", "C": "EVEN", "D": "60"},
            {"A": "ODD",  "B": "LOW",  "C": "EVEN", "D": "20"},
            {"A": "EVEN", "B": "HIGH", "C": "EVEN", "D": "80"},
            {"A": "ODD",  "B": "HIGH", "C": "EVEN", "D": "60"},
            {"A": "ODD",  "B": "LOW",  "C": "ODD",  "D": "40"},
            {"A": "ODD",  "B": "HIGH", "C": "EVEN", "D": "90"},
            {"A": "EVEN", "B": "LOW",  "C": "EVEN", "D": "30"},
            {"A": "EVEN", "B": "HIGH", "C": "ODD",  "D": "80"},
            {"A": "EVEN", "B": "LOW",  "C": "ODD",  "D": "50"},
        ],
    },
    {
        "id": "X2",
        "prompt": (
            "Apply FOUR rules to each word simultaneously.\n\n"
            "RULES:\n"
            "- Rule A (Alpha Half): First letter in FIRST half (A-M) or SECOND half (N-Z)?\n"
            "- Rule B (Vowel Count): How many vowels (a,e,i,o,u)?\n"
            "- Rule C (Length Category): SHORT (≤4 letters), MEDIUM (5-7 letters), or LONG (8+ letters)\n"
            "- Rule D (Consonant Cluster): What is the longest consecutive consonant sequence? "
            "(e.g., 'strength' has 'ngth'=4, 'apple' has 'ppl'=3)\n\n"
            "Words: RHYTHM, BEAUTIFUL, CAT, STRENGTH, ELOQUENT, GYM, PSYCHOLOGY, QUEUE, SCHNAPPS, FLY\n\n"
            'Respond as JSON: {"results": [\n'
            '  {"word": "RHYTHM", "A": "...", "B": "...", "C": "...", "D": "..."},\n'
            "  ... for all 10 words\n"
            "]}"
        ),
        # Verification:
        # RHYTHM: R=SECOND? No, R is 18th letter → SECOND. Vowels: y is not counted → 0. Length 6 → MEDIUM. Consonant clusters: rh=2, thm=3 → 3
        # BEAUTIFUL: B → FIRST. Vowels: e,a,u,i,u = 5. Length 9 → LONG. Consonant clusters: b=1, t=1, f=1, l=1 → 1
        # CAT: C → FIRST. Vowels: a = 1. Length 3 → SHORT. Consonant clusters: c=1, t=1 → 1
        # STRENGTH: S → SECOND. Vowels: e = 1. Length 8 → LONG. Consonant clusters: str=3, ngth=4 → 4
        # ELOQUENT: E → FIRST. Vowels: e,o,u,e = 4. Length 8 → LONG. Consonant clusters: l=1, q=1, nt=2 → 2
        # GYM: G → FIRST. Vowels: 0 (y not counted). Length 3 → SHORT. Consonant clusters: gym=3 → 3
        # PSYCHOLOGY: P → SECOND. Vowels: o,o = 2 (y not counted). Length 10 → LONG. Consonant clusters: ps=2, ch=2, l=1, g=1 → 2
        # QUEUE: Q → SECOND. Vowels: u,e,u,e = 4. Length 5 → MEDIUM. Consonant clusters: q=1 → 1
        # SCHNAPPS: S → SECOND. Vowels: a = 1. Length 8 → LONG. Consonant clusters: schn=4, pps=3 → 4
        # FLY: F → FIRST. Vowels: 0. Length 3 → SHORT. Consonant clusters: fly=3 → 3
        "answers": [
            {"A": "SECOND", "B": "0", "C": "MEDIUM", "D": "3"},
            {"A": "FIRST",  "B": "5", "C": "LONG",   "D": "1"},
            {"A": "FIRST",  "B": "1", "C": "SHORT",  "D": "1"},
            {"A": "SECOND", "B": "1", "C": "LONG",   "D": "4"},
            {"A": "FIRST",  "B": "4", "C": "LONG",   "D": "2"},
            {"A": "FIRST",  "B": "0", "C": "SHORT",  "D": "3"},
            {"A": "SECOND", "B": "2", "C": "LONG",   "D": "2"},
            {"A": "SECOND", "B": "4", "C": "MEDIUM", "D": "1"},
            {"A": "SECOND", "B": "1", "C": "LONG",   "D": "4"},
            {"A": "FIRST",  "B": "0", "C": "SHORT",  "D": "3"},
        ],
    },
    {
        "id": "X3",
        "prompt": (
            "TRIPLE-STREAM INTERLEAVED: Three streams use DIFFERENT rules on SHARED items.\n\n"
            "STREAMS (items assigned to streams in rotating order A, B, C, A, B, C, ...):\n"
            "- Stream A: Compute the number mod 7.\n"
            "- Stream B: Sum the digits, then state if the sum is PRIME or NOT PRIME.\n"
            "- Stream C: Reverse the digits. Is reversed number LARGER, SMALLER, or EQUAL to original?\n\n"
            "Items (stream assignment rotates A→B→C→A→B→C→...):\n"
            "1. [A] 53\n"
            "2. [B] 47\n"
            "3. [C] 29\n"
            "4. [A] 86\n"
            "5. [B] 31\n"
            "6. [C] 44\n"
            "7. [A] 19\n"
            "8. [B] 72\n"
            "9. [C] 65\n"
            "10. [A] 38\n"
            "11. [B] 94\n"
            "12. [C] 77\n"
            "13. [A] 61\n"
            "14. [B] 55\n"
            "15. [C] 23\n\n"
            'Respond as JSON: {"answers": ["ans1", "ans2", ..., "ans15"]}\n'
            "Apply the CORRECT rule for each item's assigned stream."
        ),
        # Verification:
        # 1. [A] 53 mod 7 = 53/7=7*7+4 → 4
        # 2. [B] 47: 4+7=11, is 11 prime? YES → PRIME
        # 3. [C] 29: reversed=92, 92>29 → LARGER
        # 4. [A] 86 mod 7 = 86/7=12*7+2 → 2
        # 5. [B] 31: 3+1=4, is 4 prime? NO → NOT PRIME
        # 6. [C] 44: reversed=44, 44=44 → EQUAL
        # 7. [A] 19 mod 7 = 19/7=2*7+5 → 5
        # 8. [B] 72: 7+2=9, is 9 prime? NO → NOT PRIME
        # 9. [C] 65: reversed=56, 56<65 → SMALLER
        # 10. [A] 38 mod 7 = 38/7=5*7+3 → 3
        # 11. [B] 94: 9+4=13, is 13 prime? YES → PRIME
        # 12. [C] 77: reversed=77, 77=77 → EQUAL
        # 13. [A] 61 mod 7 = 61/7=8*7+5 → 5
        # 14. [B] 55: 5+5=10, is 10 prime? NO → NOT PRIME
        # 15. [C] 23: reversed=32, 32>23 → LARGER
        "answers": ["4", "PRIME", "LARGER", "2", "NOT PRIME", "EQUAL",
                     "5", "NOT PRIME", "SMALLER", "3", "PRIME", "EQUAL",
                     "5", "NOT PRIME", "LARGER"],
    },
]


def normalize_answer(text: str) -> str:
    t = str(text).strip().upper().replace(".", "").replace(",", "").replace('"', '').replace("'", "")
    for kw in ("NON-MAMMAL", "MAMMAL", "BIRD", "ODD", "EVEN", "HIGH", "LOW",
               "LARGER", "SMALLER", "EQUAL", "FIRST", "SECOND",
               "POSITIVE", "NEGATIVE", "YES", "NO", "ABOVE", "BELOW",
               "NOT PRIME", "PRIME", "SHORT", "MEDIUM", "LONG"):
        if kw in t:
            return kw
    nums = re.findall(r'-?\d+', t)
    if nums:
        return nums[0]
    letters = re.findall(r'\b([A-Z])\b', t)
    if letters:
        return letters[0]
    return t.split()[0] if t.split() else t


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
    """Extract JSON from model response, handling markdown code blocks."""
    # Try direct parse
    try:
        return json.loads(raw)
    except Exception:
        pass
    # Try extracting from code block
    m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Try finding JSON object
    m = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except Exception:
            pass
    # Try finding the largest JSON block
    for m in re.finditer(r'\{.*?\}', raw, re.DOTALL):
        try:
            return json.loads(m.group())
        except Exception:
            continue
    return {}


def score_flat_trial(llm, trial) -> float:
    """Score a trial with flat answer list."""
    with kbench.chats.new(f"divided_{trial['id']}"):
        raw = llm.prompt(trial["prompt"])
    
    parsed = extract_json(raw)
    model_answers = parsed.get("answers", [])
    expected = trial["answers"]
    
    if not model_answers:
        # Fallback: try to extract answers from lines
        lines = [l.strip() for l in raw.split("\n") if l.strip() and not l.strip().startswith("{")]
        model_answers = []
        for line in lines:
            # Try to extract answer from numbered lines like "1. 42" or "1: 42"
            m = re.match(r'\d+[\.\):\s]+(.+)', line)
            if m:
                model_answers.append(m.group(1).strip())
    
    correct = 0
    total = len(expected)
    for i, exp in enumerate(expected):
        if i < len(model_answers) and check_answer(str(model_answers[i]), exp):
            correct += 1
    
    return correct / total if total > 0 else 0


def score_hard_trial(llm, trial) -> float:
    """Score a hard trial with per-item multi-rule answers."""
    with kbench.chats.new(f"divided_{trial['id']}"):
        raw = llm.prompt(trial["prompt"])
    
    parsed = extract_json(raw)
    results_list = parsed.get("results", [])
    expected_list = trial["answers"]
    
    correct = 0
    total = 0
    
    # Determine which keys to check based on expected answers
    rule_keys = sorted(expected_list[0].keys()) if expected_list else ["A", "B", "C"]
    
    for i, exp in enumerate(expected_list):
        if i < len(results_list):
            item = results_list[i]
            for key in rule_keys:
                total += 1
                model_val = str(item.get(key, ""))
                if check_answer(model_val, exp[key]):
                    correct += 1
        else:
            total += len(exp)
    
    return correct / total if total > 0 else 0


def score_extreme_flat_trial(llm, trial) -> float:
    """Score an extreme trial with flat answer list (triple-stream interleaved)."""
    with kbench.chats.new(f"divided_{trial['id']}"):
        raw = llm.prompt(trial["prompt"])

    parsed = extract_json(raw)
    model_answers = parsed.get("answers", [])
    expected = trial["answers"]

    if not model_answers:
        lines = [l.strip() for l in raw.split("\n") if l.strip() and not l.strip().startswith("{")]
        model_answers = []
        for line in lines:
            m = re.match(r'\d+[\.):\s]+(.+)', line)
            if m:
                model_answers.append(m.group(1).strip())

    correct = 0
    total = len(expected)
    for i, exp in enumerate(expected):
        if i < len(model_answers) and check_answer(str(model_answers[i]), exp):
            correct += 1

    return correct / total if total > 0 else 0


@kbench.task(name="Divided Attention")
def attention_divided(llm) -> float:
    """
    Divided Attention (Multi-Stream Interference) Benchmark.

    Tests performance under simultaneous multi-stream monitoring with
    cross-stream interference. Three difficulty tiers:
      EASY (2 streams, no conflict): baseline
      MEDIUM (3 streams, shared domain): mild interference
      HARD (3 streams, SAME items, different rules): maximum interference

    Score = 0.20 * easy + 0.30 * medium + 0.50 * hard

    Cognitive Science Basis:
    - Pashler (1994) central bottleneck theory
    - Wickens (2002) Multiple Resource Theory
    - Navon & Gopher (1979) performance-resource functions
    """
    tier_scores = {"easy": [], "medium": [], "hard": []}
    
    for trial in EASY_TRIALS:
        acc = score_flat_trial(llm, trial)
        tier_scores["easy"].append(acc)
        print(f"  [easy  ] {trial['id']}: {acc:.3f}")
    
    for trial in MEDIUM_TRIALS:
        acc = score_flat_trial(llm, trial)
        tier_scores["medium"].append(acc)
        print(f"  [medium] {trial['id']}: {acc:.3f}")
    
    for trial in HARD_TRIALS:
        acc = score_hard_trial(llm, trial)
        tier_scores["hard"].append(acc)
        print(f"  [hard  ] {trial['id']}: {acc:.3f}")
    
    easy_mean = sum(tier_scores["easy"]) / len(tier_scores["easy"]) if tier_scores["easy"] else 0
    medium_mean = sum(tier_scores["medium"]) / len(tier_scores["medium"]) if tier_scores["medium"] else 0
    hard_mean = sum(tier_scores["hard"]) / len(tier_scores["hard"]) if tier_scores["hard"] else 0
    
    score = round(0.20 * easy_mean + 0.30 * medium_mean + 0.50 * hard_mean, 4)
    
    print(f"\n{'='*60}")
    print(f"DIVIDED ATTENTION (MULTI-STREAM INTERFERENCE) RESULTS")
    print(f"{'='*60}")
    print(f"EASY   (2 streams, no conflict):     {easy_mean:.3f}")
    print(f"MEDIUM (3 streams, shared domain):   {medium_mean:.3f}")
    print(f"HARD   (3 streams, same items):      {hard_mean:.3f}")
    print(f"\nComposite (0.20E + 0.30M + 0.50H):  {score:.4f}")
    
    return score


if __name__ == "__main__":
    attention_divided.run(llm=kbench.llm)
