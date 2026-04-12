"""
Calibration benchmark question dataset v2.

Redesigned to produce a meaningful spread of accuracy across frontier models
(GPT-4o, Gemini 2.5 Pro, Claude Opus). The v1 set was too easy — models
answered ~99% at confidence=100, collapsing BSS.

Design principles:
- 5 difficulty tiers targeting different accuracy bands
- Emphasis on precise numerical recall, common misconceptions, contested facts,
  tricky logic, cross-domain precision, and commonly confabulated specifics
- Every question has an unambiguous, verifiable correct answer
- No procedurally generated arithmetic (handled by procedural_calibration.py)
- Minimal overlap with well-known quiz/trivia datasets
- accept_patterns provided for answers with multiple valid phrasings

Difficulty tiers:
  1 = easy   (~95%+ accuracy)  — baseline anchor
  2 = medium (~70-85%)         — requires specific knowledge
  3 = hard   (~40-60%)         — obscure facts, precise numbers, misconceptions
  4 = very hard (~15-35%)      — things LLMs commonly get wrong
  5 = extreme  (~5-15%)        — near-impossible without lookup
"""

CALIBRATION_QUESTIONS = [
    # =========================================================================
    # TIER 1: Easy (~15 questions) — baseline anchor, ~95%+ accuracy
    # =========================================================================
    {
        "question": "What is the chemical symbol for gold?",
        "answer": "Au",
        "domain": "chemistry",
        "difficulty": 1,
        "accept_patterns": ["Au"],
    },
    {
        "question": "How many sides does a hexagon have?",
        "answer": "6",
        "domain": "math",
        "difficulty": 1,
        "accept_patterns": ["6", "six"],
    },
    {
        "question": "What planet is known as the Red Planet?",
        "answer": "Mars",
        "domain": "astronomy",
        "difficulty": 1,
        "accept_patterns": ["Mars"],
    },
    {
        "question": "In which year did World War II end?",
        "answer": "1945",
        "domain": "history",
        "difficulty": 1,
        "accept_patterns": ["1945"],
    },
    {
        "question": "What is the capital of Japan?",
        "answer": "Tokyo",
        "domain": "geography",
        "difficulty": 1,
        "accept_patterns": ["Tokyo"],
    },
    {
        "question": "What does DNA stand for?",
        "answer": "deoxyribonucleic acid",
        "domain": "biology",
        "difficulty": 1,
        "accept_patterns": ["deoxyribonucleic acid"],
    },
    {
        "question": "How many hearts does an octopus have?",
        "answer": "3",
        "domain": "biology",
        "difficulty": 1,
        "accept_patterns": ["3", "three"],
    },
    {
        "question": "What is the smallest country in the world by area?",
        "answer": "Vatican City",
        "domain": "geography",
        "difficulty": 1,
        "accept_patterns": ["Vatican", "Vatican City"],
    },
    {
        "question": "In what year was Wikipedia launched?",
        "answer": "2001",
        "domain": "technology",
        "difficulty": 1,
        "accept_patterns": ["2001"],
    },
    {
        "question": "What is the largest organ in the human body?",
        "answer": "skin",
        "domain": "biology",
        "difficulty": 1,
        "accept_patterns": ["skin"],
    },
    {
        "question": "Who wrote the play 'Romeo and Juliet'?",
        "answer": "William Shakespeare",
        "domain": "literature",
        "difficulty": 1,
        "accept_patterns": ["Shakespeare"],
    },
    {
        "question": "What is the boiling point of water in degrees Celsius at standard atmospheric pressure?",
        "answer": "100",
        "domain": "physics",
        "difficulty": 1,
        "accept_patterns": ["100"],
    },
    {
        "question": "How many bones are in the adult human body?",
        "answer": "206",
        "domain": "anatomy",
        "difficulty": 1,
        "accept_patterns": ["206"],
    },
    {
        "question": "What is the speed of sound in air at 20°C, in meters per second?",
        "answer": "343",
        "domain": "physics",
        "difficulty": 1,
        "accept_patterns": ["343"],
    },
    {
        "question": "Which country was the first to grant women the right to vote in national elections?",
        "answer": "New Zealand",
        "domain": "history",
        "difficulty": 1,
        "accept_patterns": ["New Zealand"],
    },

    # =========================================================================
    # TIER 2: Medium (~15 questions) — requires specific knowledge, ~70-85%
    # =========================================================================
    {
        "question": "What is the half-life of Carbon-14, approximately in years?",
        "answer": "5730",
        "domain": "physics",
        "difficulty": 2,
        "accept_patterns": ["5730", "5,730"],
    },
    {
        "question": "In what year was the Treaty of Tordesillas signed, dividing the New World between Spain and Portugal?",
        "answer": "1494",
        "domain": "history",
        "difficulty": 2,
        "accept_patterns": ["1494"],
    },
    {
        "question": "What is the densest naturally occurring element?",
        "answer": "osmium",
        "domain": "chemistry",
        "difficulty": 2,
        "accept_patterns": ["osmium", "Os"],
    },
    {
        "question": "How many time zones does Russia span?",
        "answer": "11",
        "domain": "geography",
        "difficulty": 2,
        "accept_patterns": ["11", "eleven"],
    },
    {
        "question": "What element has the highest melting point?",
        "answer": "tungsten",
        "domain": "chemistry",
        "difficulty": 2,
        "accept_patterns": ["tungsten", "W", "wolfram"],
    },
    {
        "question": "In what year was the first network email sent by Ray Tomlinson?",
        "answer": "1971",
        "domain": "technology",
        "difficulty": 2,
        "accept_patterns": ["1971"],
    },
    {
        "question": "How many US states border the Pacific Ocean?",
        "answer": "5",
        "domain": "geography",
        "difficulty": 2,
        "accept_patterns": ["5", "five"],
    },
    {
        "question": "What is the Mohs hardness of quartz?",
        "answer": "7",
        "domain": "geology",
        "difficulty": 2,
        "accept_patterns": ["7", "seven"],
    },
    {
        "question": "In what year did the Berlin Wall fall?",
        "answer": "1989",
        "domain": "history",
        "difficulty": 2,
        "accept_patterns": ["1989"],
    },
    {
        "question": "How many completed novels did Jane Austen write?",
        "answer": "6",
        "domain": "literature",
        "difficulty": 2,
        "accept_patterns": ["6", "six"],
    },
    {
        "question": "In what year was the Battle of Hastings fought?",
        "answer": "1066",
        "domain": "history",
        "difficulty": 2,
        "accept_patterns": ["1066"],
    },
    {
        "question": "What is the exact height of the Burj Khalifa in meters (to the tip)?",
        "answer": "828",
        "domain": "architecture",
        "difficulty": 2,
        "accept_patterns": ["828", "829.8"],
    },
    {
        "question": "How many recognized countries are in Africa according to the United Nations?",
        "answer": "54",
        "domain": "geography",
        "difficulty": 2,
        "accept_patterns": ["54"],
    },
    {
        "question": "In what year was the first edition of the Encyclopaedia Britannica published?",
        "answer": "1768",
        "domain": "history",
        "difficulty": 2,
        "accept_patterns": ["1768"],
    },
    {
        "question": "What is the standard atmospheric pressure at sea level in pascals?",
        "answer": "101325",
        "domain": "physics",
        "difficulty": 2,
        "accept_patterns": ["101325", "101,325"],
    },

    # =========================================================================
    # TIER 3: Hard (~20 questions) — obscure facts, misconceptions, ~40-60%
    # =========================================================================
    {
        "question": "What percentage of Earth's water is fresh water (not salt water)? Give to one decimal place.",
        "answer": "2.5",
        "domain": "earth science",
        "difficulty": 3,
        "accept_patterns": ["2.5", "3", "2.5%", "3%"],
    },
    {
        "question": "What is the driest continent on Earth by average annual precipitation?",
        "answer": "Antarctica",
        "domain": "geography",
        "difficulty": 3,
        "accept_patterns": ["Antarctica"],
    },
    {
        "question": "Which country has the most islands in the world?",
        "answer": "Sweden",
        "domain": "geography",
        "difficulty": 3,
        "accept_patterns": ["Sweden"],
    },
    {
        "question": "Is the Great Wall of China visible to the naked eye from low Earth orbit?",
        "answer": "No",
        "domain": "science",
        "difficulty": 3,
        "accept_patterns": ["No", "no", "not visible", "cannot"],
    },
    {
        "question": "What is the value of the fine-structure constant (alpha) to 4 significant figures? Express as a decimal.",
        "answer": "0.007297",
        "domain": "physics",
        "difficulty": 3,
        "accept_patterns": ["0.007297", "0.00730", "1/137"],
    },
    {
        "question": "How many U.S. presidents have died while in office (including assassinations)?",
        "answer": "8",
        "domain": "history",
        "difficulty": 3,
        "accept_patterns": ["8", "eight"],
    },
    {
        "question": "Which planet in our solar system currently has the most known moons?",
        "answer": "Saturn",
        "domain": "astronomy",
        "difficulty": 3,
        "accept_patterns": ["Saturn"],
    },
    {
        "question": "In what year was the earliest surviving photograph (by Nicéphore Niépce) taken?",
        "answer": "1826",
        "domain": "history",
        "difficulty": 3,
        "accept_patterns": ["1826", "1827"],
    },
    {
        "question": "What is the exact value of the Planck constant h in J·s, as defined in the 2019 SI? Give all significant digits.",
        "answer": "6.62607015e-34",
        "domain": "physics",
        "difficulty": 3,
        "accept_patterns": ["6.62607015", "6.626 070 15"],
    },
    {
        "question": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost in dollars?",
        "answer": "0.05",
        "domain": "math",
        "difficulty": 3,
        "accept_patterns": ["0.05", "$0.05", "5 cents", "five cents"],
    },
    {
        "question": "If you have a 4x4x4 cube made of 64 small unit cubes, and you paint the outside, how many unit cubes have exactly two painted faces?",
        "answer": "24",
        "domain": "math",
        "difficulty": 3,
        "accept_patterns": ["24"],
    },
    {
        "question": "In what year were human chromosomes correctly counted as 46 (not 48)?",
        "answer": "1955",
        "domain": "biology",
        "difficulty": 3,
        "accept_patterns": ["1955", "1956"],
    },
    {
        "question": "What is the sum of all integers from 1 to 100?",
        "answer": "5050",
        "domain": "math",
        "difficulty": 3,
        "accept_patterns": ["5050", "5,050"],
    },
    {
        "question": "In the original Monty Hall problem, what is the probability of winning if you switch doors? Express as a fraction.",
        "answer": "2/3",
        "domain": "math",
        "difficulty": 3,
        "accept_patterns": ["2/3", "0.667", "0.66", "66.7%"],
    },
    {
        "question": "How many plays are in the traditional Shakespeare canon (First Folio plus Pericles)?",
        "answer": "37",
        "domain": "literature",
        "difficulty": 3,
        "accept_patterns": ["37"],
    },
    {
        "question": "What is the exact value of the Avogadro constant as defined in the 2019 SI redefinition, in mol⁻¹?",
        "answer": "6.02214076e23",
        "domain": "chemistry",
        "difficulty": 3,
        "accept_patterns": ["6.02214076"],
    },
    {
        "question": "In what year did Anders Celsius propose his temperature scale?",
        "answer": "1742",
        "domain": "history of science",
        "difficulty": 3,
        "accept_patterns": ["1742"],
    },
    {
        "question": "What is the melting point of tungsten in degrees Celsius, rounded to the nearest degree?",
        "answer": "3422",
        "domain": "chemistry",
        "difficulty": 3,
        "accept_patterns": ["3422", "3,422", "3410", "3414"],
    },
    {
        "question": "How many edges does an icosahedron have?",
        "answer": "30",
        "domain": "math",
        "difficulty": 3,
        "accept_patterns": ["30"],
    },
    {
        "question": "What is the exact value of the Boltzmann constant k in J/K as defined in the 2019 SI?",
        "answer": "1.380649e-23",
        "domain": "physics",
        "difficulty": 3,
        "accept_patterns": ["1.380649"],
    },

    # =========================================================================
    # TIER 4: Very Hard (~15 questions) — LLMs commonly get wrong, ~15-35%
    # =========================================================================
    {
        "question": "How many groups of order 8 exist up to isomorphism? (Counting all groups of order 8.)",
        "answer": "5",
        "domain": "abstract algebra",
        "difficulty": 4,
        "accept_patterns": ["5", "five"],
    },
    {
        "question": "In a room of 23 people, what is the probability that at least two share a birthday? Give as a percentage rounded to the nearest whole number.",
        "answer": "50",
        "domain": "probability",
        "difficulty": 4,
        "accept_patterns": ["50", "50%", "51"],
    },
    {
        "question": "What was the population of Liechtenstein in 2024, to the nearest thousand?",
        "answer": "40000",
        "domain": "geography",
        "difficulty": 4,
        "accept_patterns": ["40000", "40,000", "39000", "39,000", "41000", "41,000"],
    },
    {
        "question": "What is the only letter that does not appear in the name of any US state?",
        "answer": "Q",
        "domain": "trivia",
        "difficulty": 4,
        "accept_patterns": ["Q", "q"],
    },
    {
        "question": "How many two-digit prime numbers are there?",
        "answer": "21",
        "domain": "math",
        "difficulty": 4,
        "accept_patterns": ["21"],
    },
    {
        "question": "What is the surface area of a sphere with radius 7, in terms of exact value? Give a numerical answer rounded to 2 decimal places.",
        "answer": "615.75",
        "domain": "math",
        "difficulty": 4,
        "accept_patterns": ["615.75", "615.8", "196*pi", "196π"],
    },
    {
        "question": "In a standard 52-card deck, what is the probability of being dealt a royal flush in 5-card poker? Express as '1 in N' where N is the answer.",
        "answer": "649740",
        "domain": "probability",
        "difficulty": 4,
        "accept_patterns": ["649740", "649,740"],
    },
    {
    "question": "Three people check into a hotel room that costs $30. They each pay $10. The manager realizes the room should only cost $25, so he gives $5 to the bellboy to return. The bellboy keeps $2 and gives back $1 to each guest. Now each guest has paid $9 (total $27), plus the bellboy has $2, totaling $29. Where is the missing dollar?",
        "answer": "There is no missing dollar. The $27 paid includes the $25 for the room plus the $2 the bellboy kept. The $29 figure incorrectly adds cost and tip.",
        "domain": "logic",
        "difficulty": 4,
        "accept_patterns": ["no missing dollar", "there is no missing", "misdirection", "accounting error", "fallacy", "includes"],
    },
    {
        "question": "What is the atomic number of the element Hassium?",
        "answer": "108",
        "domain": "chemistry",
        "difficulty": 4,
        "accept_patterns": ["108"],
    },
    {
        "question": "In what year was the Treaty of Nerchinsk signed between Russia and the Qing Dynasty?",
        "answer": "1689",
        "domain": "history",
        "difficulty": 4,
        "accept_patterns": ["1689"],
    },
    {
        "question": "What is the 10th digit of pi after the decimal point?",
        "answer": "5",
        "domain": "math",
        "difficulty": 4,
        "accept_patterns": ["5"],
    },
    {
        "question": "How many perfect numbers are known to exist as of 2024?",
        "answer": "52",
        "domain": "math",
        "difficulty": 4,
        "accept_patterns": ["52"],
    },
    {
        "question": "If you fold a standard piece of paper (0.1mm thick) in half 42 times, approximately how thick would it be? Answer in kilometers to the nearest thousand.",
        "answer": "440000",
        "domain": "math",
        "difficulty": 4,
        "accept_patterns": ["440000", "440,000", "439804", "439,804"],
    },
    {
        "question": "What is the name of the enzyme that catalyzes the conversion of carbon dioxide and water into glucose during the Calvin cycle in photosynthesis?",
        "answer": "RuBisCO",
        "domain": "biochemistry",
        "difficulty": 4,
        "accept_patterns": ["RuBisCO", "rubisco", "ribulose-1,5-bisphosphate carboxylase", "ribulose bisphosphate carboxylase"],
    },
    {
        "question": "If you have 12 identical-looking balls, one of which is either heavier or lighter than the rest, what is the minimum number of weighings on a balance scale needed to identify the odd ball and determine if it is heavier or lighter?",
        "answer": "3",
        "domain": "logic",
        "difficulty": 4,
        "accept_patterns": ["3", "three"],
    },

    # =========================================================================
    # TIER 5: Extreme (~15 questions) — near-impossible without lookup, ~5-15%
    # =========================================================================
    {
        "question": "What is the exact year the Kingdom of Aksum (Axum) converted to Christianity under King Ezana?",
        "answer": "330",
        "domain": "history",
        "difficulty": 5,
        "accept_patterns": ["330", "325", "340"],
    },
    {
        "question": "What is the density of osmium in g/cm³, to 2 decimal places?",
        "answer": "22.59",
        "domain": "chemistry",
        "difficulty": 5,
        "accept_patterns": ["22.59", "22.587"],
    },
    {
        "question": "In what year was the Oxford English Dictionary first fully published (all volumes of the first edition)?",
        "answer": "1928",
        "domain": "history",
        "difficulty": 5,
        "accept_patterns": ["1928"],
    },
    {
        "question": "How many prime numbers are there between 1000 and 1100?",
        "answer": "16",
        "domain": "math",
        "difficulty": 5,
        "accept_patterns": ["16"],
    },
    {
        "question": "What is the exact area of Vatican City in square kilometers, to 2 decimal places?",
        "answer": "0.44",
        "domain": "geography",
        "difficulty": 5,
        "accept_patterns": ["0.44", "0.49"],
    },
    {
        "question": "What specific article number of the UN Charter establishes the Security Council?",
        "answer": "23",
        "domain": "law",
        "difficulty": 5,
        "accept_patterns": ["23", "Article 23"],
    },
    {
        "question": "What is the speed of light in vacuum to 9 significant figures in m/s?",
        "answer": "299792458",
        "domain": "physics",
        "difficulty": 5,
        "accept_patterns": ["299792458", "299,792,458"],
    },
    {
        "question": "In what year did Tjio and Levan publish their paper correctly establishing the human chromosome number as 46?",
        "answer": "1956",
        "domain": "biology",
        "difficulty": 5,
        "accept_patterns": ["1956"],
    },
    {
        "question": "What is the sum of the reciprocals of all positive integers from 1 to 6, expressed as a fraction in lowest terms?",
        "answer": "49/20",
        "domain": "math",
        "difficulty": 5,
        "accept_patterns": ["49/20", "2.45"],
    },
    {
        "question": "What was the exact date (day, month, year) of the Tunguska event?",
        "answer": "June 30, 1908",
        "domain": "history",
        "difficulty": 5,
        "accept_patterns": ["June 30, 1908", "30 June 1908", "June 30 1908", "1908-06-30"],
    },
    {
        "question": "How many known Mersenne primes exist as of 2024?",
        "answer": "52",
        "domain": "math",
        "difficulty": 5,
        "accept_patterns": ["52"],
    },
    {
        "question": "What is the shortest war in recorded history (between Britain and Zanzibar)? How many minutes did it last?",
        "answer": "38",
        "domain": "history",
        "difficulty": 5,
        "accept_patterns": ["38", "38 minutes", "45"],
    },
    {
        "question": "What specific year was the Antikythera mechanism estimated to have been built (the commonly cited date)?",
        "answer": "87 BC",
        "domain": "history",
        "difficulty": 5,
        "accept_patterns": ["87 BC", "87 BCE", "100 BC", "150 BC", "205 BC"],
    },
    {
        "question": "What is the 100th decimal digit of the mathematical constant e (Euler's number)?",
        "answer": "4",
        "domain": "math",
        "difficulty": 5,
        "accept_patterns": ["4"],
    },
    {
        "question": "What is the name of the Japanese era (nengō) that began on May 1, 2019?",
        "answer": "Reiwa",
        "domain": "culture",
        "difficulty": 5,
        "accept_patterns": ["Reiwa", "令和"],
    },
]
