#!/usr/bin/env python3
"""
Targeted completion runner for Learning benchmarks.
Only runs the missing model/benchmark combinations from the failed first run.
"""

import json, os, sys, time, importlib, traceback, re
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
            self.transcript = []

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
                        'ReadTimeoutError', 'ConnectTimeoutError',
                        'InternalServerException',
                    ])
                    if retryable and attempt < self._max_retries:
                        delay = self._retry_delay * (2 ** attempt)
                        print(f"  [retry {attempt+1}/{self._max_retries}] {err[:80]}... waiting {delay}s", flush=True)
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
    mod_path, fn_name = LEARNING_BENCHMARKS[benchmark_key]

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
        print(f"  ERROR: {e}", flush=True)
        print(tb[-500:] if len(tb) > 500 else tb, flush=True)
        return None, llm.transcript, str(e)[:300], elapsed


def save_transcript(benchmark_key, model_id, model_label, score, transcript, error, elapsed):
    bench_dir = os.path.join(RESULTS_DIR, benchmark_key)
    os.makedirs(bench_dir, exist_ok=True)

    safe_model = model_id.replace(':', '_').replace('/', '_')

    jsonl_path = os.path.join(bench_dir, f"{safe_model}.jsonl")
    with open(jsonl_path, 'w') as f:
        for i, entry in enumerate(transcript):
            prompt = entry["prompt"]
            response = entry["response"]

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

            row = {
                "question_id": f"Q{i+1:03d}",
                "prompt": prompt[:2000],
                "response": response[:2000],
                "parsed_answer": str(parsed_answer)[:500] if parsed_answer else None,
                "correct_answer": None,
                "score": None,
            }
            f.write(json.dumps(row) + "\n")

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
    import numpy as np
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


def is_scored(benchmark_key, model_id):
    """Check if a model already has a valid score for a benchmark."""
    safe = model_id.replace(':', '_').replace('/', '_')
    summary_path = os.path.join(RESULTS_DIR, benchmark_key, f"{safe}.summary.json")
    if os.path.exists(summary_path):
        try:
            with open(summary_path) as f:
                data = json.load(f)
            return data.get('score') is not None
        except Exception:
            pass
    return False


def main():
    # Define exactly what needs to run
    # Priority order: interference (0/10), transfer (0/10), curves (2 missing), curriculum (3 failed)
    runs = []
    
    for bench_key in ["learning_interference", "learning_transfer"]:
        for model_id in MODEL_ORDER:
            runs.append((bench_key, model_id))

    # curves: only missing GLM and Ministral
    for model_id in ["zai.glm-4.7", "mistral.ministral-3-3b-instruct"]:
        runs.append(("learning_curves", model_id))

    # curriculum: retry failed GPT-OSS, Qwen3, GLM
    for model_id in ["openai.gpt-oss-120b-1:0", "qwen.qwen3-next-80b-a3b", "zai.glm-4.7"]:
        runs.append(("learning_curriculum", model_id))

    print(f"\n{'='*60}", flush=True)
    print(f"LEARNING TRACK COMPLETION RUNNER", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"Total runs: {len(runs)}", flush=True)
    for bench_key, model_id in runs:
        label = MODEL_CATALOG[model_id][0]
        print(f"  {bench_key} × {label}", flush=True)
    print(f"{'='*60}\n", flush=True)

    completed = 0
    failed = []
    
    for i, (bench_key, model_id) in enumerate(runs):
        entry = MODEL_CATALOG[model_id]
        label, invoke_id = entry

        # Check if already done (from a partial previous run of this script)
        if is_scored(bench_key, model_id):
            print(f"\n[{i+1}/{len(runs)}] {bench_key} × {label} — already scored, skipping", flush=True)
            completed += 1
            continue

        timeout = DEFAULT_TIMEOUT
        if model_id in SLOW_MODELS or bench_key in SLOW_BENCHMARKS:
            timeout = 900

        print(f"\n[{i+1}/{len(runs)}] {bench_key} × {label} (timeout={timeout}s)", flush=True)

        score, transcript, error, elapsed = run_benchmark_with_transcript(
            bench_key, model_id, invoke_id, timeout
        )

        save_transcript(bench_key, model_id, label, score, transcript, error, elapsed)

        if score is not None:
            completed += 1
            print(f"  ✅ Score: {score:.4f} ({elapsed:.0f}s, {len(transcript)} questions)", flush=True)
        else:
            failed.append((bench_key, model_id, label, error))
            print(f"  ❌ FAILED: {error[:100]} ({elapsed:.0f}s)", flush=True)

        time.sleep(2)

    # Retry failures once
    if failed:
        print(f"\n{'='*60}", flush=True)
        print(f"RETRYING {len(failed)} FAILURES", flush=True)
        print(f"{'='*60}", flush=True)
        
        retry_failed = []
        for bench_key, model_id, label, prev_error in failed:
            invoke_id = MODEL_CATALOG[model_id][1]
            timeout = 900  # generous for retries

            print(f"\n  Retrying {bench_key} × {label}...", flush=True)
            time.sleep(10)  # extra cooldown before retry

            score, transcript, error, elapsed = run_benchmark_with_transcript(
                bench_key, model_id, invoke_id, timeout
            )

            save_transcript(bench_key, model_id, label, score, transcript, error, elapsed)

            if score is not None:
                completed += 1
                print(f"  ✅ Retry success: {score:.4f}", flush=True)
            else:
                retry_failed.append((bench_key, label, error))
                print(f"  ❌ Retry failed: {error[:100]}", flush=True)

            time.sleep(2)
        
        failed = retry_failed

    # Compute aggregate stats for all 4 benchmarks
    print(f"\n{'='*60}", flush=True)
    print("COMPUTING AGGREGATE STATS", flush=True)
    print(f"{'='*60}", flush=True)
    
    for bench_key in LEARNING_BENCHMARKS:
        stats = compute_aggregate_stats(bench_key)
        if stats:
            print(f"\n{bench_key}:", flush=True)
            print(f"  Models: {stats['n_models']}/10", flush=True)
            print(f"  Mean: {stats['mean']:.4f}  Std: {stats['std']:.4f}  Range: {stats['range']:.4f}", flush=True)
            for m, s in stats['per_model'].items():
                bar = "█" * int(s * 30)
                print(f"    {m:30s}: {s:.4f} {bar}", flush=True)
        else:
            print(f"\n{bench_key}: NO DATA", flush=True)

    # Final summary
    print(f"\n{'='*60}", flush=True)
    print(f"COMPLETION SUMMARY", flush=True)
    print(f"Completed: {completed}/{len(runs)}", flush=True)
    if failed:
        print(f"Still failed ({len(failed)}):", flush=True)
        for bench_key, label, error in failed:
            print(f"  {bench_key} × {label}: {error[:80]}", flush=True)
    print(f"{'='*60}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
