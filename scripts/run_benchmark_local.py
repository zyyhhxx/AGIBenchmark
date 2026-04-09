#!/usr/bin/env python3
"""
Run benchmarks locally against a Gemini model via the Google GenAI API.

Prerequisites:
  - GEMINI_API_KEY env var (with billing enabled for sufficient quota)
  - pip install kaggle-benchmarks google-genai

Usage:
  .venv/bin/python3 scripts/run_benchmark_local.py --model gemini-2.5-flash --benchmark metacog_canary
  .venv/bin/python3 scripts/run_benchmark_local.py --model gemini-2.5-pro --benchmark all
  .venv/bin/python3 scripts/run_benchmark_local.py --list  # list available benchmarks
"""
import argparse, json, os, sys, time, importlib, traceback

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BENCHMARKS = {
    # track_name: [(module_path, task_fn_name, data_imports)]
    "metacognition": [
        ("benchmarks.metacognition.task_canary", "metacog_canary"),
        ("benchmarks.metacognition.task_fok", "metacog_fok"),
        ("benchmarks.metacognition.task_jol", "metacog_jol"),
        ("benchmarks.metacognition.task_calibration", "metacog_calibration"),
        ("benchmarks.metacognition.task_error_detection", "metacog_error_detection"),
        ("benchmarks.metacognition.task_learning_monitoring", "metacog_learning_monitoring"),
        ("benchmarks.metacognition.task_metacognitive_control", "metacog_control"),
        ("benchmarks.metacognition.task_epistemic_revision", "metacog_epistemic_revision"),
        ("benchmarks.metacognition.task_epistemic_humility", "metacog_epistemic_humility"),
    ],
    "learning": [
        ("benchmarks.learning.task_learning_curves", "learning_curves"),
        ("benchmarks.learning.task_transfer", "learning_transfer"),
        ("benchmarks.learning.task_interference", "learning_interference"),
        ("benchmarks.learning.task_curriculum", "learning_curriculum"),
    ],
    "attention": [
        ("benchmarks.attention.task_selective", "attention_selective"),
        ("benchmarks.attention.task_vigilance", "attention_vigilance"),
        ("benchmarks.attention.task_divided", "attention_divided"),
        ("benchmarks.attention.task_instruction_update", "attention_instruction_update"),
    ],
    "executive_functions": [
        ("benchmarks.executive_functions.task_wcst", "exec_func_wcst"),
        ("benchmarks.executive_functions.task_tol", "exec_func_tol"),
        ("benchmarks.executive_functions.task_switching", "exec_func_task_switch"),
        ("benchmarks.executive_functions.task_nback", "exec_func_nback"),
        ("benchmarks.executive_functions.task_crt", "exec_func_crt"),
    ],
    "social_cognition": [
        ("benchmarks.social_cognition.task_false_belief", "social_cog_false_belief"),
        ("benchmarks.social_cognition.task_pragmatic", "social_cog_pragmatic"),
        ("benchmarks.social_cognition.task_sarcasm", "social_cog_sarcasm"),
        ("benchmarks.social_cognition.task_emotional_prosody", "social_cog_emotional_prosody"),
    ],
}

def setup_kbench_mocks():
    """Patch kaggle_benchmarks to allow local execution."""
    import kaggle_benchmarks as kbench
    
    class DummyLLM:
        def prompt(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'
        def __call__(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'
    
    kbench.llm = DummyLLM()
    if not hasattr(kbench, 'log'):
        kbench.log = lambda x: None


def create_llm(model: str):
    """Create a callable LLM wrapper for local execution."""
    from kaggle_benchmarks.actors.llms import GoogleGenAI
    import google.genai as genai
    
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    _llm = GoogleGenAI(client=client, model=model)
    
    class CallableLLM:
        """Wrapper to make LLMChat callable with retry and response_format handling."""
        def __init__(self, llm, max_retries=3, retry_delay=5):
            self._llm = llm
            self._max_retries = max_retries
            self._retry_delay = retry_delay
        
        def _call_with_retry(self, prompt, **kw):
            import time as _time
            for attempt in range(self._max_retries):
                try:
                    return self._llm.prompt(prompt, **kw)
                except Exception as e:
                    if '503' in str(e) or '429' in str(e) or 'UNAVAILABLE' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                        delay = self._retry_delay * (2 ** attempt)
                        print(f"  [retry {attempt+1}/{self._max_retries}] {str(e)[:60]}... waiting {delay}s")
                        _time.sleep(delay)
                    else:
                        raise
            return self._llm.prompt(prompt, **kw)  # Final attempt without catch
        
        def __call__(self, prompt, **kw):
            kw.pop('response_format', None)  # Not supported locally
            return self._call_with_retry(prompt, **kw)
        def prompt(self, prompt, **kw):
            kw.pop('schema', None)
            return self._call_with_retry(prompt, **kw)
        def __getattr__(self, name):
            return getattr(self._llm, name)
    
    return CallableLLM(_llm)


def run_benchmark(model: str, benchmark_name: str):
    """Run a single benchmark and return the score."""
    # Find the benchmark
    for track, benchmarks in BENCHMARKS.items():
        for mod_path, fn_name in benchmarks:
            if fn_name == benchmark_name or benchmark_name in mod_path:
                # Add track dir to sys.path for data imports
                track_dir = os.path.join(REPO, 'benchmarks', track)
                for key in list(sys.modules.keys()):
                    if key == 'data' or key.startswith('data.'):
                        del sys.modules[key]
                if track_dir not in sys.path:
                    sys.path.insert(0, track_dir)
                
                setup_kbench_mocks()
                mod = importlib.import_module(mod_path)
                task_fn = getattr(mod, fn_name)
                
                llm = create_llm(model)
                print(f"\n{'='*60}")
                print(f"Running {fn_name} with {model}")
                print(f"{'='*60}")
                
                start = time.time()
                result = task_fn.run(llm=llm)
                elapsed = time.time() - start
                
                print(f"\nScore: {result}")
                print(f"Time: {elapsed:.1f}s")
                return {"benchmark": fn_name, "model": model, "score": float(result.result) if hasattr(result, 'result') else float(result), "time_seconds": round(elapsed, 1)}
    
    print(f"Benchmark '{benchmark_name}' not found")
    return None


def main():
    parser = argparse.ArgumentParser(description="Run AGI benchmarks locally")
    parser.add_argument("--model", default="gemini-2.5-flash", help="Gemini model name")
    parser.add_argument("--benchmark", default="metacog_canary", help="Benchmark name or 'all'")
    parser.add_argument("--list", action="store_true", help="List available benchmarks")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()
    
    if args.list:
        for track, benchmarks in BENCHMARKS.items():
            print(f"\n{track}:")
            for _, fn_name in benchmarks:
                print(f"  - {fn_name}")
        return
    
    sys.path.insert(0, REPO)
    
    if args.benchmark == "all":
        results = []
        for track, benchmarks in BENCHMARKS.items():
            for _, fn_name in benchmarks:
                try:
                    r = run_benchmark(args.model, fn_name)
                    if r:
                        results.append(r)
                except Exception as e:
                    print(f"ERROR on {fn_name}: {e}")
                    results.append({"benchmark": fn_name, "model": args.model, "error": str(e)})
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {args.output}")
    else:
        run_benchmark(args.model, args.benchmark)


if __name__ == "__main__":
    main()
