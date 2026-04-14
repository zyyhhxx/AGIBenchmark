#!/usr/bin/env python3
"""
Run attention_vigilance against all 10 models with Q&A transcript logging.
Saves per-model .jsonl transcripts, .summary.json, and aggregate_stats.json.
"""
import os, sys, json, time, importlib, traceback, statistics
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, REPO)

# Reuse model catalog and Bedrock LLM from existing runner
from scripts.run_benchmark_bedrock import (
    MODEL_CATALOG, create_bedrock_llm, setup_kbench_mocks, REPO as _REPO
)

OUT_DIR = os.path.join(REPO, 'sub-workflows', 'benchmark-qa', 'results', 'qa_transcripts', 'attention_vigilance')
os.makedirs(OUT_DIR, exist_ok=True)

# Timeouts
DEFAULT_TIMEOUT = 300
DEEPSEEK_TIMEOUT = 900

# Model order
MODEL_IDS = list(MODEL_CATALOG.keys())


class TranscriptLLM:
    """Wraps a BedrockLLM to record all prompts and responses."""
    def __init__(self, inner):
        self._inner = inner
        self.transcript = []  # list of {question_id, prompt, response}
        self._call_count = 0

    def prompt(self, prompt, **kw):
        self._call_count += 1
        qid = f"q_{self._call_count:03d}"
        resp = self._inner.prompt(prompt, **kw)
        self.transcript.append({
            "question_id": qid,
            "prompt": prompt,
            "response": resp,
        })
        return resp

    def __call__(self, prompt, **kw):
        return self.prompt(prompt, **kw)

    # Forward token counts
    @property
    def _total_input_tokens(self):
        return self._inner._total_input_tokens
    @property
    def _total_output_tokens(self):
        return self._inner._total_output_tokens


def run_for_model(model_id: str) -> dict:
    """Run attention_vigilance for one model, return score + transcript."""
    entry = MODEL_CATALOG[model_id]
    label, invoke_id = entry
    is_deepseek = 'deepseek' in model_id.lower()
    timeout = DEEPSEEK_TIMEOUT if is_deepseek else DEFAULT_TIMEOUT

    print(f"\n{'='*60}")
    print(f"Running attention_vigilance — {label} ({invoke_id})")
    print(f"Timeout: {timeout}s")
    print(f"{'='*60}")

    # Setup mocks
    setup_kbench_mocks()

    # Add attention data dir to path
    attn_dir = os.path.join(REPO, 'benchmarks', 'attention')
    if attn_dir not in sys.path:
        sys.path.insert(0, attn_dir)

    # Clean module cache
    for key in list(sys.modules.keys()):
        if key == 'data' or key.startswith('data.') or 'task_vigilance' in key:
            del sys.modules[key]

    inner_llm = create_bedrock_llm(invoke_id, timeout=timeout)
    wrapper = TranscriptLLM(inner_llm)

    mod = importlib.import_module('benchmarks.attention.task_vigilance')
    task_fn = mod.attention_vigilance

    start = time.time()
    try:
        result = task_fn.run(llm=wrapper)
        elapsed = time.time() - start
        score = float(result.result) if hasattr(result, 'result') else float(result)
        error = None
    except Exception as e:
        elapsed = time.time() - start
        score = None
        error = str(e)[:300]
        print(f"  ERROR: {e}")
        traceback.print_exc()

    print(f"  Score: {score}")
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  LLM calls: {wrapper._call_count}")
    print(f"  Tokens: in={wrapper._total_input_tokens}, out={wrapper._total_output_tokens}")

    return {
        "model_id": model_id,
        "label": label,
        "score": score,
        "error": error,
        "duration_s": round(elapsed, 1),
        "transcript": wrapper.transcript,
        "input_tokens": wrapper._total_input_tokens,
        "output_tokens": wrapper._total_output_tokens,
    }


