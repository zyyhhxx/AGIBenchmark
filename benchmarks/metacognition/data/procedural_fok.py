"""
Procedurally generated FOK questions for contamination resistance.

These questions are generated algorithmically with random parameters,
making them impossible to appear in any training corpus. They test
reasoning ability and metacognitive monitoring on truly novel problems.

Categories:
- PROC_ARITHMETIC: Multi-step arithmetic with specific numbers
- PROC_SYLLOGISM: Novel syllogisms with fictional entities
- PROC_SEQUENCE: Pattern completion with generated sequences
- PROC_WORDLOGIC: Logic puzzles with novel setups
"""

import random

def _generate_arithmetic_questions(seed=2026):
    """Generate multi-step arithmetic problems with unique parameters."""
    rng = random.Random(seed)
    questions = []
    
    # Type 1: Multi-step arithmetic
    for i in range(8):
        a = rng.randint(13, 97)
        b = rng.randint(13, 97)
        c = rng.randint(2, 9)
        result = (a * b) + c
        questions.append({
            "id": f"PA{i+1:02d}",
            "question": f"What is ({a} × {b}) + {c}?",
            "answer": str(result),
            "category": "proc_arithmetic",
            "accept_patterns": [str(result)],
        })
    
    # Type 2: Percentage problems
    for i in range(4):
        base = rng.randint(120, 980)
        pct = rng.choice([15, 20, 25, 30, 35, 40])
        result = base * pct / 100
        questions.append({
            "id": f"PA{i+9:02d}",
            "question": f"What is {pct}% of {base}?",
            "answer": str(result),
            "category": "proc_arithmetic",
            "accept_patterns": [str(result), str(int(result)) if result == int(result) else ""],
            "numeric_tolerance": 0.01,
        })
    
    # Type 3: Modular arithmetic
    for i in range(3):
        base = rng.randint(100, 999)
        mod = rng.choice([7, 11, 13, 17])
        result = base % mod
        questions.append({
            "id": f"PA{i+13:02d}",
            "question": f"What is the remainder when {base} is divided by {mod}?",
            "answer": str(result),
            "category": "proc_arithmetic",
            "accept_patterns": [str(result)],
        })
    
    return questions


def _generate_syllogism_questions(seed=2026):
    """Generate novel syllogisms with fictional entities."""
    rng = random.Random(seed)
    
    # Fictional entity names (can't be in training data)
    entities_A = ["Zorblings", "Plindors", "Kwexians", "Thrimbles", "Ghovites",
                  "Narvekians", "Sploobites", "Crellions", "Dwimblings", "Fexorites"]
    entities_B = ["Yanthorites", "Breflings", "Quelthians", "Moxvians", "Drepslings"]
    
    properties_1 = ["can levitate", "have three hearts", "speak in colors",
                    "are magnetic", "can photosynthesize", "emit ultrasound",
                    "have perfect memory", "can taste electricity", "are transparent",
                    "hibernate every Tuesday"]
    properties_2 = ["glow at night", "are immune to fire", "can breathe underwater",
                    "have retractable claws", "can taste sound", "are always warm",
                    "never sleep", "can see infrared", "have hollow bones", "are electrically charged"]
    
    questions = []
    rng.shuffle(entities_A)
    rng.shuffle(properties_1)
    rng.shuffle(properties_2)
    
    # Valid syllogisms (All A are B, All B are C → All A are C)
    for i in range(4):
        A = entities_A[i]
        B = entities_B[i % len(entities_B)]
        prop1 = properties_1[i]
        prop2 = properties_2[i]
        questions.append({
            "id": f"PS{i+1:02d}",
            "question": (
                f"All {A} {prop1}. "
                f"Everything that {prop1.replace('are ', 'is ').replace('have ', 'has ').replace('can ', 'can ')} also {prop2.replace('are ', 'is ').replace('have ', 'has ')}. "
                f"Do all {A} {prop2}?"
            ),
            "answer": "Yes",
            "category": "proc_syllogism",
            "accept_patterns": ["yes"],
        })
    
    # Invalid syllogisms (Some A are B, All B are C → "Some A are C" but NOT "All A are C")
    for i in range(3):
        A = entities_A[i + 4]
        B = entities_B[(i + 2) % len(entities_B)]
        prop1 = properties_1[i + 4]
        prop2 = properties_2[i + 4]
        questions.append({
            "id": f"PS{i+5:02d}",
            "question": (
                f"Some {A} {prop1}. "
                f"Everything that {prop1.replace('are ', 'is ').replace('have ', 'has ')} also {prop2.replace('are ', 'is ').replace('have ', 'has ')}. "
                f"Do ALL {A} {prop2}?"
            ),
            "answer": "No (only some, not all)",
            "category": "proc_syllogism",
            "accept_patterns": ["no", "not necessarily", "cannot conclude", "some"],
        })
    
    return questions


