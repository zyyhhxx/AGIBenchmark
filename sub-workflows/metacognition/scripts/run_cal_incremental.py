#!/usr/bin/env python3
"""Run metacog_calibration incrementally - saves after each model, skips already-scored."""
import sys, os, json, time, traceback
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BENCH_DIR = os.path.join(REPO, 'benchmarks', 'metacognition')
sys.path.insert(0, BENCH_DIR)
sys.path.insert(0, REPO)

import importlib
import os as _os
# Remove AWS_PROFILE to use instance role
_os.environ.pop('AWS_PROFILE', None)
import boto3
from botocore.config import Config

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
PROGRESS_FILE = os.path.join(RESULTS_DIR, "calibration_v2_results.json")

MODEL_CATALOG = [
    # (result_json_key, label, invoke_id, timeout)
    ("anthropic.claude-opus-4-6-v1", "Claude Opus 4.6", "us.anthropic.claude-opus-4-6-v1", 300),
    ("anthropic.claude-sonnet-4-6", "Claude Sonnet 4.6", "us.anthropic.claude-sonnet-4-6", 300),
    ("meta.llama3-3-70b-instruct-v1_0", "Llama 3.3 70B", "us.meta.llama3-3-70b-instruct-v1:0", 300),
    ("amazon.nova-pro-v1_0", "Nova Pro", "us.amazon.nova-pro-v1:0", 300),
    ("meta.llama4-maverick-17b-instruct-v1_0", "Llama 4 Maverick 17B", "us.meta.llama4-maverick-17b-instruct-v1:0", 300),
    ("qwen.qwen3-next-80b-a3b", "Qwen3 Next 80B", "qwen.qwen3-next-80b-a3b", 300),
    ("deepseek.r1-v1_0", "DeepSeek-R1", "us.deepseek.r1-v1:0", 900),
    ("openai.gpt-oss-120b-1_0", "GPT-OSS-120B", "openai.gpt-oss-120b-1:0", 300),
    ("mistral.ministral-3-3b-instruct", "Ministral 3B", "mistral.ministral-3-3b-instruct", 300),
    ("zai.glm-4.7", "GLM 4.7", "zai.glm-4.7", 120),  # GLM is slow; short per-call timeout
]


class BedrockLLM:
    def __init__(self, model_id, timeout=300):
        session = boto3.Session(region_name='us-east-1')  # no profile
        self.client = session.client("bedrock-runtime",
                                      config=Config(read_timeout=timeout, retries={"max_attempts": 2, "mode": "adaptive"}))
        self.model_id = model_id

    def prompt(self, text, **kwargs):
        messages = [{"role": "user", "content": [{"text": text}]}]
        # DeepSeek-R1 needs more tokens to return the final text block
        max_tokens = 5000 if "deepseek" in self.model_id or "gpt-oss" in self.model_id else 2048
        inf_config = {"maxTokens": max_tokens}
        if "deepseek" not in self.model_id:
            inf_config["temperature"] = 0.0
        resp = self.client.converse(modelId=self.model_id, messages=messages,
                                     inferenceConfig=inf_config)
        content = resp["output"]["message"]["content"]
        # Handle reasoning models (DeepSeek-R1, GPT-OSS) that return reasoningContent + text
        for block in content:
            if "text" in block:
                return block["text"]
        # Fallback: extract text from reasoningContent if no text block
        for block in content:
            if "reasoningContent" in block:
                rc = block["reasoningContent"]
                if "reasoningText" in rc:
                    return rc["reasoningText"].get("text", str(rc))
        return str(content)


class FakeChats:
    class _ctx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
    def new(self, name=""): return self._ctx()


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"scores": {}}


def save_progress(data):
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def run_calibration(llm):
    # Add benchmarks/metacognition to path so 'data' imports work
    bench_dir = os.path.join(REPO, 'benchmarks', 'metacognition')
    if bench_dir not in sys.path:
        sys.path.insert(0, bench_dir)
    mod = importlib.import_module("benchmarks.metacognition.task_calibration")
    importlib.reload(mod)  # ensure fresh import with correct path
    import kaggle_benchmarks as kbench
    kbench.chats = FakeChats()
    task_fn = mod.metacog_calibration.__wrapped__ if hasattr(mod.metacog_calibration, '__wrapped__') else mod.metacog_calibration
    return task_fn(llm)


def main():
    import numpy as np
    progress = load_progress()
    scores = progress.get("scores", {})

    for result_key, label, invoke_id, timeout in MODEL_CATALOG:
        if label in scores and scores[label].get("score") is not None:
            print(f"SKIP {label}: already scored {scores[label]['score']}")
            continue

        print(f"\n{'='*60}")
        print(f"Running {label} ({invoke_id}) timeout={timeout}s")
        print(f"{'='*60}")
        sys.stdout.flush()

        llm = BedrockLLM(invoke_id, timeout=timeout)
        t0 = time.time()
        try:
            score = run_calibration(llm)
            dur = time.time() - t0
            scores[label] = {"score": round(score, 4), "duration_s": round(dur, 1), "error": None}
            print(f">>> {label}: score={score:.4f}, duration={dur:.1f}s")

            # Also save to the per-model result JSON
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
        save_progress(progress)
        time.sleep(3)

    # Final summary
    valid = [d["score"] for d in scores.values() if d["score"] is not None]
    print(f"\n{'='*60}")
    print(f"FINAL: {len(valid)}/{len(MODEL_CATALOG)} models scored")
    if valid:
        arr = np.array(valid)
        print(f"  mean={arr.mean():.4f}, std={arr.std():.4f}, range={arr.max()-arr.min():.4f}")
        print(f"  min={arr.min():.4f}, max={arr.max():.4f}")
        for label, d in sorted(scores.items(), key=lambda x: x[1].get("score") or 0, reverse=True):
            print(f"  {label}: {d['score']}")
    print(f"{'='*60}")

    # Save CSV
    csv_path = os.path.join(RESULTS_DIR, "calibration_v2_scores.csv")
    with open(csv_path, "w") as f:
        f.write("model,score,duration_s,error\n")
        for label, d in scores.items():
            s = d["score"] if d["score"] is not None else ""
            f.write(f"{label},{s},{d['duration_s']},{d.get('error') or ''}\n")
    print(f"CSV saved to {csv_path}")


if __name__ == "__main__":
    main()
