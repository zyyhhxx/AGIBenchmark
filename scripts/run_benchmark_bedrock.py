#!/usr/bin/env python3
"""
Run all benchmarks against Amazon Bedrock models.

Usage:
  .venv/bin/python3 scripts/run_benchmark_bedrock.py --model anthropic.claude-haiku-4-5-20251001-v1:0 --benchmark metacog_canary
  .venv/bin/python3 scripts/run_benchmark_bedrock.py --model all --track metacognition
  .venv/bin/python3 scripts/run_benchmark_bedrock.py --model all --track all
  .venv/bin/python3 scripts/run_benchmark_bedrock.py --list
"""
import argparse, json, os, sys, time, importlib, traceback
from datetime import datetime, timezone

os.environ['PYTHONUNBUFFERED'] = '1'

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

# ── Model Catalog ──────────────────────────────────────────────────────────────
# Maps canonical model ID → (friendly label, bedrock_invoke_id)
# Some models require cross-region inference profile IDs (us. prefix),
# others work with the foundation model ID directly.
MODEL_CATALOG = {
    "anthropic.claude-opus-4-6-v1":                   ("Claude Opus 4.6",        "us.anthropic.claude-opus-4-6-v1"),
    "deepseek.r1-v1:0":                               ("DeepSeek-R1",            "us.deepseek.r1-v1:0"),
    "openai.gpt-oss-120b-1:0":                        ("GPT-OSS-120B",           "openai.gpt-oss-120b-1:0"),
    "meta.llama3-3-70b-instruct-v1:0":                ("Llama 3.3 70B",          "us.meta.llama3-3-70b-instruct-v1:0"),
    "qwen.qwen3-next-80b-a3b":                        ("Qwen3 Next 80B",         "qwen.qwen3-next-80b-a3b"),
    "amazon.nova-pro-v1:0":                            ("Nova Pro",               "us.amazon.nova-pro-v1:0"),
    "meta.llama4-maverick-17b-instruct-v1:0":         ("Llama 4 Maverick 17B",   "us.meta.llama4-maverick-17b-instruct-v1:0"),
    "anthropic.claude-sonnet-4-6":                     ("Claude Sonnet 4.6",      "us.anthropic.claude-sonnet-4-6"),
    "zai.glm-4.7":                                     ("GLM 4.7",                "zai.glm-4.7"),
    "mistral.ministral-3-3b-instruct":                ("Ministral 3B",           "mistral.ministral-3-3b-instruct"),
}

# Reverse lookup: friendly name (lowered) → canonical model_id
_FRIENDLY_LOOKUP = {v[0].lower(): k for k, v in MODEL_CATALOG.items()}

DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-20250514-v1:0"