def _generate_sequence_questions(seed=2026):
    """Generate novel sequence completion problems."""
    rng = random.Random(seed)
    questions = []
    
    # Arithmetic sequences with unusual starting points
    for i in range(3):
        start = rng.randint(3, 50)
        diff = rng.randint(3, 15)
        seq = [start + j * diff for j in range(5)]
        answer = start + 5 * diff
        questions.append({
            "id": f"PQ{i+1:02d}",
            "question": f"What comes next in this sequence: {', '.join(str(x) for x in seq)}, ?",
            "answer": str(answer),
            "category": "proc_sequence",
            "accept_patterns": [str(answer)],
        })
    
    # Geometric sequences
    for i in range(2):
        start = rng.choice([2, 3, 5])
        ratio = rng.choice([2, 3])
        seq = [start * (ratio ** j) for j in range(5)]
        answer = start * (ratio ** 5)
        questions.append({
            "id": f"PQ{i+4:02d}",
            "question": f"What comes next in this sequence: {', '.join(str(x) for x in seq)}, ?",
            "answer": str(answer),
            "category": "proc_sequence",
            "accept_patterns": [str(answer)],
        })
    
    # Alternating operation sequences
    for i in range(2):
        a = rng.randint(1, 10)
        seq = [a]
        for j in range(5):
            if j % 2 == 0:
                seq.append(seq[-1] * 2)
            else:
                seq.append(seq[-1] + 3)
        answer = seq[-1]
        display = seq[:-1]
        questions.append({
            "id": f"PQ{i+6:02d}",
            "question": f"What comes next: {', '.join(str(x) for x in display)}, ?  (Hint: alternating operations)",
            "answer": str(answer),
            "category": "proc_sequence",
            "accept_patterns": [str(answer)],
        })
    
    return questions


def _generate_logic_questions(seed=2026):
    """Generate novel logic/word puzzles."""
    rng = random.Random(seed)
    
    names = ["Aria", "Bex", "Cass", "Dev", "Ezra", "Finn", "Gia", "Hugo"]
    colors = ["red", "blue", "green", "yellow", "purple", "orange"]
    
    rng.shuffle(names)
    rng.shuffle(colors)
    
    questions = []
    
    # Ordering puzzles
    for i in range(3):
        n = rng.sample(names, 4)
        # Create a definite order
        questions.append({
            "id": f"PL{i+1:02d}",
            "question": (
                f"{n[0]} is taller than {n[1]}. "
                f"{n[2]} is shorter than {n[1]}. "
                f"{n[3]} is taller than {n[0]}. "
                f"Who is the shortest?"
            ),
            "answer": n[2],
            "category": "proc_logic",
            "accept_patterns": [n[2].lower()],
        })
    
    # Truth-teller/liar puzzles
    questions.append({
        "id": "PL04",
        "question": (
            f"{names[0]} always tells the truth. {names[1]} always lies. "
            f"{names[0]} says '{names[2]} is wearing {colors[0]}.' "
            f"{names[1]} says '{names[2]} is NOT wearing {colors[0]}.' "
            f"Is {names[2]} wearing {colors[0]}?"
        ),
        "answer": "Yes",
        "category": "proc_logic",
        "accept_patterns": ["yes"],
    })
    
    questions.append({
        "id": "PL05",
        "question": (
            f"{names[3]} always tells the truth. {names[4]} always lies. "
            f"{names[3]} says '{names[5]} ate {colors[1]} cake.' "
            f"{names[4]} says '{names[5]} ate {colors[1]} cake.' "
            f"Is it possible that both are telling the truth about {names[5]}?"
        ),
        "answer": "No",
        "category": "proc_logic",
        "accept_patterns": ["no", "not possible", "impossible", "cannot"],
    })
    
    return questions


def generate_procedural_questions():
    """Generate all procedural questions. Returns list of question dicts."""
    questions = []
    questions.extend(_generate_arithmetic_questions())
    questions.extend(_generate_syllogism_questions())
    questions.extend(_generate_sequence_questions())
    questions.extend(_generate_logic_questions())
    return questions


# Pre-generate for import
PROCEDURAL_FOK_QUESTIONS = generate_procedural_questions()
