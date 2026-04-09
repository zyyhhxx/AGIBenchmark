#!/usr/bin/env python3
"""
Mock Validation: Run all benchmarks with mock LLM strategies.

Validates scoring pipelines produce sensible score distributions.
Strategies:
  - always_confident: high confidence, plausible-but-wrong answers
  - always_uncertain: low confidence, "I don't know"
  - random: random confidence and answers
  - perfect: approximately correct answers with calibrated confidence
"""

import sys
import os
import json
import random
import re
import importlib
import importlib.util
import traceback
from dataclasses import dataclass, fields
from contextlib import contextmanager
from unittest.mock import MagicMock
from typing import Any
from io import StringIO

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "benchmarks"))

import numpy as np


# ─── Mock Infrastructure ────────────────────────────────────────────

@contextmanager
def mock_chat(*args, **kwargs):
    yield MagicMock()


class MockLLM:
    """Mock LLM returning strategy-based responses."""
    
    def __init__(self, strategy="random"):
        self.strategy = strategy
        self.call_count = 0
    
    def __call__(self, message: str, response_format=None, schema=None, **kwargs):
        """Support llm(prompt, response_format=...) calling convention."""
        s = response_format or schema
        return self.prompt(message, schema=s, **kwargs)
    
    def prompt(self, message: str, schema=None, **kwargs):
        self.call_count += 1
        if schema is None or schema == str:
            return self._string_response(message)
        return self._schema_response(message, schema)
    
    def _string_response(self, message):
        if self.strategy == "always_confident":
            return '{"answer": "42", "confidence": 95}'
        elif self.strategy == "always_uncertain":
            return "I don't know. This is unanswerable."
        elif self.strategy == "random":
            return random.choice(["yes", "no", "42", "unknown", "A", "B", "C"])
        return "I need more context."
    
    def _schema_response(self, message, schema):
        field_list = fields(schema)
        kwargs = {}
        for f in field_list:
            kwargs[f.name] = self._field_value(f.name, f.type, message)
        return schema(**kwargs)
    
    def _field_value(self, name, ftype, message):
        nl = name.lower()
        
        # Confidence / sincerity rating
        if "confidence" in nl or nl == "sincerity_rating":
            return {"always_confident": 95, "always_uncertain": 5,
                    "random": random.randint(0, 100), "perfect": 75}[self.strategy]
        
        # Booleans
        if ftype is bool:
            mapping = {
                "is_guess":    {"always_confident": False, "always_uncertain": True,
                                "random": random.choice([True, False]), "perfect": False},
                "has_error":   {"always_confident": True, "always_uncertain": False,
                                "random": random.choice([True, False]), "perfect": True},
                "is_match":    {"always_confident": True, "always_uncertain": False,
                                "random": random.choice([True, False]), "perfect": random.choice([True, False])},
                "is_literal":  {"always_confident": True, "always_uncertain": True,
                                "random": random.choice([True, False]), "perfect": False},
                "is_sarcastic":{"always_confident": True, "always_uncertain": False,
                                "random": random.choice([True, False]), "perfect": True},
            }
            if nl in mapping:
                return mapping[nl][self.strategy]
            return random.choice([True, False])
        
        # Integers
        if ftype is int:
            if nl == "error_step":
                return {"always_confident": 2, "always_uncertain": 0,
                        "random": random.randint(0, 5), "perfect": 3}[self.strategy]
            if nl == "count":
                return random.randint(0, 10) if self.strategy == "random" else 3
            if nl == "choice":
                return random.randint(1, 4) if self.strategy == "random" else 1
            return random.randint(0, 10)
        
        # Lists (Tower of London moves)
        if nl == "moves":
            if self.strategy == "perfect":
                return ["A→C", "B→C"]
            if self.strategy == "random":
                pegs = ["A", "B", "C"]
                return [f"{random.choice(pegs)}→{random.choice(pegs)}" for _ in range(random.randint(1, 5))]
            return []
        
        # String fields
        if nl in ("answer", "task_a_answer", "task_b_answer"):
            if self.strategy == "always_confident":
                return "42"
            if self.strategy == "always_uncertain":
                return "I don't know"
            if self.strategy == "random":
                return random.choice(["A", "B", "C", "42", "yes", "no"])
            return "correct answer"
        
        if nl == "definition":
            return "I don't remember" if self.strategy == "always_uncertain" else "Some definition"
        if nl == "speaker_intent":
            return "The speaker means something indirect"
        if nl == "positions":
            return "1,3,5"
        
        return f"Mock {self.strategy}"


