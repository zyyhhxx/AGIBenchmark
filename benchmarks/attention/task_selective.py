"""
Attention Benchmark 1: Selective Attention — Conjunction Search v2

Tests the ability to filter information using multiple criteria simultaneously,
analogous to visual conjunction search in cognitive psychology.

Cognitive Science Basis:
- Treisman & Gelade (1980): Feature Integration Theory — pop-out vs conjunction search
- Wolfe (1994): Guided Search 2.0 — difficulty scales with number of shared features
- Duncan & Humphreys (1989): Target-distractor similarity determines search difficulty
- Posner & Snyder (1975): Inhibition of return in selective attention

Protocol:
- Tier 1 (Pop-out): Single-feature targets, minimal distractors (weight 0.10)
- Tier 2 (Feature conjunction): 2-feature filtering among 10+ distractors (weight 0.40)
- Tier 3 (Triple-conjunction): 3-4 feature filtering, high similarity near-misses (weight 0.50)

Score = 0.10 * tier1_acc + 0.40 * tier2_acc + 0.50 * tier3_acc
"""

import kaggle_benchmarks as kbench
import re
import json


def normalize(text: str) -> str:
    """Normalize for comparison: lowercase, strip whitespace/punctuation."""
    return re.sub(r'[^\w\s,]', '', text.strip().lower())


def check_answer(model_answer: str, correct: str, item: dict = None) -> bool:
    """Check if model answer matches expected answer(s)."""
    m = normalize(model_answer)
    c = normalize(correct)

    # Direct match
    if c in m or m in c:
        return True

    # Check alternate accepted answers
    if item:
        for alt in item.get("accept", []):
            alt_n = normalize(alt)
            if alt_n in m or m in alt_n:
                return True
        for alt in item.get("accept_also", []):
            alt_n = normalize(alt)
            if alt_n in m or m in alt_n:
                return True

    # For comma-separated list answers, check set equality
    if "," in c:
        expected_set = set(x.strip() for x in c.split(","))
        answer_set = set(x.strip() for x in m.split(","))
        if expected_set == answer_set:
            return True
        # Partial credit: check if all expected items are present
        if expected_set.issubset(answer_set) or answer_set.issubset(expected_set):
            return len(expected_set & answer_set) / max(len(expected_set), 1) > 0.8

    # For numeric answers
    try:
        if abs(float(m) - float(c)) < 0.01:
            return True
    except (ValueError, TypeError):
        pass

    return False


# ─── Item definitions ───────────────────────────────────────────────
# Inline to avoid import path issues across kbench/notebook environments

TIER1_ITEMS = [
    {"id": "T1_01", "tier": 1,
     "instruction": "What is the ONLY number in this text?",
     "text": "The cat sat on a mat near the hat by the bat under the 7 fat rat",
     "correct": "7"},
    {"id": "T1_02", "tier": 1,
     "instruction": "Which word is in ALL CAPS? Report just that word.",
     "text": "the quick brown ELEPHANT jumped over the lazy dog near the pond",
     "correct": "ELEPHANT"},
    {"id": "T1_03", "tier": 1,
     "instruction": "What is the only animal mentioned?",
     "text": "The tall granite tower overlooked the valley where a hawk circled above",
     "correct": "hawk"},
    {"id": "T1_04", "tier": 1,
     "instruction": "What is the FIRST word of the LAST sentence?",
     "text": "Rain fell gently. The streets were empty. Streetlights flickered overhead.",
     "correct": "Streetlights"},
]

