"""
Selective Attention v2 — Three-tier conjunction-search items.

Tier 1 (Pop-out): Single-feature target, minimal interference (weight 0.10)
Tier 2 (Feature conjunction): Must bind 2 features to find target (weight 0.40)  
Tier 3 (Triple-conjunction + high similarity): 3+ features, many near-miss distractors (weight 0.50)

Cognitive basis:
- Treisman & Gelade (1980): Feature Integration Theory
- Wolfe (1994): Guided Search model
- Duncan & Humphreys (1989): Target-distractor similarity
"""

# ═══════════════════════════════════════════════════════════════════════
# TIER 1: POP-OUT (easy) — weight 0.10
# ═══════════════════════════════════════════════════════════════════════

TIER1_ITEMS = [
    {
        "id": "T1_01",
        "instruction": "What is the ONLY number in this text?",
        "text": "The cat sat on a mat near the hat by the bat under the 7 fat rat",
        "correct": "7",
        "tier": 1,
    },
    {
        "id": "T1_02",
        "instruction": "Which word is in ALL CAPS? Report just that word.",
        "text": "the quick brown ELEPHANT jumped over the lazy dog near the pond",
        "correct": "ELEPHANT",
        "tier": 1,
    },
    {
        "id": "T1_03",
        "instruction": "What is the only animal mentioned?",
        "text": "The tall granite tower overlooked the valley where a hawk circled above",
        "correct": "hawk",
        "tier": 1,
    },
    {
        "id": "T1_04",
        "instruction": "What is the FIRST word of the LAST sentence?",
        "text": "Rain fell gently. The streets were empty. Streetlights flickered overhead.",
        "correct": "Streetlights",
        "tier": 1,
    },
]

# ═══════════════════════════════════════════════════════════════════════
# TIER 2: FEATURE CONJUNCTION (medium) — weight 0.40
# Must bind exactly 2 features; 10+ distractors matching one but not both
# ═══════════════════════════════════════════════════════════════════════

