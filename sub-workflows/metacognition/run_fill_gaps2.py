#!/usr/bin/env python3
"""Fill gaps using subprocess per benchmark with hard timeout."""
import json, os, sys, time, subprocess, signal
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS_DIR = os.path.join(REPO, "sub-workflows/metacognition/results")
PYTHON = os.path.join(REPO, ".venv/bin/python3")

sys.path.insert(0, os.path.join(REPO, "scripts"))
from run_benchmark_bedrock import MODEL_CATALOG, BENCHMARKS

ALL_BM = [(mp, fn) for track in BENCHMARKS.values() for mp, fn in track]
BM_LOOKUP = {fn: mp for mp, fn in ALL_BM}

MODEL_ORDER = [
    "amazon.nova-pro-v1:0",
    "mistral.ministral-3-3b-instruct",
    "anthropic.claude-sonnet-4-6",
    "openai.gpt-oss-120b-1:0",
    "deepseek.r1-v1:0",
    "qwen.qwen3-next-80b-a3b",
    "zai.glm-4.7",
    "anthropic.claude-opus-4-6-v1",
]

BM_TIMEOUT = 180  # 3 min per benchmark
MAX_TIME = 24 * 60

def rpath(mid):
    return os.path.join(RESULTS_DIR, mid.replace(':','_').replace('/','_') + '.json')

def load(mid):
    p = rpath(mid)
    if os.path.exists(p):
        try: return json.load(open(p))
        except: pass
    e = MODEL_CATALOG.get(mid, (mid, mid))
    return {"model": mid, "model_label": e[0], "timestamp": "", "scores": {}}

def save(mid, data):
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(rpath(mid), 'w') as f:
        json.dump(data, f, indent=2)

def gaps(mid):
    d = load(mid)
    s = d.get("scores", {})
    return [fn for _, fn in ALL_BM if fn not in s or s[fn].get("error")]

def run_subprocess(mid, benchmark):
    """Run single benchmark via subprocess with timeout."""
    runner = os.path.join(REPO, "scripts/run_benchmark_bedrock.py")
    cmd = [PYTHON, runner, "--model", mid, "--benchmark", benchmark,
           "--output-dir", "/tmp/bench_tmp"]
    os.makedirs("/tmp/bench_tmp", exist_ok=True)
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=BM_TIMEOUT, cwd=REPO)
        dur = time.time() - t0
        # Parse from temp output
        tmp_file = os.path.join("/tmp/bench_tmp", mid.replace(':','_').replace('/','_') + '.json')
        if os.path.exists(tmp_file):
            tmp = json.load(open(tmp_file))
            if benchmark in tmp.get("scores", {}):
                entry = tmp["scores"][benchmark]
                entry["duration_s"] = round(dur, 1)
                return entry
        # Fallback: parse stdout
        for line in (proc.stdout or '').split('\n'):
            if 'Score:' in line:
                try:
                    sc = float(line.split('Score:')[1].strip())
                    return {"score": sc, "error": None, "duration_s": round(dur,1)}
                except: pass
        if proc.returncode != 0:
            err = (proc.stderr or '')[-200:].strip() or f"exit {proc.returncode}"
            return {"score": None, "error": err, "duration_s": round(dur,1)}
        return {"score": None, "error": "no score parsed", "duration_s": round(dur,1)}
    except subprocess.TimeoutExpired:
        return {"score": None, "error": f"timeout ({BM_TIMEOUT}s)", "duration_s": BM_TIMEOUT}

def main():
    t0 = time.time()
    total, ok = 0, 0
    for mid in MODEL_ORDER:
        if time.time()-t0 > MAX_TIME:
            print("⏰ Budget hit"); break
        g = gaps(mid)
        if not g:
            print(f"✅ {MODEL_CATALOG[mid][0]}: complete"); continue
        label = MODEL_CATALOG[mid][0]
        print(f"\n{'='*60}\n{label}: {len(g)} gaps\n{'='*60}")
        data = load(mid)
        for i, fn in enumerate(g):
            if time.time()-t0 > MAX_TIME:
                print("⏰ Budget hit"); break
            print(f"  [{i+1}/{len(g)}] {fn}...", end=" ", flush=True)
            r = run_subprocess(mid, fn)
            total += 1
            data["scores"][fn] = r
            save(mid, data)
            if r.get("error"):
                print(f"ERR ({r['duration_s']:.0f}s): {str(r['error'])[:60]}")
            else:
                print(f"{r['score']:.4f} ({r['duration_s']:.0f}s)")
                ok += 1
            time.sleep(2)
    
    print(f"\n{'='*60}\nDone: {total} run, {ok} ok, {total-ok} err ({time.time()-t0:.0f}s)\n{'='*60}")

if __name__ == "__main__":
    main()