TIER2_ITEMS = [
    {"id": "T2_01", "tier": 2,
     "instruction": "Which person is wearing BOTH a hat AND glasses? Report their name only.",
     "text": "Amy wears a hat and scarf. Bob wears glasses and a tie. Carol wears a hat and glasses. Dave wears glasses and a belt. Eve wears a hat and boots.",
     "correct": "Carol"},
    {"id": "T2_02", "tier": 2,
     "instruction": "Count ONLY the numbers that appear inside parentheses. Report the count of such numbers.",
     "text": "We had 5 meetings, scored (12) points, lost 8 players, gained (3) recruits, spent 45 dollars on (7) items, and 22 people filed (1) report at session 9",
     "correct": "4"},
    {"id": "T2_03", "tier": 2,
     "instruction": "In the grid below, count how many cells contain BOTH a letter AND a number.\n[A3] [B] [7] [C2] [D] [5E] [F] [G1] [8] [H] [J4] [K] [9] [L6] [M]",
     "text": "[A3] [B] [7] [C2] [D] [5E] [F] [G1] [8] [H] [J4] [K] [9] [L6] [M]",
     "correct": "6"},
    {"id": "T2_04", "tier": 2,
     "instruction": "How many sentences contain BOTH a color word AND a number?",
     "text": "The 3 red cars drove fast. Blue sky stretched overhead. She bought 5 green apples today. The white cat slept on 2 pillows. Yellow flowers bloom in spring. He painted 4 walls brown yesterday.",
     "correct": "4"},
    {"id": "T2_05", "tier": 2,
     "instruction": "Which day had BOTH rain AND a temperature above 70°F?",
     "text": "Monday: sunny, 75°F. Tuesday: rain, 68°F. Wednesday: cloudy, 72°F. Thursday: rain, 74°F. Friday: rain, 65°F. Saturday: sunny, 80°F.",
     "correct": "Thursday"},
    {"id": "T2_06", "tier": 2,
     "instruction": "Count numbers in this list that are BOTH odd AND greater than 50.",
     "text": "12, 73, 45, 88, 51, 24, 67, 30, 99, 42, 55, 16, 81, 48, 63",
     "correct": "7"},
    {"id": "T2_07", "tier": 2,
     "instruction": "What is the SECOND-smallest number in this list? Ignore numbers in parentheses.",
     "text": "42, (3), 17, 85, (9), 31, 8, (1), 56, 23",
     "correct": "17"},
    {"id": "T2_08", "tier": 2,
     "instruction": "Find the word that appears in BOTH Sentence 1 AND Sentence 3. Exclude common words (the, a, an, in, on, of, and, to, is, was, for, with).",
     "text": "Sentence 1: The crystal river flows beneath ancient stone bridges. Sentence 2: A forgotten temple stands among silver pillars. Sentence 3: Beyond the mossy walls, crystal towers rise above the misty plains.",
     "correct": "crystal",
     "accept": ["crystal"]},
    {"id": "T2_09", "tier": 2,
     "instruction": "In the grid, find the UPPERCASE word that is an ANIMAL. Report only that word.",
     "text": "The LARGE mountain stood near BLUE water while TALL trees and the HEAVY rocks sat by the DARK cave where a HAWK nested above",
     "correct": "HAWK"},
    {"id": "T2_10", "tier": 2,
     "instruction": "How many items in the list are BOTH fruits AND red in color? List: strawberry, banana, cherry, blueberry, watermelon, apple, grape, raspberry, mango, cranberry",
     "text": "strawberry, banana, cherry, blueberry, watermelon, apple, grape, raspberry, mango, cranberry",
     "correct": "5",
     # strawberry(red,fruit YES), cherry(red YES), apple(can be red YES), raspberry(red YES), cranberry(red YES) = 5. Banana(yellow), blueberry(blue), watermelon(green outside), grape(purple), mango(orange).
     },
]

