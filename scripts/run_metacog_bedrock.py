#!/usr/bin/env python3
"""Run all 9 metacognition benchmarks against Claude Sonnet via Bedrock."""
import json, os, sys, time, importlib, traceback

os.environ.pop('AWS_PROFILE', None)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

MODEL_ID = "us.anthropic.claude-sonnet-4-6"
MODEL_LABEL = "amazon-bedrock/us.anthropic.claude-sonnet-4-6"

BENCHMARKS = [
    ("benchmarks.metacognition.task_calibration", "metacog_calibration"),
    ("benchmarks.metacognition.task_canary", "metacog_canary"),
    ("benchmarks.metacognition.task_epistemic_humility", "metacog_epistemic_humility"),
    ("benchmarks.metacognition.task_epistemic_revision", "metacog_epistemic_revision"),
    ("benchmarks.metacognition.task_error_detection", "metacog_error_detection"),
    ("benchmarks.metacognition.task_fok", "metacog_fok"),
    ("benchmarks.metacognition.task_jol", "metacog_jol"),
    ("benchmarks.metacognition.task_learning_monitoring", "metacog_learning_monitoring"),
    ("benchmarks.metacognition.task_metacognitive_control", "metacog_control"),
]


def create_bedrock_llm():
    """Create a Bedrock Claude LLM wrapper compatible with kbench task interface."""
    import boto3
    client = boto3.Session(region_name='us-east-1').client('bedrock-runtime')

    class BedrockLLM:
        def __init__(self):
            self._client = client
            self._calls = 0

        def _invoke(self, prompt, **kw):
            self._calls += 1
            max_tokens = kw.get('max_tokens', 4096)
            system_text = kw.get('system', None)
            messages = [{"role": "user", "content": [{"text": prompt}]}]
            kwargs = {
                "modelId": MODEL_ID,
                "messages": messages,
                "inferenceConfig": {"maxTokens": max_tokens},
            }
            if system_text:
                kwargs["system"] = [{"text": system_text}]

            for attempt in range(5):
                try:
                    resp = self._client.converse(**kwargs)
                    text = resp['output']['message']['content'][0]['text']
                    return text
                except Exception as e:
                    estr = str(e)
                    if 'ThrottlingException' in estr or '429' in estr or 'Too many' in estr.lower():
                        delay = 5 * (2 ** attempt)
                        print(f"  [throttle retry {attempt+1}/5] waiting {delay}s...")
                        time.sleep(delay)
                    else:
                        raise
            raise RuntimeError("Max retries exceeded")

        def _maybe_add_json_hint(self, prompt, schema=None, response_format=None):
            """If a schema/response_format was requested, append JSON instructions."""
            if schema is None and response_format is None:
                return prompt
            # Extract field names from dataclass or dict
            fields = []
            if schema is not None:
                import dataclasses
                if dataclasses.is_dataclass(schema):
                    fields = [f.name for f in dataclasses.fields(schema)]
            if fields:
                hint = f"\n\nRespond with ONLY a JSON object with these fields: {', '.join(fields)}. No other text."
            else:
                hint = "\n\nRespond with ONLY a JSON object. No other text."
            return prompt + hint

        def prompt(self, prompt, **kw):
            schema = kw.pop('schema', None)
            rf = kw.pop('response_format', None)
            prompt = self._maybe_add_json_hint(prompt, schema=schema, response_format=rf)
            return self._invoke(prompt, **kw)

        def __call__(self, prompt, **kw):
            rf = kw.pop('response_format', None)
            prompt = self._maybe_add_json_hint(prompt, response_format=rf)
            return self._invoke(prompt, **kw)

    return BedrockLLM()


def setup_kbench():
    import kaggle_benchmarks as kbench
    class DummyLLM:
        def prompt(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'
        def __call__(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'
    kbench.llm = DummyLLM()
    if not hasattr(kbench, 'log'):
        kbench.log = lambda x: None


def run_one(mod_path, fn_name, llm):
    """Run one benchmark, return result dict."""
    # Ensure data imports resolve correctly
    track_dir = os.path.join(REPO, 'benchmarks', 'metacognition')
    for key in list(sys.modules.keys()):
        if key == 'data' or key.startswith('data.'):
            del sys.modules[key]
    if track_dir not in sys.path:
        sys.path.insert(0, track_dir)

    setup_kbench()
    
    # Force reimport
    if mod_path in sys.modules:
        del sys.modules[mod_path]
    
    mod = importlib.import_module(mod_path)
    task_fn = getattr(mod, fn_name)

    print(f"\n{'='*60}")
    print(f"Running: {fn_name}")
    print(f"{'='*60}")

    start = time.time()
    try:
        result = task_fn.run(llm=llm)
        elapsed = time.time() - start
        
        # Extract score
        if hasattr(result, 'result'):
            score = float(result.result)
        else:
            score = float(result)
        
        # Try to get sub-metrics if available
        sub_metrics = {}
        if hasattr(result, 'metadata'):
            sub_metrics = result.metadata
        elif hasattr(result, 'details'):
            sub_metrics = result.details
        
        print(f"\nScore: {score:.4f}")
        print(f"Time: {elapsed:.1f}s")
        print(f"LLM calls: {llm._calls}")
        if sub_metrics:
            print(f"Sub-metrics: {json.dumps(sub_metrics, indent=2)}")
        
        return {
            "score": score,
            "time_seconds": round(elapsed, 1),
            "llm_calls": llm._calls,
            "sub_metrics": sub_metrics,
            "error": None,
        }
    except Exception as e:
        elapsed = time.time() - start
        tb = traceback.format_exc()
        print(f"\nERROR: {e}")
        print(tb)
        return {
            "score": None,
            "time_seconds": round(elapsed, 1),
            "error": str(e),
            "traceback": tb,
        }


def main():
    llm = create_bedrock_llm()
    results = {}
    
    for mod_path, fn_name in BENCHMARKS:
        # Reset call counter per benchmark
        llm._calls = 0
        r = run_one(mod_path, fn_name, llm)
        r["model"] = MODEL_LABEL
        r["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        results[fn_name] = r

    # Save results
    out_dir = os.path.join(REPO, 'results')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'metacog_bedrock_scores.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n\nAll results saved to {out_path}")

    # Summary table
    print(f"\n{'='*60}")
    print(f"SUMMARY — Claude Sonnet 4.6 (Bedrock)")
    print(f"{'='*60}")
    print(f"{'Task':<35} {'Score':>8} {'Time':>8} {'Calls':>6}")
    print(f"{'-'*35} {'-'*8} {'-'*8} {'-'*6}")
    for fn_name in [b[1] for b in BENCHMARKS]:
        r = results[fn_name]
        score_str = f"{r['score']:.4f}" if r['score'] is not None else "ERROR"
        time_str = f"{r['time_seconds']:.1f}s"
        calls_str = str(r.get('llm_calls', '?'))
        print(f"{fn_name:<35} {score_str:>8} {time_str:>8} {calls_str:>6}")


if __name__ == "__main__":
    main()