# ─── Benchmark Loading ──────────────────────────────────────────────

BENCHMARKS = [
    # (name, file_path_relative_to_benchmarks/, task_func_name, track)
    ("metacog_fok", "metacognition/task_fok.py", "metacog_fok", "metacognition"),
    ("metacog_jol", "metacognition/task_jol.py", "metacog_jol", "metacognition"),
    ("metacog_calibration", "metacognition/task_calibration.py", "metacog_calibration", "metacognition"),
    ("metacog_error_detection", "metacognition/task_error_detection.py", "metacog_error_detection", "metacognition"),
    ("metacog_learning_monitoring", "metacognition/task_learning_monitoring.py", "metacog_learning_monitoring", "metacognition"),
    ("metacog_canary", "metacognition/task_canary.py", "metacog_canary", "metacognition"),
    ("learning_curves", "learning/task_learning_curves.py", "learning_curves", "learning"),
    ("learning_interference", "learning/task_interference.py", "learning_interference", "learning"),
    ("learning_transfer", "learning/task_transfer.py", "learning_transfer", "learning"),
    ("learning_curriculum", "learning/task_curriculum.py", "learning_curriculum", "learning"),
    ("attention_selective", "attention/task_selective.py", "attention_selective", "attention"),
    ("attention_vigilance", "attention/task_vigilance.py", "attention_vigilance", "attention"),
    ("attention_divided", "attention/task_divided.py", "attention_divided", "attention"),
    ("exec_func_wcst", "executive_functions/task_wcst.py", "exec_func_wcst", "executive_functions"),
    ("exec_func_tol", "executive_functions/task_tol.py", "exec_func_tol", "executive_functions"),
    ("exec_func_nback", "executive_functions/task_nback.py", "exec_func_nback", "executive_functions"),
    ("exec_func_task_switch", "executive_functions/task_switching.py", "exec_func_task_switch", "executive_functions"),
    ("social_cog_false_belief", "social_cognition/task_false_belief.py", "social_cog_false_belief", "social_cognition"),
    ("social_cog_pragmatic", "social_cognition/task_pragmatic.py", "social_cog_pragmatic", "social_cognition"),
    ("social_cog_sarcasm", "social_cognition/task_sarcasm.py", "social_cog_sarcasm", "social_cognition"),
    # Added 2026-04-09: newer benchmarks
    ("metacog_control", "metacognition/task_metacognitive_control.py", "metacog_control", "metacognition"),
    ("metacog_epistemic_revision", "metacognition/task_epistemic_revision.py", "metacog_epistemic_revision", "metacognition"),
    ("metacog_epistemic_humility", "metacognition/task_epistemic_humility.py", "metacog_epistemic_humility", "metacognition"),
    ("attention_instruction_update", "attention/task_instruction_update.py", "attention_instruction_update", "attention"),
    ("exec_func_crt", "executive_functions/task_crt.py", "exec_func_crt", "executive_functions"),
    ("social_cog_emotional_prosody", "social_cognition/task_emotional_prosody.py", "social_cog_emotional_prosody", "social_cognition"),
]


