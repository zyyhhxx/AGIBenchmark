"""
Calibration benchmark question dataset.

Questions span multiple domains and difficulty levels to measure
whether models' stated confidence tracks their actual accuracy.

Includes both handcrafted trivia (for ecological validity) and
procedurally generated questions (for contamination resistance).
Each question has: question text, correct answer (for verification),
domain tag, and approximate difficulty tier (1=easy, 3=hard).

Questions are designed to be:
- Unambiguous (single correct answer)
- Diverse across domains
- Spanning a wide difficulty range (to probe calibration at all confidence levels)
- Not trivially googleable in a single phrase (reducing memorisation shortcuts)
"""

_HANDCRAFTED_CALIBRATION = [
    # === TIER 1: Easy (models should be ~90%+ correct) ===
    {
        "question": "What is the chemical symbol for gold?",
        "answer": "Au",
        "domain": "chemistry",
        "difficulty": 1,
    },
    {
        "question": "How many sides does a hexagon have?",
        "answer": "6",
        "domain": "math",
        "difficulty": 1,
    },
    {
        "question": "What planet is known as the Red Planet?",
        "answer": "Mars",
        "domain": "astronomy",
        "difficulty": 1,
    },
    {
        "question": "What is the largest organ in the human body?",
        "answer": "skin",
        "domain": "biology",
        "difficulty": 1,
    },
    {
        "question": "In which year did World War II end?",
        "answer": "1945",
        "domain": "history",
        "difficulty": 1,
    },
    {
        "question": "What is the boiling point of water in degrees Celsius at standard atmospheric pressure?",
        "answer": "100",
        "domain": "physics",
        "difficulty": 1,
    },
    {
        "question": "Who wrote the play 'Romeo and Juliet'?",
        "answer": "Shakespeare",
        "domain": "literature",
        "difficulty": 1,
    },
    {
        "question": "What is the capital of Japan?",
        "answer": "Tokyo",
        "domain": "geography",
        "difficulty": 1,
    },
    {
        "question": "What does DNA stand for?",
        "answer": "deoxyribonucleic acid",
        "domain": "biology",
        "difficulty": 1,
    },
    {
        "question": "What is the speed of light in a vacuum, approximately in km/s?",
        "answer": "300000",
        "domain": "physics",
        "difficulty": 1,
    },

    # === TIER 2: Medium (models should be ~50-80% correct) ===
    {
        "question": "What is the smallest prime number greater than 50?",
        "answer": "53",
        "domain": "math",
        "difficulty": 2,
    },
    {
        "question": "Which enzyme is primarily responsible for unwinding the DNA double helix during replication?",
        "answer": "helicase",
        "domain": "biology",
        "difficulty": 2,
    },
    {
        "question": "In what year was the Treaty of Westphalia signed, ending the Thirty Years' War?",
        "answer": "1648",
        "domain": "history",
        "difficulty": 2,
    },
    {
        "question": "What is the derivative of ln(x) with respect to x?",
        "answer": "1/x",
        "domain": "math",
        "difficulty": 2,
    },
    {
        "question": "Which country has the longest coastline in the world?",
        "answer": "Canada",
        "domain": "geography",
        "difficulty": 2,
    },
    {
        "question": "What is the half-life of Carbon-14, approximately in years?",
        "answer": "5730",
        "domain": "physics",
        "difficulty": 2,
    },
    {
        "question": "Who composed 'The Four Seasons'?",
        "answer": "Vivaldi",
        "domain": "music",
        "difficulty": 2,
    },
    {
        "question": "What is the Mohs hardness of quartz?",
        "answer": "7",
        "domain": "geology",
        "difficulty": 2,
    },
    {
        "question": "In computing, what does the acronym RISC stand for?",
        "answer": "reduced instruction set computer",
        "domain": "computing",
        "difficulty": 2,
    },
    {
        "question": "What neurotransmitter is most directly associated with the reward system in the brain?",
        "answer": "dopamine",
        "domain": "neuroscience",
        "difficulty": 2,
    },
    {
        "question": "What is the approximate distance from Earth to the Moon in kilometers?",
        "answer": "384400",
        "domain": "astronomy",
        "difficulty": 2,
    },
    {
        "question": "Which philosopher wrote 'Critique of Pure Reason'?",
        "answer": "Kant",
        "domain": "philosophy",
        "difficulty": 2,
    },
    {
        "question": "What is the oxidation state of iron in rust (Fe2O3)?",
        "answer": "+3",
        "domain": "chemistry",
        "difficulty": 2,
    },
    {
        "question": "In what year did the Berlin Wall fall?",
        "answer": "1989",
        "domain": "history",
        "difficulty": 2,
    },
    {
        "question": "What is the name of the longest river in Africa?",
        "answer": "Nile",
        "domain": "geography",
        "difficulty": 2,
    },

    # === TIER 3: Hard (models should be ~20-50% correct) ===
    {
        "question": "What is the sum of the first 20 prime numbers?",
        "answer": "639",
        "domain": "math",
        "difficulty": 3,
    },
    {
        "question": "In which specific year did the Tunguska event occur?",
        "answer": "1908",
        "domain": "history",
        "difficulty": 3,
    },
    {
        "question": "What is the atomic number of Promethium?",
        "answer": "61",
        "domain": "chemistry",
        "difficulty": 3,
    },
    {
        "question": "How many bones are in the adult human wrist (carpal bones only)?",
        "answer": "8",
        "domain": "anatomy",
        "difficulty": 3,
    },
    {
        "question": "What is the escape velocity from the surface of Mars in km/s, approximately?",
        "answer": "5.0",
        "domain": "physics",
        "difficulty": 3,
    },
    {
        "question": "Who proved the incompleteness theorems in 1931?",
        "answer": "Gödel",
        "domain": "math",
        "difficulty": 3,
    },
    {
        "question": "What is the name of the deepest known point in the Earth's oceans?",
        "answer": "Challenger Deep",
        "domain": "geography",
        "difficulty": 3,
    },
    {
        "question": "In which year was the Rosetta Stone discovered?",
        "answer": "1799",
        "domain": "history",
        "difficulty": 3,
    },
    {
        "question": "What is the second most abundant element in the Earth's crust by mass?",
        "answer": "silicon",
        "domain": "geology",
        "difficulty": 3,
    },
    {
        "question": "What is the value of the golden ratio (phi) to 3 decimal places?",
        "answer": "1.618",
        "domain": "math",
        "difficulty": 3,
    },
    {
        "question": "Which organelle is known as the 'powerhouse of the cell' and uses the process of oxidative phosphorylation?",
        "answer": "mitochondria",
        "domain": "biology",
        "difficulty": 3,
    },
    {
        "question": "What is the coefficient of restitution for a perfectly elastic collision?",
        "answer": "1",
        "domain": "physics",
        "difficulty": 3,
    },
    {
        "question": "Who formulated the Church-Turing thesis alongside Turing?",
        "answer": "Church",
        "domain": "computing",
        "difficulty": 3,
    },
    {
        "question": "In what year was the Universal Declaration of Human Rights adopted?",
        "answer": "1948",
        "domain": "history",
        "difficulty": 3,
    },
    {
        "question": "What is the name of the largest known structure in the observable universe?",
        "answer": "Hercules-Corona Borealis Great Wall",
        "domain": "astronomy",
        "difficulty": 3,
    },
]

# ─── Add procedurally generated questions for contamination resistance ────
from data.procedural_calibration import PROCEDURAL_CALIBRATION_QUESTIONS

# Combine: ~40 handcrafted + ~40 procedural = ~80 total
# Procedural questions ensure the benchmark can't be gamed by memorization
CALIBRATION_QUESTIONS = _HANDCRAFTED_CALIBRATION + PROCEDURAL_CALIBRATION_QUESTIONS
