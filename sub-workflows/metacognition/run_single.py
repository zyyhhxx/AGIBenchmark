#!/usr/bin/env python3
"""Run a single benchmark for a single model, output JSON result to stdout."""
import json, os, sys, time, importlib, traceback

REPO = "/home/ubuntu/.openclaw/workspace-agi-bench/repo"
sys.path.insert(0, REPO)
os.environ['PYTHONUNBUFFERED'] = '1'

from scripts.run_benchmark_bedrock import (
    MODEL_CATALOG, BENCHMARKS, setup_kbench_mocks,
    create_bedrock_llm, get_track_for_benchmark
)

def run_one(mod_path, fn_name, llm):
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
    fn = getattr(mod, fn_name)
    t0 = time.time()
    result = fn(llm)
    duration = round(time.time() - t0, 1)
    
    score = None
    if isinstance(result, (int, float)):
        score = float(result)
    elif hasattr(result, 'score'):
        score = float(result.score) if result.score is not None else None
    elif isinstance(result, dict) and 'score' in result:
        score = float(result['score']) if result['score'] is not None else None
    
    return {"score": score, "error": None, "duration_s": duration}

def main():
    model_id = sys.argv[1]
    benchmark_name = sys.argv[2]
    
    entry = MODEL_CATALOG.get(model_id)
    if not entry:
        print(json.dumps({"score": None, "error": f"unknown model {model_id}", "duration_s": 0}))
        sys.exit(1)
    
    invoke_id = entry[1]
    
    # Find benchmark
    mod_path = None
    for track in BENCHMARKS:
        for mp, fn in BENCHMARKS[track]:
            if fn == benchmark_name:
                mod_path = mp
                break
    
    if not mod_path:
        print(json.dumps({"score": None, "error": f"unknown benchmark {benchmark_name}", "duration_s": 0}))
        sys.exit(1)
    
    try:
        llm = create_bedrock_llm(invoke_id)
        result = run_one(mod_path, benchmark_name, llm)
        print("RESULT_JSON:" + json.dumps(result))
    except Exception as e:
        print("RESULT_JSON:" + json.dumps({"score": None, "error": str(e)[:300], "duration_s": 0}))
        sys.exit(1)

if __name__ == "__main__":
    main()
