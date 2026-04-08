#!/usr/bin/env python3
"""
Stress-test the 3 weakest benchmarks with adversarial mock LLM responses.
Tests: vigilance, curriculum, instruction_update

Adversarial patterns:
1. Empty/null responses
2. Malformed JSON 
3. Wildly wrong answers
4. Refusal responses
5. Extremely verbose responses
6. Numeric edge cases (negative, huge, NaN-like)
"""
import sys, os, json, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock kbench before importing tasks
import types
mock_kbench = types.ModuleType('kaggle_benchmarks')

class MockChats:
    class _ctx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
    def new(self, name): return self._ctx()

mock_kbench.chats = MockChats()
mock_kbench.llm = None

def mock_task(name=""):
    def decorator(fn):
        fn.run = lambda **kw: fn(**kw)
        fn.task_name = name
        return fn
    return decorator

mock_kbench.task = mock_task

from dataclasses import dataclass
@dataclass
class MockSchema:
    pass

sys.modules['kaggle_benchmarks'] = mock_kbench

# ─── Adversarial Response Generators ─────

ADVERSARIAL_PATTERNS = {
    "empty": "",
    "null": "null",
    "refusal": "I'm sorry, I cannot perform this task as it requires counting symbols.",
    "malformed_json": '{"count": "three", positions: [1,2,3}',
    "huge_number": '{"count": 99999, "positions": "0,1,2,3,4,5"}',
    "negative": '{"count": -5, "positions": ""}',
    "verbose": "Let me carefully analyze this sequence step by step. First, I'll look at each symbol... " * 50 + '{"count": 3, "positions": "1,5,12"}',
    "wrong_format": "The answer is 3 targets at positions 1, 5, and 12.",
    "unicode_mess": '{"count": "３", "positions": "①,⑤,⑫"}',
    "nested_json": '{"result": {"count": 3, "positions": "1,5,12"}}',
}


class AdversarialLLM:
    """Mock LLM that returns adversarial responses."""
    def __init__(self, pattern_name):
        self.pattern = pattern_name
        self.call_count = 0
    
    def prompt(self, text, schema=None):
        self.call_count += 1
        response = ADVERSARIAL_PATTERNS[self.pattern]
        
        if schema:
            # Try to return a schema object with bad data
            if self.pattern == "empty":
                raise ValueError("Empty response")
            elif self.pattern == "null":
                raise ValueError("Null response")  
            elif self.pattern == "refusal":
                raise ValueError("Model refused")
            else:
                # Return mock schema object
                obj = schema.__new__(schema)
                if hasattr(schema, '__dataclass_fields__'):
                    for field_name, field in schema.__dataclass_fields__.items():
                        if field.type == int:
                            if self.pattern == "huge_number":
                                setattr(obj, field_name, 99999)
                            elif self.pattern == "negative":
                                setattr(obj, field_name, -5)
                            else:
                                setattr(obj, field_name, 3)
                        elif field.type == str:
                            setattr(obj, field_name, "1,5,12")
                        elif field.type == bool:
                            setattr(obj, field_name, True)
                return obj
        return response
    
    def __call__(self, text, response_format=None):
        return self.prompt(text, schema=response_format)


def test_benchmark(task_fn, task_name, pattern_name):
    """Test a benchmark with an adversarial LLM pattern."""
    llm = AdversarialLLM(pattern_name)
    try:
        score = task_fn(llm=llm)
        return {"status": "ok", "score": score, "calls": llm.call_count}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200], "calls": llm.call_count}


# ─── Import benchmarks ─────
print("=" * 70)
print("ADVERSARIAL STRESS TEST — Weakest Benchmarks")
print("=" * 70)

results = {}

# Test each benchmark module
benchmark_modules = [
    ("attention.task_vigilance", "attention_vigilance"),
    ("learning.task_curriculum", "learning_curriculum"),
    ("attention.task_instruction_update", "attention_instruction_update"),
]

os.chdir(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, 'benchmarks')

for module_name, func_name in benchmark_modules:
    print(f"\n{'─'*60}")
    print(f"Testing: {module_name}.{func_name}")
    print(f"{'─'*60}")
    
    try:
        # Dynamic import
        parts = module_name.split('.')
        mod = __import__(f"benchmarks.{module_name}", fromlist=[func_name])
        task_fn = getattr(mod, func_name)
        
        results[func_name] = {}
        for pattern_name in ADVERSARIAL_PATTERNS:
            result = test_benchmark(task_fn, func_name, pattern_name)
            results[func_name][pattern_name] = result
            status = "✅" if result["status"] == "ok" else "❌"
            detail = f"score={result['score']:.4f}" if result["status"] == "ok" else f"ERROR: {result['error'][:60]}"
            print(f"  {status} {pattern_name:20s} → {detail}")
    except Exception as e:
        print(f"  ⚠️ Failed to import: {e}")
        results[func_name] = {"import_error": str(e)}

# ─── Summary ─────
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

for func_name, func_results in results.items():
    if isinstance(func_results, dict) and "import_error" not in func_results:
        total = len(func_results)
        ok = sum(1 for r in func_results.values() if r["status"] == "ok")
        crashed = total - ok
        print(f"\n{func_name}: {ok}/{total} survived ({crashed} crashes)")
        if crashed:
            for pattern, r in func_results.items():
                if r["status"] == "error":
                    print(f"  CRASH on '{pattern}': {r['error'][:80]}")
    else:
        print(f"\n{func_name}: IMPORT FAILED")

# Save results
os.makedirs('results', exist_ok=True)
with open('results/stress_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to results/stress_test_results.json")