TIER3_ITEMS = [
    {"id": "T3_01", "tier": 3,
     "instruction": "In the grid, find cells satisfying ALL THREE: (1) contain a vowel letter (A/E/I/O/U), (2) contain an EVEN number, (3) are in Row 2. Report matching cell contents comma-separated.\n\nRow 1: [A2] [E7] [I4] [O3] [U8]\nRow 2: [A5] [E6] [I1] [O4] [U2]\nRow 3: [A8] [E2] [I6] [O9] [U4]",
     "text": "Row 1: [A2] [E7] [I4] [O3] [U8] | Row 2: [A5] [E6] [I1] [O4] [U2] | Row 3: [A8] [E2] [I6] [O9] [U4]",
     "correct": "E6,O4,U2"},
    {"id": "T3_02", "tier": 3,
     "instruction": "Find ALL flights meeting ALL FOUR: (1) international, (2) duration over 3 hours, (3) departed before noon, (4) fewer than 200 passengers. Report flight numbers comma-separated.\n\nFL101: NYC→London, 7h, dep 08:00, 180 pax\nFL102: LA→Chicago, 4h, dep 06:00, 150 pax\nFL103: Paris→Tokyo, 12h, dep 11:30, 250 pax\nFL104: London→NYC, 7h, dep 09:00, 190 pax\nFL105: Sydney→Singapore, 8h, dep 14:00, 175 pax\nFL106: Berlin→Rome, 2h, dep 07:00, 120 pax\nFL107: Toronto→Mexico City, 5h, dep 10:00, 160 pax\nFL108: Dubai→Mumbai, 3.5h, dep 23:00, 195 pax",
     "text": "8 flights as above",
     "correct": "FL101,FL104,FL107"},
    {"id": "T3_03", "tier": 3,
     "instruction": "Count items that are ALL of: RED, CIRCULAR, and LARGE.\n\nItems: large red circle, small red circle, large blue circle, large red square, small red triangle, large green circle, medium red circle, large red diamond, small blue circle, large red circle, large yellow circle, tiny red circle, large red circle, medium blue square, large red triangle",
     "text": "15 items as above",
     "correct": "3"},
    {"id": "T3_04", "tier": 3,
     "instruction": "Find people meeting ALL: (1) age 30-50, (2) Technology sector, (3) city starts with 'S'. Report names comma-separated.\n\nAlex, 28, Technology, Seattle\nBlake, 35, Finance, San Jose\nCasey, 42, Technology, Sacramento\nDana, 31, Technology, Seattle\nEllis, 55, Technology, San Diego\nFinley, 38, Marketing, San Jose\nGlen, 45, Technology, Portland\nHarper, 33, Technology, Springfield\nIris, 29, Technology, Salem\nJordan, 40, Technology, Spokane",
     "text": "10 people as above",
     "correct": "Casey,Dana,Harper,Jordan"},
    {"id": "T3_05", "tier": 3,
     "instruction": "Find trades meeting ALL: (1) BUY order, (2) price $50-$100, (3) quantity over 500, (4) on TUESDAY. Report tickers comma-separated.\n\nMon: BUY AAPL 150@$75\nTue: SELL MSFT 600@$80\nTue: BUY GOOG 800@$55\nWed: BUY TSLA 300@$90\nTue: BUY AMZN 700@$110\nTue: BUY META 550@$65\nThu: BUY NFLX 450@$72\nTue: BUY NVDA 200@$95\nFri: BUY INTC 900@$48\nTue: BUY ORCL 650@$88",
     "text": "10 trades as above",
     "correct": "GOOG,META,ORCL"},
    {"id": "T3_06", "tier": 3,
     "instruction": "Find players meeting ALL: (1) won more games than lost, (2) scored exactly 3 goals in at least one game, (3) no red cards. Report names comma-separated.\n\nAlex: W3-L2, goals [2,3,1,0,4], cards [Y,Y,-,-,Y]\nBlair: W4-L1, goals [3,1,3,2,5], cards [-,Y,R,-,-]\nCasey: W2-L3, goals [1,0,3,2,1], cards [-,-,-,Y,-]\nDrew: W3-L2, goals [3,2,0,3,1], cards [Y,-,-,-,Y]\nEmery: W4-L1, goals [2,4,1,3,2], cards [-,-,-,-,-]",
     "text": "5 players as above",
     "correct": "Alex,Drew,Emery"},
    {"id": "T3_07", "tier": 3,
     "instruction": "Find events meeting ALL THREE: (1) weekday (Mon-Fri), (2) starts at or after 13:00, (3) lasts more than 1 hour. Report event names comma-separated.\n\nMon 09:00-10:30 Chemistry\nMon 14:00-15:00 History\nTue 13:00-15:30 Biology\nWed 08:00-09:00 Math\nThu 11:00-13:00 Physics\nSat 14:00-16:00 Art\nFri 15:00-17:30 Literature\nSun 10:00-12:00 Music\nTue 16:00-16:45 French\nThu 14:00-14:30 Ethics",
     "text": "10 events as above",
     "correct": "Biology,Literature"},
    {"id": "T3_08", "tier": 3,
     "instruction": "Find compounds meeting ALL: (1) molecular weight > 100, (2) contain oxygen, (3) contain carbon (organic), (4) liquid at room temperature. Report names comma-separated.\n\nWater H2O: MW 18, liquid\nEthanol C2H5OH: MW 46, liquid\nAcetone C3H6O: MW 58, liquid\nToluene C7H8: MW 92, liquid\nChloroform CHCl3: MW 119, liquid\nAcetic acid C2H4O2: MW 60, liquid\nDiethyl ether C4H10O: MW 74, liquid\nBenzaldehyde C7H6O: MW 106, liquid\nSulfuric acid H2SO4: MW 98, liquid\nCyclohexanone C6H10O: MW 98, liquid\nMethyl salicylate C8H8O3: MW 152, liquid\nNitrobenzene C6H5NO2: MW 123, liquid",
     "text": "12 compounds as above",
     "correct": "Benzaldehyde,Methyl salicylate,Nitrobenzene"},
    {"id": "T3_09", "tier": 3,
     "instruction": "Find rows where ALL hold: (1) Status='Active', (2) Score above 80, (3) Region is 'West' or 'East', (4) Category starts with 'A'. Report ID numbers comma-separated.\n\nID=101, Active, Score=92, West, Analytics\nID=102, Active, Score=75, East, Accounting\nID=103, Inactive, Score=88, West, Auditing\nID=104, Active, Score=85, North, Analytics\nID=105, Active, Score=91, East, Auditing\nID=106, Active, Score=60, West, Analytics\nID=107, Inactive, Score=95, East, Accounting\nID=108, Active, Score=83, West, Budget\nID=109, Active, Score=89, East, Analytics\nID=110, Active, Score=77, West, Auditing",
     "text": "10 rows as above",
     "correct": "101,105,109"},
    {"id": "T3_10", "tier": 3,
     "instruction": "Find books meeting ALL: (1) published after 2010, (2) non-fiction, (3) more than 300 pages, (4) author's last name A-M. Report titles comma-separated.\n\nThe Silent Code, Fiction, 2015, 280p, by N. Torres\nData Horizons, Non-fiction, 2018, 350p, by K. Fernandez\nMidnight Garden, Fiction, 2020, 400p, by A. Chang\nQuantum Minds, Non-fiction, 2012, 290p, by J. Blake\nClimate Rethink, Non-fiction, 2021, 420p, by L. Marsh\nNeural Paths, Non-fiction, 2019, 310p, by P. Quinn\nOcean Systems, Non-fiction, 2008, 380p, by B. Adams\nFuture Ethics, Non-fiction, 2022, 340p, by D. Kim\nStar Maps, Fiction, 2017, 500p, by H. Lee\nCell Biology, Non-fiction, 2016, 275p, by M. Grant",
     "text": "10 books as above",
     "correct": "Data Horizons,Climate Rethink,Future Ethics"},
    {"id": "T3_11", "tier": 3,
     "instruction": "Find employees meeting ALL: (1) salary > $70,000, (2) joined before 2020, (3) department is Engineering or Research, (4) performance rating >= 4. Report names comma-separated.\n\nAlice, $85K, 2018, Engineering, rating 4.2\nBob, $65K, 2019, Engineering, rating 4.5\nClara, $92K, 2017, Research, rating 3.8\nDan, $78K, 2021, Engineering, rating 4.1\nEva, $88K, 2016, Research, rating 4.6\nFinn, $71K, 2019, Marketing, rating 4.3\nGrace, $95K, 2015, Engineering, rating 4.0\nHank, $73K, 2018, Research, rating 4.4\nIvy, $80K, 2020, Engineering, rating 4.7\nJack, $76K, 2019, Engineering, rating 3.9",
     "text": "10 employees as above",
     "correct": "Alice,Eva,Grace,Hank"},
    {"id": "T3_12", "tier": 3,
     "instruction": "Find products meeting ALL: (1) rating above 4.0, (2) price under $50, (3) in stock (qty > 0), (4) category is 'Electronics' or 'Tools', (5) weight under 2 lbs. Report product names comma-separated.\n\nUSB Hub, Electronics, $35, rating 4.3, qty 50, 0.5 lb\nDrill Bit Set, Tools, $28, rating 4.5, qty 0, 1.2 lb\nBluetooth Speaker, Electronics, $55, rating 4.7, qty 30, 1.8 lb\nMultimeter, Tools, $42, rating 4.1, qty 15, 1.5 lb\nPhone Case, Accessories, $15, rating 4.6, qty 100, 0.2 lb\nSoldering Iron, Tools, $38, rating 4.4, qty 8, 0.8 lb\nHDMI Cable, Electronics, $12, rating 3.9, qty 200, 0.3 lb\nLevel Tool, Tools, $45, rating 4.2, qty 12, 2.5 lb\nWireless Mouse, Electronics, $29, rating 4.0, qty 75, 0.4 lb\nTape Measure, Tools, $18, rating 4.8, qty 45, 0.6 lb",
     "text": "10 products as above",
     "correct": "USB Hub,Multimeter,Soldering Iron,Tape Measure"},
]


