"""
Social Cognition Benchmark 1: False-Belief Theory of Mind (v6)

Tests Theory of Mind through Sally-Anne style false-belief attribution
across multiple difficulty levels, heavily weighted toward higher-order
nested belief reasoning (4th and 5th order).

v5 Rationale:
Prior iterations (v3, v4) showed that 1st-3rd order false-belief is
effectively reading comprehension for LLMs — all frontier models score >0.85.
Only 4th-order nested belief scenarios discriminated (Opus scored 0.667).
Batch multi-scenario tracking and misleading cues both FAILED to lower scores.

This version:
- Removes the batch section entirely (it increased scores, not decreased them)
- Expands 4th-order from 6→12 scenarios with complex deception chains
- Adds 8 "5th-order" scenarios (5-character narratives with cascading lies)
- Heavily weights higher-order: 70% of score from 4th+5th order

Score = 0.00 * tier1 + 0.00 * tier2 + 0.05 * tier3 + 0.70 * tier4 + 0.25 * tier5

Cognitive Science Basis:
- Wimmer & Perner (1983): original false-belief paradigm
- Baron-Cohen, Leslie & Frith (1985): Sally-Anne test
- Perner & Wimmer (1985): 2nd-order false beliefs
- Miller (2009): 3rd-order ToM in adults
- Liddle & Nettle (2006): higher-order intentionality limits
- Kinderman, Dunbar & Bentall (1998): 4th/5th order ToM difficulty scaling
- Dunbar (1998): social brain hypothesis — human limit ~5th-6th order

Shortcut Resistance:
- Higher-order scenarios require genuine recursive mentalizing
- Cascading lies create divergence between reality and attributed beliefs
- 5-character scenarios with multiple intermediaries stress working memory
- Misleading cues in 4th-order scenarios penalize heuristic reasoning
"""

import kaggle_benchmarks as kbench
import json as _json
def _safe_log(data): print(_json.dumps(data, indent=2, default=str))
from dataclasses import dataclass
import numpy as np
from data.false_belief_scenarios import FALSE_BELIEF_SCENARIOS


@dataclass
class ToMResponse:
    """Model's response to a ToM question."""
    answer: str       # The answer
    reasoning: str    # Brief explanation


def check_answer(model_answer: str, accept_patterns: list) -> bool:
    """Check if model's answer matches any accept pattern."""
    model_lower = model_answer.lower().strip()
    return any(pattern.lower() in model_lower for pattern in accept_patterns)


def check_misleading(model_answer: str, misleading_patterns: list) -> bool:
    """Check if model gave the misleading (heuristic-based) answer."""
    model_lower = model_answer.lower().strip()
    return any(pattern.lower() in model_lower for pattern in misleading_patterns)


