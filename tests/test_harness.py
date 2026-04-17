"""
Local test harness for benchmark tasks.

Provides a mock LLM that returns predictable responses,
allowing us to verify task logic without Kaggle access.
"""

import sys
import json
import re
from dataclasses import dataclass

# Mock the kaggle_benchmarks module
class MockChat:
    def __init__(self, name, **kwargs):
        self.name = name
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

class MockChats:
    def new(self, name, **kwargs):
        return MockChat(name, **kwargs)

class MockLLM:
    """Mock LLM that returns plausible but simple responses."""

    def prompt(self, text, schema=None):
        """Return a reasonable mock response based on the prompt."""
        text_lower = text.lower()

        # For FOK Phase 1 (confidence rating)
        if "do not answer the question" in text_lower and "confidence" in text_lower:
            if schema:
                obj = schema.__new__(schema)
                obj.confidence = 70
                obj.reasoning = "I think I know this"
                return obj
            return '{"confidence": 70, "reasoning": "I think I know this"}'

        # For FOK Phase 2 (answering)
        if "answer the following question" in text_lower:
            if schema:
                obj = schema.__new__(schema)
                obj.answer = "mock answer"
                obj.is_guess = False
                return obj
            return '{"answer": "mock answer", "is_guess": false}'

        # For calibration (answer + confidence)
        if "rate your confidence" in text_lower and "answer" in text_lower:
            if schema:
                obj = schema.__new__(schema)
                obj.answer = "42"
                obj.confidence = 60
                return obj
            return '{"answer": "42", "confidence": 60}'

        # For JOL confidence
        if "how confident" in text_lower and "recall" in text_lower:
            if schema:
                obj = schema.__new__(schema)
                obj.confidence = 65
                obj.reasoning = "medium difficulty"
                return obj
            return '{"confidence": 65, "reasoning": "medium difficulty"}'

        # For recall
        if "what was its definition" in text_lower:
            if schema:
                obj = schema.__new__(schema)
                obj.definition = "a small wooden bridge"
                obj.confidence = 50
                return obj
            return '{"definition": "a small wooden bridge", "confidence": 50}'

        # For error detection
        if "review the following" in text_lower and "error" in text_lower:
            if schema:
                obj = schema.__new__(schema)
                obj.has_error = True
                obj.error_step = 1
                obj.explanation = "mock error found"
                obj.confidence = 75
                return obj
            return '{"has_error": true, "error_step": 1, "explanation": "mock", "confidence": 75}'

        # For Stroop
        if "follow this instruction" in text_lower:
            if schema:
                obj = schema.__new__(schema)
                obj.answer = "mock"
                return obj
            return '{"answer": "mock"}'

        # For rule system tasks
        if "apply" in text_lower and "rules" in text_lower:
            if schema:
                obj = schema.__new__(schema)
                obj.answer = "mock output"
                if hasattr(schema, '__dataclass_fields__') and 'reasoning' in schema.__dataclass_fields__:
                    obj.reasoning = "applied rules"
                return obj
            return '{"answer": "mock output", "reasoning": "applied rules"}'

        # For vigilance
        if "count how many" in text_lower:
            if schema:
                obj = schema.__new__(schema)
                obj.count = 2
                obj.positions = "3,7"
                return obj
            return '{"count": 2, "positions": "3,7"}'

        # For dual task
        if "two tasks" in text_lower or "task a" in text_lower:
            if schema and hasattr(schema, '__dataclass_fields__'):
                obj = schema.__new__(schema)
                if 'task_a_answer' in schema.__dataclass_fields__:
                    obj.task_a_answer = "85"
                    obj.task_b_answer = "chrysanthemum"
                    return obj
                obj.answer = "85"
                return obj
            return '{"answer": "85"}'

        # Default: echo something
        if schema:
            obj = schema.__new__(schema)
            for field_name in schema.__dataclass_fields__:
                if 'answer' in field_name:
                    setattr(obj, field_name, "mock")
                elif 'confidence' in field_name:
                    setattr(obj, field_name, 50)
                elif 'count' in field_name:
                    setattr(obj, field_name, 0)
                else:
                    setattr(obj, field_name, "mock")
            return obj
        return '{"answer": "mock"}'


# Create mock module
class MockKBench:
    chats = MockChats()
    llm = MockLLM()

    @staticmethod
    def task(name=None, **kwargs):
        def decorator(func):
            class MockTask:
                def __init__(self, fn):
                    self.fn = fn
                    self.__name__ = fn.__name__

                def run(self, llm=None):
                    result = self.fn(llm or MockKBench.llm)
                    print(f"\n>>> Task '{name or fn.__name__}' returned score: {result}")
                    return result

            return MockTask(func)
        return decorator


# Install mock
sys.modules['kaggle_benchmarks'] = MockKBench()


def test_task(task_path: str, cwd: str = None):
    """Test a single task file."""
    import importlib.util
    import os

    if cwd:
        os.chdir(cwd)
        sys.path.insert(0, cwd)

    print(f"\n{'='*60}")
    print(f"TESTING: {task_path}")
    print(f"{'='*60}")

    try:
        spec = importlib.util.spec_from_file_location("test_task", task_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print(f"✅ {task_path}: PASSED")
        return True
    except Exception as e:
        print(f"❌ {task_path}: FAILED — {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import os
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    tasks = [
        ("benchmarks/metacognition", "benchmarks/metacognition/task_calibration.py"),
        ("benchmarks/metacognition", "benchmarks/metacognition/task_fok.py"),
        ("benchmarks/metacognition", "benchmarks/metacognition/task_error_detection.py"),
        ("benchmarks/attention", "benchmarks/attention/task_selective.py"),
    ]

    passed = 0
    failed = 0
    for cwd, path in tasks:
        full_cwd = os.path.join(base, cwd)
        full_path = os.path.join(base, path)
        if test_task(full_path, full_cwd):
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
