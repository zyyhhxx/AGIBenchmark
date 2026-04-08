"""
Executive Functions Benchmark 4: N-back Working Memory

Tests working memory updating — a core executive function.

The model sees a sequence of letters one at a time and must identify when
the current letter matches the one N positions back. N varies from 1 to 3.

Cognitive Science Basis:
- N-back task (Kirchner, 1958; Owen et al., 2005)
- Working memory updating is a core executive function (Miyake et al., 2000)
- Difficulty increases with N (1-back ~ easy, 3-back ~ hard for humans)
- d-prime (signal detection) measures discrimination between targets and non-targets

Metrics:
- d-prime per N level: sensitivity (hit rate vs. false alarm rate)
- Hit rate: proportion of targets correctly identified
- False alarm rate: proportion of non-targets incorrectly called targets
- N-level scaling: performance should degrade as N increases

Score = weighted average d-prime across N levels, normalized to [0, 1]

Shortcut Resistance:
- Sequences are procedurally generated with controlled target rates
- Letters are consonants only (no word formation cues)
- Must track temporal position, not just item identity
- 3-back is genuinely taxing for working memory
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import numpy as np
from data.nback_stimuli import NBACK_SEQUENCES


@dataclass
class NbackResponse:
    """Model's N-back judgment."""
    is_match: bool    # Does this item match the one N positions back?
    reasoning: str    # Brief explanation


def compute_dprime(hits: int, misses: int, false_alarms: int, correct_rejections: int) -> float:
    """
    Compute d-prime (sensitivity index) from signal detection theory.
    
    d' = Z(hit_rate) - Z(false_alarm_rate)
    Uses log-linear correction to avoid infinite values.
    """
    # Log-linear correction (Hautus, 1995)
    hit_rate = (hits + 0.5) / (hits + misses + 1)
    fa_rate = (false_alarms + 0.5) / (false_alarms + correct_rejections + 1)
    
    # Z-transform (inverse normal CDF)
    from scipy.stats import norm
    d_prime = norm.ppf(hit_rate) - norm.ppf(fa_rate)
    
    return round(float(d_prime), 4)


def dprime_fallback(hits, misses, false_alarms, correct_rejections):
    """Compute d-prime without scipy (manual Z approximation)."""
    hit_rate = (hits + 0.5) / (hits + misses + 1)
    fa_rate = (false_alarms + 0.5) / (false_alarms + correct_rejections + 1)
    
    # Rational approximation of inverse normal CDF (Abramowitz & Stegun)
    def norm_ppf(p):
        # Beasley-Springer-Moro algorithm
        a = [0, -3.969683028665376e+01, 2.209460984245205e+02,
             -2.759285104469687e+02, 1.383577518672690e+02,
             -3.066479806614716e+01, 2.506628277459239e+00]
        b = [0, -5.447609879822406e+01, 1.615858368580409e+02,
             -1.556989798598866e+02, 6.680131188771972e+01,
             -1.328068155288572e+01]
        c = [0, -7.784894002430293e-03, -3.223964580411365e-01,
             -2.400758277161838e+00, -2.549732539343734e+00,
             4.374664141464968e+00, 2.938163982698783e+00]
        d = [0, 7.784695709041462e-03, 3.224671290700398e-01,
             2.445134137142996e+00, 3.754408661907416e+00]
        
        p_low = 0.02425
        p_high = 1 - p_low
        
        if p < p_low:
            q = np.sqrt(-2 * np.log(p))
            return (((((c[1]*q+c[2])*q+c[3])*q+c[4])*q+c[5])*q+c[6]) / \
                   ((((d[1]*q+d[2])*q+d[3])*q+d[4])*q+1)
        elif p <= p_high:
            q = p - 0.5
            r = q * q
            return (((((a[1]*r+a[2])*r+a[3])*r+a[4])*r+a[5])*r+a[6])*q / \
                   (((((b[1]*r+b[2])*r+b[3])*r+b[4])*r+b[5])*r+1)
        else:
            q = np.sqrt(-2 * np.log(1 - p))
            return -(((((c[1]*q+c[2])*q+c[3])*q+c[4])*q+c[5])*q+c[6]) / \
                    ((((d[1]*q+d[2])*q+d[3])*q+d[4])*q+1)
    
    d_prime = norm_ppf(hit_rate) - norm_ppf(fa_rate)
    return round(float(d_prime), 4)


