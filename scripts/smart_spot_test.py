#!/usr/bin/env python3
"""
Smart spot tester — rotates across Gemini models to maximize free-tier quota.

Free tier: 20 requests/day per model. With 4+ models, that's 80+ tests/day.
Run via cron every 72 seconds (20 req/day = ~1 per 72 sec per model).

Usage:
  .venv/bin/python3 scripts/smart_spot_test.py [--count N] [--delay SECS]
  
State persisted in scripts/.spot_test_state.json
Results appended to results/spot_test_results.jsonl
"""
import google.genai as genai
import os, json, time, sys, argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(REPO, "scripts/.spot_test_state.json")
RESULTS_FILE = os.path.join(REPO, "results/spot_test_results.jsonl")

# Models with separate daily quotas (20 req/day each)
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite", 
    "gemini-2.0-flash",
    "gemini-2.5-pro",
]

# Benchmark spot tests — each tests a specific cognitive ability
TESTS = [
    # CRT variants
    {"id": "crt-variant1", "track": "executive_functions", "construct": "response_inhibition",
     "prompt": "A notebook and a pen cost $2.20 in total. The notebook costs $2.00 more than the pen. How much does the pen cost? Give ONLY the dollar amount, nothing else.",
     "expected": "0.10", "accept": ["0.10", "$0.10", "0.1", "$0.1", "10 cents"],
     "trap": ["0.20", "$0.20", "0.2", "$0.2", "20 cents"]},
    
    {"id": "crt-variant2", "track": "executive_functions", "construct": "response_inhibition",
     "prompt": "In a lake, there is a patch of lily pads. Every day, the patch doubles in size. If it takes 60 days for the patch to cover the entire lake, how many days would it take for the patch to cover half of the lake? Give ONLY the number.",
     "expected": "59", "accept": ["59"], "trap": ["30"]},

    {"id": "crt-variant3", "track": "executive_functions", "construct": "response_inhibition",
     "prompt": "If 8 machines take 8 minutes to make 8 widgets, how many minutes would it take 100 machines to make 100 widgets? Give ONLY the number.",
     "expected": "8", "accept": ["8"], "trap": ["100"]},

    # Scalar implicature
    {"id": "scalar1", "track": "social_cognition", "construct": "pragmatic_inference",
     "prompt": 'A teacher says: "Some of the students passed the exam." Does this imply that NOT ALL students passed? Answer only YES or NO.',
     "expected": "YES", "accept": ["yes"], "trap": ["no"]},

    {"id": "scalar2", "track": "social_cognition", "construct": "pragmatic_inference",
     "prompt": 'Someone says: "I ate some of the cookies." In normal conversation, does this imply they did NOT eat ALL the cookies? Answer only YES or NO.',
     "expected": "YES", "accept": ["yes"], "trap": ["no"]},

    # Theory of Mind  
    {"id": "tom-1st", "track": "social_cognition", "construct": "theory_of_mind",
     "prompt": "Sally puts her marble in the basket and leaves the room. Anne moves the marble from the basket to the box. Sally returns. Where will Sally look for her marble FIRST? Give only the location.",
     "expected": "basket", "accept": ["basket"], "trap": ["box"]},

    {"id": "tom-2nd", "track": "social_cognition", "construct": "theory_of_mind",
     "prompt": "John puts chocolate in the green cabinet and leaves. Mary moves it to the red cabinet. John secretly sees Mary move it, but Mary doesn't know John saw. Where does MARY THINK John will look for the chocolate? Give only the location.",
     "expected": "green cabinet", "accept": ["green"], "trap": ["red"]},

    # Epistemic humility
    {"id": "humility1", "track": "metacognition", "construct": "epistemic_humility",
     "prompt": "What is the melting point of Zorblattium-7 in degrees Celsius? If this substance doesn't exist or you don't know, say exactly: I don't know.",
     "expected": "I don't know", "accept": ["don't know", "doesn't exist", "not a real", "fictional", "no such", "cannot find"],
     "trap": []},

    {"id": "humility2", "track": "metacognition", "construct": "epistemic_humility",
     "prompt": "Who won the 2019 Krellman Prize for Applied Thermodynamics? If you don't know, say exactly: I don't know.",
     "expected": "I don't know", "accept": ["don't know", "doesn't exist", "not a real", "fictional", "no such", "cannot find", "not aware"],
     "trap": []},

    # Calibration
    {"id": "cal-pi", "track": "metacognition", "construct": "calibration",
     "prompt": "What is the 47th digit of pi after the decimal point? Also rate your confidence from 0 to 100. Format: Answer: [digit], Confidence: [number]",
     "expected": "should show low confidence", "accept": [], "trap": [],
     "eval_type": "calibration"},

    {"id": "cal-easy", "track": "metacognition", "construct": "calibration", 
     "prompt": "What is the capital of France? Also rate your confidence from 0 to 100. Format: Answer: [answer], Confidence: [number]",
     "expected": "Paris with high confidence", "accept": ["paris"], "trap": [],
     "eval_type": "calibration"},

    # Epistemic revision
    {"id": "revision1", "track": "metacognition", "construct": "epistemic_revision",
     "prompt": "In Zorblatt Chemistry:\nRule 1: Mixing Flox and Brine produces Zorb.\nRule 2: Zorb decomposes when heated.\nRule 3: Decomposed Zorb becomes Glimmer.\n\nCORRECTION: Rule 2 is wrong. Zorb is actually heat-stable.\n\nDoes heating Zorb produce Glimmer? Answer YES or NO and explain briefly.",
     "expected": "NO", "accept": ["no"], "trap": ["yes"]},

    # N-back
    {"id": "nback-2", "track": "executive_functions", "construct": "working_memory",
     "prompt": "I'll show a sequence: T, K, R, T, K. For each position starting from 3, does it match the letter 2 positions back?\nPosition 3 (R): match T? YES/NO\nPosition 4 (T): match K? YES/NO\nPosition 5 (K): match R? YES/NO\nGive three answers separated by commas.",
     "expected": "NO, NO, NO", "accept": ["no, no, no", "no no no"], "trap": []},

    # Stroop
    {"id": "stroop1", "track": "attention", "construct": "selective_attention",
     "prompt": "The word 'GREEN' is printed in red ink. What COLOR is the INK (not the word)? Give only the color.",
     "expected": "red", "accept": ["red"], "trap": ["green"]},

    # Sarcasm
    {"id": "sarcasm1", "track": "social_cognition", "construct": "sarcasm_detection",
     "prompt": 'After waiting 3 hours at the DMV: "Well, that was quick!" Is this sarcastic? Answer YES or NO.',
     "expected": "YES", "accept": ["yes"], "trap": ["no"]},

    # Understatement
    {"id": "understatement1", "track": "social_cognition", "construct": "pragmatic_inference",
     "prompt": 'A billionaire says: "I\'ve done alright for myself." Is this an understatement? Answer YES or NO.',
     "expected": "YES", "accept": ["yes"], "trap": ["no"]},

    # Relevance implicature
    {"id": "relevance1", "track": "social_cognition", "construct": "pragmatic_inference",
     "prompt": 'A: "How\'s the new restaurant?" B: "Well, the parking is convenient." Is B implying the food is NOT good? Answer YES or NO.',
     "expected": "YES", "accept": ["yes"], "trap": ["no"]},

    # Set-shifting
    {"id": "wcst1", "track": "executive_functions", "construct": "set_shifting",
     "prompt": "Cards: A=Red Triangle, B=Blue Circle, C=Green Square.\nSort by COLOR: Blue Star → which card (A/B/C)?\nNow sort by SHAPE: Red Circle → which card (A/B/C)?\nFormat: COLOR: [letter], SHAPE: [letter]",
     "expected": "B, B", "accept": ["b, b", "b and b", "color: b", "b.*b"], "trap": []},

    # Planning (Tower of London)
    {"id": "plan1", "track": "executive_functions", "construct": "planning",
     "prompt": "You have 3 pegs (A, B, C). Peg A has a red ball on top and blue ball below. Peg B is empty. Peg C is empty. Goal: red on C, blue on B. Only move top ball. What is the minimum number of moves? Give ONLY the number.",
     "expected": "3", "accept": ["3", "three"], "trap": ["2"]},
]

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"model_index": 0, "test_index": 0, "daily_counts": {}, "last_reset": ""}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def append_result(result):
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, 'a') as f:
        f.write(json.dumps(result) + '\n')

