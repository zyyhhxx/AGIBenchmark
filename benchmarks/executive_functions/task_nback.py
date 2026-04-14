"""
N-back Working Memory v3 — Harder variant targeting LLM ceiling effects.

Changes from v2:
- Dropped trivial 1-back. Levels: 2, 3, 4, 5-back.
- Batch presentation: model sees sequence segments, must answer for ALL marked
  positions. The N-back reference letter is NOT revealed in the prompt.
- Transformation N-back: at 4-back and 5-back, half the conditions use a
  "next consonant" rule instead of identity matching.
- Lure trials (~12%): letters match at N±1 but NOT at N.
- Longer sequences: 80 items for 4-back and 5-back.
- Scoring: weighted d-prime, heavier weight on harder conditions.

Cognitive Science Basis:
- N-back (Kirchner, 1958; Owen et al., 2005)
- Dual/transformation N-back (Jaeggi et al., 2008)
- Lure trials increase false alarm rates (Kane et al., 2007)
"""

import kaggle_benchmarks as kbench
import re
import json as _json
import numpy as np
from dataclasses import dataclass
from benchmarks.executive_functions.data.nback_stimuli import NBACK_V3, _NEXT_CONSONANT


def _safe_log(data): print(_json.dumps(data, indent=2, default=str))


def _strip_think(text: str) -> str:
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def _parse_yes_no(raw: str, expected_count: int) -> list:
    """Parse YES/NO responses from model output."""
    raw = _strip_think(raw)
    raw = re.sub(r'//.*', '', raw)
    # Try JSON array
    try:
        m = re.search(r'\[.*\]', raw, re.DOTALL)
        if m:
            arr = _json.loads(m.group())
            if len(arr) == expected_count:
                return [str(x).strip().upper() for x in arr]
    except Exception:
        pass
    # Fallback: extract YES/NO tokens
    tokens = re.findall(r'\b(YES|NO|yes|no|Yes|No)\b', raw)
    result = [t.upper() for t in tokens]
    return result[:expected_count]


def run_nback_condition(llm, data: dict, condition_name: str) -> list:
    """Run one N-back condition with batch segment presentation."""
    seq = data["sequence"]
    n = data["n_back"]
    transform = data["transform"]
    segment_size = 10
    letters = [item["letter"] for item in seq]
    all_results = []

    for seg_start in range(0, len(seq), segment_size):
        seg_end = min(seg_start + segment_size, len(seq))
        eval_items = [item for item in seq[seg_start:seg_end] if item["position"] >= n]
        if not eval_items:
            continue

        # Build display — show FULL sequence up to this segment
        display_lines = []
        for i in range(seg_end):
            letter = letters[i]
            marker = " <-- respond" if seg_start <= i < seg_end and i >= n else ""
            display_lines.append(f"  [{i:2d}] {letter}{marker}")

        positions = [item["position"] for item in eval_items]

        if transform:
            rule_text = (
                f"Rule: For each marked position, answer YES if the letter is the "
                f"NEXT CONSONANT in the alphabet after the letter exactly {n} positions "
                f"earlier (B→C→D→F→G→H→J→K→L→M→N→P→Q→R→S→T→V→W→X→Z→B). "
                f"Answer NO otherwise."
            )
        else:
            rule_text = (
                f"Rule: For each marked position, answer YES if the letter is the "
                f"SAME as the letter exactly {n} positions earlier. Answer NO otherwise."
            )

        with kbench.chats.new(f"{condition_name}_seg{seg_start}"):
            prompt = (
                f"**{n}-Back {'Transform ' if transform else ''}Task — "
                f"Segment {seg_start // segment_size + 1}**\n\n"
                f"{rule_text}\n\n"
                f"Sequence so far:\n"
                + "\n".join(display_lines) + "\n\n"
                f"For positions {positions}, respond with ONLY a JSON array of "
                f"YES/NO strings. Example: [\"YES\", \"NO\", \"NO\", ...]\n"
                f"Give exactly {len(eval_items)} responses."
            )

            raw = llm.prompt(prompt)
            responses = _parse_yes_no(raw, len(eval_items))

            while len(responses) < len(eval_items):
                responses.append("NO")

            for item, resp in zip(eval_items, responses):
                correct = (resp == item["correct_response"])
                all_results.append({
                    "position": item["position"],
                    "letter": item["letter"],
                    "type": item["type"],
                    "correct_response": item["correct_response"],
                    "model_response": resp,
                    "correct": correct,
                    "is_hit": resp == "YES" and item["correct_response"] == "YES",
                    "is_miss": resp == "NO" and item["correct_response"] == "YES",
                    "is_false_alarm": resp == "YES" and item["correct_response"] == "NO",
                    "quartile": item["quartile"],
                })

    return all_results