def load_benchmark_func(file_rel, task_func_name):
    """
    Load a benchmark module without triggering .run() at module scope.
    
    Strategy: Read source, comment out the .run() line, exec in a namespace
    with the right sys.path and a mock kbench.llm.
    """
    bench_dir = os.path.join(REPO, "benchmarks")
    file_path = os.path.join(bench_dir, file_rel)
    track_dir = os.path.dirname(file_path)
    
    with open(file_path) as f:
        source = f.read()
    
    # Comment out any .run(llm=...) calls at module level
    source = re.sub(r'^(\w+\.run\(.*\))$', r'# MOCK_DISABLED: \1', source, flags=re.MULTILINE)
    
    # Build module namespace
    mod_name = f"mock_bench_{task_func_name}"
    
    # Ensure data/ imports work by adding the track directory to sys.path
    old_path = sys.path[:]
    sys.path.insert(0, track_dir)
    
    # Clear any cached 'data' package and submodules so each track gets its own
    data_mods = [k for k in sys.modules if k == 'data' or k.startswith('data.')]
    saved_mods = {k: sys.modules.pop(k) for k in data_mods}
    
    import kaggle_benchmarks as kbench
    
    # Provide mock kbench.llm and kbench.log to prevent AttributeError
    had_llm = hasattr(kbench, 'llm')
    old_llm = getattr(kbench, 'llm', None)
    kbench.llm = MagicMock()
    
    had_log = hasattr(kbench, 'log')
    old_log = getattr(kbench, 'log', None)
    kbench.log = lambda *a, **kw: None
    
    # Patch chats.new
    old_new = kbench.chats.new
    kbench.chats.new = mock_chat
    
    try:
        # Compile and exec
        code = compile(source, file_path, 'exec')
        namespace = {"__name__": mod_name, "__file__": file_path}
        exec(code, namespace)
        
        # Extract the task function
        task_obj = namespace.get(task_func_name)
        if task_obj is None:
            raise ValueError(f"Task function '{task_func_name}' not found in {file_rel}")
        
        # Get the underlying callable (may be wrapped by @kbench.task)
        fn = None
        if hasattr(task_obj, '__wrapped__'):
            fn = task_obj.__wrapped__
        elif hasattr(task_obj, 'fn'):
            fn = task_obj.fn
        elif hasattr(task_obj, '_fn'):
            fn = task_obj._fn
        elif callable(task_obj):
            fn = task_obj
        
        if fn is None:
            raise ValueError(f"Cannot extract callable from {task_func_name}")
        
        return fn
        
    finally:
        sys.path[:] = old_path
        kbench.chats.new = old_new
        if had_llm:
            kbench.llm = old_llm
        else:
            try:
                del kbench.llm
            except AttributeError:
                pass
        # Restore log
        if had_log:
            kbench.log = old_log
        else:
            try:
                del kbench.log
            except AttributeError:
                pass
        # Clean up data modules loaded for this track
        for k in list(sys.modules):
            if k == 'data' or k.startswith('data.'):
                del sys.modules[k]


def run_one(bench_name, file_rel, task_func_name, strategy):
    """Run a single benchmark with a mock LLM strategy. Returns score or error string."""
    mock_llm = MockLLM(strategy=strategy)
    
    try:
        fn = load_benchmark_func(file_rel, task_func_name)
        
        # Suppress verbose print output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            score = fn(mock_llm)
        finally:
            sys.stdout = old_stdout
        
        return float(score)
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {str(e)[:300]}"


# ─── Main ───────────────────────────────────────────────────────────