def evaluate(test, response_text):
    text_lower = response_text.lower()
    
    got_intended = any(p.lower() in text_lower for p in test.get("accept", []))
    got_trap = any(p.lower() in text_lower for p in test.get("trap", []))
    
    if test.get("eval_type") == "calibration":
        # Extract confidence number
        import re
        conf_match = re.search(r'confidence[:\s]*(\d+)', text_lower)
        confidence = int(conf_match.group(1)) if conf_match else None
        return {"type": "calibration", "confidence": confidence, "response": response_text[:300]}
    
    return {
        "correct": got_intended and not got_trap,
        "got_intended": got_intended,
        "fell_for_trap": got_trap,
        "response": response_text[:300]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1, help="Number of tests to run")
    parser.add_argument("--delay", type=int, default=5, help="Seconds between requests")
    args = parser.parse_args()

    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    state = load_state()
    
    # Reset daily counts if new day
    today = time.strftime("%Y-%m-%d")
    if state.get("last_reset") != today:
        state["daily_counts"] = {}
        state["last_reset"] = today
    
    ran = 0
    for _ in range(args.count):
        # Find a model with quota remaining
        model = None
        for attempt in range(len(MODELS)):
            candidate = MODELS[(state["model_index"] + attempt) % len(MODELS)]
            if state["daily_counts"].get(candidate, 0) < 18:  # leave 2 buffer
                model = candidate
                state["model_index"] = (state["model_index"] + attempt + 1) % len(MODELS)
                break
        
        if model is None:
            print("All models exhausted for today.")
            break
        
        test = TESTS[state["test_index"] % len(TESTS)]
        state["test_index"] = (state["test_index"] + 1) % len(TESTS)
        
        print(f"[{model}] Testing: {test['id']} ({test['construct']})...")
        
        try:
            resp = client.models.generate_content(model=model, contents=test["prompt"])
            answer = resp.text.strip()
            
            eval_result = evaluate(test, answer)
            result = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model": model,
                "test_id": test["id"],
                "track": test["track"],
                "construct": test["construct"],
                "expected": test["expected"],
                **eval_result
            }
            
            state["daily_counts"][model] = state["daily_counts"].get(model, 0) + 1
            append_result(result)
            
            status = "✓" if eval_result.get("correct") else ("📊" if eval_result.get("type") == "calibration" else "✗")
            print(f"  {status} Response: {answer[:100]}")
            ran += 1
            
        except Exception as e:
            err = str(e)
            if "429" in err:
                print(f"  ⚠ Rate limited on {model}, marking exhausted")
                state["daily_counts"][model] = 20
            else:
                print(f"  ❌ Error: {err[:100]}")
        
        save_state(state)
        
        if ran < args.count:
            time.sleep(args.delay)
    
    print(f"\nRan {ran}/{args.count} tests. Daily usage: {json.dumps(state['daily_counts'])}")
    
    # Print summary of all results
    if os.path.exists(RESULTS_FILE):
        results = []
        with open(RESULTS_FILE) as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))
        
        if results:
            correct = sum(1 for r in results if r.get("correct"))
            total = sum(1 for r in results if "correct" in r)
            cal = sum(1 for r in results if r.get("type") == "calibration")
            print(f"\nAll-time results: {correct}/{total} correct + {cal} calibration tests")
            
            # By model
            by_model = {}
            for r in results:
                m = r["model"]
                if m not in by_model:
                    by_model[m] = {"correct": 0, "total": 0}
                if "correct" in r:
                    by_model[m]["total"] += 1
                    if r["correct"]:
                        by_model[m]["correct"] += 1
            for m, d in sorted(by_model.items()):
                print(f"  {m}: {d['correct']}/{d['total']}")

if __name__ == "__main__":
    main()