@kbench.task(name="exec_func_nback")
def exec_func_nback(llm) -> float:
    """
    N-back Working Memory Benchmark.

    Tests working memory updating across N=1, 2, 3 levels.
    Model must identify when current item matches the one N steps back.

    Score = normalized weighted d-prime across N levels.

    Cognitive Science Basis: Kirchner (1958), Owen et al. (2005), Miyake et al. (2000).
    Human d-prime: ~3.5 (1-back), ~2.5 (2-back), ~1.5 (3-back).
    """
    level_results = {}
    
    for n_level in [1, 2, 3]:
        sequence = NBACK_SEQUENCES[n_level]
        hits = 0
        misses = 0
        false_alarms = 0
        correct_rejections = 0
        trial_details = []
        
        # Present sequence with sliding context window
        for i, trial in enumerate(sequence):
            if i < n_level:
                # First N items: no N-back comparison possible
                continue
            
            # Show recent context (last N+2 items for context, current highlighted)
            context_start = max(0, i - n_level - 1)
            context_items = [sequence[j]["item"] for j in range(context_start, i)]
            current_item = trial["item"]
            
            prompt = (
                f"{n_level}-BACK TASK — Position {trial['position']}\n\n"
                f"Rule: Say 'MATCH' if the current letter is the SAME as the letter "
                f"that appeared {n_level} position{'s' if n_level > 1 else ''} ago. "
                f"Otherwise say 'NO MATCH'.\n\n"
                f"Recent sequence: {' '.join(context_items)}\n"
                f"Current letter: **{current_item}**\n"
                f"Letter {n_level} back: **{sequence[i - n_level]['item']}**\n\n"
                f"Is this a MATCH or NO MATCH?"
            )
            
            with kbench.chats.new(f"nback_{n_level}_{i}"):
                response = llm(prompt, response_format=NbackResponse)
            
            model_says_match = response.is_match
            is_target = trial["is_target"]
            
            if is_target and model_says_match:
                hits += 1
            elif is_target and not model_says_match:
                misses += 1
            elif not is_target and model_says_match:
                false_alarms += 1
            else:
                correct_rejections += 1
            
            trial_details.append({
                "position": trial["position"],
                "item": trial["item"],
                "is_target": is_target,
                "model_match": model_says_match,
                "correct": (is_target == model_says_match),
            })
        
        # Compute d-prime
        try:
            d_prime = compute_dprime(hits, misses, false_alarms, correct_rejections)
        except ImportError:
            d_prime = dprime_fallback(hits, misses, false_alarms, correct_rejections)
        
        hit_rate = hits / max(hits + misses, 1)
        fa_rate = false_alarms / max(false_alarms + correct_rejections, 1)
        accuracy = (hits + correct_rejections) / max(len(trial_details), 1)
        
        level_results[n_level] = {
            "d_prime": d_prime,
            "hit_rate": round(hit_rate, 4),
            "false_alarm_rate": round(fa_rate, 4),
            "accuracy": round(accuracy, 4),
            "hits": hits,
            "misses": misses,
            "false_alarms": false_alarms,
            "correct_rejections": correct_rejections,
        }
    
    # ── Composite Score ──
    # Weighted d-prime: 1-back (0.2), 2-back (0.3), 3-back (0.5) — harder = more weight
    weights = {1: 0.2, 2: 0.3, 3: 0.5}
    
    # Normalize d-prime to [0, 1]: d'=0 → 0, d'=4 → 1
    def normalize_dprime(dp):
        return float(np.clip(dp / 4.0, 0, 1))
    
    weighted_score = sum(
        weights[n] * normalize_dprime(level_results[n]["d_prime"])
        for n in [1, 2, 3]
    )
    
    score = round(float(np.clip(weighted_score, 0, 1)), 4)
    
    # ── Log ──
    kbench.log({
        "benchmark": "N-back Working Memory",
        "per_level": {str(n): level_results[n] for n in [1, 2, 3]},
        "composite_score": score,
        "score_weights": weights,
        "n_level_scaling": {
            str(n): level_results[n]["d_prime"] for n in [1, 2, 3]
        },
    })
    
    return score

exec_func_nback.run(llm=kbench.llm)
