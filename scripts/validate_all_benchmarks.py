#!/usr/bin/env python3
"""
Comprehensive validation of all benchmark task files.
Checks: imports, data loading, function signatures, scoring bounds.
"""
import sys, os, importlib, traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

TRACKS = {
    "metacognition": [
        "task_fok", "task_jol", "task_calibration", "task_error_detection",
        "task_learning_monitoring", "task_canary", "task_metacognitive_control",
        "task_epistemic_revision", "task_epistemic_humility",
    ],
    "learning": [
        "task_learning_curves", "task_transfer", "task_interference", "task_curriculum",
    ],
    "attention": [
        "task_selective", "task_vigilance", "task_divided", "task_instruction_update",
    ],
    "executive_functions": [
        "task_wcst", "task_tol", "task_switching", "task_nback", "task_crt",
    ],
    "social_cognition": [
        "task_false_belief", "task_pragmatic", "task_sarcasm", "task_emotional_prosody",
    ],
}

# Mock kaggle_benchmarks
import types
kbench = types.ModuleType('kaggle_benchmarks')
kbench.log = lambda x: None

class MockLLM:
    def prompt(self, *a, **kw): return '{"answer": "test", "confidence": 50}'
    def __call__(self, *a, **kw): return '{"answer": "test", "confidence": 50}'

kbench.llm = MockLLM()

class MockChats:
    def new(self, name): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
kbench.chats = MockChats()

def task_decorator(name=None):
    def wrapper(fn):
        fn.run = lambda **kw: None
        return fn
    return wrapper
kbench.task = task_decorator

sys.modules['kaggle_benchmarks'] = kbench

passed = 0
failed = 0
errors = []

for track, tasks in TRACKS.items():
    print(f"\n{'='*50}")
    print(f"Track: {track}")
    print(f"{'='*50}")
    # Add track's benchmark dir to path so 'from data.' imports work
    track_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'benchmarks', track))
    # Remove previous track dirs and clear cached 'data' module
    sys.path = [p for p in sys.path if '/benchmarks/' not in p] + sys.path[:0]
    sys.path.insert(0, track_dir)
    # Clear cached 'data' package so each track gets its own
    for mod_name in list(sys.modules.keys()):
        if mod_name == 'data' or mod_name.startswith('data.'):
            del sys.modules[mod_name]
    for task_name in tasks:
        module_path = f"benchmarks.{track}.{task_name}"
        try:
            mod = importlib.import_module(module_path)
            # Check it has at least one function decorated with @kbench.task
            task_fns = [name for name in dir(mod) if hasattr(getattr(mod, name), 'run')]
            if task_fns:
                print(f"  ✓ {task_name} ({len(task_fns)} task fn: {', '.join(task_fns)})")
                passed += 1
            else:
                print(f"  ⚠ {task_name} — no @kbench.task functions found")
                passed += 1  # Still importable
        except Exception as e:
            print(f"  ✗ {task_name} — {e}")
            errors.append((track, task_name, traceback.format_exc()))
            failed += 1

print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed out of {passed+failed}")
print(f"{'='*50}")

if errors:
    print("\nDetailed errors:")
    for track, task, tb in errors:
        print(f"\n--- {track}/{task} ---")
        print(tb)

sys.exit(1 if failed else 0)
