"""
Social Cognition Benchmark 2: Pragmatic Inference

Tests understanding of pragmatic meaning — what speakers intend vs. what
they literally say. Covers Gricean maxims and implicatures.

Cognitive Science Basis:
- Grice (1975): Cooperative principle and conversational maxims
- Scalar implicature: "some" → "not all" (Horn, 1984)
- Indirect speech acts (Searle, 1975)
- Irony comprehension requires theory of mind + context integration
- Politeness theory (Brown & Levinson, 1987)
- Relevance theory (Sperber & Wilson, 1986)

Three difficulty tiers:
1. Direct (25 items, weight 0.15): scalar implicature, indirect requests, irony, understatement, relevance
2. Indirect/contextual (10 items, weight 0.35): domain implicature, politeness indirection, maxim violations, strategic ambiguity
3. Complex multi-layer (10 items, weight 0.50): litotes, rhetorical reversal, multi-layer irony, presupposition traps, performative contradictions

Metrics:
- Per-tier: intended_accuracy - 0.1 * literal_trap_rate
- Composite = 0.15 * direct + 0.35 * indirect + 0.50 * complex

Shortcut Resistance:
- Hard tiers require world knowledge + social reasoning, not just "opposite of literal"
- Complex tier includes reverse traps where literal interpretation is closer to correct
- Narrow acceptance patterns prevent vague answers from matching
"""

import kaggle_benchmarks as kbench
import json as _json
def _safe_log(data): print(_json.dumps(data, indent=2, default=str))
from dataclasses import dataclass
import numpy as np
from data.pragmatic_items import PRAGMATIC_ITEMS_DIRECT, PRAGMATIC_ITEMS_INDIRECT, PRAGMATIC_ITEMS_COMPLEX


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


def _score_tier(items, llm, tier_label):
    """Run items for one tier, return (score, details)."""
    results = []
    category_results = {}

    for item in items:
        cat = item["type"]
        if cat not in category_results:
            category_results[cat] = {"intended": 0, "literal": 0, "total": 0}

        prompt = (
            f"Read this situation carefully:\n\n"
            f"Context: {item['context']}\n\n"
            f"Question: {item['question']}\n\n"
            f"Consider both the literal meaning and what the speaker actually intends "
            f"to communicate. What is the speaker's TRUE intended meaning?\n\n"
            f"Give a concise answer (1-3 sentences) focused on the intended meaning."
        )

        with kbench.chats.new(f"pragmatic_{item['id']}"):
            try:
                response = llm.prompt(prompt, schema=PragmaticResponse)
                speaker_intent = response.speaker_intent
                is_literal = response.is_literal
            except Exception:
                raw = llm.prompt(prompt)
                speaker_intent = raw
                is_literal = False

        got_intended = check_patterns(speaker_intent, item["intended_accept"])
        got_literal = check_patterns(speaker_intent, item["literal_accept"])

        # If model gives both intended and literal markers, count intended
        if got_intended:
            got_literal = False

        results.append({
            "id": item["id"],
            "type": cat,
            "tier": tier_label,
            "got_intended": got_intended,
            "got_literal": got_literal,
            "model_answer": speaker_intent,
            "marked_literal": is_literal,
        })

        category_results[cat]["total"] += 1
        if got_intended:
            category_results[cat]["intended"] += 1
        if got_literal:
            category_results[cat]["literal"] += 1

    n = len(results)
    intended_acc = sum(1 for r in results if r["got_intended"]) / max(n, 1)
    literal_trap = sum(1 for r in results if r["got_literal"]) / max(n, 1)
    tier_score = max(0.0, intended_acc - 0.1 * literal_trap)

    return tier_score, intended_acc, literal_trap, results, category_results


@kbench.task(name="social_cog_pragmatic", version=2)
def social_cog_pragmatic(llm) -> float:
    """
    Pragmatic Inference Benchmark (v2 — difficulty-tiered).

    Tests understanding of speaker intent beyond literal meaning across
    three difficulty tiers: direct implicature, indirect/contextual, and
    complex multi-layer pragmatics.

    Composite = 0.15 * direct + 0.35 * indirect + 0.50 * complex

    Cognitive Science: Grice (1975), Horn (1984), Searle (1975),
    Brown & Levinson (1987), Sperber & Wilson (1986).
    Human performance: ~90-95% direct, ~75-85% indirect, ~60-75% complex.
    """
    # Run each tier
    direct_score, direct_acc, direct_lit, direct_results, direct_cats = \
        _score_tier(PRAGMATIC_ITEMS_DIRECT, llm, "direct")
    indirect_score, indirect_acc, indirect_lit, indirect_results, indirect_cats = \
        _score_tier(PRAGMATIC_ITEMS_INDIRECT, llm, "indirect")
    complex_score, complex_acc, complex_lit, complex_results, complex_cats = \
        _score_tier(PRAGMATIC_ITEMS_COMPLEX, llm, "complex")

    # Difficulty-weighted composite
    composite = 0.15 * direct_score + 0.35 * indirect_score + 0.50 * complex_score
    composite = round(float(np.clip(composite, 0, 1)), 4)

    all_results = direct_results + indirect_results + complex_results

    # Merge category results
    all_cats = {}
    for cats in [direct_cats, indirect_cats, complex_cats]:
        for cat, data in cats.items():
            if cat not in all_cats:
                all_cats[cat] = {"intended": 0, "literal": 0, "total": 0}
            all_cats[cat]["intended"] += data["intended"]
            all_cats[cat]["literal"] += data["literal"]
            all_cats[cat]["total"] += data["total"]

    cat_scores = {}
    for cat, data in all_cats.items():
        cat_scores[cat] = {
            "intended_accuracy": round(data["intended"] / max(data["total"], 1), 4),
            "literal_trap_rate": round(data["literal"] / max(data["total"], 1), 4),
            "count": data["total"],
        }

    _safe_log({
        "benchmark": "Pragmatic Inference v2 (difficulty-tiered)",
        "n_items": len(all_results),
        "composite_score": composite,
        "tier_scores": {
            "direct": {"score": round(direct_score, 4), "weight": 0.15,
                       "intended_acc": round(direct_acc, 4), "literal_trap": round(direct_lit, 4),
                       "n_items": len(PRAGMATIC_ITEMS_DIRECT)},
            "indirect": {"score": round(indirect_score, 4), "weight": 0.35,
                         "intended_acc": round(indirect_acc, 4), "literal_trap": round(indirect_lit, 4),
                         "n_items": len(PRAGMATIC_ITEMS_INDIRECT)},
            "complex": {"score": round(complex_score, 4), "weight": 0.50,
                        "intended_acc": round(complex_acc, 4), "literal_trap": round(complex_lit, 4),
                        "n_items": len(PRAGMATIC_ITEMS_COMPLEX)},
        },
        "by_category": cat_scores,
        "per_item": all_results,
    })

    return composite


if __name__ == '__main__':
    social_cog_pragmatic.run(llm=kbench.llm)