@kbench.task(name="False Belief (Theory of Mind)")
def social_cog_false_belief(llm) -> float:
    """
    False-Belief Theory of Mind Benchmark (v6).

    Individual scenarios only (no batch section).
    Heavy weighting toward 4th and 5th order nested beliefs.
    
    Scoring: 0.00 * tier1 + 0.00 * tier2 + 0.05 * tier3 + 0.70 * tier4 + 0.25 * tier5

    Cognitive Science: Wimmer & Perner (1983), Kinderman et al. (1998), Miller (2009).
    Human 1st-order: ~95% adults. 2nd-order: ~80%. 3rd-order: ~60%. 4th-order: ~40%.
    5th-order (5-character cascading deception): ~20-30%.
    """
    results = []
    
    for scenario in FALSE_BELIEF_SCENARIOS:
        scenario_results = {
            "id": scenario["id"],
            "order": scenario["order"],
            "misleading": scenario.get("misleading", False),
        }
        
        base_prompt = f"Read this scenario carefully:\n\n{scenario['scenario']}\n\n"
        
        # Belief question (the key ToM test)
        with kbench.chats.new(f"tom_belief_{scenario['id']}"):
            belief_prompt = base_prompt + f"Question: {scenario['belief_question']}\nAnswer briefly."
            try:
                response = llm.prompt(belief_prompt, schema=ToMResponse)
                belief_answer = response.answer
            except Exception:
                belief_answer = llm.prompt(belief_prompt)
            belief_correct = check_answer(belief_answer, scenario["belief_accept"])
            scenario_results["belief_correct"] = belief_correct
            scenario_results["belief_answer"] = belief_answer
            
            # Track misleading errors
            if scenario.get("misleading", False):
                scenario_results["gave_misleading_answer"] = check_misleading(
                    belief_answer, scenario.get("misleading_answer", [])
                )
        
        # Reality control question
        with kbench.chats.new(f"tom_reality_{scenario['id']}"):
            reality_prompt = base_prompt + f"Question: {scenario['reality_question']}\nAnswer briefly."
            try:
                response = llm.prompt(reality_prompt, schema=ToMResponse)
                reality_answer = response.answer
            except Exception:
                reality_answer = llm.prompt(reality_prompt)
            reality_correct = check_answer(reality_answer, scenario["reality_accept"])
            scenario_results["reality_correct"] = reality_correct
        
        # Memory control question
        with kbench.chats.new(f"tom_memory_{scenario['id']}"):
            memory_prompt = base_prompt + f"Question: {scenario['memory_question']}\nAnswer briefly."
            try:
                response = llm.prompt(memory_prompt, schema=ToMResponse)
                memory_answer = response.answer
            except Exception:
                memory_answer = llm.prompt(memory_prompt)
            memory_correct = check_answer(memory_answer, scenario["memory_accept"])
            scenario_results["memory_correct"] = memory_correct
        
        results.append(scenario_results)
    
    # ── Compute Tiered Metrics ──
    tier1 = [r for r in results if r["order"] == 1]
    tier2 = [r for r in results if r["order"] == 2]
    tier3 = [r for r in results if r["order"] == 3]
    tier4 = [r for r in results if r["order"] == 4]
    tier5 = [r for r in results if r["order"] == 5]
    misleading = [r for r in results if r.get("misleading", False)]
    
    def tier_score(tier_results):
        """Compute control-adjusted belief accuracy for a tier."""
        if not tier_results:
            return 0.0, 0.0, 0.0
        
        belief_acc = sum(1 for r in tier_results if r["belief_correct"]) / len(tier_results)
        
        reality_correct = sum(1 for r in tier_results if r["reality_correct"])
        memory_correct = sum(1 for r in tier_results if r["memory_correct"])
        control_acc = (reality_correct + memory_correct) / (2 * len(tier_results))
        
        control_penalty = max(0, 1.0 - control_acc)
        adjusted = max(0, belief_acc - control_penalty)
        
        return adjusted, belief_acc, control_acc
    
    t1_adj, t1_belief, t1_ctrl = tier_score(tier1)
    t2_adj, t2_belief, t2_ctrl = tier_score(tier2)
    t3_adj, t3_belief, t3_ctrl = tier_score(tier3)
    t4_adj, t4_belief, t4_ctrl = tier_score(tier4)
    t5_adj, t5_belief, t5_ctrl = tier_score(tier5)
    
    # Composite: heavily weighted toward 4th-order (most discriminating tier)
    # 0.05 * 1st + 0.05 * 2nd + 0.10 * 3rd + 0.60 * 4th + 0.20 * 5th
    score = 0.00 * t1_adj + 0.00 * t2_adj + 0.05 * t3_adj + 0.70 * t4_adj + 0.25 * t5_adj
    score = round(float(np.clip(score, 0, 1)), 4)
    
    # Misleading error rate (diagnostic)
    misleading_errors = sum(1 for r in misleading if r.get("gave_misleading_answer", False))
    misleading_error_rate = misleading_errors / max(len(misleading), 1)
    
    _safe_log({
        "benchmark": "False-Belief Theory of Mind v6",
        "n_scenarios": len(results),
        "scoring": "0.00*T1 + 0.00*T2 + 0.05*T3 + 0.70*T4 + 0.25*T5",
        "tiers": {
            "1st_order": {"count": len(tier1), "adjusted": round(t1_adj, 4), "belief": round(t1_belief, 4), "control": round(t1_ctrl, 4)},
            "2nd_order": {"count": len(tier2), "adjusted": round(t2_adj, 4), "belief": round(t2_belief, 4), "control": round(t2_ctrl, 4)},
            "3rd_order": {"count": len(tier3), "adjusted": round(t3_adj, 4), "belief": round(t3_belief, 4), "control": round(t3_ctrl, 4)},
            "4th_order": {"count": len(tier4), "adjusted": round(t4_adj, 4), "belief": round(t4_belief, 4), "control": round(t4_ctrl, 4)},
            "5th_order": {"count": len(tier5), "adjusted": round(t5_adj, 4), "belief": round(t5_belief, 4), "control": round(t5_ctrl, 4)},
        },
        "misleading": {
            "count": len(misleading),
            "error_rate": round(misleading_error_rate, 4),
        },
        "per_scenario": [
            {"id": r["id"], "order": r["order"], "belief_correct": r["belief_correct"],
             "belief_answer": r.get("belief_answer", ""), "reality_correct": r["reality_correct"],
             "memory_correct": r["memory_correct"]}
            for r in results
        ],
        "composite_score": score,
    })
    
    return score

if __name__ == '__main__':
    social_cog_false_belief.run(llm=kbench.llm)
