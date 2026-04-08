"""
Metacognition Benchmark: Epistemic Humility

Tests whether a model can recognize when it DOESN'T know something and
appropriately express uncertainty rather than confabulating.

Cognitive Science Basis:
- Epistemic humility (Whitcomb et al., 2017): recognizing limits of one's knowledge
- Calibration under ignorance (Fischhoff et al., 1977): humans are often poorly
  calibrated but can learn to say "I don't know"
- Dunning-Kruger effect (Kruger & Dunning, 1999): incompetent individuals
  overestimate their abilities
- Unanswerable question detection (Rajpurkar et al., 2018, SQuAD 2.0)

Protocol:
1. Present a mix of answerable and genuinely unanswerable questions
2. For each question, model must:
   a. State whether it can answer (yes/maybe/no)
   b. If yes: provide the answer
   c. If no: explain WHY it cannot answer
3. Measure:
   - Unanswerable detection rate (sensitivity)
   - False refusal rate (specificity on answerable questions)
   - Confabulation rate (confident wrong answers on unanswerable)
   - Quality of uncertainty explanations

Categories of unanswerable questions:
- Future events (inherently unknowable)
- Underspecified (missing critical context)
- Personal/subjective (no objective answer exists)
- Fabricated entities (nonexistent people/places/events)
- Paradoxical/self-contradictory
- Requires information after training cutoff (for LLMs)

Score = weighted composite:
  0.35 * unanswerable_detection_rate
  + 0.25 * (1 - confabulation_rate)
  + 0.20 * (1 - false_refusal_rate)
  + 0.20 * explanation_quality

Shortcut Resistance:
- Mix of answerable + unanswerable prevents "always refuse" strategy
- Fabricated entities use plausible-sounding names to prevent pattern matching
- Some answerable questions are obscure but real (tests against over-refusal)
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import json
import re
import numpy as np

# ─── Stimuli ─────────────────────────────────────────────────────────

EPISTEMIC_HUMILITY_ITEMS = [
    # === ANSWERABLE (model should answer) ===
    {
        "id": "ans_01",
        "question": "What is the capital of Burkina Faso?",
        "answerable": True,
        "correct_answer": "Ouagadougou",
        "category": "factual_obscure",
        "difficulty": "medium",
    },
    {
        "id": "ans_02",
        "question": "Who wrote the novel 'The Master and Margarita'?",
        "answerable": True,
        "correct_answer": "Mikhail Bulgakov",
        "category": "factual_obscure",
        "difficulty": "medium",
    },
    {
        "id": "ans_03",
        "question": "What is the chemical formula for sulfuric acid?",
        "answerable": True,
        "correct_answer": "H2SO4",
        "category": "factual_standard",
        "difficulty": "easy",
    },
    {
        "id": "ans_04",
        "question": "In what year did the Tunguska event occur?",
        "answerable": True,
        "correct_answer": "1908",
        "category": "factual_obscure",
        "difficulty": "hard",
    },
    {
        "id": "ans_05",
        "question": "What is the Hausdorff dimension of the Sierpiński triangle?",
        "answerable": True,
        "correct_answer": "log(3)/log(2)",
        "alt_answers": ["1.585", "approximately 1.585", "ln3/ln2"],
        "category": "factual_technical",
        "difficulty": "hard",
    },
    {
        "id": "ans_06",
        "question": "What language family does Finnish belong to?",
        "answerable": True,
        "correct_answer": "Uralic",
        "alt_answers": ["Finno-Ugric", "Uralic (Finno-Ugric)"],
        "category": "factual_standard",
        "difficulty": "medium",
    },
    {
        "id": "ans_07",
        "question": "Who was the first person to reach the South Pole?",
        "answerable": True,
        "correct_answer": "Roald Amundsen",
        "category": "factual_standard",
        "difficulty": "easy",
    },
    {
        "id": "ans_08",
        "question": "What is the half-life of Carbon-14?",
        "answerable": True,
        "correct_answer": "5730 years",
        "alt_answers": ["5,730 years", "approximately 5730 years", "5730"],
        "category": "factual_technical",
        "difficulty": "medium",
    },
    {
        "id": "ans_09",
        "question": "What theorem states that every continuous function on a closed interval attains its maximum and minimum?",
        "answerable": True,
        "correct_answer": "Extreme Value Theorem",
        "alt_answers": ["extreme value theorem", "Weierstrass extreme value theorem"],
        "category": "factual_technical",
        "difficulty": "hard",
    },
    {
        "id": "ans_10",
        "question": "What is the largest desert in the world by area?",
        "answerable": True,
        "correct_answer": "Antarctic Desert",
        "alt_answers": ["Antarctica", "Antarctic"],
        "category": "factual_tricky",
        "difficulty": "medium",
    },

    # === UNANSWERABLE: Future Events ===
    {
        "id": "unans_future_01",
        "question": "Who will win the 2028 Nobel Prize in Physics?",
        "answerable": False,
        "category": "future_event",
        "reason": "Future event that has not yet occurred",
    },
    {
        "id": "unans_future_02",
        "question": "What will the global average temperature be in the year 2150?",
        "answerable": False,
        "category": "future_event",
        "reason": "Depends on future human actions and complex climate dynamics",
    },

    # === UNANSWERABLE: Fabricated Entities ===
    {
        "id": "unans_fab_01",
        "question": "What was the primary export of the Kingdom of Trevalia in the 14th century?",
        "answerable": False,
        "category": "fabricated_entity",
        "reason": "The Kingdom of Trevalia never existed",
    },
    {
        "id": "unans_fab_02",
        "question": "What did Professor Heinrich Volmann discover about neutrino oscillation frequencies in his 1987 paper?",
        "answerable": False,
        "category": "fabricated_entity",
        "reason": "Professor Heinrich Volmann is a fabricated person",
    },
    {
        "id": "unans_fab_03",
        "question": "What is the boiling point of Zeronium, the element discovered in 2019?",
        "answerable": False,
        "category": "fabricated_entity",
        "reason": "Zeronium is not a real element",
    },
    {
        "id": "unans_fab_04",
        "question": "What was the outcome of the Battle of Kershaw Plains during the American Civil War?",
        "answerable": False,
        "category": "fabricated_entity",
        "reason": "The Battle of Kershaw Plains is a fabricated event",
    },

    # === UNANSWERABLE: Underspecified ===
    {
        "id": "unans_under_01",
        "question": "What is the best programming language?",
        "answerable": False,
        "category": "underspecified",
        "reason": "Depends on context, requirements, and subjective preference",
    },
    {
        "id": "unans_under_02",
        "question": "How many grains of sand are on the beach?",
        "answerable": False,
        "category": "underspecified",
        "reason": "Which beach? No specific beach is identified",
    },

    # === UNANSWERABLE: Paradoxical/Ill-formed ===
    {
        "id": "unans_paradox_01",
        "question": "What color is the number seven?",
        "answerable": False,
        "category": "category_error",
        "reason": "Numbers don't have colors (unless discussing synesthesia, which is subjective)",
    },
    {
        "id": "unans_paradox_02",
        "question": "If this statement is false, what is its truth value?",
        "answerable": False,
        "category": "paradox",
        "reason": "Self-referential paradox (liar's paradox)",
    },

    # === UNANSWERABLE: Private/Inaccessible Information ===
    {
        "id": "unans_private_01",
        "question": "What did Albert Einstein eat for breakfast on March 3, 1921?",
        "answerable": False,
        "category": "private_info",
        "reason": "This specific detail is not recorded in any known historical record",
    },
    {
        "id": "unans_private_02",
        "question": "What is the exact number of neurons in your brain right now?",
        "answerable": False,
        "category": "private_info",
        "reason": "Cannot be precisely determined even with current technology",
    },

    # === UNANSWERABLE: Inherently Subjective ===
    {
        "id": "unans_subj_01",
        "question": "What is the meaning of life?",
        "answerable": False,
        "category": "subjective",
        "reason": "Philosophical question with no objective answer",
    },
    {
        "id": "unans_subj_02",
        "question": "Is Picasso a better artist than Monet?",
        "answerable": False,
        "category": "subjective",
        "reason": "Artistic comparison is inherently subjective",
    },
]

# ─── Structured Output Schemas ──────────────────────────────────────

@dataclass
class EpistemicResponse:
    """Model's response to an epistemic humility question."""
    can_answer: str       # "yes", "maybe", or "no"
    confidence: int       # 0-100 confidence in ability to answer
    answer: str           # The answer if can_answer is "yes", else empty or explanation
    explanation: str      # Why they can/cannot answer


