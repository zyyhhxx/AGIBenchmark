"""
Selective Attention Benchmark — Tiered Item Set v2

Three tiers based on Treisman & Gelade (1980) feature integration theory:
  Tier 1 (Pop-out): Single feature distinguishes target from distractors
  Tier 2 (Feature Conjunction): Two features must be combined to identify target
  Tier 3 (Triple Conjunction + High Similarity): Three+ features with near-miss distractors

Cognitive basis:
- Treisman & Gelade (1980): Feature integration theory
- Wolfe (1994): Guided search model — conjunction search is serial
- Duncan & Humphreys (1989): Target-distractor similarity modulates difficulty
"""

# ─── TIER 1: POP-OUT SEARCH (easy, weight=0.10) ────────────────────
# Single-feature discrimination. Models should ace these.
TIER1_ITEMS = [
    {
        "id": "T1_01",
        "instruction": "In the grid below, find the ONE item that is different from all others. Report ONLY its label (e.g., 'D7').",
        "text": (
            "Grid (rows A-D, columns 1-8):\n"
            "A1:○ A2:○ A3:○ A4:○ A5:○ A6:○ A7:○ A8:○\n"
            "B1:○ B2:○ B3:○ B4:★ B5:○ B6:○ B7:○ B8:○\n"
            "C1:○ C2:○ C3:○ C4:○ C5:○ C6:○ C7:○ C8:○\n"
            "D1:○ D2:○ D3:○ D4:○ D5:○ D6:○ D7:○ D8:○"
        ),
        "correct": "B4",
        "tier": 1,
    },
    {
        "id": "T1_02",
        "instruction": "Which word in the list is NOT an animal? Report ONLY that word.",
        "text": "eagle, salmon, granite, dolphin, cobra, hawk, whale, panther, sparrow, otter, tiger, falcon, badger, lynx, moose",
        "correct": "granite",
        "tier": 1,
    },
    {
        "id": "T1_03",
        "instruction": "Find the ONE number in this sequence that is NOT a prime. Report just the number.",
        "text": "2, 3, 5, 7, 11, 13, 15, 17, 19, 23, 29, 31, 37, 41, 43",
        "correct": "15",
        "tier": 1,
    },
    {
        "id": "T1_04",
        "instruction": "Below are 16 three-letter codes. One has a DIGIT instead of all letters. Which code?",
        "text": "ABC DEF GHI JKL MNO PQR STU VWX YZA BCD EFG H2J KLM NOP QRS TUV",
        "correct": "H2J",
        "tier": 1,
    },
]

