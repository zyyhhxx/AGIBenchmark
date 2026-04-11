#!/usr/bin/env python3
"""
Run social_cog_pragmatic benchmark against 3 models, storing artifacts
in repo/benchmarks/social_cognition/.

This script:
1. Sets kbench client.directory to benchmarks/social_cognition/
2. Runs with version=2 tiered definition
3. Creates proper .task.json and .run.json artifacts
"""
import os, sys, time, json, importlib, traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
os.environ['PYTHONUNBUFFERED'] = '1'
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'benchmarks' / 'social_cognition'))

# Models to test (3 for spread)
MODELS = [
    ("anthropic.claude-sonnet-4-6", "Claude Sonnet 4.6", "us.anthropic.claude-sonnet-4-6"),
    ("amazon.nova-pro-v1:0", "Nova Pro", "us.amazon.nova-pro-v1:0"),
    ("mistral.ministral-3-3b-instruct", "Ministral 3B", "mistral.ministral-3-3b-instruct"),
]

CALL_TIMEOUT = 120


def create_bedrock_llm(invoke_id):
    import boto3
    from botocore.config import Config

    os.environ.pop('AWS_PROFILE', None)
    config = Config(
        read_timeout=CALL_TIMEOUT,
        connect_timeout=30,
        retries={'max_attempts': 0}
    )
    client = boto3.Session(region_name='us-east-1').client('bedrock-runtime', config=config)

    class BedrockLLM:
        def __init__(self):
            self._client = client
            self._model_id = invoke_id
            self._total_input_tokens = 0
            self._total_output_tokens = 0

        def _call(self, prompt, max_tokens=4096):
            for attempt in range(3):
                try:
                    resp = self._client.converse(
                        modelId=self._model_id,
                        messages=[{"role": "user", "content": [{"text": prompt}]}],
                        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.0}
                    )
                    text = resp['output']['message']['content'][0]['text']
                    usage = resp.get('usage', {})
                    self._total_input_tokens += usage.get('inputTokens', 0)
                    self._total_output_tokens += usage.get('outputTokens', 0)
                    return text
                except Exception as e:
                    if attempt < 2:
                        wait = 5 * (attempt + 1)
                        print(f"    Retry {attempt+1}/3 after {e.__class__.__name__}: {str(e)[:100]}")
                        time.sleep(wait)
                    else:
                        raise

        def prompt(self, text, schema=None, **kwargs):
            if schema is not None:
                # Add JSON instruction
                text += "\n\nRespond with valid JSON matching this schema: " + str({
                    f.name: str(f.type) for f in schema.__dataclass_fields__.values()
                } if hasattr(schema, '__dataclass_fields__') else {})
            raw = self._call(text)
            if schema is not None and hasattr(schema, '__dataclass_fields__'):
                try:
                    # Try to parse JSON
                    import re
                    json_match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
                    if json_match:
                        d = json.loads(json_match.group())
                        return schema(**{k: d.get(k, '') for k in schema.__dataclass_fields__})
                except Exception:
                    pass
                # Fallback: construct from raw
                return schema(**{k: raw if k == 'speaker_intent' else (False if 'bool' in str(f.type) else '')
                                for k, f in schema.__dataclass_fields__.items()})
            return raw

        def __call__(self, prompt, **kw):
            return self.prompt(prompt, **kw)

    return BedrockLLM()


def setup_kbench(artifact_dir):
    """Set up kbench for local execution with artifacts in artifact_dir."""
    import kaggle_benchmarks as kbench
    from pathlib import Path

    # Set artifact output directory
    kbench.client.directory = Path(artifact_dir)
    print(f"kbench client.directory = {kbench.client.directory}")

    # Mock chats context manager
    class DummyChatCtx:
        def new(self, name="", orphan=False):
            return self
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass

    if not hasattr(kbench.chats, 'new') or kbench.chats is None:
        kbench.chats = DummyChatCtx()
    else:
        # Patch the existing chats module's new method to be a no-op context manager
        original_new = kbench.chats.new
        class PatchedChats:
            def new(self, name="", orphan=False):
                return DummyChatCtx()
        kbench.chats = PatchedChats()

    return kbench