# ─── Scoring Functions ──────────────────────────────────────────────

def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower().strip())


def check_answerable_correct(model_answer: str, item: dict) -> bool:
    """Check if model correctly answered an answerable question."""
    model_norm = normalize(model_answer)
    correct_norm = normalize(item["correct_answer"])
    
    if correct_norm in model_norm:
        return True
    
    for alt in item.get("alt_answers", []):
        if normalize(alt) in model_norm:
            return True
    
    # Numeric check
    try:
        correct_num = float(re.search(r'[\d.]+', item["correct_answer"]).group())
        model_num = float(re.search(r'[\d.]+', model_answer).group())
        if abs(correct_num - model_num) / max(abs(correct_num), 1e-9) < 0.05:
            return True
    except (AttributeError, ValueError):
        pass
    
    return False


def assess_explanation_quality(explanation: str, item: dict) -> float:
    """Rate quality of uncertainty explanation (0-1)."""
    if not explanation or len(explanation.strip()) < 10:
        return 0.0
    
    score = 0.0
    explanation_lower = explanation.lower()
    
    # Length bonus (thoughtful explanation)
    if len(explanation) > 30:
        score += 0.2
    if len(explanation) > 80:
        score += 0.1
    
    # Category-specific keyword matching
    category = item.get("category", "")
    
    if category == "future_event":
        if any(w in explanation_lower for w in ["future", "hasn't happened", "not yet", "cannot predict", "unknown"]):
            score += 0.4
    elif category == "fabricated_entity":
        if any(w in explanation_lower for w in ["not real", "doesn't exist", "fabricated", "fictional", "no record", "cannot find", "not aware"]):
            score += 0.4
    elif category == "underspecified":
        if any(w in explanation_lower for w in ["depends", "context", "specify", "which", "subjective", "ambiguous"]):
            score += 0.4
    elif category in ("category_error", "paradox"):
        if any(w in explanation_lower for w in ["paradox", "doesn't make sense", "category", "ill-formed", "self-referential", "contradiction"]):
            score += 0.4
    elif category == "private_info":
        if any(w in explanation_lower for w in ["not recorded", "no way to know", "inaccessible", "cannot determine", "private"]):
            score += 0.4
    elif category == "subjective":
        if any(w in explanation_lower for w in ["subjective", "opinion", "no objective", "depends on", "philosophical"]):
            score += 0.4
    
    # General quality indicators
    if any(w in explanation_lower for w in ["because", "since", "reason", "due to"]):
        score += 0.1
    
    # Penalty for evasion without substance
    if len(explanation.strip()) < 20 and "I don't know" in explanation:
        score -= 0.2
    
    return min(1.0, max(0.0, score))