def _dprime(hits, misses, fa, cr):
    """Compute d-prime with log-linear correction."""
    hr = (hits + 0.5) / (hits + misses + 1)
    far = (fa + 0.5) / (fa + cr + 1)
    # Rational approx of inverse normal CDF
    def _ppf(p):
        import math
        if p <= 0: return -4.0
        if p >= 1: return 4.0
        if p < 0.5:
            t = math.sqrt(-2 * math.log(p))
            return -(2.515517 + 0.802853*t + 0.010328*t*t) / \
                    (1 + 1.432788*t + 0.189269*t*t + 0.001308*t*t*t) + t
        else:
            return -_ppf(1 - p)
    return round(_ppf(hr) - _ppf(far), 4)


@kbench.task(name="N-Back Working Memory")
def exec_func_nback(llm) -> float:
    """
    N-back Working Memory v3.
    
    Tests working memory updating across N=2,3,4,5 with lure trials
    and transformation rules at higher N levels.
    
    Score = weighted normalized d-prime across conditions.
    """
    conditions = [
        ("2back", NBACK_V3["2back"], 0.08),
        ("3back", NBACK_V3["3back"], 0.15),
        ("4back", NBACK_V3["4back"], 0.15),
        ("4back_transform", NBACK_V3["4back_transform"], 0.20),
        ("5back", NBACK_V3["5back"], 0.15),
        ("5back_transform", NBACK_V3["5back_transform"], 0.27),
    ]
    
    condition_results = {}
    for cond_name, cond_data, weight in conditions:
        results = run_nback_condition(llm, cond_data, cond_name)
        
        hits = sum(1 for r in results if r["is_hit"])
        misses = sum(1 for r in results if r["is_miss"])
        fa = sum(1 for r in results if r["is_false_alarm"])
        cr = sum(1 for r in results if r["correct"] and r["correct_response"] == "NO")
        
        dp = _dprime(hits, misses, fa, cr)
        accuracy = sum(1 for r in results if r["correct"]) / max(len(results), 1)
        
        # Lure-specific false alarm rate
        lure_items = [r for r in results if r["type"] == "lure"]
        lure_fa = sum(1 for r in lure_items if r["model_response"] == "YES") / max(len(lure_items), 1)
        
        condition_results[cond_name] = {
            "d_prime": dp,
            "accuracy": round(accuracy, 4),
            "hits": hits, "misses": misses,
            "false_alarms": fa, "correct_rejections": cr,
            "lure_false_alarm_rate": round(lure_fa, 4),
            "n_items": len(results),
            "weight": weight,
        }
    
    # Composite: weighted normalized d-prime (d'=0→0, d'=4→1)
    score = sum(
        w * float(np.clip(condition_results[name]["d_prime"] / 4.0, 0, 1))
        for name, _, w in conditions
    )
    score = round(float(np.clip(score, 0, 1)), 4)
    
    # Logging
    print(f"\n{'='*60}")
    print(f"N-BACK WORKING MEMORY v3 RESULTS")
    print(f"{'='*60}")
    for name, _, w in conditions:
        cr = condition_results[name]
        print(f"\n  {name} (weight={w}):")
        print(f"    d'={cr['d_prime']:.3f}  acc={cr['accuracy']:.2%}  "
              f"hits={cr['hits']} miss={cr['misses']} FA={cr['false_alarms']} CR={cr['correct_rejections']}")
        print(f"    lure FA rate={cr['lure_false_alarm_rate']:.2%}")
    print(f"\n  COMPOSITE SCORE: {score:.4f}")
    print(f"{'='*60}")
    
    _safe_log({
        "benchmark": "N-back v3",
        "conditions": condition_results,
        "composite_score": score,
    })
    
    return score
