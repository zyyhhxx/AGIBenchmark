#!/usr/bin/env python3
"""Run metacog_calibration v2 (with 12 new d=5 items) against all 10 Bedrock models."""
import sys, os, json, time, traceback
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)

import importlib
import boto3
from botocore.config import Config

BEDROCK_CONFIG = Config(
    read_timeout=300,
    retries={"max_attempts": 3, "mode": "adaptive"},
)

MODEL_CATALOG = {
    "anthropic.claude-opus-4-6-v1":               ("Claude Opus 4.6",        "us.anthropic.claude-opus-4-6-v1"),
    "deepseek.r1-v1:0":                           ("DeepSeek-R1",            "us.deepseek.r1-v1:0"),
    "openai.gpt-oss-120b-1:0":                    ("GPT-OSS-120B",           "openai.gpt-oss-120b-1:0"),
    "meta.llama3-3-70b-instruct-v1:0":            ("Llama 3.3 70B",          "us.meta.llama3-3-70b-instruct-v1:0"),
    "qwen.qwen3-next-80b-a3b":                    ("Qwen3 Next 80B",         "qwen.qwen3-next-80b-a3b"),
    "amazon.nova-pro-v1:0":                        ("Nova Pro",               "us.amazon.nova-pro-v1:0"),
    "meta.llama4-maverick-17b-instruct-v1:0":     ("Llama 4 Maverick 17B",   "us.meta.llama4-maverick-17b-instruct-v1:0"),
    "anthropic.claude-sonnet-4-6":                 ("Claude Sonnet 4.6",      "us.anthropic.claude-sonnet-4-6"),
    "zai.glm-4.7":                                 ("GLM 4.7",                "zai.glm-4.7"),
    "mistral.ministral-3-3b-instruct":            ("Ministral 3B",           "mistral.ministral-3-3b-instruct"),
}

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

OUTPUT_CSV = os.path.join(RESULTS_DIR, "calibration_v2_scores.csv")


class BedrockLLM:
    """Minimal LLM wrapper for Bedrock Converse API."""
    def __init__(self, model_id):
        self.client = boto3.client("bedrock-runtime", region_name="us-east-1", config=BEDROCK_CONFIG)
        self.model_id = model_id

    def prompt(self, text, **kwargs):
        messages = [{"role": "user", "content": [{"text": text}]}]
        try:
            resp = self.client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={"maxTokens": 2048, "temperature": 0.0},
            )
            return resp["output"]["message"]["content"][0]["text"]
        except Exception as e:
            return f"ERROR: {e}"


class FakeChats:
    """Minimal chat context manager for kbench compatibility."""
    class _ctx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
    def new(self, name=""):
        return self._ctx()


def run_calibration(llm):
    """Import and run task_calibration directly."""
    mod = importlib.import_module("benchmarks.metacognition.task_calibration")
    # Patch kbench.chats for local use
    import kaggle_benchmarks as kbench
    kbench.chats = FakeChats()
    
    task_fn = mod.metacog_calibration.__wrapped__ if hasattr(mod.metacog_calibration, '__wrapped__') else mod.metacog_calibration
    # The kbench task decorator wraps the function; we need to call the inner function
    # Actually, let's just call the module's function directly
    return task_fn(llm)


def main():
    scores = {}
    
    for model_id, (label, invoke_id) in MODEL_CATALOG.items():
        print(f"\n{'='*60}")
        print(f"Running metacog_calibration for {label} ({invoke_id})")
        print(f"{'='*60}")
        
        llm = BedrockLLM(invoke_id)
        t0 = time.time()
        
        try:
            score = run_calibration(llm)
            duration = time.time() - t0
            scores[label] = {"score": round(score, 4), "duration_s": round(duration, 1), "error": None}
            print(f"\n>>> {label}: score={score:.4f}, duration={duration:.1f}s")
        except Exception as e:
            duration = time.time() - t0
            scores[label] = {"score": None, "duration_s": round(duration, 1), "error": str(e)}
            print(f"\n>>> {label}: ERROR after {duration:.1f}s: {e}")
            traceback.print_exc()
        
        # Rate limit pause
        time.sleep(5)
    
    # Save results
    result_file = os.path.join(RESULTS_DIR, "calibration_v2_results.json")
    with open(result_file, "w") as f:
        json.dump({"timestamp": datetime.now(timezone.utc).isoformat(), "scores": scores}, f, indent=2)
    print(f"\nResults saved to {result_file}")
    
    # Save CSV
    with open(OUTPUT_CSV, "w") as f:
        f.write("model,score,duration_s,error\n")
        for label, data in scores.items():
            s = data["score"] if data["score"] is not None else ""
            f.write(f"{label},{s},{data['duration_s']},{data['error'] or ''}\n")
    print(f"CSV saved to {OUTPUT_CSV}")
    
    # Summary
    valid_scores = [d["score"] for d in scores.values() if d["score"] is not None]
    if valid_scores:
        import numpy as np
        arr = np.array(valid_scores)
        print(f"\n{'='*60}")
        print(f"SUMMARY: {len(valid_scores)}/{len(scores)} models scored")
        print(f"  mean={arr.mean():.4f}, std={arr.std():.4f}, range={arr.max()-arr.min():.4f}")
        print(f"  min={arr.min():.4f}, max={arr.max():.4f}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
