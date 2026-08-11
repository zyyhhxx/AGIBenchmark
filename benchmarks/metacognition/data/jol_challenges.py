"""
JOL v2: Novel Learning Challenges

Each challenge is a mini-learning task with:
- lesson: Material to study (novel rules/systems/patterns)
- preview: Brief description shown BEFORE studying (for JOL prediction)
- test_questions: Questions to test comprehension after studying
- difficulty: 1-5 (calibrated to create genuine variance in model performance)

Design principles:
- All material is NOVEL (not in training data)
- Challenges range from trivially learnable to genuinely hard
- Harder challenges have: more rules, exceptions, counterintuitive logic,
  multi-step inference, or ambiguous specifications
- Tests require APPLICATION, not mere repetition
"""

LEARNING_CHALLENGES = [
    # === DIFFICULTY 1: Simple, clear rules ===
    {
        "id": "color_mix",
        "preview": "Learn a 3-rule color mixing system and predict one result",
        "difficulty": 1,
        "lesson": (
            "In the Chromax system:\n"
            "- Mixing RED + BLUE = PURPLE\n"
            "- Mixing BLUE + YELLOW = GREEN\n"
            "- Mixing RED + YELLOW = ORANGE\n"
            "- Mixing any color with WHITE = LIGHT version of that color"
        ),
        "test_questions": [
            {"q": "In Chromax, what do you get from mixing BLUE + YELLOW + WHITE?",
             "a": "light green"},
        ],
    },
    {
        "id": "greeting_rules",
        "preview": "Learn greeting conventions for a fictional culture",
        "difficulty": 1,
        "lesson": (
            "In Valdori culture:\n"
            "- Greet elders by touching your forehead\n"
            "- Greet peers by clasping both hands\n"
            "- Greet children by waving with your left hand\n"
            "- Anyone wearing a blue sash is always greeted as an elder regardless of age"
        ),
        "test_questions": [
            {"q": "How do you greet a young child wearing a blue sash in Valdori culture?",
             "a": "touching your forehead"},
        ],
    },
    {
        "id": "simple_cipher",
        "preview": "Learn a letter substitution cipher with 4 mappings",
        "difficulty": 1,
        "lesson": (
            "In Kryptex code:\n"
            "- A becomes Z, B becomes Y, C becomes X, D becomes W\n"
            "- All other letters stay the same"
        ),
        "test_questions": [
            {"q": "Encode 'BACK' in Kryptex code", "a": "YZXK"},
        ],
    },
    {
        "id": "animal_sounds",
        "preview": "Learn which sounds 4 fictional animals make",
        "difficulty": 1,
        "lesson": (
            "On Planet Zenn:\n"
            "- A Glorb says 'meep meep'\n"
            "- A Schniff says 'wub wub'\n"
            "- A Trelk says 'boop'\n"
            "- A Vennox says 'zzzzip'"
        ),
        "test_questions": [
            {"q": "You hear 'wub wub' followed by 'boop' on Planet Zenn. What animals did you encounter, in order?",
             "a": "schniff then trelk"},
        ],
    },

    # === DIFFICULTY 2: Moderate complexity, some inference needed ===
    {
        "id": "tax_system",
        "preview": "Learn a 5-bracket tax calculation system and compute a tax amount",
        "difficulty": 2,
        "lesson": (
            "Novaria Tax Brackets (applied progressively):\n"
            "- First 100 gold: 0% tax\n"
            "- 101-500 gold: 10% tax\n"
            "- 501-1000 gold: 20% tax\n"
            "- 1001-5000 gold: 30% tax\n"
            "- Above 5000 gold: 50% tax\n\n"
            "Tax is progressive: each bracket only applies to income within that range."
        ),
        "test_questions": [
            {"q": "How much tax does someone earning 600 gold pay in Novaria?",
             "a": "60"},
        ],
    },
    {
        "id": "kinship_terms",
        "preview": "Learn kinship terminology in a fictional language and identify relationships",
        "difficulty": 2,
        "lesson": (
            "In Talvek kinship:\n"
            "- 'doma' = parent (any gender)\n"
            "- 'filka' = child (any gender)\n"
            "- 'sibro' = sibling\n"
            "- Compound: X-Y means 'X of Y' (e.g., doma-filka = parent of child = grandparent)\n"
            "- 'doma-doma' = grandparent\n"
            "- 'filka-sibro' = child of sibling = nephew/niece"
        ),
        "test_questions": [
            {"q": "What is a 'sibro-doma' in Talvek kinship? Describe the relationship.",
             "a": "sibling of parent"},
        ],
    },
    {
        "id": "sequence_rule",
        "preview": "Learn a number transformation rule and apply it to a new input",
        "difficulty": 2,
        "lesson": (
            "The Fenwick Transform:\n"
            "- Take a sequence of numbers\n"
            "- Replace each number with the sum of itself and all numbers to its left\n"
            "- Example: [2, 3, 1] becomes [2, 5, 6]\n"
            "  (2 stays 2, 3 becomes 2+3=5, 1 becomes 2+3+1=6)"
        ),
        "test_questions": [
            {"q": "Apply the Fenwick Transform to [4, 1, 3, 2]",
             "a": "4 5 8 10"},
        ],
    },
    {
        "id": "priority_queue",
        "preview": "Learn task scheduling rules with priorities and dependencies",
        "difficulty": 2,
        "lesson": (
            "Zenith Scheduler Rules:\n"
            "- Tasks have priority 1 (highest) to 5 (lowest)\n"
            "- Higher priority tasks run first\n"
            "- If same priority: alphabetical order\n"
            "- A task with a dependency must wait until its dependency completes\n"
            "- Dependencies override priority (even high-priority waits)"
        ),
        "test_questions": [
            {"q": "Tasks: A(pri=1), B(pri=2, depends on C), C(pri=3), D(pri=2). What order do they execute?",
             "a": "A, D, C, B"},
        ],
    },
    {
        "id": "potion_brewing",
        "preview": "Learn potion recipes with ingredient interactions",
        "difficulty": 2,
        "lesson": (
            "Alchemist's Rules:\n"
            "- Healing Potion = Water + Moonpetal + Heat\n"
            "- Strength Potion = Water + Ironroot + Stir\n"
            "- If Moonpetal and Ironroot are in the same mixture, it becomes Poison\n"
            "- Heat must be applied AFTER all ingredients are added\n"
            "- Adding Starleaf to any potion doubles its duration"
        ),
        "test_questions": [
            {"q": "You add Water, Moonpetal, Ironroot, then Heat. What do you get?",
             "a": "poison"},
        ],
    },

    # === DIFFICULTY 3: Complex multi-step, exceptions, or tricky logic ===
    {
        "id": "voting_system",
        "preview": "Learn a complex ranked-choice voting system with elimination rules",
        "difficulty": 3,
        "lesson": (
            "Quorum Voting Rules:\n"
            "- Each voter ranks all candidates 1st, 2nd, 3rd\n"
            "- Count first-choice votes. If any candidate has >50%, they win.\n"
            "- If no majority: eliminate the candidate with FEWEST first-choice votes\n"
            "- Eliminated candidate's voters transfer to their 2nd choice\n"
            "- EXCEPTION: If a candidate is last-ranked by more than 40% of voters, "
            "they are eliminated first regardless of first-choice count\n"
            "- Tie in elimination: eliminate the one with more last-place votes"
        ),
        "test_questions": [
            {"q": "5 voters rank 3 candidates (A,B,C). Rankings: "
             "Voter 1: A>B>C, Voter 2: A>C>B, Voter 3: B>C>A, "
             "Voter 4: C>B>A, Voter 5: C>A>B. "
             "Who wins under Quorum rules?",
             "a": "C"},
        ],
    },
    {
        "id": "transport_network",
        "preview": "Learn routing rules in a fictional transport network with conditional paths",
        "difficulty": 3,
        "lesson": (
            "Nexus Transit Network:\n"
            "- 5 stations: Alpha, Beta, Gamma, Delta, Epsilon\n"
            "- Direct routes: Alpha-Beta (2 min), Beta-Gamma (3 min), "
            "Gamma-Delta (1 min), Delta-Epsilon (4 min), Alpha-Delta (6 min)\n"
            "- Express route: Alpha to Epsilon direct (5 min) but ONLY during Peak hours\n"
            "- During Off-Peak: Alpha to Epsilon requires transfers\n"
            "- If any station on your route is 'congested', add 2 min per congested station passed through\n"
            "- Cannot pass through a congested station more than once"
        ),
        "test_questions": [
            {"q": "During Off-Peak with Beta congested, what is the fastest route "
             "from Alpha to Epsilon and how many minutes?",
             "a": "Alpha to Delta to Epsilon, 10 minutes"},
        ],
    },
    {
        "id": "grammar_system",
        "preview": "Learn verb conjugation rules in a constructed language with irregular forms",
        "difficulty": 3,
        "lesson": (
            "Velansi Verb Conjugation:\n"
            "- Base form: verb root (e.g., 'tal' = to go)\n"
            "- Present tense: add '-ek' (talek = going)\n"
            "- Past tense: add '-um' (talum = went)\n"
            "- Future tense: add '-ira' (talira = will go)\n"
            "- Negation: prefix 'ne-' (netalek = not going)\n"
            "- EXCEPTION: If root ends in vowel, drop the vowel before adding suffix\n"
            "  (e.g., 'vire' becomes 'virek' not 'vireek')\n"
            "- EXCEPTION: Negation of past tense uses 'nu-' instead of 'ne-'\n"
            "  (e.g., nutalum = did not go)"
        ),
        "test_questions": [
            {"q": "How do you say 'will not write' in Velansi if 'skrive' means 'to write'?",
             "a": "neskrivira"},
        ],
    },
    {
        "id": "card_game",
        "preview": "Learn scoring rules for a card game with combos and penalties",
        "difficulty": 3,
        "lesson": (
            "Blitz Card Scoring:\n"
            "- Number cards (1-9): face value in points\n"
            "- Three of a kind: triple the sum (e.g., three 5s = 45 not 15)\n"
            "- Run of 3+ consecutive numbers: +10 bonus per card in run\n"
            "- A card can count toward EITHER a three-of-a-kind OR a run, not both\n"
            "- Special: any 6 or 8 in your hand (adjacent to 7) gets doubled\n"
            "- PENALTY: if you have no combos (no runs, no three-of-a-kind), halve total"
        ),
        "test_questions": [
            {"q": "Hand: 5, 6, 7, 7, 7. What's the maximum score? "
             "Show which combo you use.",
             "a": "80"},
        ],
    },

    # === DIFFICULTY 4: High complexity, many interacting rules ===
    {
        "id": "ecosystem_sim",
        "preview": "Learn predator-prey-resource rules and predict population outcomes after 1 cycle",
        "difficulty": 4,
        "lesson": (
            "EcoSim Population Rules (per cycle):\n"
            "- Species: Grazers (G), Hunters (H), Plants (P)\n"
            "- Plants grow: P_new = P * 1.5 (rounded down), max 100\n"
            "- Grazers eat: each G consumes 2P. If P < 2*G, excess G die (keep P//2 grazers).\n"
            "- Surviving G reproduce: G_new = G + G//3\n"
            "- Hunters eat: each H consumes 1G. If G < H, excess H die (keep G hunters).\n"
            "- Surviving H reproduce: H_new = H + H//4\n"
            "- Order of operations: Plants grow, then Grazers eat, then Grazers reproduce, "
            "then Hunters eat, then Hunters reproduce\n"
            "- All division is integer (floor)"
        ),
        "test_questions": [
            {"q": "Start: P=20, G=8, H=3. What are P, G, H after 1 full cycle?",
             "a": "P=14, G=7, H=3"},
        ],
    },
    {
        "id": "type_system",
        "preview": "Learn type inference rules for a mini programming language",
        "difficulty": 4,
        "lesson": (
            "MiniType Language Rules:\n"
            "- Literals: numbers are Int, quoted strings are Str, true/false are Bool\n"
            "- Operator +: Int+Int gives Int, Str+Str gives Str (concat), mixed gives Error\n"
            "- Comparison (==, <, >): same-type gives Bool, mixed-type gives Error\n"
            "- 'if COND then A else B': COND must be Bool, A and B must have same type, "
            "result has that type\n"
            "- 'let x = EXPR in BODY': x has type of EXPR within BODY\n"
            "- Functions: 'fn(x: T) -> BODY' has type T -> ReturnType(BODY)\n"
            "- Calling f(arg): arg type must match f's parameter type"
        ),
        "test_questions": [
            {"q": "What is the type of: let f = fn(x: Int) -> x + 1 in f(3) == 4",
             "a": "Bool"},
        ],
    },
    {
        "id": "calendar_system",
        "preview": "Learn a non-standard calendar system and compute day-of-week",
        "difficulty": 4,
        "lesson": (
            "The Hexian Calendar:\n"
            "- 6 days per week: Solday, Lunday, Marday, Merday, Jovday, Venday\n"
            "- 5 weeks per month (30 days per month)\n"
            "- 12 months per year (360 days)\n"
            "- Year 1, Day 1 = Solday\n"
            "- Every 6th year is a 'Leap Year' with an extra day (Nullday) at end of year\n"
            "- Nullday doesn't count as part of any week (next year starts with next weekday)\n"
            "- Month names: Prim, Sek, Tert, Quart, Quint, Sext, Sept, Oct, Nov, Dec, Undec, Duodec"
        ),
        "test_questions": [
            {"q": "What day of the week is Year 2, Month Prim, Day 1?",
             "a": "Solday"},
        ],
    },
    {
        "id": "logic_gates",
        "preview": "Learn a custom logic gate circuit with a delay element and compute output after 2 cycles",
        "difficulty": 4,
        "lesson": (
            "Circuit Rules:\n"
            "- Gates: AND, OR, NOT, XOR (standard logic)\n"
            "- DELAY gate: outputs the PREVIOUS cycle's input (starts at 0 on cycle 1)\n"
            "- All gates compute simultaneously per cycle\n"
            "- Inputs A and B are constant.\n\n"
            "Circuit:\n"
            "- Wire1 = A AND B\n"
            "- Wire2 = A XOR B\n"
            "- Wire3 = DELAY(Wire2)\n"
            "- Output = Wire1 OR Wire3"
        ),
        "test_questions": [
            {"q": "If A=1, B=0 (constant), what is Output after cycle 1 and after cycle 2?",
             "a": "cycle 1: 0, cycle 2: 1"},
        ],
    },

    # === DIFFICULTY 5: Very complex, counterintuitive, or multi-constraint ===
    {
        "id": "auction_mechanism",
        "preview": "Learn a sealed-bid auction with counterintuitive winner selection and penalty rules",
        "difficulty": 5,
        "lesson": (
            "Nexus Auction Rules:\n"
            "- Players submit sealed bids (integers 1-100)\n"
            "- Winner: LOWEST UNIQUE bid (not the highest!)\n"
            "- If no unique bid exists, the MOST COMMON bid wins, split equally\n"
            "- PENALTY: if your bid is within 5 of another player's bid, you pay a proximity fee of 3 coins\n"
            "- Proximity fee is paid regardless of winning\n"
            "- Winner's prize equals the SECOND-lowest unique bid value\n"
            "- If only one unique bid exists, winner's prize = their own bid times 2\n"
            "- Net prize = prize minus any proximity fees the winner owes"
        ),
        "test_questions": [
            {"q": "Bids: Player A=10, Player B=10, Player C=25, Player D=30, Player E=7. "
             "Who wins and what is their net prize?",
             "a": "Player E wins, net prize 22"},
        ],
    },
    {
        "id": "resource_allocation",
        "preview": "Learn multi-constraint resource allocation with priority overrides and min/max rules",
        "difficulty": 5,
        "lesson": (
            "Council Resource Allocation:\n"
            "- 100 units to distribute among 4 districts: North, South, East, West\n"
            "- Base allocation: proportional to population (N=30%, S=25%, E=20%, W=25%)\n"
            "- NEED modifier: districts in 'crisis' get 1.5x their base share; "
            "other districts reduced proportionally to maintain total=100\n"
            "- MINIMUM rule: no district gets less than 15 units\n"
            "- MAXIMUM rule: no district gets more than 35 units\n"
            "- Constraint resolution order: apply crisis first, then check min/max, "
            "then redistribute excess/deficit proportionally among unconstrained districts"
        ),
        "test_questions": [
            {"q": "East is in crisis. Calculate the final allocation for each district (round to integers, total=100).",
             "a": "N=26, S=22, E=30, W=22"},
        ],
    },
    {
        "id": "state_machine",
        "preview": "Learn a state machine with 4 states, 3 inputs, and output rules; trace execution",
        "difficulty": 5,
        "lesson": (
            "DFA-X State Machine:\n"
            "- States: S0 (start), S1, S2, S3, HALT\n"
            "- Input alphabet: {a, b, c}\n"
            "- Transitions (state + input -> new state, output):\n"
            "  S0+a -> S1, output '1'\n"
            "  S0+b -> S2, output '0'\n"
            "  S0+c -> S0, output '' (nothing)\n"
            "  S1+a -> S2, output '1'\n"
            "  S1+b -> S0, output '01'\n"
            "  S1+c -> S3, output '1'\n"
            "  S2+a -> HALT, output '00'\n"
            "  S2+b -> S1, output '1'\n"
            "  S2+c -> S0, output '0'\n"
            "  S3+a -> S1, output '11'\n"
            "  S3+b -> HALT, output '0'\n"
            "  S3+c -> S2, output '10'\n"
            "- HALT immediately stops (remaining input ignored)"
        ),
        "test_questions": [
            {"q": "What is the complete output string for input 'acba'?",
             "a": "110"},
        ],
    },
    {
        "id": "negotiation_protocol",
        "preview": "Learn multi-party negotiation rules with bluffing detection and counter-offers",
        "difficulty": 5,
        "lesson": (
            "Nexus Trade Protocol:\n"
            "- Two traders, A and B, each have a hidden reserve price\n"
            "- Rounds alternate: A offers first, B counter-offers, repeat\n"
            "- An offer is accepted if it meets or exceeds the other's reserve price\n"
            "- BLUFF DETECTION: if a trader's offer increases by >20% from their previous offer, "
            "the other trader may call 'bluff'\n"
            "- If bluff called correctly (offerer's reserve is below their current offer): "
            "deal forced at the offerer's reserve price\n"
            "- If bluff called incorrectly: caller pays 10% penalty of item value (100 coins)\n"
            "- After 4 rounds with no deal: item sold to third party at average of last two offers"
        ),
        "test_questions": [
            {"q": "A's reserve=40, B's reserve=60. Round 1: A offers 30. Round 2: B counters 80. "
             "Round 3: A offers 50 (67% increase from 30). B calls bluff on A. "
             "Is the bluff call correct and what happens?",
             "a": "correct, deal at 40"},
        ],
    },
]
