#!/usr/bin/env python3
"""Fill gaps in benchmark results. Merges into existing result files."""
import json, os, sys, time, importlib, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")

# Import runner components
sys.path.insert(0, os.path.join(REPO, "scripts"))
from run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS, create_bedrock_llm, run_one

ALL_BENCHMARKS = []
for track_benchmarks in BENCHMARKS.values():
    ALL_BENCHMARKS.extend(track_benchmarks)

# Models ordered: fast/cheap first, slow/expensive last
MODEL_ORDER = [
    "meta.llama3-3-70b-instruct-v1:0",
    "meta.llama4-maverick-17b-instruct-v1:0",
    "amazon.nova-pro-v1:0",
    "mistral.ministral-3-3b-instruct",
    "anthropic.claude-sonnet-4-6",
    "openai.gpt-oss-120b-1:0",
    "deepseek.r1-v1:0",
    "qwen.qwen3-next-80b-a3b",
    "zai.glm-4.7",
    "anthropic.claude-opus-4-6-v1",
]

MAX_TIME = 24 * 60  # 24 min

def result_path(model_id):
    safe = model_id.replace(':', '_').replace('/', '_')
    return os.path.join(RESULTS_DIR, f"{safe}.json")

def load_results(model_id):
    p = result_path(model_id)
    if os.path.exists(p):
        try: return json.load(open(p))
        except: pass
    entry = MODEL_CATALOG.get(model_id, (model_id, model_id))
    return {"model": model_id, "model_label": entry[0], "timestamp": "", "scores": {}}

def save_results(model_id, data):
    from datetime import datetime, timezone
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(result_path(model_id), 'w') as f:
        json.dump(data, f, indent=2)

def get_gaps(model_id):
    data = load_results(model_id)
    scores = data.get("scores", {})
    gaps = []
    for mod_path, fn_name in ALL_BENCHMARKS:
        if fn_name not in scores or scores[fn_name].get("error"):
            gaps.append((mod_path, fn_name))
    return gaps

def main():
    start = time.time()
    total_run = 0
    total_ok = 0

    for model_id in MODEL_ORDER:
        if time.time() - start > MAX_TIME:
            print(f"\n⏰ Time budget hit. Stopping.")
            break

        gaps = get_gaps(model_id)
        if not gaps:
            print(f"✅ {MODEL_CATALOG[model_id][0]}: complete ({len(ALL_BENCHMARKS)} benchmarks)")
            continue

        label = MODEL_CATALOG[model_id][0]
        invoke_id = MODEL_CATALOG[model_id][1]
        print(f"\n{'='*60}")
        print(f"{label}: {len(gaps)} gaps to fill")
        print(f"{'='*60}")

        llm = create_bedrock_llm(invoke_id)
        data = load_results(model_id)

        for i, (mod_path, fn_name) in enumerate(gaps):
            if time.time() - start > MAX_TIME:
                print(f"  ⏰ Time budget. Saving progress.")
                break

            print(f"  [{i+1}/{len(gaps)}] {fn_name}...", end=" ", flush=True)
            r = run_one(mod_path, fn_name, llm, model_id, label)
            total_run += 1

            data["scores"][fn_name] = {
                "score": r["score"],
                "error": r["error"],
                "duration_s": r["duration_s"],
            }
            save_results(model_id, data)

            if r["error"]:
                print(f"ERROR ({r['duration_s']:.0f}s): {r['error'][:60]}")
            else:
                print(f"{r['score']:.4f} ({r['duration_s']:.0f}s)")
                total_ok += 1

            time.sleep(2)

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"Gap-fill: {total_run} run, {total_ok} ok, {total_run-total_ok} err ({elapsed:.0f}s)")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