def main():
    random.seed(42)
    np.random.seed(42)
    
    # Patch kbench globally for the entire validation run
    import kaggle_benchmarks as kbench
    kbench.chats.new = mock_chat
    kbench.llm = MagicMock()
    if not hasattr(kbench, 'log'):
        kbench.log = lambda *a, **kw: None
    
    strategies = ["always_confident", "always_uncertain", "random", "perfect"]
    results = {}
    issues = []
    
    print(f"{'='*80}")
    print(f"MOCK VALIDATION: {len(BENCHMARKS)} benchmarks × {len(strategies)} strategies")
    print(f"{'='*80}\n")
    
    for bench_name, file_rel, task_func_name, track in BENCHMARKS:
        print(f"\n{'─'*60}")
        print(f"  {bench_name} ({track})")
        print(f"{'─'*60}")
        
        bench_scores = {}
        
        for strategy in strategies:
            random.seed(42 + hash(strategy))
            np.random.seed(42)
            
            score = run_one(bench_name, file_rel, task_func_name, strategy)
            bench_scores[strategy] = score
            
            if isinstance(score, float):
                flag = "" if 0.0 <= score <= 1.0 else " ⚠ OUT OF RANGE"
                print(f"  {strategy:20s}: {score:.4f}{flag}")
            else:
                print(f"  {strategy:20s}: {score}")
                issues.append(f"{bench_name}/{strategy}: {score}")
        
        # Validation checks
        checks = []
        numeric = {k: v for k, v in bench_scores.items() if isinstance(v, float)}
        
        if len(numeric) >= 2:
            for s, v in numeric.items():
                if v < 0 or v > 1:
                    checks.append(f"⚠ {s} score {v:.4f} outside [0,1]")
            
            vals = list(numeric.values())
            if len(set(round(v, 4) for v in vals)) == 1:
                checks.append("⚠ All strategies produce identical scores")
            
            if "perfect" in numeric and "always_uncertain" in numeric:
                if numeric["perfect"] < numeric["always_uncertain"] - 0.15:
                    checks.append(f"⚠ Perfect ({numeric['perfect']:.3f}) < Uncertain ({numeric['always_uncertain']:.3f})")
        
        for c in checks:
            print(f"  {c}")
            issues.append(f"{bench_name}: {c}")
        
        results[bench_name] = {"track": track, "scores": bench_scores, "checks": checks}
    
    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    total = len(BENCHMARKS)
    passed = sum(1 for r in results.values()
                 if all(isinstance(v, float) and 0 <= v <= 1 for v in r["scores"].values())
                 and not r["checks"])
    errored = sum(1 for r in results.values()
                  if any(isinstance(v, str) for v in r["scores"].values()))
    warned = total - passed - errored
    
    print(f"  Total benchmarks: {total}")
    print(f"  ✓ Clean pass:     {passed}")
    print(f"  ⚠ Warnings:       {warned}")
    print(f"  ✗ Errors:         {errored}")
    print(f"  Issues total:     {len(issues)}")
    
    if issues:
        print(f"\n  Issues:")
        for iss in issues[:30]:  # Cap output
            print(f"    • {iss[:120]}")
    
    # Score distribution table
    print(f"\n\n{'─'*80}")
    print(f"  SCORE DISTRIBUTION TABLE")
    print(f"{'─'*80}")
    print(f"  {'Benchmark':35s} {'Confident':>10s} {'Uncertain':>10s} {'Random':>10s} {'Perfect':>10s}")
    print(f"  {'─'*35} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")
    
    for bench_name, _, _, track in BENCHMARKS:
        r = results[bench_name]["scores"]
        row = f"  {bench_name:35s}"
        for strat in strategies:
            v = r.get(strat, "N/A")
            if isinstance(v, float):
                row += f" {v:10.4f}"
            else:
                row += f" {'ERR':>10s}"
        print(row)
    
    # Save
    output_path = os.path.join(REPO, "results", "mock_validation_full.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    json_results = {}
    for name, data in results.items():
        json_results[name] = {
            "track": data["track"],
            "scores": {k: v if isinstance(v, (int, float)) else str(v) for k, v in data["scores"].items()},
            "checks": data["checks"],
        }
    
    with open(output_path, "w") as f:
        json.dump(json_results, f, indent=2)
    
    print(f"\n  Saved to: {output_path}")
    return 0 if errored == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
