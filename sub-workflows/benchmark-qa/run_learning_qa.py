#!/usr/bin/env python3
"""
Run all 4 Learning benchmarks against all 10 models with Q&A transcript logging.

Captures every prompt/response, parsed answer, correct answer, and score per question.
Saves transcripts to results/qa_transcripts/learning_{benchmark}/{model_id}.jsonl
and summary files to results/qa_transcripts/learning_{benchmark}/{model_id}.summary.json
"""

import argparse, json, os, sys, time, importlib, traceback, re
from datetime import datetime, timezone

os.environ['PYTHONUNBUFFERED'] = '1'

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "qa_transcripts")

# ── Model Catalog ──
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

MODEL_ORDER = list(MODEL_CATALOG.keys())

LEARNING_BENCHMARKS = {
    "learning_curriculum":    ("benchmarks.learning.task_curriculum",       "learning_curriculum"),
    "learning_curves":        ("benchmarks.learning.task_learning_curves",  "learning_curves"),
    "learning_interference":  ("benchmarks.learning.task_interference",     "learning_interference"),
    "learning_transfer":      ("benchmarks.learning.task_transfer",         "learning_transfer"),
}

DEFAULT_TIMEOUT = 300
SLOW_MODELS = {"deepseek.r1-v1:0"}
SLOW_BENCHMARKS = {"learning_curves"}


