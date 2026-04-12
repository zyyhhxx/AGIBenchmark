#!/usr/bin/env python3
"""Quick test of learning_curves v3 against 3 models."""
import sys, os, time, json, traceback
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)

import boto3
from botocore.config import Config

os.environ.pop('AWS_PROFILE', None)
config = Config(read_timeout=900, retries={"max_attempts": 3, "mode": "adaptive"})
client = boto3.Session(region_name='us-east-1').client("bedrock-runtime", config=config)

MODELS = [
    ("us.anthropic.claude-opus-4-6-v1", "Claude Opus 4.6"),
    ("us.amazon.nova-pro-v1:0", "Nova Pro"),
    ("mistral.ministral-3-3b-instruct", "Ministral 3B"),
]


class BedrockLLM:
    def __init__(self, model_id):
        self.model_id = model_id

    def prompt(self, text, schema=None):
        body = {
            "messages": [{"role": "user", "content": [{"text": text}]}],
        }
        # Add inference config
        body["inferenceConfig"] = {"maxTokens": 2048, "temperature": 0}

        for attempt in range(3):
            try:
                resp = client.converse(modelId=self.model_id, **body)
                output = resp["output"]["message"]["content"][0]["text"]
                if schema:
                    import re
                    m = re.search(r'\{.*\}', output, re.DOTALL)
                    if m:
                        parsed = json.loads(m.group())
                        return type('Obj', (), parsed)()
                return output
            except Exception as e:
                if attempt < 2:
                    time.sleep(5 * (attempt + 1))
                else:
                    raise


# Minimal kbench mock
class MockChats:
    class _ctx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
    def new(self, label): return self._ctx()

class MockKbench:
    class chats_cls:
        @staticmethod
        def new(label):
            return MockChats._ctx()
    chats = chats_cls()

# Monkey-patch kbench
import kaggle_benchmarks as kbench
kbench.chats = MockKbench.chats

from benchmarks.learning.task_learning_curves import learning_curves

scores = {}
for model_id, label in MODELS:
    print(f"\n{'='*60}")
    print(f"Running learning_curves v3 on {label} ({model_id})")
    print(f"{'='*60}")
    t0 = time.time()
    try:
        llm = BedrockLLM(model_id)
        # Call the underlying function directly
        score = learning_curves.fn(llm)
        elapsed = time.time() - t0
        scores[label] = score
        print(f"\n>>> {label}: score={score:.4f} (took {elapsed:.0f}s)")
    except Exception as e:
        elapsed = time.time() - t0
        print(f"\n>>> {label}: ERROR after {elapsed:.0f}s: {e}")
        traceback.print_exc()
        scores[label] = None
    time.sleep(5)

print(f"\n{'='*60}")
print("SUMMARY — learning_curves v3")
print(f"{'='*60}")
valid = [v for v in scores.values() if v is not None]
for label, score in scores.items():
    print(f"  {label}: {score}")
if len(valid) >= 2:
    print(f"\n  mean = {np.mean(valid):.4f}")
    print(f"  std  = {np.std(valid):.4f}")
    print(f"  range = {max(valid) - min(valid):.4f}")
    print(f"  TARGET std >= 0.08: {'PASS ✅' if np.std(valid) >= 0.08 else 'FAIL ❌'}")
