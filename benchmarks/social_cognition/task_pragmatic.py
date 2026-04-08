"""
Social Cognition Benchmark 2: Pragmatic Inference

Tests understanding of pragmatic meaning — what speakers intend vs. what
they literally say. Covers Gricean maxims and implicatures.

Cognitive Science Basis:
- Grice (1975): Cooperative principle and conversational maxims
- Scalar implicature: "some" → "not all" (Horn, 1984)
- Indirect speech acts (Searle, 1975)
- Irony comprehension requires theory of mind + context integration

Categories tested:
1. Scalar implicature (5 items)
2. Indirect requests (5 items)
3. Irony/sarcasm (5 items)
4. Understatement (5 items)

Metrics:
- Intended meaning accuracy: model identifies the speaker's actual intent
- Literal trap rate: how often model gives the literal (surface) interpretation
- Category breakdown: performance by pragmatic type

Score = intended_accuracy (primary) - 0.1 * literal_trap_rate (penalty)

Shortcut Resistance:
- Each item has both literal and intended meaning — model must choose
- Diverse pragmatic types prevent single-strategy shortcuts
- Rich context makes simple pattern matching insufficient
- Intended meanings require world knowledge + social reasoning
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
from data.pragmatic_items import PRAGMATIC_ITEMS


@dataclass
class PragmaticResponse:
    """Model's pragmatic inference response."""
    speaker_intent: str   # What the speaker actually means/intends
    is_literal: bool      # Is the statement meant literally or figuratively?
    reasoning: str        # Brief explanation


def check_patterns(text: str, patterns: list) -> bool:
    """Check if text matches any pattern."""
    text_lower = text.lower()
    return any(p.lower() in text_lower for p in patterns)


@kbench.task(name="social_cog_pragmatic")
def social_cog_pragmatic(llm) -> float:
    """
    Pragmatic Inference Benchmark.

    Tests understanding of speaker intent beyond literal meaning.
    Covers scalar implicature, indirect requests, irony, and understatement.

    Score = intended_accuracy - 0.1 * literal_trap_rate

    Cognitive Science: Grice (1975), Horn (1984), Searle (1975).
    Human performance: ~90-95% for adults on intended meaning.
    """
    results = []
    category_results = {}
    
    for item in PRAGMATIC_ITEMS:
        cat = item["type"]
        if cat not in category_results:
            category_results[cat] = {"intended": 0, "literal": 0, "total": 0}
        
        prompt = (
            f"Read this situation carefully:\n\n"
            f"Context: {item['context']}\n\n"
            f"Question: {item['question']}\n\n"
            f"Consider both the literal meaning and what the speaker actually intends "
            f"to communicate. What is the speaker's TRUE intended meaning?"
        )
        
        with kbench.chats.new(f"pragmatic_{item['id']}"):
            response = llm(prompt, response_format=PragmaticResponse)
        
        got_intended = check_patterns(response.speaker_intent, item["intended_accept"])
        got_literal = check_patterns(response.speaker_intent, item["literal_accept"])
        
        # If model gives both intended and literal markers, count intended
        if got_intended:
            got_literal = False
        
        results.append({
            "id": item["id"],
            "type": cat,
            "got_intended": got_intended,
            "got_literal": got_literal,
            "model_answer": response.speaker_intent,
            "marked_literal": response.is_literal,
        })
        
        category_results[cat]["total"] += 1
        if got_intended:
            category_results[cat]["intended"] += 1
        if got_literal:
            category_results[cat]["literal"] += 1
    
    # ── Compute Metrics ──
    
    intended_acc = sum(1 for r in results if r["got_intended"]) / len(results)
    literal_trap = sum(1 for r in results if r["got_literal"]) / len(results)
    
    # Category breakdown
    cat_scores = {}
    for cat, data in category_results.items():
        cat_scores[cat] = {
            "intended_accuracy": round(data["intended"] / max(data["total"], 1), 4),
            "literal_trap_rate": round(data["literal"] / max(data["total"], 1), 4),
            "count": data["total"],
        }
    
    # ── Composite Score ──
    score = intended_acc - 0.1 * literal_trap
    score = round(float(np.clip(score, 0, 1)), 4)
    
    kbench.log({
        "benchmark": "Pragmatic Inference",
        "n_items": len(results),
        "intended_accuracy": round(intended_acc, 4),
        "literal_trap_rate": round(literal_trap, 4),
        "composite_score": score,
        "by_category": cat_scores,
        "per_item": results,
    })
    
    return score

social_cog_pragmatic.run(llm=kbench.llm)