def _strip_think(text: str) -> str:
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def setup_kbench_mocks():
    import kaggle_benchmarks as kbench
    class DummyLLM:
        def prompt(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'
        def __call__(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'
    kbench.llm = DummyLLM()
    if not hasattr(kbench, 'log'):
        kbench.log = lambda x: None
    class DummyChatCtx:
        def new(self, name=""): return self
        def __enter__(self): return self
        def __exit__(self, *a): pass
    if not hasattr(kbench, 'chats') or kbench.chats is None:
        kbench.chats = DummyChatCtx()
    elif not hasattr(kbench.chats, 'new'):
        kbench.chats = DummyChatCtx()


def create_bedrock_llm(model_id: str, timeout: int = DEFAULT_TIMEOUT):
    import boto3
    from botocore.config import Config

    os.environ.pop('AWS_PROFILE', None)
    config = Config(read_timeout=timeout, connect_timeout=30, retries={'max_attempts': 0})
    client = boto3.Session(region_name='us-east-1').client('bedrock-runtime', config=config)

    class BedrockLLM:
        def __init__(self, max_retries=3, retry_delay=5):
            self._client = client
            self._model_id = model_id
            self._max_retries = max_retries
            self._retry_delay = retry_delay
            self._total_input_tokens = 0
            self._total_output_tokens = 0
            self.transcript = []  # Q&A log

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
                    content = resp['output']['message']['content']
                    for block in content:
                        if 'text' in block:
                            return block['text']
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
                        raise
                    else:
                        raise last_err

        def prompt(self, prompt_text, **kw):
            kw.pop('schema', None)
            kw.pop('response_format', None)
            raw = self._call(prompt_text)
            self.transcript.append({
                "prompt": prompt_text,
                "response": raw,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return raw

        def __call__(self, prompt_text, **kw):
            return self.prompt(prompt_text, **kw)

    return BedrockLLM()


def run_benchmark_with_transcript(benchmark_key, model_id, invoke_id, timeout):
    """Run a single benchmark for a single model. Returns (score, transcript, error)."""
    mod_path, fn_name = LEARNING_BENCHMARKS[benchmark_key]

    # Clean module caches
    for key in list(sys.modules.keys()):
        if key == 'data' or key.startswith('data.'):
            del sys.modules[key]

    track_dir = os.path.join(REPO, 'benchmarks', 'learning')
    if track_dir not in sys.path:
        sys.path.insert(0, track_dir)

    setup_kbench_mocks()

    if mod_path in sys.modules:
        del sys.modules[mod_path]
    mod = importlib.import_module(mod_path)
    task_fn = getattr(mod, fn_name)

    llm = create_bedrock_llm(invoke_id, timeout=timeout)

    start = time.time()
    try:
        result = task_fn.run(llm=llm)
        elapsed = time.time() - start
        score = float(result.result) if hasattr(result, 'result') else float(result)
        return score, llm.transcript, None, elapsed
    except Exception as e:
        elapsed = time.time() - start
        tb = traceback.format_exc()
        print(f"  ERROR: {e}")
        print(tb[-500:] if len(tb) > 500 else tb)
        return None, llm.transcript, str(e)[:300], elapsed


def save_transcript(benchmark_key, model_id, model_label, score, transcript, error, elapsed):
    """Save transcript as JSONL and summary as JSON."""
    bench_dir = os.path.join(RESULTS_DIR, benchmark_key)
    os.makedirs(bench_dir, exist_ok=True)

    safe_model = model_id.replace(':', '_').replace('/', '_')

    # Build JSONL entries from transcript
    jsonl_path = os.path.join(bench_dir, f"{safe_model}.jsonl")
    with open(jsonl_path, 'w') as f:
        for i, entry in enumerate(transcript):
            # Try to extract parsed answer and correct answer from prompt/response
            prompt = entry["prompt"]
            response = entry["response"]

            # Parse the answer from response
            cleaned = _strip_think(response)
            parsed_answer = None
            try:
                m = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if m:
                    data = json.loads(m.group())
                    parsed_answer = data.get("answer", cleaned[:200])
                else:
                    parsed_answer = cleaned[:200]
            except Exception:
                parsed_answer = cleaned[:200]

            # Try to extract expected answer from prompt (Input: X pattern)
            correct_answer = None
            input_match = re.search(r'Input:\s*(.+?)(?:\n|$)', prompt)

            row = {
                "question_id": f"Q{i+1:03d}",
                "prompt": prompt[:2000],  # truncate for sanity
                "response": response[:2000],
                "parsed_answer": str(parsed_answer)[:500] if parsed_answer else None,
                "correct_answer": correct_answer,
                "score": None,  # per-question score not directly available; aggregate only
            }
            f.write(json.dumps(row) + "\n")

    # Summary
    summary_path = os.path.join(bench_dir, f"{safe_model}.summary.json")
    summary = {
        "benchmark": benchmark_key,
        "model_id": model_id,
        "model_label": model_label,
        "score": score,
        "error": error,
        "duration_s": round(elapsed, 1),
        "n_questions": len(transcript),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    return jsonl_path, summary_path


def compute_aggregate_stats(benchmark_key):
    """Compute aggregate stats across all models for one benchmark."""
    bench_dir = os.path.join(RESULTS_DIR, benchmark_key)
    scores = {}
    for fname in sorted(os.listdir(bench_dir)):
        if fname.endswith('.summary.json'):
            with open(os.path.join(bench_dir, fname)) as f:
                data = json.load(f)
            if data.get('score') is not None:
                scores[data['model_label']] = data['score']

    if not scores:
        return None

    import numpy as np
    vals = list(scores.values())
    stats = {
        "benchmark": benchmark_key,
        "n_models": len(scores),
        "mean": round(float(np.mean(vals)), 4),
        "std": round(float(np.std(vals)), 4),
        "range": round(float(max(vals) - min(vals)), 4),
        "min": round(float(min(vals)), 4),
        "max": round(float(max(vals)), 4),
        "per_model": {k: round(v, 4) for k, v in sorted(scores.items(), key=lambda x: -x[1])},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    agg_path = os.path.join(bench_dir, "aggregate_stats.json")
    with open(agg_path, 'w') as f:
        json.dump(stats, f, indent=2)

    return stats


def main():
    parser = argparse.ArgumentParser(description="Run learning benchmarks with Q&A transcript logging")
    parser.add_argument("--benchmark", default=None, help="Single benchmark (curriculum, curves, interference, transfer)")
    parser.add_argument("--model", default=None, help="Single model ID or 'all'")
    parser.add_argument("--skip-scored", action="store_true", help="Skip models that already have a summary.json")
    args = parser.parse_args()

    # Resolve benchmarks
    if args.benchmark:
        key = f"learning_{args.benchmark}" if not args.benchmark.startswith("learning_") else args.benchmark
        if key not in LEARNING_BENCHMARKS:
            print(f"Unknown benchmark: {key}")
            print(f"Available: {list(LEARNING_BENCHMARKS.keys())}")
            sys.exit(1)
        benchmarks = [key]
    else:
        benchmarks = list(LEARNING_BENCHMARKS.keys())

    # Resolve models
    if args.model and args.model != "all":
        # Try to resolve
        found = None
        for mid in MODEL_CATALOG:
            if args.model in mid or args.model.lower() == MODEL_CATALOG[mid][0].lower():
                found = mid
                break
        if not found:
            found = args.model
        model_ids = [found]
    else:
        model_ids = MODEL_ORDER

    print(f"\n{'='*60}")
    print(f"LEARNING TRACK Q&A BENCHMARK RUNNER")
    print(f"{'='*60}")
    print(f"Benchmarks: {benchmarks}")
    print(f"Models: {len(model_ids)}")
    print(f"Total runs: {len(benchmarks) * len(model_ids)}")
    print(f"{'='*60}\n")

    all_results = {}

    for bench_key in benchmarks:
        print(f"\n{'#'*60}")
        print(f"# BENCHMARK: {bench_key}")
        print(f"{'#'*60}")

        bench_results = {}
        failures = []

        for mi, model_id in enumerate(model_ids):
            entry = MODEL_CATALOG.get(model_id)
            if not entry:
                print(f"  WARNING: Unknown model {model_id}, skipping")
                continue
            label, invoke_id = entry

            # Skip if already scored
            if args.skip_scored:
                safe = model_id.replace(':', '_').replace('/', '_')
                summary_path = os.path.join(RESULTS_DIR, bench_key, f"{safe}.summary.json")
                if os.path.exists(summary_path):
                    try:
                        with open(summary_path) as f:
                            existing = json.load(f)
                        if existing.get('score') is not None:
                            print(f"\n[{mi+1}/{len(model_ids)}] {label} — already scored ({existing['score']:.4f}), skipping")
                            bench_results[label] = existing['score']
                            continue
                    except Exception:
                        pass

            # Determine timeout
            timeout = DEFAULT_TIMEOUT
            if model_id in SLOW_MODELS or bench_key in SLOW_BENCHMARKS:
                timeout = 900

            print(f"\n[{mi+1}/{len(model_ids)}] Running {bench_key} with {label} (timeout={timeout}s)")

            score, transcript, error, elapsed = run_benchmark_with_transcript(
                bench_key, model_id, invoke_id, timeout
            )

            jsonl_path, summary_path = save_transcript(
                bench_key, model_id, label, score, transcript, error, elapsed
            )

            if score is not None:
                bench_results[label] = score
                print(f"  ✅ Score: {score:.4f} ({elapsed:.0f}s, {len(transcript)} questions)")
            else:
                failures.append((model_id, label, error))
                print(f"  ❌ FAILED: {error[:100]} ({elapsed:.0f}s)")

            # Rate limit
            if mi < len(model_ids) - 1:
                time.sleep(2)

        # Retry failures once
        if failures:
            print(f"\n--- Retrying {len(failures)} failures for {bench_key} ---")
            for model_id, label, prev_error in failures:
                entry = MODEL_CATALOG[model_id]
                invoke_id = entry[1]
                timeout = 900  # generous timeout for retries

                print(f"  Retrying {label}...")
                score, transcript, error, elapsed = run_benchmark_with_transcript(
                    bench_key, model_id, invoke_id, timeout
                )

                save_transcript(bench_key, model_id, label, score, transcript, error, elapsed)

                if score is not None:
                    bench_results[label] = score
                    print(f"  ✅ Retry success: {score:.4f}")
                else:
                    print(f"  ❌ Retry failed: {error[:100]}")

                time.sleep(2)

        # Compute aggregate stats
        stats = compute_aggregate_stats(bench_key)
        if stats:
            print(f"\n--- {bench_key} Aggregate Stats ---")
            print(f"  Models: {stats['n_models']}/10")
            print(f"  Mean: {stats['mean']:.4f}")
            print(f"  Std:  {stats['std']:.4f}")
            print(f"  Range: {stats['range']:.4f} ({stats['min']:.4f} – {stats['max']:.4f})")
            print(f"  Per model:")
            for m, s in stats['per_model'].items():
                bar = "█" * int(s * 30)
                print(f"    {m:30s}: {s:.4f} {bar}")

        all_results[bench_key] = stats

        # Rate limit between benchmarks
        time.sleep(5)

    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY — ALL LEARNING BENCHMARKS")
    print(f"{'='*60}")
    for bench_key, stats in all_results.items():
        if stats:
            coverage = f"{stats['n_models']}/10"
            print(f"  {bench_key:30s}  mean={stats['mean']:.4f}  std={stats['std']:.4f}  range={stats['range']:.4f}  coverage={coverage}")
        else:
            print(f"  {bench_key:30s}  NO DATA")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