ALL_ITEMS = TIER1_ITEMS + TIER2_ITEMS + TIER3_ITEMS


@kbench.task(name="Selective Attention", version=2)
def attention_selective(llm) -> float:
    """
    Selective Attention — Conjunction Search Benchmark v2.

    Tests ability to filter information using multiple criteria simultaneously,
    analogous to visual conjunction search (Treisman & Gelade, 1980).

    Three difficulty tiers:
    - Tier 1 (Pop-out): single feature, easy (weight 0.10)
    - Tier 2 (Conjunction): 2 features to bind (weight 0.40)
    - Tier 3 (Triple-conjunction): 3-5 features, many near-miss distractors (weight 0.50)

    Score = 0.10 * tier1_acc + 0.40 * tier2_acc + 0.50 * tier3_acc
    """
    tier_results = {1: [], 2: [], 3: []}

    for item in ALL_ITEMS:
        with kbench.chats.new(f"sel_{item['id']}"):
            # Build prompt with full item context
            prompt = (
                f"Follow this instruction carefully and respond with ONLY the answer.\n\n"
                f"{item['instruction']}\n\n"
            )
            # Only add text field if it provides additional context beyond instruction
            if item["text"] and item["text"] not in item["instruction"]:
                prompt += f"Text: {item['text']}\n\n"

            prompt += "Answer:"

            try:
                raw = llm.prompt(prompt)
                answer = raw.strip()
            except Exception as e:
                answer = f"ERROR: {e}"

            correct = check_answer(answer, item["correct"], item)
            tier_results[item["tier"]].append({
                "id": item["id"],
                "correct": correct,
                "answer": answer[:80],
                "expected": item["correct"],
            })

    # Compute per-tier accuracy
    tier_accs = {}
    for tier in [1, 2, 3]:
        items = tier_results[tier]
        tier_accs[tier] = sum(1 for r in items if r["correct"]) / len(items) if items else 0

    # Composite score with tier weights
    score = round(
        0.10 * tier_accs[1] +
        0.40 * tier_accs[2] +
        0.50 * tier_accs[3],
        4
    )

    # Logging
    print(f"\n{'='*60}")
    print(f"SELECTIVE ATTENTION v2 — CONJUNCTION SEARCH RESULTS")
    print(f"{'='*60}")
    print(f"Treisman & Gelade (1980); Wolfe (1994); Duncan & Humphreys (1989)")

    for tier in [1, 2, 3]:
        tier_names = {1: "POP-OUT (easy)", 2: "FEATURE CONJUNCTION (medium)", 3: "TRIPLE-CONJUNCTION (hard)"}
        items = tier_results[tier]
        acc = tier_accs[tier]
        weight = {1: 0.10, 2: 0.40, 3: 0.50}[tier]
        print(f"\n--- TIER {tier}: {tier_names[tier]} (n={len(items)}, acc={acc:.2%}, weight={weight}) ---")
        for r in items:
            status = "✓" if r["correct"] else "✗"
            print(f"  {status} {r['id']}: got '{r['answer'][:40]}', expected '{r['expected'][:40]}'")

    print(f"\n--- SUMMARY ---")
    print(f"Tier 1 (pop-out):            {tier_accs[1]:.2%} × 0.10 = {0.10 * tier_accs[1]:.4f}")
    print(f"Tier 2 (conjunction):        {tier_accs[2]:.2%} × 0.40 = {0.40 * tier_accs[2]:.4f}")
    print(f"Tier 3 (triple-conjunction): {tier_accs[3]:.2%} × 0.50 = {0.50 * tier_accs[3]:.4f}")
    print(f"Composite score:             {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    attention_selective.run(llm=kbench.llm)
