#!/usr/bin/env python3
"""Re-run social_cog_sarcasm benchmark against all 10 models (3-tier 85-item redesign).
Calls the task function directly instead of through kbench .run() to pass real Bedrock LLM."""
import json, os, sys, time, traceback
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'benchmarks', 'social_cognition'))
sys.path.insert(0, os.path.join(REPO, 'scripts'))

from run_benchmark_bedrock import MODEL_CATALOG, create_bedrock_llm, setup_kbench_mocks, CALL_TIMEOUT

OUTPUT_DIR = os.path.join(REPO, 'sub-workflows', 'benchmark-qa', 'results', 'qa_transcripts', 'social_cog_sarcasm_v2')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Prevent module-level .run() from executing by patching kbench before import
setup_kbench_mocks()
import kaggle_benchmarks as kbench

# Monkey-patch the task decorator to NOT auto-run
_orig_task = kbench.task
def _noop_task(*args, **kwargs):
    def decorator(fn):
        fn.run = lambda **kw: fn(kw.get('llm', kbench.llm))
        return fn
    if args and callable(args[0]):
        return decorator(args[0])
    return decorator
kbench.task = _noop_task

# Now import the task module — .run() at bottom will use DummyLLM but we don't care
# We'll call the underlying function directly with real LLM
for key in list(sys.modules.keys()):
    if 'sarcasm' in key or key == 'data' or key.startswith('data.'):
        del sys.modules[key]

from benchmarks.social_cognition.task_sarcasm import social_cog_sarcasm


def run_sarcasm_one_model(model_id):
    entry = MODEL_CATALOG[model_id]
    label, invoke_id = entry
    
    safe_name = model_id.replace(':', '_').replace('/', '_')
    out_path = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
    if os.path.exists(out_path):
        with open(out_path) as f:
            existing = json.load(f)
        if existing.get('score') is not None:
            print(f"SKIP {label}: already scored {existing['score']:.4f}")
            return existing
    
    print(f"\n{'='*60}")
    print(f"Running social_cog_sarcasm with {label} ({invoke_id})")
    print(f"{'='*60}")
    
    llm = create_bedrock_llm(invoke_id, timeout=CALL_TIMEOUT)
    
    start = time.time()
    try:
        score = social_cog_sarcasm(llm)
        score = float(score)
        elapsed = time.time() - start
        print(f"  Score: {score:.4f}")
        print(f"  Time: {elapsed:.1f}s")
        print(f"  Tokens: in={llm._total_input_tokens}, out={llm._total_output_tokens}")
        
        output = {
            "model": model_id,
            "model_label": label,
            "score": score,
            "error": None,
            "duration_s": round(elapsed, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "v2_3tier_85items",
        }
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ERROR: {e}")
        print(traceback.format_exc()[-500:])
        output = {
            "model": model_id,
            "model_label": label,
            "score": None,
            "error": str(e)[:300],
            "duration_s": round(elapsed, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "v2_3tier_85items",
        }
    
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    return output


def main():
    models = list(MODEL_CATALOG.keys())
    print(f"Running sarcasm v2 (85 items, 3-tier) against {len(models)} models")
    print(f"Output: {OUTPUT_DIR}\n")
    
    results = {}
    for i, model_id in enumerate(models):
        r = run_sarcasm_one_model(model_id)
        results[model_id] = r
        if i < len(models) - 1:
            time.sleep(3)
    
    # Summary
    print(f"\n{'='*60}")
    print("SARCASM v2 RESULTS SUMMARY")
    print(f"{'='*60}")
    scores = []
    for mid, r in results.items():
        label = r.get('model_label', mid)
        score = r.get('score')
        if score is not None:
            scores.append(score)
            print(f"  {label:35s} → {score:.4f}  ({r.get('duration_s', '?')}s)")
        else:
            print(f"  {label:35s} → ERROR: {(r.get('error') or '')[:60]}")
    
    if scores:
        import numpy as np
        arr = np.array(scores)
        print(f"\n  mean={arr.mean():.4f}, std={arr.std():.4f}, range={arr.max()-arr.min():.4f}")
        print(f"  min={arr.min():.4f}, max={arr.max():.4f}, n={len(scores)}/10")
        print(f"  std >= 0.08: {'PASS ✅' if arr.std() >= 0.08 else 'FAIL ❌'}")


if __name__ == '__main__':
    main()
