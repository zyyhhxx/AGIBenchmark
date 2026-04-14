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
- Tier 1 (Pop-out): Single-feature targets, minimal distractors (weight 0.08)
- Tier 2 (Feature conjunction): 2-feature filtering among 10+ distractors (weight 0.22)
- Tier 3 (Triple-conjunction): 3-4 feature filtering, high similarity near-misses (weight 0.35)
- Tier 4 (Quadruple-conjunction): 5-7 feature filtering, edge cases, ambiguous near-misses (weight 0.35)

Score = 0.08 * tier1_acc + 0.22 * tier2_acc + 0.35 * tier3_acc + 0.35 * tier4_acc
"""

import kaggle_benchmarks as kbench
import re
import json



def _strip_think(text: str) -> str:
    """Remove <think>...</think> blocks from model output."""
    import re as _re
    return _re.sub(r'<think>.*?</think>', '', text, flags=_re.DOTALL).strip()

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

# Tier 4: Quadruple-conjunction search — 4+ simultaneous constraints with
# high similarity near-misses and ambiguous edge cases. Each item requires
# checking at least 4 independent dimensions.
TIER4_ITEMS = [
    {"id": "T4_01", "tier": 4,
     "instruction": "Find students meeting ALL SIX criteria: (1) GPA above 3.5, (2) age 20-25, (3) major is STEM (Science, Technology, Engineering, Math), (4) has internship experience, (5) no disciplinary record, (6) enrolled full-time. Report names comma-separated.\n\nAlice, GPA 3.8, age 22, Computer Science, internship: yes, disciplinary: none, full-time\nBob, GPA 3.6, age 24, Mathematics, internship: yes, disciplinary: none, part-time\nClara, GPA 3.9, age 21, Biology, internship: yes, disciplinary: none, full-time\nDave, GPA 3.4, age 23, Engineering, internship: yes, disciplinary: none, full-time\nEva, GPA 3.7, age 26, Physics, internship: yes, disciplinary: none, full-time\nFinn, GPA 3.5, age 20, Chemistry, internship: no, disciplinary: none, full-time\nGrace, GPA 3.8, age 22, English, internship: yes, disciplinary: none, full-time\nHank, GPA 3.6, age 24, Statistics, internship: yes, disciplinary: warning, full-time\nIvy, GPA 3.7, age 23, Computer Engineering, internship: yes, disciplinary: none, full-time\nJack, GPA 3.9, age 25, Data Science, internship: yes, disciplinary: none, full-time",
     "text": "10 students as above",
     # Alice: 3.8>3.5 YES, 22 in 20-25 YES, CS=STEM YES, intern YES, no disc YES, full-time YES → YES
     # Bob: 3.6>3.5 YES, 24 YES, Math=STEM YES, intern YES, no disc YES, part-time NO → NO
     # Clara: 3.9>3.5 YES, 21 YES, Biology=STEM YES, intern YES, no disc YES, full-time YES → YES
     # Dave: 3.4>3.5 NO → NO
     # Eva: 3.7>3.5 YES, 26 NOT in 20-25 NO → NO
     # Finn: 3.5>3.5 NO (must be ABOVE 3.5) → NO
     # Grace: 3.8 YES, 22 YES, English NOT STEM → NO
     # Hank: 3.6 YES, 24 YES, Statistics=STEM YES, intern YES, disciplinary: warning → NO
     # Ivy: 3.7 YES, 23 YES, CompEng=STEM YES, intern YES, no disc YES, full-time YES → YES
     # Jack: 3.9 YES, 25 YES, DataSci=STEM YES, intern YES, no disc YES, full-time YES → YES
     "correct": "Alice,Clara,Ivy,Jack"},
    {"id": "T4_02", "tier": 4,
     "instruction": "Find recipes meeting ALL FIVE: (1) prep time ≤30 min, (2) vegetarian, (3) fewer than 500 calories per serving, (4) contains at least 3 of these allergens-free: gluten-free, nut-free, dairy-free, soy-free, (5) rated 4+ stars. Report recipe names comma-separated.\n\nPasta Primavera: prep 25 min, vegetarian, 480 cal, gluten:yes dairy:yes nut-free soy-free, 4.2 stars\nQuinoa Bowl: prep 20 min, vegetarian, 320 cal, gluten-free nut-free dairy-free soy-free, 4.5 stars\nChicken Stir-Fry: prep 15 min, non-vegetarian, 410 cal, gluten-free nut-free dairy-free soy:yes, 4.3 stars\nVeggie Curry: prep 35 min, vegetarian, 380 cal, gluten-free nut-free dairy-free soy-free, 4.7 stars\nCaprese Salad: prep 10 min, vegetarian, 290 cal, gluten-free nut-free soy-free dairy:yes, 4.1 stars\nTofu Scramble: prep 20 min, vegetarian, 310 cal, gluten-free dairy-free nut-free soy:yes, 3.8 stars\nFruit Smoothie: prep 5 min, vegetarian, 180 cal, gluten-free dairy-free nut-free soy-free, 4.4 stars\nCheese Quesadilla: prep 15 min, vegetarian, 520 cal, nut-free soy-free gluten:yes dairy:yes, 4.0 stars\nRice Paper Rolls: prep 25 min, vegetarian, 220 cal, gluten-free nut-free dairy-free soy:yes, 4.6 stars\nBean Salad: prep 15 min, vegetarian, 270 cal, gluten-free nut-free dairy-free soy-free, 4.3 stars",
     "text": "10 recipes as above",
     # Pasta Primavera: ≤30 YES, veg YES, <500 YES, allergen-free: nut-free+soy-free=2 NO (need ≥3) → NO
     # Quinoa Bowl: ≤30 YES, veg YES, <500 YES, gluten-free+nut-free+dairy-free+soy-free=4 YES, 4.5≥4 YES → YES
     # Chicken Stir-Fry: non-vegetarian → NO
     # Veggie Curry: prep 35 >30 → NO
     # Caprese Salad: ≤30 YES, veg YES, <500 YES, gluten-free+nut-free+soy-free=3 YES, 4.1≥4 YES → YES
     # Tofu Scramble: ≤30 YES, veg YES, <500 YES, gluten-free+dairy-free+nut-free=3 YES, 3.8<4 NO → NO
     # Fruit Smoothie: ≤30 YES, veg YES, <500 YES, gluten-free+dairy-free+nut-free+soy-free=4 YES, 4.4≥4 YES → YES
     # Cheese Quesadilla: ≤30 YES, veg YES, 520≥500 NO → NO
     # Rice Paper Rolls: ≤30 YES, veg YES, <500 YES, gluten-free+nut-free+dairy-free=3 YES, 4.6≥4 YES → YES
     # Bean Salad: ≤30 YES, veg YES, <500 YES, gluten-free+nut-free+dairy-free+soy-free=4 YES, 4.3≥4 YES → YES
     "correct": "Quinoa Bowl,Caprese Salad,Fruit Smoothie,Rice Paper Rolls,Bean Salad"},
    {"id": "T4_03", "tier": 4,
     "instruction": "Find apartments meeting ALL SIX: (1) rent under $2000/mo, (2) 2+ bedrooms, (3) has parking, (4) allows pets, (5) within 3 miles of downtown, (6) built after 2000. Report unit IDs comma-separated.\n\nA101: $1800/mo, 2 bed, parking: yes, pets: yes, 2.5 mi from downtown, built 2005\nA102: $2100/mo, 3 bed, parking: yes, pets: yes, 1.0 mi from downtown, built 2010\nA103: $1500/mo, 1 bed, parking: yes, pets: yes, 2.0 mi from downtown, built 2015\nA104: $1900/mo, 2 bed, parking: no, pets: yes, 1.5 mi from downtown, built 2008\nA105: $1750/mo, 2 bed, parking: yes, pets: no, 2.8 mi from downtown, built 2012\nA106: $1650/mo, 3 bed, parking: yes, pets: yes, 3.5 mi from downtown, built 2003\nA107: $1400/mo, 2 bed, parking: yes, pets: yes, 2.0 mi from downtown, built 1998\nA108: $1850/mo, 2 bed, parking: yes, pets: yes, 1.2 mi from downtown, built 2018\nA109: $1950/mo, 4 bed, parking: yes, pets: yes, 2.9 mi from downtown, built 2001\nA110: $1700/mo, 2 bed, parking: yes, pets: yes, 3.0 mi from downtown, built 2006",
     "text": "10 apartments as above",
     # A101: <2000 YES, 2bed YES, parking YES, pets YES, 2.5≤3 YES, 2005>2000 YES → YES
     # A102: $2100≥2000 NO → NO
     # A103: 1bed <2 NO → NO
     # A104: parking NO → NO
     # A105: pets NO → NO
     # A106: 3.5>3 NO → NO
     # A107: 1998≤2000 NO → NO
     # A108: <2000 YES, 2bed YES, parking YES, pets YES, 1.2≤3 YES, 2018>2000 YES → YES
     # A109: <2000 YES, 4bed≥2 YES, parking YES, pets YES, 2.9≤3 YES, 2001>2000 YES → YES
     # A110: <2000 YES, 2bed YES, parking YES, pets YES, 3.0≤3 YES, 2006>2000 YES → YES
     "correct": "A101,A108,A109,A110"},
    {"id": "T4_04", "tier": 4,
     "instruction": "Find stocks meeting ALL FIVE criteria: (1) P/E ratio between 10 and 25, (2) dividend yield above 2%, (3) market cap over $10B, (4) positive revenue growth (YoY), (5) debt-to-equity ratio under 1.5. Report tickers comma-separated.\n\nAAPL: P/E 28, div 0.5%, cap $2.8T, rev growth +8%, D/E 1.8\nJNJ: P/E 15, div 3.0%, cap $380B, rev growth +3%, D/E 0.4\nTSLA: P/E 65, div 0%, cap $800B, rev growth +15%, D/E 0.1\nPFE: P/E 12, div 5.8%, cap $160B, rev growth -15%, D/E 0.8\nJPM: P/E 11, div 2.5%, cap $520B, rev growth +6%, D/E 1.2\nNKE: P/E 30, div 1.5%, cap $140B, rev growth +4%, D/E 0.9\nKO: P/E 22, div 3.1%, cap $260B, rev growth +2%, D/E 1.6\nABBV: P/E 18, div 3.8%, cap $290B, rev growth +5%, D/E 2.1\nPG: P/E 24, div 2.4%, cap $350B, rev growth +3%, D/E 0.7\nXOM: P/E 14, div 3.5%, cap $450B, rev growth +12%, D/E 0.3",
     "text": "10 stocks as above",
     # AAPL: P/E 28 >25 NO → NO
     # JNJ: P/E 15 YES, div 3.0>2 YES, cap 380B>10B YES, rev +3% YES, D/E 0.4<1.5 YES → YES
     # TSLA: P/E 65 >25 NO → NO
     # PFE: P/E 12 YES, div 5.8>2 YES, cap 160B YES, rev -15% NOT positive NO → NO
     # JPM: P/E 11 YES, div 2.5>2 YES, cap 520B YES, rev +6% YES, D/E 1.2<1.5 YES → YES
     # NKE: P/E 30 >25 NO → NO
     # KO: P/E 22 YES, div 3.1>2 YES, cap 260B YES, rev +2% YES, D/E 1.6≥1.5 NO → NO
     # ABBV: P/E 18 YES, div 3.8>2 YES, cap 290B YES, rev +5% YES, D/E 2.1≥1.5 NO → NO
     # PG: P/E 24 YES, div 2.4>2 YES, cap 350B YES, rev +3% YES, D/E 0.7<1.5 YES → YES
     # XOM: P/E 14 YES, div 3.5>2 YES, cap 450B YES, rev +12% YES, D/E 0.3<1.5 YES → YES
     "correct": "JNJ,JPM,PG,XOM"},
    {"id": "T4_05", "tier": 4,
     "instruction": "Find servers meeting ALL SEVEN: (1) uptime above 99.9%, (2) CPU usage under 80%, (3) memory usage under 75%, (4) disk usage under 90%, (5) located in US or EU, (6) running Linux, (7) last patched within 30 days (today is day 100). Report server IDs comma-separated.\n\nSRV01: uptime 99.95%, CPU 72%, mem 68%, disk 85%, US-East, Linux, patched day 95\nSRV02: uptime 99.80%, CPU 55%, mem 60%, disk 70%, EU-West, Linux, patched day 80\nSRV03: uptime 99.99%, CPU 88%, mem 45%, disk 50%, US-West, Linux, patched day 92\nSRV04: uptime 99.92%, CPU 65%, mem 72%, disk 88%, EU-Central, Linux, patched day 75\nSRV05: uptime 99.95%, CPU 70%, mem 74%, disk 91%, US-East, Linux, patched day 98\nSRV06: uptime 99.91%, CPU 45%, mem 55%, disk 60%, Asia-Pacific, Linux, patched day 90\nSRV07: uptime 99.98%, CPU 78%, mem 70%, disk 82%, US-West, Windows, patched day 96\nSRV08: uptime 99.93%, CPU 60%, mem 65%, disk 75%, EU-West, Linux, patched day 85\nSRV09: uptime 99.96%, CPU 50%, mem 48%, disk 55%, US-Central, Linux, patched day 99\nSRV10: uptime 99.88%, CPU 42%, mem 38%, disk 40%, EU-East, Linux, patched day 88",
     "text": "10 servers as above",
     # SRV01: 99.95>99.9 YES, 72<80 YES, 68<75 YES, 85<90 YES, US YES, Linux YES, day95→100-95=5≤30 YES → YES
     # SRV02: 99.80<99.9 NO → NO
     # SRV03: 99.99 YES, 88≥80 NO → NO
     # SRV04: 99.92 YES, 65<80 YES, 72<75 YES, 88<90 YES, EU YES, Linux YES, day75→100-75=25≤30 YES → YES
     # SRV05: 99.95 YES, 70<80 YES, 74<75 YES, 91≥90 NO → NO
     # SRV06: 99.91 YES, 45<80 YES, 55<75 YES, 60<90 YES, Asia-Pacific NOT US/EU NO → NO
     # SRV07: 99.98 YES, 78<80 YES, 70<75 YES, 82<90 YES, US YES, Windows NOT Linux NO → NO
     # SRV08: 99.93 YES, 60<80 YES, 65<75 YES, 75<90 YES, EU YES, Linux YES, day85→100-85=15≤30 YES → YES
     # SRV09: 99.96 YES, 50<80 YES, 48<75 YES, 55<90 YES, US YES, Linux YES, day99→100-99=1≤30 YES → YES
     # SRV10: 99.88<99.9 NO → NO
     "correct": "SRV01,SRV04,SRV08,SRV09"},
    {"id": "T4_06", "tier": 4,
     "instruction": "Find candidates meeting ALL criteria: (1) experience 5-15 years, (2) has a Master's or PhD, (3) speaks at least 2 languages, (4) willing to relocate, (5) salary expectation under $150K, (6) no employment gap longer than 6 months in last 5 years. Report names comma-separated.\n\nAlice: 8 yrs exp, PhD, speaks English+French+Mandarin, relocate: yes, expects $140K, gaps: none\nBob: 12 yrs exp, Master's, speaks English, relocate: yes, expects $130K, gaps: none\nClara: 4 yrs exp, PhD, speaks English+Spanish, relocate: yes, expects $120K, gaps: none\nDave: 10 yrs exp, Bachelor's, speaks English+German+Japanese, relocate: yes, expects $125K, gaps: none\nEva: 7 yrs exp, Master's, speaks English+Italian, relocate: no, expects $135K, gaps: none\nFinn: 14 yrs exp, Master's, speaks English+Portuguese, relocate: yes, expects $145K, gaps: 8 months in 2023\nGrace: 6 yrs exp, PhD, speaks English+Korean, relocate: yes, expects $155K, gaps: none\nHank: 11 yrs exp, Master's, speaks English+Arabic+Hindi, relocate: yes, expects $128K, gaps: none\nIvy: 9 yrs exp, Master's, speaks English+Russian, relocate: yes, expects $138K, gaps: 3 months in 2022\nJack: 16 yrs exp, PhD, speaks English+French, relocate: yes, expects $142K, gaps: none",
     "text": "10 candidates as above",
     # Alice: 8 YES (5-15), PhD YES, 3 langs YES, relocate YES, $140K<150K YES, no gap YES → YES
     # Bob: 12 YES, Master's YES, 1 lang NO → NO
     # Clara: 4 <5 NO → NO
     # Dave: 10 YES, Bachelor's NO → NO
     # Eva: 7 YES, Master's YES, 2 langs YES, relocate NO → NO
     # Finn: 14 YES, Master's YES, 2 langs YES, relocate YES, $145K<150K YES, 8mo gap >6 NO → NO
     # Grace: 6 YES, PhD YES, 2 langs YES, relocate YES, $155K≥150K NO → NO
     # Hank: 11 YES, Master's YES, 3 langs YES, relocate YES, $128K<150K YES, no gap YES → YES
     # Ivy: 9 YES, Master's YES, 2 langs YES, relocate YES, $138K<150K YES, 3mo≤6 YES → YES
     # Jack: 16 >15 NO → NO
     "correct": "Alice,Hank,Ivy"},
]


ALL_ITEMS = TIER1_ITEMS + TIER2_ITEMS + TIER3_ITEMS + TIER4_ITEMS


@kbench.task(name="Selective Attention", version=2)
def attention_selective(llm) -> float:
    """Selective Attention — Conjunction Search Benchmark v2.

    Tests ability to filter information using multiple criteria simultaneously,
    analogous to visual conjunction search (Treisman & Gelade, 1980).

    Four difficulty tiers:
    """
    tier_results = {1: [], 2: [], 3: [], 4: []}

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
                answer = _strip_think(raw)
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
    for tier in [1, 2, 3, 4]:
        items = tier_results[tier]
        tier_accs[tier] = sum(1 for r in items if r["correct"]) / len(items) if items else 0

    # Composite score with tier weights
    score = round(
        0.08 * tier_accs[1] +
        0.22 * tier_accs[2] +
        0.35 * tier_accs[3] +
        0.35 * tier_accs[4],
        4
    )

    # Logging
    print(f"\n{'='*60}")
    print(f"SELECTIVE ATTENTION v2 — CONJUNCTION SEARCH RESULTS")
    print(f"{'='*60}")
    print(f"Treisman & Gelade (1980); Wolfe (1994); Duncan & Humphreys (1989)")

    for tier in [1, 2, 3, 4]:
        tier_names = {1: "POP-OUT (easy)", 2: "FEATURE CONJUNCTION (medium)",
                      3: "TRIPLE-CONJUNCTION (hard)", 4: "QUADRUPLE-CONJUNCTION (extreme)"}
        items = tier_results[tier]
        acc = tier_accs[tier]
        weight = {1: 0.08, 2: 0.22, 3: 0.35, 4: 0.35}[tier]
        print(f"\n--- TIER {tier}: {tier_names[tier]} (n={len(items)}, acc={acc:.2%}, weight={weight}) ---")
        for r in items:
            status = "✓" if r["correct"] else "✗"
            print(f"  {status} {r['id']}: got '{r['answer'][:40]}', expected '{r['expected'][:40]}'")

    print(f"\n--- SUMMARY ---")
    print(f"Tier 1 (pop-out):                {tier_accs[1]:.2%} × 0.08 = {0.08 * tier_accs[1]:.4f}")
    print(f"Tier 2 (conjunction):            {tier_accs[2]:.2%} × 0.22 = {0.22 * tier_accs[2]:.4f}")
    print(f"Tier 3 (triple-conjunction):      {tier_accs[3]:.2%} × 0.35 = {0.35 * tier_accs[3]:.4f}")
    print(f"Tier 4 (quadruple-conjunction):   {tier_accs[4]:.2%} × 0.35 = {0.35 * tier_accs[4]:.4f}")
    print(f"Composite score:                 {score:.4f}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    attention_selective.run(llm=kbench.llm)