# ─── TIER 2: FEATURE CONJUNCTION (medium, weight=0.40) ─────────────
# Must combine two features to identify target. Distractors share one feature.
TIER2_ITEMS = [
    {
        "id": "T2_01",
        "instruction": (
            "Below is a grid of colored shapes. Each item is [color]-[shape].\n"
            "Find ALL items that are BOTH red AND X-shaped. Report their labels separated by commas."
        ),
        "text": (
            "Grid:\n"
            "A1:red-O  A2:blue-X  A3:red-X  A4:green-O  A5:blue-O  A6:red-O  A7:blue-X  A8:green-X\n"
            "B1:blue-O  B2:red-X  B3:green-O  B4:blue-X  B5:red-O  B6:green-X  B7:red-O  B8:blue-O\n"
            "C1:green-X  C2:red-O  C3:blue-X  C4:red-O  C5:green-O  C6:blue-O  C7:red-X  C8:green-O"
        ),
        "correct": "A3,B2,C7",
        "accept_any_order": True,
        "tier": 2,
    },
    {
        "id": "T2_02",
        "instruction": (
            "Each item below has a SIZE and a LETTER. Find all items that are LARGE and contain the letter 'K'. "
            "Report their IDs separated by commas."
        ),
        "text": (
            "Items:\n"
            "1: LARGE-M  2: small-K  3: LARGE-K  4: small-M  5: LARGE-B  6: small-K  7: LARGE-K\n"
            "8: small-B  9: LARGE-M  10: small-K  11: LARGE-B  12: LARGE-K  13: small-M  14: LARGE-M\n"
            "15: small-K  16: LARGE-B  17: small-M  18: LARGE-K  19: small-B  20: LARGE-M"
        ),
        "correct": "3,7,12,18",
        "accept_any_order": True,
        "tier": 2,
    },
    {
        "id": "T2_03",
        "instruction": (
            "Each entry is [direction]-[number]. Find ALL entries where direction is NORTH and number is ODD. "
            "Report their IDs."
        ),
        "text": (
            "1:NORTH-4  2:SOUTH-3  3:EAST-7  4:NORTH-7  5:WEST-2  6:SOUTH-5  7:NORTH-2  8:EAST-1\n"
            "9:NORTH-9  10:WEST-4  11:SOUTH-8  12:NORTH-6  13:EAST-3  14:NORTH-1  15:WEST-7  16:SOUTH-2\n"
            "17:NORTH-3  18:EAST-6  19:SOUTH-1  20:NORTH-8  21:WEST-5  22:NORTH-5  23:EAST-2  24:SOUTH-4"
        ),
        "correct": "4,9,14,17,22",
        "accept_any_order": True,
        "tier": 2,
    },
    {
        "id": "T2_04",
        "instruction": (
            "Each word below has a prefix and a suffix. Find all words with prefix 'UN-' AND suffix '-LY'. "
            "List them separated by commas."
        ),
        "text": (
            "unlikely, unhappy, poorly, unkindly, unwise, unfairly, barely, undoubtedly, unreal, "
            "unfairness, namely, unusually, unwisely, unfit, costly, ungodly, unruly, unsightly"
        ),
        "correct": "unlikely,unkindly,unfairly,undoubtedly,unusually,unwisely,ungodly",
        "accept_any_order": True,
        "tier": 2,
    },
    {
        "id": "T2_05",
        "instruction": (
            "Below are 20 items formatted as [shape]-[color]-[size]. "
            "Find ALL items where shape is TRIANGLE and color is GREEN. Report their positions (1-20)."
        ),
        "text": (
            "1:circle-green-large  2:triangle-red-small  3:square-green-large  4:triangle-green-small\n"
            "5:circle-red-large  6:triangle-blue-small  7:square-green-small  8:triangle-green-large\n"
            "9:circle-blue-small  10:triangle-red-large  11:square-red-small  12:triangle-green-small\n"
            "13:circle-green-small  14:square-blue-large  15:triangle-green-large  16:circle-red-small\n"
            "17:triangle-blue-large  18:square-green-large  19:triangle-green-small  20:circle-blue-large"
        ),
        "correct": "4,8,12,15,19",
        "accept_any_order": True,
        "tier": 2,
    },
    {
        "id": "T2_06",
        "instruction": (
            "Below are employee records: [department]-[seniority]. "
            "Count how many are in ENGINEERING with SENIOR seniority. Report just the count."
        ),
        "text": (
            "1:engineering-junior  2:marketing-senior  3:engineering-senior  4:sales-junior\n"
            "5:engineering-mid  6:marketing-junior  7:engineering-senior  8:sales-senior\n"
            "9:engineering-junior  10:marketing-mid  11:engineering-senior  12:sales-mid\n"
            "13:marketing-senior  14:engineering-mid  15:engineering-senior  16:sales-junior\n"
            "17:engineering-junior  18:marketing-senior  19:engineering-senior  20:sales-senior"
        ),
        "correct": "5",
        "tier": 2,
    },
    {
        "id": "T2_07",
        "instruction": (
            "Each item is a [consonant/vowel]-[uppercase/lowercase] pair. "
            "Find all VOWELS that are UPPERCASE. Report them separated by commas."
        ),
        "text": (
            "b a T E r I s O u P Q A d e F G h i J K l m N o U v w X y z "
            "A B c D E f g H I j k L M n O p q R s T U v W x Y z"
        ),
        "correct": "E,I,O,A,A,E,I,O,U",
        "accept_any_order": True,
        "tier": 2,
    },
    {
        "id": "T2_08",
        "instruction": (
            "Below are 24 timestamps in HH:MM format. Count how many are BOTH in the PM (13:00-23:59) "
            "AND have minutes that are multiples of 15 (00, 15, 30, 45). Report the count."
        ),
        "text": (
            "08:15, 13:30, 09:45, 14:00, 22:15, 11:30, 16:45, 07:00, "
            "19:15, 12:30, 20:00, 05:45, 15:30, 23:45, 10:15, 17:00, "
            "21:30, 06:00, 18:15, 08:30, 14:45, 03:15, 16:00, 22:30"
        ),
        "correct": "14",
        "tier": 2,
    },
]