# ── Benchmark Registry (all 5 tracks, 29 benchmarks) ──────────────────────────
BENCHMARKS = {
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

# Rate limiting
DELAY_BETWEEN_BENCHMARKS = 2   # seconds
DELAY_BETWEEN_MODELS = 5       # seconds
CALL_TIMEOUT = 300              # seconds per Bedrock call
SLOW_BENCHMARKS = {'exec_func_wcst', 'exec_func_tol', 'exec_func_nback', 'exec_func_crt', 'exec_func_task_switch', 'attention_divided', 'attention_instruction_update'}
SLOW_TIMEOUT = 300              # seconds for known slow benchmarks


def resolve_model_id(model_arg: str) -> str:
    """Resolve a model argument to a Bedrock model ID."""
    if model_arg in MODEL_CATALOG:
        return model_arg
    # Check friendly name
    key = model_arg.lower()
    if key in _FRIENDLY_LOOKUP:
        return _FRIENDLY_LOOKUP[key]
    # Partial match
    for mid in MODEL_CATALOG:
        if model_arg in mid:
            return mid
    return model_arg  # pass through as-is


def get_benchmarks_for_track(track: str):
    """Return list of (mod_path, fn_name) for a track or all tracks."""
    if track == "all":
        result = []
        for t in BENCHMARKS:
            result.extend(BENCHMARKS[t])
        return result
    if track in BENCHMARKS:
        return BENCHMARKS[track]
    return []


def get_track_for_benchmark(fn_name: str) -> str:
    """Return the track name for a benchmark function name."""
    for track, benchmarks in BENCHMARKS.items():
        for _, name in benchmarks:
            if name == fn_name:
                return track
    return "unknown"


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


def create_bedrock_llm(model_id: str, timeout: int = CALL_TIMEOUT):
    """Create a callable LLM that uses AWS Bedrock Converse API with retry + timeout."""
    import boto3
    from botocore.config import Config

    os.environ.pop('AWS_PROFILE', None)
    config = Config(
        read_timeout=timeout,
        connect_timeout=30,
        retries={'max_attempts': 0}  # we handle retries ourselves
    )
    client = boto3.Session(region_name='us-east-1').client('bedrock-runtime', config=config)

    class BedrockLLM:
        def __init__(self, max_retries=3, retry_delay=5):
            self._client = client
            self._model_id = model_id
            self._max_retries = max_retries
            self._retry_delay = retry_delay
            self._total_input_tokens = 0
            self._total_output_tokens = 0

        def _call(self, prompt, max_tokens=4096):
            last_err = None
            for attempt in range(self._max_retries + 1):
                try:
                    resp = self._client.converse(
                        modelId=self._model_id,
                        messages=[{'role': 'user', 'content': [{'text': prompt}]}],
                        inferenceConfig={'maxTokens': max_tokens, 'temperature': 0.0}
                    )
                    usage = resp.get('usage', {})
                    self._total_input_tokens += usage.get('inputTokens', 0)
                    self._total_output_tokens += usage.get('outputTokens', 0)
                    # Handle models that return reasoningContent before text
                    content = resp['output']['message']['content']
                    for block in content:
                        if 'text' in block:
                            return block['text']
                    # Fallback: if only reasoningContent, extract that
                    for block in content:
                        if 'reasoningContent' in block:
                            rt = block['reasoningContent']
                            if isinstance(rt, dict) and 'reasoningText' in rt:
                                return rt['reasoningText'].get('text', str(rt))
                            return str(rt)
                    return str(content)
                except Exception as e:
                    last_err = e
                    err = str(e)
                    retryable = any(k in err for k in [
                        '429', 'ThrottlingException', 'Too many', 'Rate',
                        'ServiceUnavailable', 'ModelTimeoutException',
                        'ReadTimeoutError', 'ConnectTimeoutError'
                    ])
                    if retryable and attempt < self._max_retries:
                        delay = self._retry_delay * (2 ** attempt)
                        print(f"  [retry {attempt+1}/{self._max_retries}] {err[:80]}... waiting {delay}s")
                        time.sleep(delay)
                    elif attempt < self._max_retries:
                        # Non-retryable error, but not last attempt — raise immediately
                        raise
                    else:
                        raise last_err

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
                return raw
            return None, prompt

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


def run_one(mod_path, fn_name, llm, model_id, model_label, invoke_id=None):
    """Run a single benchmark task, return result dict."""
    # Clean data module cache
    for key in list(sys.modules.keys()):
        if key == 'data' or key.startswith('data.'):
            del sys.modules[key]

    track = get_track_for_benchmark(fn_name)
    track_dir = os.path.join(REPO, 'benchmarks', track)
    if track_dir not in sys.path:
        sys.path.insert(0, track_dir)

    setup_kbench_mocks()

    # Re-import to pick up fresh data modules
    if mod_path in sys.modules:
        del sys.modules[mod_path]
    mod = importlib.import_module(mod_path)
    task_fn = getattr(mod, fn_name)

    print(f"\n{'='*60}")
    print(f"Running {fn_name} with {model_label} ({model_id})")
    print(f"{'='*60}")

    start = time.time()
    try:
        result = task_fn.run(llm=llm)
        elapsed = time.time() - start
        score = float(result.result) if hasattr(result, 'result') else float(result)
        print(f"  Score: {score}")
        print(f"  Time: {elapsed:.1f}s")
        print(f"  Tokens: in={llm._total_input_tokens}, out={llm._total_output_tokens}")
        return {
            "benchmark": fn_name,
            "score": score,
            "error": None,
            "duration_s": round(elapsed, 1),
        }
    except Exception as e:
        elapsed = time.time() - start
        tb = traceback.format_exc()
        print(f"  ERROR: {e}")
        print(tb[-500:] if len(tb) > 500 else tb)
        return {
            "benchmark": fn_name,
            "score": None,
            "error": str(e)[:200],
            "duration_s": round(elapsed, 1),
        }


def run_model(model_id: str, benchmarks: list, output_dir: str):
    """Run all specified benchmarks for one model. Save results to output_dir/{model_id}.json."""
    entry = MODEL_CATALOG.get(model_id)
    label = entry[0] if entry else model_id
    invoke_id = entry[1] if entry else model_id
    print(f"\n{'#'*60}")
    print(f"# MODEL: {label} ({model_id})")
    print(f"# Benchmarks: {len(benchmarks)}")
    print(f"{'#'*60}")

    llm = create_bedrock_llm(invoke_id)
    scores = {}

    # Resume: load existing results and skip completed benchmarks
    safe_name = model_id.replace(':', '_').replace('/', '_')
    out_path = os.path.join(output_dir, f"{safe_name}.json")
    if os.path.exists(out_path):
        try:
            with open(out_path) as f:
                existing = json.load(f)
            for bname, bdata in existing.get('scores', {}).items():
                if bdata.get('score') is not None:  # skip completed (not errored)
                    scores[bname] = bdata
            print(f"  Resumed: {len(scores)} benchmarks already scored, skipping them")
        except Exception as e:
            print(f"  Warning: could not load existing results: {e}")

    for i, (mod_path, fn_name) in enumerate(benchmarks):
        if fn_name in scores and scores[fn_name].get('score') is not None:
            print(f"\n[{i+1}/{len(benchmarks)}] {fn_name} — already scored ({scores[fn_name]['score']:.4f}), skipping")
            continue
        # Use longer timeout for slow benchmarks
        if fn_name in SLOW_BENCHMARKS:
            bench_llm = create_bedrock_llm(invoke_id, timeout=SLOW_TIMEOUT)
        else:
            bench_llm = llm
        r = run_one(mod_path, fn_name, bench_llm, model_id, label, invoke_id)
        scores[fn_name] = {
            "score": r["score"],
            "error": r["error"],
            "duration_s": r["duration_s"],
        }
        # Incremental save after each benchmark
        os.makedirs(output_dir, exist_ok=True)
        safe_name = model_id.replace(':', '_').replace('/', '_')
        out_path = os.path.join(output_dir, f"{safe_name}.json")
        output = {
            "model": model_id,
            "model_label": label,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scores": scores,
        }
        with open(out_path, 'w') as f:
            json.dump(output, f, indent=2)
        sys.stdout.flush()
        # Rate limit between benchmarks
        if i < len(benchmarks) - 1:
            time.sleep(DELAY_BETWEEN_BENCHMARKS)

    print(f"\nResults saved to {out_path}")

    # Print summary for this model
    print(f"\n--- {label} Summary ---")
    for bname, data in scores.items():
        if data["score"] is not None:
            print(f"  {bname:45s} → {data['score']:.4f}  ({data['duration_s']}s)")
        else:
            print(f"  {bname:45s} → ERROR: {(data['error'] or '')[:50]}  ({data['duration_s']}s)")
    print(f"Total tokens: in={llm._total_input_tokens}, out={llm._total_output_tokens}")

    return output


def main():
    parser = argparse.ArgumentParser(description="Run AGI benchmarks via Amazon Bedrock")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="Model ID, friendly name, or 'all'. Default: claude-sonnet-4")
    parser.add_argument("--track", default="all",
                        help="Track: metacognition, learning, attention, executive_functions, social_cognition, all")
    parser.add_argument("--benchmark", default=None,
                        help="Single benchmark name (overrides --track)")
    parser.add_argument("--output-dir", default=os.path.join(REPO, "results"),
                        help="Output directory for result JSON files")
    parser.add_argument("--list", action="store_true", help="List models and benchmarks")
    args = parser.parse_args()

    if args.list:
        print("\n=== Models ===")
        for mid, (label, invoke_id) in MODEL_CATALOG.items():
            print(f"  {mid:55s}  ({label})  -> {invoke_id}")
        print(f"\n=== Benchmarks ({sum(len(v) for v in BENCHMARKS.values())} total) ===")
        for track, benchmarks in BENCHMARKS.items():
            print(f"\n  {track}:")
            for _, fn_name in benchmarks:
                print(f"    - {fn_name}")
        return

    # Resolve benchmarks
    if args.benchmark:
        # Find matching benchmark
        found = []
        for track, benchmarks in BENCHMARKS.items():
            for mod_path, fn_name in benchmarks:
                if fn_name == args.benchmark or args.benchmark in mod_path:
                    found.append((mod_path, fn_name))
        if not found:
            print(f"No benchmark matched '{args.benchmark}'")
            sys.exit(1)
        targets = found
    else:
        targets = get_benchmarks_for_track(args.track)
        if not targets:
            print(f"No benchmarks for track '{args.track}'")
            sys.exit(1)

    # Resolve models
    if args.model == "all":
        model_ids = list(MODEL_CATALOG.keys())
    else:
        model_ids = [resolve_model_id(args.model)]

    print(f"\nModels: {len(model_ids)}")
    print(f"Benchmarks: {len(targets)}")
    print(f"Total runs: {len(model_ids) * len(targets)}")

    all_results = {}
    for i, model_id in enumerate(model_ids):
        result = run_model(model_id, targets, args.output_dir)
        all_results[model_id] = result
        # Rate limit between models
        if i < len(model_ids) - 1:
            print(f"\n--- Waiting {DELAY_BETWEEN_MODELS}s before next model ---")
            time.sleep(DELAY_BETWEEN_MODELS)

    # Final summary
    if len(model_ids) > 1:
        print(f"\n{'='*60}")
        print("FINAL SUMMARY — ALL MODELS")
        print(f"{'='*60}")
        for mid, res in all_results.items():
            label = res["model_label"]
            scores = res["scores"]
            valid = [s["score"] for s in scores.values() if s["score"] is not None]
            errors = sum(1 for s in scores.values() if s["error"] is not None)
            avg = sum(valid) / len(valid) if valid else 0
            print(f"  {label:30s}  avg={avg:.4f}  ok={len(valid)}/{len(scores)}  errors={errors}")


if __name__ == "__main__":
    main()