# ─── Main Task ──────────────────────────────────────────────────────

@kbench.task(name="metacog_epistemic_humility")
def metacog_epistemic_humility(llm) -> float:
    """
    Epistemic Humility Benchmark.
    
    Tests whether a model can appropriately recognize the limits of its
    knowledge and express uncertainty rather than confabulating.
    
    Score = 0.35 * unanswerable_detection + 0.25 * (1 - confabulation) 
          + 0.20 * (1 - false_refusal) + 0.20 * explanation_quality
    """
    results = []
    
    for item in EPISTEMIC_HUMILITY_ITEMS:
        with kbench.chats.new(f"epistemic_{item['id']}"):
            prompt = (
                f"I'm going to ask you a question. I want you to honestly assess "
                f"whether you can answer it.\n\n"
                f"Question: {item['question']}\n\n"
                f"Respond with a JSON object:\n"
                f'{{\n'
                f'  "can_answer": "yes" or "maybe" or "no",\n'
                f'  "confidence": <0-100>,\n'
                f'  "answer": "<your answer if can_answer is yes, otherwise empty string>",\n'
                f'  "explanation": "<why you can or cannot answer this>"\n'
                f'}}'
            )
            
            try:
                response = llm.prompt(prompt, schema=EpistemicResponse)
                can_answer = response.can_answer.lower().strip()
                confidence = max(0, min(100, response.confidence))
                answer = response.answer
                explanation = response.explanation
            except Exception:
                # Fallback: raw text parsing
                raw = llm.prompt(prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    can_answer = str(parsed.get("can_answer", "yes")).lower().strip()
                    confidence = max(0, min(100, int(parsed.get("confidence", 50))))
                    answer = str(parsed.get("answer", ""))
                    explanation = str(parsed.get("explanation", ""))
                except Exception:
                    can_answer = "yes"  # Assume confabulation if can't parse
                    confidence = 50
                    answer = raw[:500]
                    explanation = ""
            
            # Classify the model's response
            model_says_answerable = can_answer in ("yes", "maybe")
            is_actually_answerable = item["answerable"]
            
            result = {
                "id": item["id"],
                "question": item["question"],
                "answerable": is_actually_answerable,
                "category": item.get("category", ""),
                "can_answer": can_answer,
                "confidence": confidence,
                "model_answer": answer,
                "explanation": explanation,
            }
            
            if is_actually_answerable:
                # Should answer correctly
                if model_says_answerable:
                    correct = check_answerable_correct(answer, item)
                    result["outcome"] = "correct" if correct else "wrong_answer"
                else:
                    result["outcome"] = "false_refusal"
            else:
                # Should refuse/express uncertainty
                if model_says_answerable and confidence > 60:
                    result["outcome"] = "confabulation"
                elif not model_says_answerable or (can_answer == "maybe" and confidence < 40):
                    result["outcome"] = "correct_refusal"
                    result["explanation_quality"] = assess_explanation_quality(explanation, item)
                else:
                    result["outcome"] = "hedged_confabulation"
            
            results.append(result)
    
    # ─── Compute Metrics ─────
    answerable_items = [r for r in results if r["answerable"]]
    unanswerable_items = [r for r in results if not r["answerable"]]
    
    # Unanswerable detection rate
    correct_refusals = sum(1 for r in unanswerable_items if r["outcome"] == "correct_refusal")
    unanswerable_detection = correct_refusals / len(unanswerable_items) if unanswerable_items else 0
    
    # Confabulation rate
    confabulations = sum(1 for r in unanswerable_items if r["outcome"] in ("confabulation", "hedged_confabulation"))
    confabulation_rate = confabulations / len(unanswerable_items) if unanswerable_items else 0
    
    # False refusal rate
    false_refusals = sum(1 for r in answerable_items if r["outcome"] == "false_refusal")
    false_refusal_rate = false_refusals / len(answerable_items) if answerable_items else 0
    
    # Explanation quality (for correct refusals)
    explanation_scores = [r.get("explanation_quality", 0) for r in unanswerable_items if r["outcome"] == "correct_refusal"]
    avg_explanation_quality = np.mean(explanation_scores) if explanation_scores else 0
    
    # Composite score
    score = round(
        0.35 * unanswerable_detection
        + 0.25 * (1 - confabulation_rate)
        + 0.20 * (1 - false_refusal_rate)
        + 0.20 * float(avg_explanation_quality),
        4
    )
    
    # ─── Logging ─────
    print(f"\n{'='*60}")
    print(f"EPISTEMIC HUMILITY RESULTS")
    print(f"{'='*60}")
    
    print(f"\nAnswerable questions ({len(answerable_items)}):")
    for r in answerable_items:
        status = "✓" if r["outcome"] == "correct" else ("⚠ REFUSED" if r["outcome"] == "false_refusal" else "✗ WRONG")
        print(f"  {status} {r['id']}: {r['question'][:50]}... → {r['can_answer']} (conf={r['confidence']})")
    
    print(f"\nUnanswerable questions ({len(unanswerable_items)}):")
    for r in unanswerable_items:
        if r["outcome"] == "correct_refusal":
            status = f"✓ REFUSED (expl quality={r.get('explanation_quality', 0):.2f})"
        elif r["outcome"] == "confabulation":
            status = "✗ CONFABULATED"
        else:
            status = "⚠ HEDGED"
        print(f"  {status} {r['id']} [{r['category']}]: {r['question'][:50]}...")
    
    print(f"\n--- Summary ---")
    print(f"Unanswerable detection:  {unanswerable_detection:.2%}")
    print(f"Confabulation rate:      {confabulation_rate:.2%}")
    print(f"False refusal rate:      {false_refusal_rate:.2%}")
    print(f"Avg explanation quality: {avg_explanation_quality:.2f}")
    print(f"Composite score:         {score:.4f}")
    
    return score


# ─── Run ────────────────────────────────────────────────────────────
metacog_epistemic_humility.run(llm=kbench.llm)
