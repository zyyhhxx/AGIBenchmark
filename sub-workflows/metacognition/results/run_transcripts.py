#!/usr/bin/env python3
"""
Run all 9 metacog benchmarks across 10 models with full Q&A transcript logging.

Wraps the BedrockLLM to capture every prompt+response pair, then writes them
to JSONL files at: qa_transcripts/<benchmark>/<model>.jsonl

Each line: {"question_id": N, "prompt": "...", "response": "...", "parsed_answer": "...", "correct_answer": "...", "score": ...}
"""
import argparse, json, os, sys, time, importlib, traceback, re
from datetime import datetime, timezone

os.environ['PYTHONUNBUFFERED'] = '1'

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)

from scripts.run_benchmark_bedrock import (
    MODEL_CATALOG, BENCHMARKS, DELAY_BETWEEN_BENCHMARKS, DELAY_BETWEEN_MODELS,
    CALL_TIMEOUT, SLOW_BENCHMARKS, SLOW_TIMEOUT,
    create_bedrock_llm, setup_kbench_mocks, get_track_for_benchmark
)

TRANSCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qa_transcripts')
METACOG_BENCHMARKS = BENCHMARKS['metacognition']  # 9 benchmarks


class TranscriptLLM:
    """Wraps a BedrockLLM to log every prompt+response."""

    def __init__(self, inner):
        self._inner = inner
        self.transcript = []  # list of {"prompt": ..., "response": ...}
        # Forward token counters
        self._total_input_tokens = getattr(inner, '_total_input_tokens', 0)
        self._total_output_tokens = getattr(inner, '_total_output_tokens', 0)

    def _record(self, prompt, response):
        self.transcript.append({
            "prompt": prompt,
            "response": str(response) if not isinstance(response, str) else response,
        })
        self._total_input_tokens = self._inner._total_input_tokens
        self._total_output_tokens = self._inner._total_output_tokens

    def prompt(self, prompt, **kw):
        result = self._inner.prompt(prompt, **kw)
        self._record(prompt, result)
        return result

    def __call__(self, prompt, **kw):
        result = self._inner(prompt, **kw)
        self._record(prompt, result)
        return result


def run_benchmark_with_transcript(mod_path, fn_name, model_id, model_label, invoke_id, timeout):
    """Run one benchmark, return (score, transcript, error)."""
    # Clean module cache
    for key in list(sys.modules.keys()):
        if key == 'data' or key.startswith('data.'):
            del sys.modules[key]

    track = get_track_for_benchmark(fn_name)
    track_dir = os.path.join(REPO, 'benchmarks', track)
    if track_dir not in sys.path:
        sys.path.insert(0, track_dir)

    setup_kbench_mocks()

    if mod_path in sys.modules:
        del sys.modules[mod_path]
    mod = importlib.import_module(mod_path)
    task_fn = getattr(mod, fn_name)

    inner_llm = create_bedrock_llm(invoke_id, timeout=timeout)
    wrapped_llm = TranscriptLLM(inner_llm)

    print(f"\n{'='*60}")
    print(f"Running {fn_name} with {model_label}")
    print(f"{'='*60}")

    start = time.time()
    try:
        result = task_fn.run(llm=wrapped_llm)
        elapsed = time.time() - start
        score = float(result.result) if hasattr(result, 'result') else float(result)
        print(f"  Score: {score:.4f}  ({elapsed:.1f}s, {len(wrapped_llm.transcript)} calls)")
        return score, wrapped_llm.transcript, None, elapsed
    except Exception as e:
        elapsed = time.time() - start
        tb = traceback.format_exc()
        print(f"  ERROR: {e}")
        print(tb[-300:])
        return None, wrapped_llm.transcript, str(e)[:200], elapsed


