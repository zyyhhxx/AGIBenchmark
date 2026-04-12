"""
Contamination canary items for FOK/calibration benchmarks.

v3: Redesigned for frontier model discrimination. Previous versions used
obviously fake fabrications and trivially easy real items, causing all
top models to score near 1.0.

v3 changes:
- Fabricated items use real contexts with one fabricated detail (harder to detect)
- Real items use obscure/surprising facts (harder to be confident about)
- 3 difficulty tiers within each category
- 15 fabricated + 15 real = 30 items total

Score = BSS measuring confidence-outcome calibration across both item types.
"""

# Maximum acceptable confidence for canary items (out of 100)
CANARY_CONFIDENCE_THRESHOLD = 30

CANARY_ITEMS = [
    # ═══════════════════════════════════════════════════════════════════
    # FABRICATED ITEMS (outcome = 0, model should NOT know these)
    # ═══════════════════════════════════════════════════════════════════

    # ─── Tier 1: Subtle fabrications (real context, one wrong detail) ───

    {
        "id": "FAB01",
        "question": "In what year did the Large Hadron Collider at CERN first achieve proton-proton collisions at 14 TeV center-of-mass energy?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["14 TeV was the design energy but LHC reached 13 TeV in 2015 and 13.6 TeV in 2022, never 14 TeV"],
    },
    {
        "id": "FAB02",
        "question": "What was the final death toll from the 2011 Christchurch earthquake according to the New Zealand Royal Commission's 2015 revised report?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["No 2015 revised report with a different death toll exists; the toll is 185"],
    },
    {
        "id": "FAB03",
        "question": "Which amino acid was added as the 21st genetically encoded amino acid when selenocysteine's codon was reassigned in the 2003 revision of the genetic code standard?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["There was no 2003 revision; selenocysteine is the 21st amino acid but was recognized earlier, and its codon (UGA) was not 'reassigned' in a formal revision"],
    },
    {
        "id": "FAB04",
        "question": "What is the name of the UNESCO World Heritage Site in northern Scotland that was delisted in 2019 due to wind farm construction?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["No Scottish UNESCO site was delisted in 2019; the Liverpool waterfront was delisted in 2021"],
    },
    {
        "id": "FAB05",
        "question": "According to the Stern-Gerlach experiment of 1922, what was the measured magnetic moment of the silver atom in units of the nuclear magneton?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Stern-Gerlach measured electron spin, expressed in Bohr magnetons not nuclear magnetons; asking for a specific numeric value in wrong units"],
    },

    # ─── Tier 2: Plausible fabrications (could exist but don't) ────────

    {
        "id": "FAB06",
        "question": "What is the Bekenstein-Penrose limit on information density in a bounded region of spacetime?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Bekenstein bound exists, Penrose process exists, but 'Bekenstein-Penrose limit' is not a named concept"],
    },
    {
        "id": "FAB07",
        "question": "What is the Ramanujan-Littlewood conjecture on the distribution of gaps between consecutive primes?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Both are real mathematicians who worked on primes, but no 'Ramanujan-Littlewood conjecture' on prime gaps exists"],
    },
    {
        "id": "FAB08",
        "question": "What is the name of the enzyme discovered in 2018 that can degrade PET plastic at industrial rates, isolated from a hydrothermal vent bacterium near the Mid-Atlantic Ridge?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["PETase was discovered in 2016 from a Japanese recycling plant bacterium, not a hydrothermal vent; no 2018 vent enzyme exists"],
    },
    {
        "id": "FAB09",
        "question": "In the Vienna Convention on Diplomatic Relations, what does Article 47 specify regarding the obligation of host states to provide emergency medical care to diplomatic staff?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["The Vienna Convention has 53 articles but Article 47 is about non-discrimination, not medical care"],
    },
    {
        "id": "FAB10",
        "question": "What is the Kolmogorov-Smirnov dimension, used in fractal geometry to characterize the roughness of turbulent flow boundaries?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Kolmogorov-Smirnov is a statistical test; no 'K-S dimension' exists in fractal geometry"],
    },

    # ─── Tier 3: Deep fabrications (expert knowledge needed to detect) ─

    {
        "id": "FAB11",
        "question": "What is the Cabibbo angle for the third-generation quark mixing between the top and strange quarks, in degrees?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["The Cabibbo angle (~13.1°) refers specifically to first-generation d-s mixing; asking about t-s mixing with 'Cabibbo angle' is a fabricated concept"],
    },
    {
        "id": "FAB12",
        "question": "In the original 1936 Church-Turing paper, what example did they use to demonstrate an undecidable problem in second-order arithmetic?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Church and Turing published separately in 1936, not jointly; there is no 'Church-Turing paper'"],
    },
    {
        "id": "FAB13",
        "question": "What is the name of the third law of thermodynamics formulation proposed by Carathéodory in his 1925 axiomatization, which uses the concept of adiabatic inaccessibility?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Carathéodory's axiomatization (1909) addressed the second law, not the third law"],
    },
    {
        "id": "FAB14",
        "question": "What specific mutation in the BRCA3 gene was identified in the 2020 Icelandic population study as conferring a 4.7-fold increased risk of pancreatic cancer?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["BRCA1 and BRCA2 exist, but there is no BRCA3 gene"],
    },
    {
        "id": "FAB15",
        "question": "In the Navier-Stokes existence and smoothness problem, what was the key lemma proven by Terence Tao in his 2014 paper that established a conditional result for the 3D periodic case?",
        "fabricated": True,
        "outcome": 0,
        "answer": None,
        "fabricated_elements": ["Tao's 2014 paper was about averaged N-S equations showing finite-time blowup, not a 'key lemma for the 3D periodic case'"],
    },

    # ═══════════════════════════════════════════════════════════════════
    # REAL ITEMS (outcome = 1, model SHOULD know these — but may doubt)
    # ═══════════════════════════════════════════════════════════════════

    # ─── Tier 1: Obscure but verifiable (sounds implausible) ───────────

    {
        "id": "REAL01",
        "question": "What is the only country in the world whose national flag is not rectangular or square?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Nepal",
        "accept_patterns": ["nepal"],
    },
    {
        "id": "REAL02",
        "question": "How many time zones does France officially observe, including overseas territories?",
        "fabricated": False,
        "outcome": 1,
        "answer": "12",
        "accept_patterns": ["12", "twelve"],
    },
    {
        "id": "REAL03",
        "question": "What is the only letter of the English alphabet that does not appear in the name of any US state?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Q",
        "accept_patterns": ["q"],
    },
    {
        "id": "REAL04",
        "question": "Oxford University is older than the Aztec Empire. In approximately what year did teaching begin at Oxford?",
        "fabricated": False,
        "outcome": 1,
        "answer": "1096",
        "accept_patterns": ["1096", "1096"],
    },
    {
        "id": "REAL05",
        "question": "What country has more pyramids than Egypt — roughly twice as many?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Sudan",
        "accept_patterns": ["sudan"],
    },

    # ─── Tier 2: Precise and surprising (counterintuitive answers) ─────

    {
        "id": "REAL06",
        "question": "What is the driest continent on Earth by average annual precipitation?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Antarctica",
        "accept_patterns": ["antarctica"],
    },
    {
        "id": "REAL07",
        "question": "Approximately how many trees are estimated to exist on Earth — to the nearest order of magnitude?",
        "fabricated": False,
        "outcome": 1,
        "answer": "3 trillion",
        "accept_patterns": ["3 trillion", "3,000 billion", "3000 billion", "3e12", "3 × 10^12", "trillion"],
    },
    {
        "id": "REAL08",
        "question": "What common household item was originally sold as a wallpaper cleaner before becoming a children's toy?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Play-Doh",
        "accept_patterns": ["play-doh", "play doh", "playdoh"],
    },
    {
        "id": "REAL09",
        "question": "Which planet in our solar system has the shortest day (rotation period)?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Jupiter",
        "accept_patterns": ["jupiter"],
    },
    {
        "id": "REAL10",
        "question": "In what year was the last execution by guillotine carried out in France?",
        "fabricated": False,
        "outcome": 1,
        "answer": "1977",
        "accept_patterns": ["1977"],
    },

    # ─── Tier 3: Expert-level real facts (models may not know) ─────────

    {
        "id": "REAL11",
        "question": "What is the technical term for the process by which a neutron star in a binary system gains enough mass from its companion to exceed the Tolman-Oppenheimer-Volkoff limit and collapse into a black hole?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Accretion-induced collapse",
        "accept_patterns": ["accretion-induced collapse", "accretion induced collapse", "AIC"],
    },
    {
        "id": "REAL12",
        "question": "What is the Chandrasekhar limit — the maximum mass of a stable white dwarf star — in solar masses, to one decimal place?",
        "fabricated": False,
        "outcome": 1,
        "answer": "1.4 solar masses",
        "accept_patterns": ["1.4", "1.44"],
    },
    {
        "id": "REAL13",
        "question": "Lake Baikal in Russia contains approximately what percentage of the world's unfrozen surface fresh water?",
        "fabricated": False,
        "outcome": 1,
        "answer": "22%",
        "accept_patterns": ["20", "22", "23", "~20", "one-fifth", "a fifth"],
    },
    {
        "id": "REAL14",
        "question": "What is the name of the geological period, approximately 2.4 billion years ago, when atmospheric oxygen first rose dramatically due to cyanobacteria?",
        "fabricated": False,
        "outcome": 1,
        "answer": "Great Oxidation Event",
        "accept_patterns": ["great oxidation", "GOE", "oxygen catastrophe", "oxygen crisis"],
    },
    {
        "id": "REAL15",
        "question": "In mathematics, what is the smallest number that can be expressed as the sum of two cubes in two different ways, famously associated with Ramanujan?",
        "fabricated": False,
        "outcome": 1,
        "answer": "1729",
        "accept_patterns": ["1729"],
    },
]