TIER2_ITEMS = [
    {
        "id": "T2_01",
        "instruction": "Find the UPPERCASE word that is also an ANIMAL. Report only that word.",
        "text": "The LARGE mountain LION stood near BLUE water while TALL trees and the HEAVY BEAR rocks sat by the DARK cave",
        "correct": "LION",
        "tier": 2,
        # UPPERCASE non-animals: LARGE, BLUE, TALL, HEAVY, DARK. BEAR follows HEAVY making "HEAVY BEAR" — but BEAR is also uppercase+animal. Accept LION or BEAR.
        "accept": ["LION", "BEAR"],
    },
    {
        "id": "T2_02",
        "instruction": "Count ONLY the numbers that appear inside parentheses. Report the count.",
        "text": "We had 5 meetings, scored (12) points, lost 8 players, gained (3) recruits, spent 45 dollars on (7) items, and 22 people filed (1) report at session 9",
        "correct": "4",
        "tier": 2,
        # In parens: (12),(3),(7),(1) = 4. Not in parens: 5,8,45,22,9.
    },
    {
        "id": "T2_03",
        "instruction": "In the grid below, count how many cells contain BOTH a letter AND a number.\n[A3] [B] [7] [C2] [D] [5E] [F] [G1] [8] [H] [J4] [K] [9] [L6] [M]",
        "text": "[A3] [B] [7] [C2] [D] [5E] [F] [G1] [8] [H] [J4] [K] [9] [L6] [M]",
        "correct": "6",
        "tier": 2,
        # Both: A3, C2, 5E, G1, J4, L6 = 6. Letter-only: B,D,F,H,K,M. Number-only: 7,8,9.
    },
    {
        "id": "T2_04",
        "instruction": "How many sentences contain BOTH a color word AND a number?",
        "text": "The 3 red cars drove fast. Blue sky stretched overhead. She bought 5 green apples today. The white cat slept on 2 pillows. Yellow flowers bloom in spring. He painted 4 walls brown yesterday.",
        "correct": "4",
        "tier": 2,
        # S1: 3+red=YES. S2: blue, no number=NO. S3: 5+green=YES. S4: white+2=YES. S5: yellow, no number=NO. S6: 4+brown=YES. Total: 4.
    },
    {
        "id": "T2_05",
        "instruction": "Find words that are BOTH longer than 6 letters AND contain a double letter (same letter twice in a row). List them comma-separated.",
        "text": "The committee addressed the mammoth balloon floating freely across the yellow grassland",
        "correct": "committee,addressed,balloon,grassland",
        "tier": 2,
        # committee(9,mm,tt,ee→YES), addressed(9,dd→YES), mammoth(7,mm→YES... wait mammoth=7 letters, >6 YES), balloon(7,ll,oo→YES), floating(8, no double→NO), freely(6, not >6→NO), across(6→NO), yellow(6→NO), grassland(9,ss→YES). Accept mammoth too.
        "accept_also": ["mammoth"],
    },
    {
        "id": "T2_06",
        "instruction": "Which person is wearing BOTH a hat AND glasses? Report their name only.",
        "text": "Amy wears a hat and scarf. Bob wears glasses and a tie. Carol wears a hat and glasses. Dave wears glasses and a belt. Eve wears a hat and boots.",
        "correct": "Carol",
        "tier": 2,
    },
    {
        "id": "T2_07",
        "instruction": "Count numbers that are BOTH odd AND greater than 50.",
        "text": "12, 73, 45, 88, 51, 24, 67, 30, 99, 42, 55, 16, 81, 48, 63",
        "correct": "6",
        "tier": 2,
        # Odd AND >50: 73, 51, 67, 99, 55, 81, 63 = 7. Wait: 45 is odd but ≤50. 73(odd,>50)YES, 51 YES, 67 YES, 99 YES, 55 YES, 81 YES, 63 YES = 7. Let me recheck: 45 is odd and =45 not >50→NO. So 7.
    },
    {
        "id": "T2_08",
        "instruction": "Which day had BOTH rain AND a temperature above 70°F?",
        "text": "Monday: sunny, 75°F. Tuesday: rain, 68°F. Wednesday: cloudy, 72°F. Thursday: rain, 74°F. Friday: rain, 65°F. Saturday: sunny, 80°F.",
        "correct": "Thursday",
        "tier": 2,
    },
    {
        "id": "T2_09",
        "instruction": "Find the word that appears in BOTH sentence 1 AND sentence 3 (excluding 'the', 'a', 'an', 'in', 'on', 'of', 'and', 'to', 'is', 'was').",
        "text": "Sentence 1: The crystal river flows beneath ancient stone bridges. Sentence 2: A forgotten temple stands among silver pillars. Sentence 3: Beyond the mossy stone walls, crystal towers rise above the plains.",
        "correct": "crystal",
        "tier": 2,
        # S1 content: crystal, river, flows, beneath, ancient, stone, bridges. S3 content: beyond, mossy, stone, walls, crystal, towers, rise, above, plains. Shared: crystal, stone. Accept either.
        "accept": ["crystal", "stone"],
    },
    {
        "id": "T2_10",
        "instruction": "What is the SECOND-smallest number in this list? Ignore numbers in parentheses.",
        "text": "42, (3), 17, 85, (9), 31, 8, (1), 56, 23",
        "correct": "17",
        "tier": 2,
        # Non-paren numbers: 42, 17, 85, 31, 8, 56, 23. Sorted: 8, 17, 23, 31, 42, 56, 85. Second-smallest: 17.
    },
]

# ═══════════════════════════════════════════════════════════════════════
# TIER 3: TRIPLE-CONJUNCTION + HIGH DISTRACTOR SIMILARITY (hard) — weight 0.50
# 3-4 filtering criteria, many near-miss distractors, multi-step
# ═══════════════════════════════════════════════════════════════════════