def save_transcript(result: dict):
    """Save .jsonl transcript and .summary.json for one model."""
    model_id = result["model_id"]
    safe_name = model_id.replace(':', '_').replace('/', '_')

    # Save JSONL transcript
    jsonl_path = os.path.join(OUT_DIR, f"{safe_name}.jsonl")
    with open(jsonl_path, 'w') as f:
        for entry in result["transcript"]:
            # We don't have parsed_answer/correct_answer at this level since
            # the benchmark handles scoring internally. Record what we can.
            record = {
                "question_id": entry["question_id"],
                "prompt": entry["prompt"],
                "response": entry["response"],
                "parsed_answer": None,  # internal to benchmark
                "correct_answer": None,
                "score": None,
            }
            f.write(json.dumps(record) + '\n')

    # Save summary
    summary = {
        "model_id": model_id,
        "model_label": result["label"],
        "benchmark": "attention_vigilance",
        "score": result["score"],
        "error": result["error"],
        "duration_s": result["duration_s"],
        "llm_calls": len(result["transcript"]),
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    summary_path = os.path.join(OUT_DIR, f"{safe_name}.summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"  Saved: {jsonl_path}")
    print(f"  Saved: {summary_path}")


def save_aggregate(all_results: list):
    """Compute and save aggregate stats across all models."""
    scores = [r["score"] for r in all_results if r["score"] is not None]
    n_success = len(scores)
    n_fail = len(all_results) - n_success

    agg = {
        "benchmark": "attention_vigilance",
        "n_models": len(all_results),
        "n_success": n_success,
        "n_fail": n_fail,
        "scores": {r["model_id"]: r["score"] for r in all_results},
        "labels": {r["model_id"]: r["label"] for r in all_results},
    }

    if scores:
        agg["mean"] = round(statistics.mean(scores), 4)
        agg["std"] = round(statistics.stdev(scores), 4) if len(scores) > 1 else 0.0
        agg["min"] = round(min(scores), 4)
        agg["max"] = round(max(scores), 4)
        agg["range"] = round(max(scores) - min(scores), 4)
    else:
        agg["mean"] = agg["std"] = agg["min"] = agg["max"] = agg["range"] = None

    agg["timestamp"] = datetime.now(timezone.utc).isoformat()

    path = os.path.join(OUT_DIR, "aggregate_stats.json")
    with open(path, 'w') as f:
        json.dump(agg, f, indent=2)
    print(f"\nAggregate stats saved: {path}")
    return agg


def main():
    print(f"attention_vigilance Q&A benchmark run")
    print(f"Models: {len(MODEL_IDS)}")
    print(f"Output: {OUT_DIR}")

    all_results = []
    failures = []

    for i, model_id in enumerate(MODEL_IDS):
        # Skip if already completed
        safe_name = model_id.replace(':', '_').replace('/', '_')
        summary_path = os.path.join(OUT_DIR, f"{safe_name}.summary.json")
        if os.path.exists(summary_path):
            try:
                with open(summary_path) as f:
                    existing = json.load(f)
                if existing.get("score") is not None:
                    print(f"\n[{i+1}/10] {MODEL_CATALOG[model_id][0]} — already scored ({existing['score']:.4f}), skipping")
                    all_results.append({
                        "model_id": model_id,
                        "label": existing["model_label"],
                        "score": existing["score"],
                        "error": None,
                        "duration_s": existing["duration_s"],
                        "transcript": [],
                        "input_tokens": existing.get("input_tokens", 0),
                        "output_tokens": existing.get("output_tokens", 0),
                    })
                    continue
            except Exception:
                pass

        print(f"\n[{i+1}/10] Running {MODEL_CATALOG[model_id][0]}...")
        result = run_for_model(model_id)
        save_transcript(result)
        all_results.append(result)

        if result["score"] is None:
            failures.append((model_id, result["error"]))

        # Rate limit
        if i < len(MODEL_IDS) - 1:
            time.sleep(5)

    # Retry failures once with doubled timeout
    if failures:
        print(f"\n{'='*60}")
        print(f"RETRYING {len(failures)} failures with doubled timeout")
        print(f"{'='*60}")
        for model_id, err in failures:
            entry = MODEL_CATALOG[model_id]
            label = entry[0]
            is_deepseek = 'deepseek' in model_id.lower()
            timeout = (DEEPSEEK_TIMEOUT if is_deepseek else DEFAULT_TIMEOUT) * 2

            print(f"\nRetrying {label} with {timeout}s timeout...")
            # Temporarily patch timeout
            orig_default = DEFAULT_TIMEOUT
            result = run_for_model(model_id)
            save_transcript(result)

            # Update in all_results
            for j, r in enumerate(all_results):
                if r["model_id"] == model_id:
                    all_results[j] = result
                    break

    # Aggregate
    agg = save_aggregate(all_results)

    # Print final summary
    print(f"\n{'='*60}")
    print(f"ATTENTION_VIGILANCE — FINAL RESULTS")
    print(f"{'='*60}")
    sorted_results = sorted(all_results, key=lambda r: r["score"] if r["score"] is not None else -1, reverse=True)
    for r in sorted_results:
        s = f"{r['score']:.4f}" if r["score"] is not None else f"ERROR: {r['error'][:50]}"
        print(f"  {r['label']:30s} {s}  ({r['duration_s']}s)")

    print(f"\nAggregate: mean={agg.get('mean')}, std={agg.get('std')}, range={agg.get('range')}")
    print(f"Coverage: {agg['n_success']}/10")


if __name__ == "__main__":
    main()
