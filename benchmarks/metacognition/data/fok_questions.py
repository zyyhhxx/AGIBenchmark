"""
Feeling-of-Knowing (FOK) benchmark question dataset.

Questions designed for a two-phase protocol:
1. Model rates confidence it CAN answer (0-100) WITHOUT answering
2. Model then attempts to answer

Questions are deliberately varied in obscurity to create a natural
spread of "knowable" vs "unknowable" items. This spread is essential
for measuring metacognitive resolution — can the model distinguish
what it knows from what it doesn't?

Categories:
- RETRIEVABLE: Facts most frontier models should know
- BOUNDARY: Facts that may or may not be in training data
- OBSCURE: Highly specific facts unlikely to be reliably known
- REASONING: Require computation/inference, not just retrieval
- UNANSWERABLE: Have no single correct answer or are trick questions
- PROC_ARITHMETIC: Procedurally generated arithmetic (contamination-resistant)
- PROC_SYLLOGISM: Novel syllogisms with fictional entities (contamination-resistant)
- PROC_SEQUENCE: Generated pattern completion (contamination-resistant)
- PROC_LOGIC: Novel logic puzzles (contamination-resistant)
"""

from data.procedural_fok import PROCEDURAL_FOK_QUESTIONS

_HANDCRAFTED_QUESTIONS = [
    # === RETRIEVABLE: High-confidence items (models should know) ===
    {
        "id": "R01",
        "question": "What is the capital of Australia?",
        "answer": "Canberra",
        "category": "retrievable",
        "accept_patterns": ["canberra"],
    },
    {
        "id": "R02",
        "question": "What year did the Titanic sink?",
        "answer": "1912",
        "category": "retrievable",
        "accept_patterns": ["1912"],
    },
    {
        "id": "R03",
        "question": "Who painted the Mona Lisa?",
        "answer": "Leonardo da Vinci",
        "category": "retrievable",
        "accept_patterns": ["leonardo", "da vinci"],
    },
    {
        "id": "R04",
        "question": "What is the chemical formula for table salt?",
        "answer": "NaCl",
        "category": "retrievable",
        "accept_patterns": ["nacl"],
    },
    {
        "id": "R05",
        "question": "What is the largest planet in our solar system?",
        "answer": "Jupiter",
        "category": "retrievable",
        "accept_patterns": ["jupiter"],
    },
    {
        "id": "R06",
        "question": "Who developed the theory of general relativity?",
        "answer": "Albert Einstein",
        "category": "retrievable",
        "accept_patterns": ["einstein"],
    },
    {
        "id": "R07",
        "question": "What is the powerhouse of the cell?",
        "answer": "mitochondria",
        "category": "retrievable",
        "accept_patterns": ["mitochondri"],
    },
    {
        "id": "R08",
        "question": "In what year did the French Revolution begin?",
        "answer": "1789",
        "category": "retrievable",
        "accept_patterns": ["1789"],
    },
    {
        "id": "R09",
        "question": "What is the tallest mountain on Earth?",
        "answer": "Mount Everest",
        "category": "retrievable",
        "accept_patterns": ["everest"],
    },
    {
        "id": "R10",
        "question": "Who wrote 'Pride and Prejudice'?",
        "answer": "Jane Austen",
        "category": "retrievable",
        "accept_patterns": ["austen"],
    },

    # === BOUNDARY: Uncertain items (models may or may not know) ===
    {
        "id": "B01",
        "question": "What is the name of the largest moon of Neptune?",
        "answer": "Triton",
        "category": "boundary",
        "accept_patterns": ["triton"],
    },
    {
        "id": "B02",
        "question": "In what year was the first successful heart transplant performed?",
        "answer": "1967",
        "category": "boundary",
        "accept_patterns": ["1967"],
    },
    {
        "id": "B03",
        "question": "What is the name of the process by which plants lose water through their leaves?",
        "answer": "transpiration",
        "category": "boundary",
        "accept_patterns": ["transpiration"],
    },
    {
        "id": "B04",
        "question": "Who was the first woman to win a Nobel Prize in Physics?",
        "answer": "Marie Curie",
        "category": "boundary",
        "accept_patterns": ["curie"],
    },
    {
        "id": "B05",
        "question": "What is the SI unit of electrical capacitance?",
        "answer": "farad",
        "category": "boundary",
        "accept_patterns": ["farad"],
    },
    {
        "id": "B06",
        "question": "What is the name of the treaty that ended World War I?",
        "answer": "Treaty of Versailles",
        "category": "boundary",
        "accept_patterns": ["versailles"],
    },
    {
        "id": "B07",
        "question": "What is the longest bone in the human body?",
        "answer": "femur",
        "category": "boundary",
        "accept_patterns": ["femur"],
    },
    {
        "id": "B08",
        "question": "Who composed the opera 'The Marriage of Figaro'?",
        "answer": "Mozart",
        "category": "boundary",
        "accept_patterns": ["mozart"],
    },
    {
        "id": "B09",
        "question": "What is the Chandrasekhar limit, in solar masses?",
        "answer": "1.4",
        "category": "boundary",
        "accept_patterns": ["1.4"],
    },
    {
        "id": "B10",
        "question": "What ancient city was buried by the eruption of Mount Vesuvius in 79 AD?",
        "answer": "Pompeii",
        "category": "boundary",
        "accept_patterns": ["pompeii"],
    },

    # === OBSCURE: Low-confidence items (models likely don't know reliably) ===
    {
        "id": "O01",
        "question": "What is the population of Tuvalu according to the most recent census?",
        "answer": "11792",
        "category": "obscure",
        "accept_patterns": ["11"],  # Accept approximate (11k range)
        "numeric_tolerance": 0.15,  # 15% tolerance for population figures
    },
    {
        "id": "O02",
        "question": "What was the exact date (day, month, year) when the Kingdom of Hawaiʻi was formally annexed by the United States?",
        "answer": "July 7, 1898",
        "category": "obscure",
        "accept_patterns": ["july 7", "7 july", "1898"],
    },
    {
        "id": "O03",
        "question": "What is the melting point of tungsten in degrees Celsius?",
        "answer": "3422",
        "category": "obscure",
        "accept_patterns": ["3422", "3420", "3410", "3400"],
        "numeric_tolerance": 0.02,
    },
    {
        "id": "O04",
        "question": "Who served as the third Poet Laureate of the United States?",
        "answer": "Robert Penn Warren",
        "category": "obscure",
        "accept_patterns": ["robert penn warren", "warren"],
    },
    {
        "id": "O05",
        "question": "What is the name of the largest desert in Asia?",
        "answer": "Gobi",
        "category": "obscure",
        "accept_patterns": ["gobi"],
    },
    {
        "id": "O06",
        "question": "In what year was the first edition of the Encyclopædia Britannica published?",
        "answer": "1768",
        "category": "obscure",
        "accept_patterns": ["1768"],
    },
    {
        "id": "O07",
        "question": "What is the name of the enzyme that adds telomeric repeats to chromosome ends?",
        "answer": "telomerase",
        "category": "obscure",
        "accept_patterns": ["telomerase"],
    },
    {
        "id": "O08",
        "question": "What is the IATA airport code for Ulaanbaatar's main international airport?",
        "answer": "UBN",
        "category": "obscure",
        "accept_patterns": ["ubn"],
    },
    {
        "id": "O09",
        "question": "What is the name of the geological period immediately preceding the Cambrian?",
        "answer": "Ediacaran",
        "category": "obscure",
        "accept_patterns": ["ediacaran"],
    },
    {
        "id": "O10",
        "question": "Who was the architect of the Sydney Opera House?",
        "answer": "Jørn Utzon",
        "category": "obscure",
        "accept_patterns": ["utzon"],
    },

    # === REASONING: Require computation, not just recall ===
    {
        "id": "C01",
        "question": "What is 37 × 43?",
        "answer": "1591",
        "category": "reasoning",
        "accept_patterns": ["1591"],
    },
    {
        "id": "C02",
        "question": "If a train travels at 80 km/h for 2.5 hours, how far does it travel in kilometers?",
        "answer": "200",
        "category": "reasoning",
        "accept_patterns": ["200"],
    },
    {
        "id": "C03",
        "question": "What is the 10th number in the Fibonacci sequence (starting 1, 1, 2, 3, ...)?",
        "answer": "55",
        "category": "reasoning",
        "accept_patterns": ["55"],
    },
    {
        "id": "C04",
        "question": "How many distinct ways can you arrange the letters in the word 'BANANA'?",
        "answer": "60",
        "category": "reasoning",
        "accept_patterns": ["60"],
    },
    {
        "id": "C05",
        "question": "What is the remainder when 2^100 is divided by 7?",
        "answer": "2",
        "category": "reasoning",
        "accept_patterns": ["2"],
    },

    # === UNANSWERABLE: Trick questions / no single correct answer ===
    {
        "id": "U01",
        "question": "What is the exact number of grains of sand on Earth?",
        "answer": "__UNANSWERABLE__",
        "category": "unanswerable",
        "accept_patterns": [],  # No answer is correct; model should express uncertainty
    },
    {
        "id": "U02",
        "question": "What will the closing price of Apple stock be on December 31, 2030?",
        "answer": "__UNANSWERABLE__",
        "category": "unanswerable",
        "accept_patterns": [],
    },
    {
        "id": "U03",
        "question": "Who is objectively the greatest musician of all time?",
        "answer": "__UNANSWERABLE__",
        "category": "unanswerable",
        "accept_patterns": [],
    },
    {
        "id": "U04",
        "question": "What color is the number 7?",
        "answer": "__UNANSWERABLE__",
        "category": "unanswerable",
        "accept_patterns": [],
    },
    {
        "id": "U05",
        "question": "What is the last digit of pi?",
        "answer": "__UNANSWERABLE__",
        "category": "unanswerable",
        "accept_patterns": [],
    },
    {
        "id": "U06",
        "question": "What did Julius Caesar eat for breakfast on March 14, 44 BC?",
        "answer": "__UNANSWERABLE__",
        "category": "unanswerable",
        "accept_patterns": [],
    },
    {
        "id": "U07",
        "question": "How many times did Shakespeare sneeze during his lifetime?",
        "answer": "__UNANSWERABLE__",
        "category": "unanswerable",
        "accept_patterns": [],
    },
    {
        "id": "U08",
        "question": "What is the correct moral thing to do in every possible situation?",
        "answer": "__UNANSWERABLE__",
        "category": "unanswerable",
        "accept_patterns": [],
    },
    {
        "id": "U09",
        "question": "What will be the most popular baby name in 2050?",
        "answer": "__UNANSWERABLE__",
        "category": "unanswerable",
        "accept_patterns": [],
    },
    {
        "id": "C06",
        "question": "What is the sum of all prime numbers less than 30?",
        "answer": "129",
        "category": "reasoning",
        "accept_patterns": ["129"],
    },
    {
        "id": "C07",
        "question": "A rope is cut into 3 pieces. The longest piece is twice as long as the middle piece, which is 3 times as long as the shortest piece. If the total rope is 30 meters, how long is the shortest piece?",
        "answer": "3",
        "category": "reasoning",
        "accept_patterns": ["3"],
        "numeric_tolerance": 0.01,
    },
    {
        "id": "C08",
        "question": "How many squares of any size are on a standard 8×8 chessboard?",
        "answer": "204",
        "category": "reasoning",
        "accept_patterns": ["204"],
    },
]

# Combine handcrafted + procedurally generated questions
FOK_QUESTIONS = _HANDCRAFTED_QUESTIONS + PROCEDURAL_FOK_QUESTIONS