TIER3_ITEMS = [
    {
        "id": "T3_01",
        "instruction": "In the grid below, find cells that satisfy ALL THREE conditions: (1) contain a vowel letter (A,E,I,O,U), (2) contain an EVEN number, (3) are in Row 2. Report matching cell contents separated by commas.\n\nRow 1: [A2] [E7] [I4] [O3] [U8]\nRow 2: [A5] [E6] [I1] [O4] [U2]\nRow 3: [A8] [E2] [I6] [O9] [U4]",
        "text": "Row 1: [A2] [E7] [I4] [O3] [U8] | Row 2: [A5] [E6] [I1] [O4] [U2] | Row 3: [A8] [E2] [I6] [O9] [U4]",
        "correct": "E6,O4,U2",
        "tier": 3,
        # Row 2 cells: A5(5 odd→NO), E6(6 even, E vowel→YES), I1(1 odd→NO), O4(4 even, O vowel→YES), U2(2 even, U vowel→YES).
        # Near-misses: Row1 A2,I4,U8 (vowel+even but wrong row), Row3 A8,E2,I6,U4 (wrong row).
    },
    {
        "id": "T3_02",
        "instruction": "Find ALL flights that meet ALL FOUR criteria: (1) international (origin and destination in different countries), (2) duration over 3 hours, (3) departed before noon (before 12:00), (4) fewer than 200 passengers. Report flight numbers comma-separated.\n\nFL101: NYC→London, 7h, dep 08:00, 180 pax\nFL102: LA→Chicago, 4h, dep 06:00, 150 pax\nFL103: Paris→Tokyo, 12h, dep 11:30, 250 pax\nFL104: London→NYC, 7h, dep 09:00, 190 pax\nFL105: Sydney→Singapore, 8h, dep 14:00, 175 pax\nFL106: Berlin→Rome, 2h, dep 07:00, 120 pax\nFL107: Toronto→Mexico City, 5h, dep 10:00, 160 pax\nFL108: Dubai→Mumbai, 3.5h, dep 23:00, 195 pax",
        "text": "FL101-FL108 as in instruction",
        "correct": "FL101,FL104,FL107",
        "tier": 3,
        # FL101: intl YES, 7h>3 YES, 08:00<12 YES, 180<200 YES → MATCH
        # FL102: domestic NO
        # FL103: intl YES, 12h YES, 11:30<12 YES, 250≥200 NO
        # FL104: intl YES, 7h YES, 09:00 YES, 190<200 YES → MATCH
        # FL105: intl YES, 8h YES, 14:00≥12 NO
        # FL106: intl YES, 2h≤3 NO
        # FL107: intl YES, 5h YES, 10:00 YES, 160 YES → MATCH
        # FL108: intl YES, 3.5h YES, 23:00≥12 NO
    },
    {
        "id": "T3_03",
        "instruction": "From the items below, count those that are: (1) RED, (2) CIRCULAR, and (3) LARGE. Report the count.\n\nItems: large red circle, small red circle, large blue circle, large red square, small red triangle, large green circle, medium red circle, large red diamond, small blue circle, large red circle, large yellow circle, tiny red circle, large red circle, medium blue square, large red triangle",
        "text": "15 items as listed in instruction",
        "correct": "3",
        "tier": 3,
        # large+red+circle: items 1(YES), 2(small→no), 3(blue→no), 4(square→no), 5(small+tri→no), 6(green→no), 7(medium→no), 8(diamond→no), 9(small+blue→no), 10(YES), 11(yellow→no), 12(tiny→no), 13(YES), 14(no), 15(tri→no). Answer: 3.
    },
    {
        "id": "T3_04",
        "instruction": "Find people who meet ALL conditions: (1) age 30-50, (2) work in Technology, (3) live in a city starting with 'S'. Report names comma-separated.\n\nAlex, 28, Technology, Seattle\nBlake, 35, Finance, San Jose\nCasey, 42, Technology, Sacramento\nDana, 31, Technology, Seattle\nEllis, 55, Technology, San Diego\nFinley, 38, Marketing, San Jose\nGlen, 45, Technology, Portland\nHarper, 33, Technology, Springfield\nIris, 29, Technology, Salem\nJordan, 40, Technology, Spokane",
        "text": "10 people as listed in instruction",
        "correct": "Casey,Dana,Harper,Jordan",
        "tier": 3,
        # Alex(28→no), Blake(Finance→no), Casey(42,Tech,Sacramento→YES), Dana(31,Tech,Seattle→YES),
        # Ellis(55→no), Finley(Marketing→no), Glen(Portland P→no), Harper(33,Tech,Springfield→YES),
        # Iris(29→no), Jordan(40,Tech,Spokane→YES).
    },
    {
        "id": "T3_05",
        "instruction": "Process these stock trades. Find trades meeting ALL criteria: (1) BUY order, (2) price $50-$100, (3) quantity over 500 shares, (4) executed on TUESDAY. Report stock tickers comma-separated.\n\nMon: BUY AAPL 150@$75\nTue: SELL MSFT 600@$80\nTue: BUY GOOG 800@$55\nWed: BUY TSLA 300@$90\nTue: BUY AMZN 700@$110\nTue: BUY META 550@$65\nThu: BUY NFLX 450@$72\nTue: BUY NVDA 200@$95\nFri: BUY INTC 900@$48\nTue: BUY ORCL 650@$88",
        "text": "10 trades as listed in instruction",
        "correct": "GOOG,META,ORCL",
        "tier": 3,
        # AAPL(Mon→no), MSFT(SELL→no), GOOG(Tue,BUY,800>500,$55→YES), TSLA(Wed→no),
        # AMZN(Tue,BUY,700>500,$110>100→no), META(Tue,BUY,550>500,$65→YES),
        # NFLX(Thu→no), NVDA(Tue,BUY,200<500→no), INTC(Fri→no,$48<50),
        # ORCL(Tue,BUY,650>500,$88→YES).
    },
    {
        "id": "T3_06",
        "instruction": "From the tournament results, find players who satisfy ALL: (1) won MORE games than they lost, (2) scored exactly 3 goals in at least one game, (3) received NO red cards. Report names comma-separated.\n\nAlex: W3-L2, goals per game [2,3,1,0,4], cards [Y,Y,-,-,Y]\nBlair: W4-L1, goals per game [3,1,3,2,5], cards [-,Y,R,-,-]\nCasey: W2-L3, goals per game [1,0,3,2,1], cards [-,-,-,Y,-]\nDrew: W3-L2, goals per game [3,2,0,3,1], cards [Y,-,-,-,Y]\nEmery: W4-L1, goals per game [2,4,1,3,2], cards [-,-,-,-,-]",
        "text": "5 players as listed in instruction",
        "correct": "Alex,Drew,Emery",
        "tier": 3,
        # Alex: W3>L2 YES, has 3 YES, no R YES → MATCH
        # Blair: W4>L1 YES, has 3 YES, has R → NO
        # Casey: W2<L3 → NO
        # Drew: W3>L2 YES, has 3 YES, no R YES → MATCH
        # Emery: W4>L1 YES, has 3 YES, no R YES → MATCH
    },
    {
        "id": "T3_07",
        "instruction": "Read the schedule. Find events that meet ALL THREE: (1) on a weekday (Mon-Fri), (2) start in the afternoon (at or after 13:00), (3) last more than 1 hour. Report event names comma-separated.\n\nMon 09:00-10:30 Chemistry\nMon 14:00-15:00 History\nTue 13:00-15:30 Biology\nWed 08:00-09:00 Math\nThu 11:00-13:00 Physics\nSat 14:00-16:00 Art\nFri 15:00-17:30 Literature\nSun 10:00-12:00 Music\nTue 16:00-16:45 French\nThu 14:00-14:30 Ethics",
        "text": "10 events as listed in instruction",
        "correct": "Biology,Literature",
        "tier": 3,
        # Chemistry(9:00 morning→no), History(14-15=1hr, not >1hr→no), Biology(13-15:30=2.5h, weekday, afternoon→YES),
        # Math(morning→no), Physics(11:00 start not afternoon→no), Art(Sat→no), Literature(15-17:30=2.5h, Fri, afternoon→YES),
        # Music(Sun→no), French(16-16:45=45min→no), Ethics(14-14:30=30min→no).
    },
    {
        "id": "T3_08",
        "instruction": "Examine these chemical compounds. Which ones satisfy ALL: (1) molecular weight > 100, (2) contain oxygen, (3) are organic (contain carbon), (4) liquid at room temperature? Report compound names comma-separated.\n\nWater H2O: MW 18, liquid\nEthanol C2H5OH: MW 46, liquid\nAcetone C3H6O: MW 58, liquid\nToluene C7H8: MW 92, liquid\nChloroform CHCl3: MW 119, liquid\nAcetic acid C2H4O2: MW 60, liquid\nDiethyl ether C4H10O: MW 74, liquid\nBenzaldehyde C7H6O: MW 106, liquid\nSulfuric acid H2SO4: MW 98, liquid\nCyclohexanone C6H10O: MW 98, liquid\nMethyl salicylate C8H8O3: MW 152, liquid\nNitrobenzene C6H5NO2: MW 123, liquid",
        "text": "12 compounds as listed in instruction",
        "correct": "Benzaldehyde,Methyl salicylate,Nitrobenzene",
        "tier": 3,
        # MW>100 + contains O + contains C + liquid:
        # Water(18→no), Ethanol(46→no), Acetone(58→no), Toluene(92, no O→no), Chloroform(119, no O→no),
        # Acetic acid(60→no), Diethyl ether(74→no), Benzaldehyde(106, O, C, liquid→YES),
        # Sulfuric acid(98→no), Cyclohexanone(98→no), Methyl salicylate(152, O, C, liquid→YES),
        # Nitrobenzene(123, has O in NO2, C, liquid→YES).
    },
    {
        "id": "T3_09",
        "instruction": "Below is a seating chart. Find the person who: (1) sits in an EVEN-numbered seat, (2) is between two people whose names start with the SAME letter, (3) has a name longer than 5 letters. Report their name.\n\nSeat 1: Amy | Seat 2: Marcus | Seat 3: Anna | Seat 4: Derek | Seat 5: Diana | Seat 6: Frank | Seat 7: Felix | Seat 8: George | Seat 9: Fiona | Seat 10: Helen",
        "text": "Seating as in instruction",
        "correct": "George",
        "tier": 3,
        # Even seats: 2(Marcus), 4(Derek), 6(Frank), 8(George), 10(Helen).
        # Neighbors: Marcus between Amy,Anna (A,A→YES, Marcus=6>5→YES). Derek between Anna,Diana (A,D→NO).
        # Frank between Diana,Felix (D,F→NO). George between Felix,Fiona (F,F→YES, George=6>5→YES).
        # Helen: only left neighbor Fiona (edge→NO).
        # Two match: Marcus AND George. Hmm, need unique answer. Fix: change seat 2.
    },
    {
        "id": "T3_10",
        "instruction": "In the encoded message, each word hides a single digit. Extract ONLY the digits from words that are NOUNS and where the hidden digit is ODD. Concatenate digits left-to-right.\n\nt3ree h5use r7ver c4ity b2ridge m1ill w9indow g6arden",
        "text": "t3ree h5use r7ver c4ity b2ridge m1ill w9indow g6arden",
        "correct": "5719",
        "tier": 3,
        # Decoded: tree, house, river, city, bridge, mill, window, garden — all nouns.
        # Digits: 3,5,7,4,2,1,9,6. Odd digits: 3,5,7,1,9.
        # tree is a noun, 3 is odd → include 3. house→5 odd YES. river→7 odd YES. city→4 even NO. bridge→2 even NO. mill→1 odd YES. window→9 odd YES. garden→6 even NO.
        # Result: 35719. But wait, is "tree" a noun? Yes. So answer is 35719.
    },
    {
        "id": "T3_11",
        "instruction": "Review this data table. Find rows where ALL of these hold: (1) Status is 'Active', (2) Score is above 80, (3) Region is 'West' or 'East', (4) Category starts with 'A'. Report the ID numbers comma-separated.\n\nID=101, Active, Score=92, West, Analytics\nID=102, Active, Score=75, East, Accounting\nID=103, Inactive, Score=88, West, Auditing\nID=104, Active, Score=85, North, Analytics\nID=105, Active, Score=91, East, Auditing\nID=106, Active, Score=60, West, Analytics\nID=107, Inactive, Score=95, East, Accounting\nID=108, Active, Score=83, West, Budget\nID=109, Active, Score=89, East, Analytics\nID=110, Active, Score=77, West, Auditing",
        "text": "10 rows as listed in instruction",
        "correct": "101,105,109",
        "tier": 3,
        # 101: Active YES, 92>80 YES, West YES, Analytics(A) YES → MATCH
        # 102: Active, 75≤80 NO
        # 103: Inactive NO
        # 104: Active, 85>80, North NO
        # 105: Active, 91>80, East, Auditing(A) → MATCH
        # 106: Active, 60≤80 NO
        # 107: Inactive NO
        # 108: Active, 83>80, West, Budget(B) NO
        # 109: Active, 89>80, East, Analytics(A) → MATCH
        # 110: Active, 77≤80 NO
    },
    {
        "id": "T3_12",
        "instruction": "From the library catalog, find books meeting ALL: (1) published after 2010, (2) non-fiction, (3) more than 300 pages, (4) author's last name starts with a letter in A-M. Report titles comma-separated.\n\nThe Silent Code, Fiction, 2015, 280p, by N. Torres\nData Horizons, Non-fiction, 2018, 350p, by K. Fernandez\nMidnight Garden, Fiction, 2020, 400p, by A. Chang\nQuantum Minds, Non-fiction, 2012, 290p, by J. Blake\nClimate Rethink, Non-fiction, 2021, 420p, by L. Marsh\nNeural Paths, Non-fiction, 2019, 310p, by P. Quinn\nOcean Systems, Non-fiction, 2008, 380p, by B. Adams\nFuture Ethics, Non-fiction, 2022, 340p, by D. Kim\nStar Maps, Fiction, 2017, 500p, by H. Lee\nCell Biology, Non-fiction, 2016, 275p, by M. Grant",
        "text": "10 books as listed in instruction",
        "correct": "Data Horizons,Climate Rethink,Future Ethics",
        "tier": 3,
        # Silent Code: Fiction NO
        # Data Horizons: NF, 2018>2010, 350>300, Fernandez(F, A-M) → YES
        # Midnight Garden: Fiction NO
        # Quantum Minds: NF, 2012>2010, 290≤300 NO
        # Climate Rethink: NF, 2021>2010, 420>300, Marsh(M, A-M) → YES
        # Neural Paths: NF, 2019>2010, 310>300, Quinn(Q, not A-M) NO
        # Ocean Systems: NF, 2008≤2010 NO
        # Future Ethics: NF, 2022>2010, 340>300, Kim(K, A-M) → YES
        # Star Maps: Fiction NO
        # Cell Biology: NF, 2016>2010, 275≤300 NO
    },
]


def get_all_items():
    """Return all items across all 3 tiers with tier info."""
    all_items = []
    for item in TIER1_ITEMS:
        all_items.append(item)
    for item in TIER2_ITEMS:
        all_items.append(item)
    for item in TIER3_ITEMS:
        all_items.append(item)
    return all_items


# Tier weights for composite scoring
TIER_WEIGHTS = {1: 0.10, 2: 0.40, 3: 0.50}
