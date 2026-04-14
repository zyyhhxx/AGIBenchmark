#!/usr/bin/env python3
"""Run calibration for a single model by index (0-9)."""
import sys, os, json, time, traceback
from datetime import datetime, timezone

idx = int(sys.argv[1])

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BENCH_DIR = os.path.join(REPO, 'benchmarks', 'metacognition')
sys.path.insert(0, BENCH_DIR)
sys.path.insert(0, REPO)

os.environ.pop('AWS_PROFILE', None)
import boto3
from botocore.config import Config

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
PROGRESS_FILE = os.path.join(RESULTS_DIR, "calibration_v2_results.json")

MODEL_CATALOG = [
    ("anthropic.claude-opus-4-6-v1", "Claude Opus 4.6", "us.anthropic.claude-opus-4-6-v1", 300),
    ("anthropic.claude-sonnet-4-6", "Claude Sonnet 4.6", "us.anthropic.claude-sonnet-4-6", 300),
    ("meta.llama3-3-70b-instruct-v1_0", "Llama 3.3 70B", "us.meta.llama3-3-70b-instruct-v1:0", 300),
    ("amazon.nova-pro-v1_0", "Nova Pro", "us.amazon.nova-pro-v1:0", 300),
    ("meta.llama4-maverick-17b-instruct-v1_0", "Llama 4 Maverick 17B", "us.meta.llama4-maverick-17b-instruct-v1:0", 300),
    ("qwen.qwen3-next-80b-a3b", "Qwen3 Next 80B", "qwen.qwen3-next-80b-a3b", 300),
    ("zai.glm-4.7", "GLM 4.7", "zai.glm-4.7", 300),
    ("deepseek.r1-v1_0", "DeepSeek-R1", "us.deepseek.r1-v1:0", 900),
    ("openai.gpt-oss-120b-1_0", "GPT-OSS-120B", "openai.gpt-oss-120b-1:0", 300),
    ("mistral.ministral-3-3b-instruct", "Ministral 3B", "mistral.ministral-3-3b-instruct", 300),
]

result_key, label, invoke_id, timeout = MODEL_CATALOG[idx]

class BedrockLLM:
    def __init__(self, model_id, timeout=300):
        session = boto3.Session(region_name='us-east-1')
        self.client = session.client("bedrock-runtime",
                                      config=Config(read_timeout=timeout, retries={"max_attempts": 2, "mode": "adaptive"}))
        self.model_id = model_id
    def prompt(self, text, **kwargs):
        messages = [{"role": "user", "content": [{"text": text}]}]
        resp = self.client.converse(modelId=self.model_id, messages=messages,
                                     inferenceConfig={"maxTokens": 2048, "temperature": 0.0})
        content = resp["output"]["message"]["content"]
        # Handle different response formats (some models use reasoningContent)
        for block in content:
            if "text" in block:
                return block["text"]
        # Fallback: try to extract any text-like content
        for block in content:
            if "reasoningContent" in block:
                rc = block["reasoningContent"]
                if isinstance(rc, dict) and "reasoningText" in rc:
                    # For reasoning models, the actual answer may be in a later block
                    continue
        # If only reasoning content, return the reasoning text
        for block in content:
            if "reasoningContent" in block:
                rc = block["reasoningContent"]
                if isinstance(rc, dict) and "reasoningText" in rc:
                    return rc["reasoningText"]["text"] if isinstance(rc["reasoningText"], dict) else str(rc["reasoningText"])
        return str(content)

class FakeChats:
    class _ctx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
    def new(self, name=""): return self._ctx()

import importlib
def run_calibration(llm):
    mod = importlib.import_module("benchmarks.metacognition.task_calibration")
    importlib.reload(mod)
    import kaggle_benchmarks as kbench
    kbench.chats = FakeChats()
    task_fn = mod.metacog_calibration.__wrapped__ if hasattr(mod.metacog_calibration, '__wrapped__') else mod.metacog_calibration
    return task_fn(llm)

# Load progress
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE) as f:
        progress = json.load(f)
else:
    progress = {"scores": {}}

scores = progress.get("scores", {})
if label in scores and scores[label].get("score") is not None:
    print(f"SKIP {label}: already scored {scores[label]['score']}")
    sys.exit(0)

print(f"Running {label} ({invoke_id}) timeout={timeout}s")
sys.stdout.flush()

llm = BedrockLLM(invoke_id, timeout)
t0 = time.time()
try:
    score = run_calibration(llm)
    dur = time.time() - t0
    scores[label] = {"score": round(score, 4), "duration_s": round(dur, 1), "error": None}
    print(f">>> {label}: score={score:.4f}, duration={dur:.1f}s")
    # Save to per-model JSON too
    rfile = os.path.join(RESULTS_DIR, f"{result_key}.json")
    if os.path.exists(rfile):
        with open(rfile) as f:
            rdata = json.load(f)
        rdata.setdefault("benchmarks", {})["metacog_calibration"] = {"score": round(score, 4)}
        with open(rfile, "w") as f:
            json.dump(rdata, f, indent=2)
except Exception as e:
    dur = time.time() - t0
    scores[label] = {"score": None, "duration_s": round(dur, 1), "error": str(e)[:200]}
    print(f">>> {label}: ERROR after {dur:.1f}s: {e}")
    traceback.print_exc()

progress["scores"] = scores
progress["timestamp"] = datetime.now(timezone.utc).isoformat()
with open(PROGRESS_FILE, "w") as f:
    json.dump(progress, f, indent=2)
print("DONE")
