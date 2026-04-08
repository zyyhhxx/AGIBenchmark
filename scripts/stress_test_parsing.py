#!/usr/bin/env python3
"""
Stress-test scoring/parsing robustness of weak benchmarks.
Instead of importing full modules, extract and test parsing functions.
"""
import json, re, os, sys
import numpy as np

print("=" * 70)
print("ADVERSARIAL PARSING STRESS TEST")
print("=" * 70)

# ─── Adversarial LLM responses ─────
ADVERSARIAL_RESPONSES = [
    ("empty", ""),
    ("null", "null"),
    ("refusal", "I'm sorry, I cannot perform this task."),
    ("malformed_json", '{"count": "three", positions: [1,2,3}'),
    ("huge_number", '{"count": 99999, "positions": "0,1,2,3,4,5"}'),
    ("negative", '{"count": -5, "positions": ""}'),
    ("verbose_with_json", "Let me think... " * 50 + '{"count": 3, "positions": "1,5,12"}'),
    ("just_number", "3"),
    ("unicode", '{"count": "３"}'),
    ("nested", '{"result": {"count": 3}}'),
    ("html", "<p>The count is <b>3</b></p>"),
    ("markdown", "**Count:** 3\n**Positions:** 1, 5, 12"),
    ("only_whitespace", "   \n\t  "),
    ("very_long", "a" * 100000),
]

# ─── Test 1: Vigilance count parsing (from task_vigilance.py) ─────
print("\n── Vigilance: Count Parsing ──")

def vigilance_parse(raw):
    """Simulate the fallback parsing from vigilance benchmark."""
    try:
        parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
        return int(parsed.get("count", 0))
    except Exception:
        nums = re.findall(r'\d+', raw)
        return int(nums[0]) if nums else 0

for name, response in ADVERSARIAL_RESPONSES:
    try:
        count = vigilance_parse(response)
        print(f"  ✅ {name:25s} → count={count}")
    except Exception as e:
        print(f"  ❌ {name:25s} → CRASH: {str(e)[:60]}")

# ─── Test 2: Curriculum response parsing ─────
print("\n── Curriculum: Answer Parsing ──")

def curriculum_parse(raw, expected_answer="42"):
    """Simulate curriculum benchmark answer extraction."""
    raw_lower = raw.strip().lower()
    # Try JSON first
    try:
        data = json.loads(raw)
        answer = str(data.get("answer", ""))
    except Exception:
        answer = raw.strip()
    
    # Normalize and check
    answer_clean = re.sub(r'[^\w\s]', '', answer).strip().lower()
    expected_clean = re.sub(r'[^\w\s]', '', expected_answer).strip().lower()
    return expected_clean in answer_clean

for name, response in ADVERSARIAL_RESPONSES:
    try:
        correct = curriculum_parse(response)
        print(f"  ✅ {name:25s} → correct={correct}")
    except Exception as e:
        print(f"  ❌ {name:25s} → CRASH: {str(e)[:60]}")

# ─── Test 3: Instruction update parsing ─────
print("\n── Instruction Update: Response Parsing ──")

def instruction_update_parse(raw, schema_fields=None):
    """Simulate instruction_update response parsing."""
    try:
        data = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
        return data
    except Exception:
        return {"answer": raw.strip()[:100] if raw.strip() else "UNKNOWN"}

for name, response in ADVERSARIAL_RESPONSES:
    try:
        result = instruction_update_parse(response)
        print(f"  ✅ {name:25s} → {json.dumps(result)[:60]}")
    except Exception as e:
        print(f"  ❌ {name:25s} → CRASH: {str(e)[:60]}")

# ─── Test 4: Score computation edge cases ─────
print("\n── Score Computation Edge Cases ──")

edge_cases = [
    ("all_zeros", [0, 0, 0], [0, 0, 0]),
    ("all_ones", [1, 1, 1], [1, 1, 1]),
    ("empty_lists", [], []),
    ("single_item", [0.5], [1]),
    ("nan_values", [float('nan'), 0.5], [1, 0]),
    ("negative_acc", [-0.5, 0.5], [1, 0]),
    ("huge_conf", [10000, 50], [1, 0]),
]

for name, confs, accs in edge_cases:
    try:
        if len(confs) == 0:
            score = 0.0
        else:
            confs_arr = np.array(confs)
            accs_arr = np.array(accs)
            overall = np.nanmean(accs_arr)
            score = float(np.clip(overall, 0, 1))
        print(f"  ✅ {name:25s} → score={score:.4f}")
    except Exception as e:
        print(f"  ❌ {name:25s} → CRASH: {str(e)[:60]}")

# ─── Summary ─────
print(f"\n{'='*70}")
print("All parsing tests complete. Check for ❌ marks above.")
print("If any CRASH, the corresponding benchmark needs additional error handling.")
