#!/usr/bin/env python3
"""
Run metacognition benchmarks locally against Claude Sonnet via AWS Bedrock.

Usage:
  .venv/bin/python3 scripts/run_benchmark_bedrock.py --benchmark metacog_canary
  .venv/bin/python3 scripts/run_benchmark_bedrock.py --benchmark all --output results/metacog_bedrock_scores.json
"""
import argparse, json, os, sys, time, importlib, traceback
os.environ['PYTHONUNBUFFERED'] = '1'

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"
MODEL_LABEL = "Claude Sonnet 4 (Bedrock)"

METACOG_BENCHMARKS = [
    ("benchmarks.metacognition.task_canary", "metacog_canary"),
    ("benchmarks.metacognition.task_fok", "metacog_fok"),
    ("benchmarks.metacognition.task_jol", "metacog_jol"),
    ("benchmarks.metacognition.task_calibration", "metacog_calibration"),
    ("benchmarks.metacognition.task_error_detection", "metacog_error_detection"),
    ("benchmarks.metacognition.task_learning_monitoring", "metacog_learning_monitoring"),
    ("benchmarks.metacognition.task_metacognitive_control", "metacog_control"),
    ("benchmarks.metacognition.task_epistemic_revision", "metacog_epistemic_revision"),
    ("benchmarks.metacognition.task_epistemic_humility", "metacog_epistemic_humility"),
]