def main():
    artifact_dir = REPO / 'benchmarks' / 'social_cognition'
    kbench = setup_kbench(artifact_dir)

    # Clear any stale data module cache
    for key in list(sys.modules.keys()):
        if key == 'data' or key.startswith('data.'):
            del sys.modules[key]

    # Import task (fresh)
    if 'task_pragmatic' in sys.modules:
        del sys.modules['task_pragmatic']
    if 'benchmarks.social_cognition.task_pragmatic' in sys.modules:
        del sys.modules['benchmarks.social_cognition.task_pragmatic']

    from task_pragmatic import social_cog_pragmatic

    print(f"Task name: {social_cog_pragmatic.name}")
    print(f"Task version: {social_cog_pragmatic.version}")
    print(f"Store task: {social_cog_pragmatic.store_task}")
    print(f"Store run: {social_cog_pragmatic.store_run}")
    print()

    scores = {}

    for model_id, label, invoke_id in MODELS:
        print(f"\n{'='*60}")
        print(f"Running social_cog_pragmatic with {label} ({invoke_id})")
        print(f"{'='*60}")

        llm = create_bedrock_llm(invoke_id)

        start = time.time()
        try:
            result = social_cog_pragmatic.run(llm=llm, _id=label.replace(' ', '_'))
            elapsed = time.time() - start
            score = float(result.result) if hasattr(result, 'result') else float(result)
            scores[label] = score
            print(f"\n  Score: {score}")
            print(f"  Time: {elapsed:.1f}s")
            print(f"  Tokens: in={llm._total_input_tokens}, out={llm._total_output_tokens}")
        except Exception as e:
            elapsed = time.time() - start
            print(f"\n  ERROR: {e}")
            traceback.print_exc()
            scores[label] = None

        # Wait between models to avoid throttling
        time.sleep(3)

    # Summary
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    valid_scores = [s for s in scores.values() if s is not None]
    for label, score in scores.items():
        print(f"  {label}: {score}")

    if len(valid_scores) >= 2:
        import numpy as np
        mean = np.mean(valid_scores)
        std = np.std(valid_scores)
        rng = max(valid_scores) - min(valid_scores)
        print(f"\n  Mean: {mean:.4f}")
        print(f"  Std: {std:.4f}")
        print(f"  Range: {rng:.4f}")
        print(f"  Target std >= 0.10: {'PASS' if std >= 0.10 else 'FAIL'}")

    # Verify artifacts
    print(f"\n{'='*60}")
    print("ARTIFACT VERIFICATION")
    print(f"{'='*60}")
    for f in sorted(artifact_dir.glob('social_cog_pragmatic*')):
        print(f"  {f.name} ({f.stat().st_size} bytes)")
        with open(f) as fh:
            d = json.load(fh)
        if f.name.endswith('.task.json'):
            print(f"    versionNumber: {d.get('versionNumber')}")
            defn = d.get('definition', '')
            has_tiers = 'PRAGMATIC_ITEMS_DIRECT' in defn or 'difficulty-tiered' in defn
            print(f"    has tiered definition: {has_tiers}")
        elif f.name.endswith('.run.json'):
            print(f"    score: {d.get('score')}")
            tv = d.get('taskVersion', {})
            print(f"    taskVersion.versionNumber: {tv.get('versionNumber')}")
            tv_defn = tv.get('definition', '')
            has_tiers = 'PRAGMATIC_ITEMS_DIRECT' in tv_defn or 'difficulty-tiered' in tv_defn
            print(f"    taskVersion has tiered definition: {has_tiers}")

    print("\nDone.")


if __name__ == '__main__':
    main()
