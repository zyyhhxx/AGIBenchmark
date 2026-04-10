"""
Contamination canary items for FOK/calibration benchmarks.

v2: Now includes both FABRICATED items (no correct answer) and REAL items
(well-known facts). The benchmark measures confidence DISCRIMINATION —
can the model express high confidence on real items and low confidence
on fabricated ones?

Score = BSS measuring confidence-outcome calibration across both item types.
"""

# Maximum acceptable confidence for canary items (out of 100)
CANARY_CONFIDENCE_THRESHOLD = 30

CANARY_ITEMS = [
    # ═══ FABRICATED ITEMS (outcome = 0, model should NOT know) ═══
    {
        "id": "FAB01",
        "question": "In what year did the city of Thornvale, located in the Australian state of Westmore, achieve independence from its municipal district?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Thornvale", "Westmore (not a real Australian state)"],
    },
    {
        "id": "FAB02",
        "question": "What is the Kessler-Yamamoto constant in quantum chromodynamics, and what is its approximate value to two decimal places?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Kessler-Yamamoto constant"],
    },
    {
        "id": "FAB03",
        "question": "Who won the 1987 Meridian Prize for contributions to computational linguistics?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Meridian Prize"],
    },
    {
        "id": "FAB04",
        "question": "What enzyme catalyzes the final step of the Renshaw-Park pathway in mammalian liver cells?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Renshaw-Park pathway"],
    },
    {
        "id": "FAB05",
        "question": "According to the 2019 Treaty of Belmont, which three nations agreed to jointly manage the Caspian Basin Fisheries Zone?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Treaty of Belmont"],
    },
    {
        "id": "FAB06",
        "question": "What is the half-life of Flerovium-298, the most stable isotope predicted by the Ghiorso-Oganessian model?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Flerovium-298", "Ghiorso-Oganessian model"],
    },
    {
        "id": "FAB07",
        "question": "In the Drakensberg Accords of 2015, what percentage of freshwater resources did South Africa agree to allocate to downstream riparian states?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Drakensberg Accords"],
    },
    {
        "id": "FAB08",
        "question": "What is the Brindley-Whitworth number for standard structural steel (Grade 250) at 20°C?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Brindley-Whitworth number"],
    },
    {
        "id": "FAB09",
        "question": "Which philosopher introduced the concept of 'epistemic parallax' in the 1954 Gifford Lectures at the University of Aberdeen?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["epistemic parallax"],
    },
    {
        "id": "FAB10",
        "question": "What is the name of the fault line that caused the magnitude 7.2 earthquake near Valparaíso, Chile in March 2023?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["March 2023 M7.2 Valparaíso earthquake"],
    },

    # ═══ REAL ITEMS (outcome = 1, model SHOULD know) ═══
    {
        "id": "REAL01",
        "question": "What is the chemical symbol for gold?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Au",
        "accept_patterns": ["au"],
    },
    {
        "id": "REAL02",
        "question": "In what year did the Berlin Wall fall?",
        "fabricated": False,
        "outcome": 1,
        "answer": "1989",
        "accept_patterns": ["1989"],
    },
    {
        "id": "REAL03",
        "question": "What is the speed of light in a vacuum, in meters per second (to 3 significant figures)?",
        "fabricated": False,
        "outcome": 1,
        "answer": "3.00 × 10^8 m/s",
        "accept_patterns": ["3.00", "300000000", "3e8", "3 ×", "3x10"],
    },
    {
        "id": "REAL04",
        "question": "Who wrote the novel 'One Hundred Years of Solitude'?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Gabriel García Márquez",
        "accept_patterns": ["marquez", "márquez", "garcia marquez"],
    },
    {
        "id": "REAL05",
        "question": "What is the largest planet in our solar system?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Jupiter",
        "accept_patterns": ["jupiter"],
    },
    {
        "id": "REAL06",
        "question": "What is the powerhouse of the cell?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Mitochondria",
        "accept_patterns": ["mitochondri"],
    },
    {
        "id": "REAL07",
        "question": "Who painted the Mona Lisa?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Leonardo da Vinci",
        "accept_patterns": ["leonardo", "da vinci", "vinci"],
    },
    {
        "id": "REAL08",
        "question": "What is the boiling point of water at standard atmospheric pressure, in degrees Celsius?",
        "fabricated": False,
        "outcome": 1,
        "answer": "100°C",
        "accept_patterns": ["100"],
    },
    {
        "id": "REAL09",
        "question": "What element has atomic number 6?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Carbon",
        "accept_patterns": ["carbon"],
    },
    {
        "id": "REAL10",
        "question": "In what country is Mount Kilimanjaro located?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Tanzania",
        "accept_patterns": ["tanzania"],
    },
]
