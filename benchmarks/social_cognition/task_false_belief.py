"""
Social Cognition Benchmark 1: False-Belief Theory of Mind

Tests Theory of Mind through Sally-Anne style false-belief attribution.
Includes both 1st-order (what does X believe?) and 2nd-order
(what does X think Y believes?) belief questions.

Cognitive Science Basis:
- Wimmer & Perner (1983): original false-belief paradigm
- Baron-Cohen, Leslie & Frith (1985): Sally-Anne test
- Perner & Wimmer (1985): 2nd-order false beliefs
- Premack & Woodruff (1978): theory of mind in apes

Key Innovation:
- Reality and memory control questions isolate ToM from comprehension
- Score = belief_accuracy - control_accuracy (positive = genuine ToM)
- 2nd-order beliefs are harder (require recursive mentalizing)

Metrics:
- 1st-order belief accuracy
- 2nd-order belief accuracy
- Control question accuracy (reality + memory)
- ToM score: belief_accuracy - max(0, 1 - control_accuracy)
  (Penalizes if controls fail, isolates ToM from comprehension)

Score = 0.30 * first_order + 0.40 * second_order + 0.30 * control_adjusted

Shortcut Resistance:
- Correct answer to belief question is ALWAYS different from reality
- Control questions verify comprehension
- 2nd-order requires recursive mentalizing, not pattern matching
- Diverse scenarios prevent template matching
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


@kbench.task(name="social_cog_false_belief")
def social_cog_false_belief(llm) -> float:
    """
    False-Belief Theory of Mind Benchmark.

    Tests 1st-order and 2nd-order belief attribution through
    Sally-Anne style scenarios with reality/memory control questions.

    Score = 0.30 * first_order + 0.40 * second_order + 0.30 * control_adjusted

    Cognitive Science: Wimmer & Perner (1983), Baron-Cohen et al. (1985).
    Human 1st-order accuracy: ~95% (adults), ~50% (4-year-olds).
    Human 2nd-order accuracy: ~80% (adults).
    """
    results = []
    
    for scenario in FALSE_BELIEF_SCENARIOS:
        scenario_results = {"id": scenario["id"], "order": scenario["order"]}
        
        # Present scenario and ask all 3 questions in sequence
        base_prompt = f"Read this scenario carefully:\n\n{scenario['scenario']}\n\n"
        
        # Belief question (the key ToM test)
        with kbench.chats.new(f"tom_belief_{scenario['id']}"):
            belief_prompt = base_prompt + f"Question: {scenario['belief_question']}\nAnswer briefly."
            try:
                response = llm(belief_prompt, response_format=ToMResponse)
                belief_answer = response.answer
            except Exception:
                belief_answer = llm(belief_prompt)
            belief_correct = check_answer(belief_answer, scenario["belief_accept"])
            scenario_results["belief_correct"] = belief_correct
            scenario_results["belief_answer"] = belief_answer
        
        # Reality control question
        with kbench.chats.new(f"tom_reality_{scenario['id']}"):
            reality_prompt = base_prompt + f"Question: {scenario['reality_question']}\nAnswer briefly."
            try:
                response = llm(reality_prompt, response_format=ToMResponse)
                reality_answer = response.answer
            except Exception:
                reality_answer = llm(reality_prompt)
            reality_correct = check_answer(reality_answer, scenario["reality_accept"])
            scenario_results["reality_correct"] = reality_correct
        
        # Memory control question
        with kbench.chats.new(f"tom_memory_{scenario['id']}"):
            memory_prompt = base_prompt + f"Question: {scenario['memory_question']}\nAnswer briefly."
            try:
                response = llm(memory_prompt, response_format=ToMResponse)
                memory_answer = response.answer
            except Exception:
                memory_answer = llm(memory_prompt)
            memory_correct = check_answer(memory_answer, scenario["memory_accept"])
            scenario_results["memory_correct"] = memory_correct
        
        results.append(scenario_results)
    
    # ── Compute Metrics ──
    
    first_order = [r for r in results if r["order"] == 1]
    second_order = [r for r in results if r["order"] == 2]
    
    fo_belief_acc = sum(1 for r in first_order if r["belief_correct"]) / max(len(first_order), 1)
    so_belief_acc = sum(1 for r in second_order if r["belief_correct"]) / max(len(second_order), 1)
    
    # Control accuracy (reality + memory combined)
    all_reality_correct = sum(1 for r in results if r["reality_correct"])
    all_memory_correct = sum(1 for r in results if r["memory_correct"])
    control_acc = (all_reality_correct + all_memory_correct) / (2 * len(results))
    
    # Control-adjusted score: belief accuracy penalized by control failures
    # If controls are perfect (1.0), no penalty. If controls fail, it suggests
    # the model doesn't understand the scenario, so ToM score is unreliable.
    control_penalty = max(0, 1.0 - control_acc)
    fo_adjusted = max(0, fo_belief_acc - control_penalty)
    so_adjusted = max(0, so_belief_acc - control_penalty)
    
    # ── Composite Score ──
    score = (
        0.30 * fo_adjusted +
        0.40 * so_adjusted +
        0.30 * control_acc
    )
    score = round(float(np.clip(score, 0, 1)), 4)
    
    _safe_log({
        "benchmark": "False-Belief Theory of Mind",
        "n_scenarios": len(results),
        "first_order": {
            "count": len(first_order),
            "belief_accuracy": round(fo_belief_acc, 4),
            "adjusted": round(fo_adjusted, 4),
        },
        "second_order": {
            "count": len(second_order),
            "belief_accuracy": round(so_belief_acc, 4),
            "adjusted": round(so_adjusted, 4),
        },
        "control_accuracy": round(control_acc, 4),
        "control_penalty": round(control_penalty, 4),
        "composite_score": score,
        "per_scenario": results,
    })
    
    return score

social_cog_false_belief.run(llm=kbench.llm)