def setup_kbench_mocks():
    """Patch kaggle_benchmarks for local execution."""
    import kaggle_benchmarks as kbench
    from unittest.mock import MagicMock

    class DummyLLM:
        def prompt(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'
        def __call__(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'

    kbench.llm = DummyLLM()
    if not hasattr(kbench, 'log'):
        kbench.log = lambda x: None
    
    # Mock chats context manager
    class DummyChatCtx:
        def new(self, name=""):
            return self
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass
    
    if not hasattr(kbench, 'chats') or kbench.chats is None:
        kbench.chats = DummyChatCtx()
    elif not hasattr(kbench.chats, 'new'):
        kbench.chats = DummyChatCtx()


def create_bedrock_llm():
    """Create a callable LLM that uses AWS Bedrock Converse API."""
    import boto3
    os.environ.pop('AWS_PROFILE', None)
    client = boto3.Session(region_name='us-east-1').client('bedrock-runtime')

    class BedrockLLM:
        def __init__(self, max_retries=5, retry_delay=5):
            self._client = client
            self._max_retries = max_retries
            self._retry_delay = retry_delay
            self._total_input_tokens = 0
            self._total_output_tokens = 0

        def _call(self, prompt, max_tokens=4096):
            for attempt in range(self._max_retries):
                try:
                    resp = self._client.converse(
                        modelId=MODEL_ID,
                        messages=[{'role': 'user', 'content': [{'text': prompt}]}],
                        inferenceConfig={'maxTokens': max_tokens, 'temperature': 0.0}
                    )
                    usage = resp.get('usage', {})
                    self._total_input_tokens += usage.get('inputTokens', 0)
                    self._total_output_tokens += usage.get('outputTokens', 0)
                    return resp['output']['message']['content'][0]['text']
                except Exception as e:
                    err = str(e)
                    if any(k in err for k in ['429', 'ThrottlingException', 'Too many', 'Rate']):
                        delay = self._retry_delay * (2 ** attempt)
                        print(f"  [retry {attempt+1}/{self._max_retries}] throttled, waiting {delay}s")
                        time.sleep(delay)
                    else:
                        raise
            return self._call_raw(prompt, max_tokens)  # final attempt

        def _call_raw(self, prompt, max_tokens=4096):
            resp = self._client.converse(
                modelId=MODEL_ID,
                messages=[{'role': 'user', 'content': [{'text': prompt}]}],
                inferenceConfig={'maxTokens': max_tokens, 'temperature': 0.0}
            )
            usage = resp.get('usage', {})
            self._total_input_tokens += usage.get('inputTokens', 0)
            self._total_output_tokens += usage.get('outputTokens', 0)
            return resp['output']['message']['content'][0]['text']

        def _handle_response_format(self, prompt, kw):
            """If response_format is a dataclass, request JSON and parse response."""
            import re as _re
            rf = kw.pop('response_format', None)
            kw.pop('schema', None)
            if rf is not None and hasattr(rf, '__dataclass_fields__'):
                fields = {k: v.type.__name__ if hasattr(v.type, '__name__') else str(v.type)
                          for k, v in rf.__dataclass_fields__.items()}
                json_prompt = prompt + (f"\n\nRespond with ONLY a JSON object with these fields: {json.dumps(fields)}. "
                                        f"No other text before or after the JSON.")
                raw = self._call(json_prompt)
                try:
                    m = _re.search(r'\{.*\}', raw, _re.DOTALL)
                    if m:
                        data = json.loads(m.group())
                        # Coerce types for dataclass fields
                        import dataclasses
                        field_types = {f.name: f.type for f in dataclasses.fields(rf)}
                        coerced = {}
                        for fname, ftype in field_types.items():
                            val = data.get(fname)
                            if ftype is int and val is not None:
                                coerced[fname] = int(val)
                            elif ftype is bool and val is not None:
                                coerced[fname] = bool(val)
                            elif ftype is str:
                                coerced[fname] = str(val) if val is not None else ''
                            elif ftype is float and val is not None:
                                coerced[fname] = float(val)
                            else:
                                coerced[fname] = val
                        return rf(**coerced)
                except Exception:
                    pass
                # Fallback: return raw string (caller will catch AttributeError)
                return raw
            return None, prompt  # No response_format

        def __call__(self, prompt, **kw):
            rf = kw.get('response_format')
            if rf is not None and hasattr(rf, '__dataclass_fields__'):
                return self._handle_response_format(prompt, kw)
            kw.pop('response_format', None)
            kw.pop('schema', None)
            return self._call(prompt)

        def prompt(self, prompt, **kw):
            rf = kw.get('response_format')
            if rf is not None and hasattr(rf, '__dataclass_fields__'):
                return self._handle_response_format(prompt, kw)
            kw.pop('response_format', None)
            kw.pop('schema', None)
            return self._call(prompt)

    return BedrockLLM()


def run_one(mod_path, fn_name, llm):
    """Run a single benchmark task, return result dict."""
    # Clean data module cache
    for key in list(sys.modules.keys()):
        if key == 'data' or key.startswith('data.'):
            del sys.modules[key]

    track_dir = os.path.join(REPO, 'benchmarks', 'metacognition')
    if track_dir not in sys.path:
        sys.path.insert(0, track_dir)

    setup_kbench_mocks()
    mod = importlib.import_module(mod_path)
    task_fn = getattr(mod, fn_name)

    print(f"\n{'='*60}")
    print(f"Running {fn_name} with {MODEL_LABEL}")
    print(f"{'='*60}")

    start = time.time()
    try:
        result = task_fn.run(llm=llm)
        elapsed = time.time() - start
        score = float(result.result) if hasattr(result, 'result') else float(result)
        print(f"\nScore: {score}")
        print(f"Time: {elapsed:.1f}s")
        print(f"Tokens: in={llm._total_input_tokens}, out={llm._total_output_tokens}")
        return {
            "task": fn_name,
            "score": score,
            "time_seconds": round(elapsed, 1),
            "model": MODEL_LABEL,
            "model_id": MODEL_ID,
            "error": None
        }
    except Exception as e:
        elapsed = time.time() - start
        tb = traceback.format_exc()
        print(f"\nERROR: {e}")
        print(tb)
        return {
            "task": fn_name,
            "score": None,
            "time_seconds": round(elapsed, 1),
            "model": MODEL_LABEL,
            "model_id": MODEL_ID,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="all")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    llm = create_bedrock_llm()
    results = []

    if args.benchmark == "all":
        targets = METACOG_BENCHMARKS
    else:
        targets = [(m, f) for m, f in METACOG_BENCHMARKS if f == args.benchmark or args.benchmark in m]

    if not targets:
        print(f"No benchmark matched '{args.benchmark}'")
        return

    for mod_path, fn_name in targets:
        r = run_one(mod_path, fn_name, llm)
        results.append(r)
        print(f"\n--- Cumulative tokens: in={llm._total_input_tokens}, out={llm._total_output_tokens} ---\n")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for r in results:
        status = f"{r['score']:.4f}" if r['score'] is not None else f"ERROR: {r['error'][:60]}"
        print(f"  {r['task']:40s} → {status}  ({r['time_seconds']}s)")
    print(f"\nTotal tokens: in={llm._total_input_tokens}, out={llm._total_output_tokens}")

    if args.output:
        os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
        # Structure as {task: {score, model, timestamp, ...}}
        from datetime import datetime, timezone
        structured = {}
        for r in results:
            structured[r['task']] = {
                "score": r['score'],
                "time_seconds": r['time_seconds'],
                "model": r['model'],
                "model_id": r['model_id'],
                "error": r['error'],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        with open(args.output, 'w') as f:
            json.dump(structured, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