def save_transcript(benchmark, model_safe, transcript, score, error, duration):
    """Save transcript to qa_transcripts/<benchmark>/<model>.jsonl"""
    out_dir = os.path.join(TRANSCRIPT_DIR, benchmark)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{model_safe}.jsonl")

    with open(out_path, 'w') as f:
        for i, entry in enumerate(transcript):
            record = {
                "question_id": i,
                "prompt": entry["prompt"],
                "response": entry["response"],
                "parsed_answer": "",  # Would need benchmark-specific parsing
                "correct_answer": "",  # Not available generically
                "score": score if i == len(transcript) - 1 else None,  # Final entry gets aggregate score
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    # Also write a summary line
    summary_path = os.path.join(out_dir, f"{model_safe}.summary.json")
    with open(summary_path, 'w') as f:
        json.dump({
            "benchmark": benchmark,
            "model": model_safe,
            "score": score,
            "error": error,
            "duration_s": round(duration, 1),
            "n_calls": len(transcript),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, f, indent=2)

    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="all", help="Model ID or 'all'")
    parser.add_argument("--benchmark", default=None, help="Single benchmark name")
    parser.add_argument("--timeout-deepseek", type=int, default=900)
    parser.add_argument("--timeout-default", type=int, default=300)
    args = parser.parse_args()

    # Resolve models
    if args.model == "all":
        model_ids = list(MODEL_CATALOG.keys())
    else:
        model_ids = [args.model]

    # Resolve benchmarks
    if args.benchmark:
        targets = [(m, n) for m, n in METACOG_BENCHMARKS if n == args.benchmark]
    else:
        targets = METACOG_BENCHMARKS

    print(f"Models: {len(model_ids)}, Benchmarks: {len(targets)}")
    print(f"Total runs: {len(model_ids) * len(targets)}")
    print(f"Transcript dir: {TRANSCRIPT_DIR}")

    all_scores = {}  # model -> {benchmark -> score}

    for mi, model_id in enumerate(model_ids):
        entry = MODEL_CATALOG.get(model_id)
        label = entry[0] if entry else model_id
        invoke_id = entry[1] if entry else model_id
        safe_name = model_id.replace(':', '_').replace('/', '_')

        print(f"\n{'#'*60}")
        print(f"# MODEL {mi+1}/{len(model_ids)}: {label}")
        print(f"{'#'*60}")

        model_scores = {}

        for bi, (mod_path, fn_name) in enumerate(targets):
            # Check if transcript already exists
            transcript_path = os.path.join(TRANSCRIPT_DIR, fn_name, f"{safe_name}.jsonl")
            if os.path.exists(transcript_path) and os.path.getsize(transcript_path) > 0:
                # Load existing score from summary
                summary_path = os.path.join(TRANSCRIPT_DIR, fn_name, f"{safe_name}.summary.json")
                if os.path.exists(summary_path):
                    with open(summary_path) as f:
                        summ = json.load(f)
                    if summ.get("score") is not None:
                        print(f"\n[{bi+1}/{len(targets)}] {fn_name} — already has transcript (score={summ['score']:.4f}), skipping")
                        model_scores[fn_name] = summ["score"]
                        continue

            # Determine timeout
            is_deepseek = 'deepseek' in model_id.lower()
            timeout = args.timeout_deepseek if is_deepseek else args.timeout_default
            if fn_name in SLOW_BENCHMARKS:
                timeout = max(timeout, SLOW_TIMEOUT)

            score, transcript, error, duration = run_benchmark_with_transcript(
                mod_path, fn_name, model_id, label, invoke_id, timeout
            )

            save_transcript(fn_name, safe_name, transcript, score, error, duration)
            model_scores[fn_name] = score

            if bi < len(targets) - 1:
                time.sleep(DELAY_BETWEEN_BENCHMARKS)

        all_scores[model_id] = model_scores

        if mi < len(model_ids) - 1:
            time.sleep(DELAY_BETWEEN_MODELS)

    # Print final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")

    # Count transcripts
    total_expected = len(model_ids) * len(targets)
    total_exists = 0
    total_scored = 0
    for model_id in model_ids:
        safe_name = model_id.replace(':', '_').replace('/', '_')
        for _, fn_name in targets:
            path = os.path.join(TRANSCRIPT_DIR, fn_name, f"{safe_name}.jsonl")
            if os.path.exists(path):
                total_exists += 1
            s = all_scores.get(model_id, {}).get(fn_name)
            if s is not None:
                total_scored += 1

    print(f"Transcripts: {total_exists}/{total_expected}")
    print(f"Scored: {total_scored}/{total_expected}")

    for model_id, scores in all_scores.items():
        label = MODEL_CATALOG.get(model_id, (model_id,))[0]
        valid = [v for v in scores.values() if v is not None]
        avg = sum(valid) / len(valid) if valid else 0
        print(f"  {label:30s}  avg={avg:.4f}  ok={len(valid)}/{len(targets)}")

    # Generate score matrix CSV
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'score_matrix_metacog_v2.csv')
    benchmarks_list = [fn for _, fn in targets]
    with open(csv_path, 'w') as f:
        f.write("model," + ",".join(benchmarks_list) + "\n")
        for model_id in model_ids:
            label = MODEL_CATALOG.get(model_id, (model_id,))[0]
            scores = all_scores.get(model_id, {})
            row = [label]
            for fn in benchmarks_list:
                s = scores.get(fn)
                row.append(f"{s:.4f}" if s is not None else "")
            f.write(",".join(row) + "\n")
    print(f"\nScore matrix saved to: {csv_path}")


if __name__ == "__main__":
    main()