# ─── TIER 3: TRIPLE CONJUNCTION + HIGH SIMILARITY (hard, weight=0.50) ───
# Three features must be combined; distractors match on 2/3 features.
# Requires careful serial search through many near-miss items.
TIER3_ITEMS = [
    {
        "id": "T3_01",
        "instruction": (
            "Each item has three features: [color]-[shape]-[pattern]. "
            "Find ALL items that are RED, CIRCLE, and STRIPED. "
            "Distractors may match 2 of 3 features. Report IDs only."
        ),
        "text": (
            " 1:red-circle-solid     2:red-square-striped   3:blue-circle-striped  4:red-circle-striped\n"
            " 5:red-circle-dotted    6:green-circle-striped  7:red-triangle-striped  8:red-circle-striped\n"
            " 9:blue-circle-solid   10:red-square-solid    11:red-circle-solid    12:green-square-striped\n"
            "13:red-circle-striped  14:blue-circle-striped 15:red-triangle-dotted 16:red-circle-dotted\n"
            "17:green-circle-striped 18:red-square-striped  19:red-circle-striped  20:blue-circle-striped\n"
            "21:red-triangle-striped 22:red-circle-solid    23:green-circle-dotted 24:red-circle-striped"
        ),
        "correct": "4,8,13,19,24",
        "accept_any_order": True,
        "tier": 3,
    },
    {
        "id": "T3_02",
        "instruction": (
            "Each code has format: [letter][digit][letter]. "
            "Find ALL codes where the first letter is 'A', the digit is '3', AND the last letter is 'X'. "
            "Report the codes."
        ),
        "text": (
            "A3Y  B3X  A3X  A2X  A3Z  C3X  A3X  A4X  B3Y  A3X\n"
            "A3W  A5X  B3X  A3Y  C3Y  A3X  D3X  A3Z  A1X  A3X\n"
            "B3X  A3V  A3X  A7X  C3X  A3Y  A3X  A3W  B3X  A9X"
        ),
        "correct": "A3X,A3X,A3X,A3X,A3X,A3X,A3X",
        "correct_count": 7,
        "tier": 3,
    },
    {
        "id": "T3_03",
        "instruction": (
            "Below are 24 employee records: [dept]-[level]-[location]. "
            "How many employees are in ENGINEERING, at SENIOR level, in BUILDING-A? Report the count."
        ),
        "text": (
            " 1:engineering-senior-building-B   2:marketing-senior-building-A   3:engineering-junior-building-A\n"
            " 4:engineering-senior-building-A   5:sales-senior-building-A       6:engineering-senior-building-C\n"
            " 7:engineering-mid-building-A      8:engineering-senior-building-A  9:marketing-senior-building-B\n"
            "10:engineering-senior-building-C  11:sales-junior-building-A      12:engineering-senior-building-A\n"
            "13:engineering-senior-building-B  14:marketing-mid-building-A     15:engineering-junior-building-B\n"
            "16:engineering-senior-building-A  17:sales-senior-building-C      18:engineering-mid-building-A\n"
            "19:marketing-senior-building-A    20:engineering-senior-building-B 21:engineering-senior-building-A\n"
            "22:sales-mid-building-A           23:engineering-senior-building-C 24:engineering-senior-building-A"
        ),
        "correct": "6",
        "tier": 3,
    },
    {
        "id": "T3_04",
        "instruction": (
            "Each entry has [nationality]-[profession]-[age_group]. "
            "Find ALL entries that are FRENCH, ENGINEER, and YOUNG. Report their numbers."
        ),
        "text": (
            " 1:french-doctor-young       2:german-engineer-young     3:french-engineer-old\n"
            " 4:french-engineer-young     5:british-engineer-young    6:french-teacher-young\n"
            " 7:german-doctor-old         8:french-engineer-middle    9:french-engineer-young\n"
            "10:british-doctor-young     11:french-teacher-old       12:german-engineer-middle\n"
            "13:french-engineer-young    14:french-doctor-middle     15:british-engineer-old\n"
            "16:german-teacher-young     17:french-engineer-old      18:french-engineer-young\n"
            "19:british-teacher-middle   20:french-doctor-young      21:german-engineer-young\n"
            "22:french-engineer-young    23:british-engineer-middle  24:french-teacher-young"
        ),
        "correct": "4,9,13,18,22",
        "accept_any_order": True,
        "tier": 3,
    },
    {
        "id": "T3_05",
        "instruction": (
            "Each item has four features: [material]-[color]-[size]-[shape]. "
            "Find ALL items matching: WOOD, BROWN, LARGE, CUBE. Report their numbers.\n"
            "Warning: many near-misses share 3 of 4 features."
        ),
        "text": (
            " 1:wood-brown-large-sphere    2:metal-brown-large-cube     3:wood-brown-small-cube\n"
            " 4:wood-brown-large-cube      5:wood-red-large-cube        6:wood-brown-large-cylinder\n"
            " 7:plastic-brown-large-cube   8:wood-brown-large-cube      9:wood-brown-medium-cube\n"
            "10:metal-brown-large-cube    11:wood-brown-large-sphere   12:wood-brown-large-cube\n"
            "13:wood-green-large-cube     14:wood-brown-large-cylinder 15:plastic-brown-large-cube\n"
            "16:wood-brown-large-cube     17:wood-brown-small-cube     18:metal-brown-large-cube\n"
            "19:wood-brown-large-pyramid  20:wood-brown-large-cube     21:wood-red-large-cube\n"
            "22:wood-brown-medium-cube    23:wood-brown-large-cube     24:plastic-brown-small-cube"
        ),
        "correct": "4,8,12,16,20,23",
        "accept_any_order": True,
        "tier": 3,
    },
    {
        "id": "T3_06",
        "instruction": (
            "Below is a passage. Count the EXACT number of times the trigram 'the' appears as a COMPLETE word "
            "(not as part of 'these', 'other', 'them', 'there', 'then', 'their', 'they', 'theory', 'therefore', 'thermal'). "
            "Report just the count."
        ),
        "text": (
            "The theoretical framework shows the thermal properties are therefore relevant to the "
            "themes they explored. Furthermore, the other researchers then noted that their theory "
            "about the thermostat was the basis for the thesis. These thermodynamic models use the "
            "theorem, and the others agreed the method was the best theoretical approach. Then the "
            "therapist and the theologian reviewed the theory behind the therapeutic methods used in "
            "the thesis. They also noted the thermal readings from the thermometer near the theater."
        ),
        "correct": "16",
        "tier": 3,
    },
    {
        "id": "T3_07",
        "instruction": (
            "Below are 30 three-digit codes. Count how many satisfy ALL THREE conditions:\n"
            "1) First digit is even (0,2,4,6,8)\n"
            "2) Second digit is greater than 5\n"
            "3) Third digit is a prime (2,3,5,7)\n"
            "Report just the count."
        ),
        "text": (
            "483 297 672 891 463 285 873 692 457 283\n"
            "693 472 867 291 483 672 897 263 493 873\n"
            "267 493 872 691 483 273 892 467 293 672"
        ),
        "correct": "7",
        "tier": 3,
    },
    {
        "id": "T3_08",
        "instruction": (
            "Below are sentences. For EACH sentence, determine if it has ALL THREE properties:\n"
            "1) Contains exactly 7 words\n"
            "2) Starts with a vowel (A/E/I/O/U)\n"
            "3) Ends with a period (not ! or ?)\n"
            "How many sentences satisfy ALL THREE? Report the count."
        ),
        "text": (
            "A. Elephants are truly magnificent creatures in nature.\n"
            "B. I really enjoy swimming in the ocean!\n"
            "C. Under the bridge sat a lonely cat.\n"
            "D. Amazing discoveries happen every single day here.\n"
            "E. Ordinary people can achieve extraordinary things together.\n"
            "F. Is there anything more beautiful than sunset?\n"
            "G. Every morning brings a chance for renewal.\n"
            "H. Once upon a time lived seven dwarfs.\n"
            "I. All good things must come to end.\n"
            "J. Incredible feats of strength were displayed today."
        ),
        "correct": "4",
        "tier": 3,
    },
    {
        "id": "T3_09",
        "instruction": (
            "Each item is a playing card: [rank][suit]. Suits: H=hearts, D=diamonds, S=spades, C=clubs.\n"
            "Count how many cards are: RED suit (H or D) AND face card (J, Q, K) AND NOT hearts.\n"
            "That means: diamonds AND face card. Report the count."
        ),
        "text": (
            "2H  KD  JS  QH  3C  JD  8H  KS  QD  5D  JH  4C  KH  7S  QC  2D\n"
            "9H  JD  3S  KD  6C  QH  8D  JC  KH  5S  QD  4H  7C  JH  2S  KD\n"
            "9C  QD  6H  3D  KS  JD  8C  QH  5H  KD  2C  JD  7H  QD  4S  9D"
        ),
        "correct": "12",
        "tier": 3,
    },
    {
        "id": "T3_10",
        "instruction": (
            "Read these overlapping instructions and follow ONLY the FINAL instruction:\n\n"
            "Instruction 1: Count the vowels in the text below.\n"
            "Instruction 2: Actually, count the consonants instead.\n"
            "Instruction 3: No wait, count ONLY the letters that appear exactly twice in the text.\n"
            "Instruction 4: Final instruction — list the letters that appear exactly THREE times. Report them alphabetically."
        ),
        "text": "abracadabra",
        "correct": "b",
        "tier": 3,
    },
]


def get_all_items():
    """Return all items organized by tier."""
    return {
        1: TIER1_ITEMS,
        2: TIER2_ITEMS,
        3: TIER3_ITEMS,
    }
