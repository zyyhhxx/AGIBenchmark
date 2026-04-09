#!/usr/bin/env python3
"""
Drip-feed spot tester — runs ONE test per invocation, rotating models.
Designed to be called by cron every 5 minutes.
With 4 models × 18 tests/day = 72 tests/day, covering all 20 test items.

Usage: .venv/bin/python3 scripts/drip_spot_test.py
"""
import google.genai as genai
import os, json, time, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

STATE_FILE = os.path.join(REPO, "scripts/.drip_test_state.json")
RESULTS_FILE = os.path.join(REPO, "results/spot_test_results.jsonl")

MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.5-pro",
]

TESTS = [
    {"id": "crt-v1", "track": "exec_func", "prompt": "A notebook and a pen cost $2.20 in total. The notebook costs $2.00 more than the pen. How much does the pen cost? Give ONLY the dollar amount.", "accept": ["0.10", "$0.10", "0.1"], "trap": ["0.20", "$0.20"]},
    {"id": "crt-v2", "track": "exec_func", "prompt": "In a lake, lily pads double daily. 60 days to cover the lake. How many days to cover half? Give ONLY the number.", "accept": ["59"], "trap": ["30"]},
    {"id": "crt-v3", "track": "exec_func", "prompt": "If 8 machines take 8 minutes to make 8 widgets, how many minutes for 100 machines to make 100 widgets? Give ONLY the number.", "accept": ["8"], "trap": ["100"]},
    {"id": "scalar1", "track": "social_cog", "prompt": 'Teacher says: "Some students passed." Does this imply NOT ALL passed? Answer YES or NO only.', "accept": ["yes"], "trap": ["no"]},
    {"id": "scalar2", "track": "social_cog", "prompt": '"I ate some cookies." In conversation, implies NOT ALL were eaten? YES or NO only.', "accept": ["yes"], "trap": ["no"]},
    {"id": "tom-1st", "track": "social_cog", "prompt": "Sally puts marble in basket, leaves. Anne moves marble to box. Sally returns. Where does Sally look first? One word.", "accept": ["basket"], "trap": ["box"]},
    {"id": "tom-2nd", "track": "social_cog", "prompt": "John puts chocolate in green cabinet, leaves. Mary moves to red cabinet. John secretly sees but Mary doesn't know he saw. Where does MARY THINK John will look? One word/color.", "accept": ["green"], "trap": ["red"]},
    {"id": "humility1", "track": "metacog", "prompt": "What is the melting point of Zorblattium-7 in Celsius? If unknown, say 'I don't know'.", "accept": ["don't know", "doesn't exist", "not real", "fictional", "no such"], "trap": []},
    {"id": "humility2", "track": "metacog", "prompt": "Who won the 2019 Krellman Prize for Applied Thermodynamics? If unknown, say 'I don't know'.", "accept": ["don't know", "doesn't exist", "not real", "no such", "not aware"], "trap": []},
    {"id": "revision1", "track": "metacog", "prompt": "Rules: Flox+Brine→Zorb. Zorb decomposes when heated. Decomposed Zorb→Glimmer. CORRECTION: Zorb is heat-stable. Does heating Zorb produce Glimmer? YES or NO.", "accept": ["no"], "trap": ["yes"]},
    {"id": "stroop1", "track": "attention", "prompt": "The word 'GREEN' is printed in red ink. What color is the INK? One word.", "accept": ["red"], "trap": ["green"]},
    {"id": "sarcasm1", "track": "social_cog", "prompt": 'After 3 hours at DMV: "Well, that was quick!" Sarcastic? YES or NO.', "accept": ["yes"], "trap": ["no"]},
    {"id": "understate1", "track": "social_cog", "prompt": 'Billionaire: "I\'ve done alright for myself." Understatement? YES or NO.', "accept": ["yes"], "trap": ["no"]},
    {"id": "relevance1", "track": "social_cog", "prompt": '"How\'s the restaurant?" "The parking is convenient." Implying food is NOT good? YES or NO.', "accept": ["yes"], "trap": ["no"]},
    {"id": "plan1", "track": "exec_func", "prompt": "3 pegs A,B,C. A has red(top) and blue(bottom). Goal: red on C, blue on B. Move only top ball. Minimum moves? Number only.", "accept": ["3"], "trap": ["2"]},
    {"id": "nback2", "track": "exec_func", "prompt": "Sequence: T,K,R,T,K. 2-back test from position 3: Does R match T(pos1)? Does T match K(pos2)? Does K match R(pos3)? Three YES/NO answers, comma-separated.", "accept": ["no, no, no", "no,no,no"], "trap": []},
    {"id": "cal-hard", "track": "metacog", "prompt": "What is 347×283? Also rate confidence 0-100. Format: Answer: [num], Confidence: [num]", "accept": [], "trap": [], "eval": "calibration", "correct_answer": "98201"},
    {"id": "wcst1", "track": "exec_func", "prompt": "Cards: A=Red Triangle, B=Blue Circle, C=Green Square. Sort by COLOR: Blue Star→? Then by SHAPE: Red Circle→? Two letters.", "accept": ["b, b", "b b", "b,b"], "trap": []},
    {"id": "irony1", "track": "social_cog", "prompt": 'Student gets F: "Another academic triumph!" What do they actually mean? Literal success or sarcastic failure?', "accept": ["sarcas", "fail", "ironic", "opposite", "badly"], "trap": ["success", "triumph"]},
    {"id": "fok1", "track": "metacog", "prompt": "Rate your confidence (0-100) BEFORE answering: What is the remainder when 847 is divided by 13? Format: Confidence: [num], Answer: [num]", "accept": [], "trap": [], "eval": "calibration", "correct_answer": "2"},
]

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"model_idx": 0, "test_idx": 0, "counts": {}, "day": ""}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def main():
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    state = load_state()
    today = time.strftime("%Y-%m-%d")
    if state.get("day") != today:
        state["counts"] = {}
        state["day"] = today

    # Find available model
    model = None
    for i in range(len(MODELS)):
        m = MODELS[(state["model_idx"] + i) % len(MODELS)]
        if state["counts"].get(m, 0) < 18:
            model = m
            state["model_idx"] = (state["model_idx"] + i + 1) % len(MODELS)
            break
    if not model:
        print("All models exhausted today.")
        save_state(state)
        return

    test = TESTS[state["test_idx"] % len(TESTS)]
    state["test_idx"] = (state["test_idx"] + 1) % len(TESTS)

    print(f"[{model}] {test['id']}...", end=" ")
    try:
        resp = client.models.generate_content(model=model, contents=test["prompt"])
        answer = resp.text.strip()
        state["counts"][model] = state["counts"].get(model, 0) + 1

        text_lower = answer.lower()
        if test.get("eval") == "calibration":
            import re
            conf = re.search(r'confidence[:\s]*(\d+)', text_lower)
            ans = re.search(r'answer[:\s]*(\d+)', text_lower)
            result = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model": model, "test_id": test["id"], "track": test["track"],
                "type": "calibration",
                "confidence": int(conf.group(1)) if conf else None,
                "model_answer": ans.group(1) if ans else answer[:100],
                "correct_answer": test.get("correct_answer"),
                "correct": (ans.group(1) == test["correct_answer"]) if ans and test.get("correct_answer") else None,
                "raw": answer[:200]
            }
        else:
            got = any(p.lower() in text_lower for p in test["accept"])
            trap = any(p.lower() in text_lower for p in test["trap"]) if test["trap"] else False
            result = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model": model, "test_id": test["id"], "track": test["track"],
                "correct": got and not trap, "got_intended": got, "fell_for_trap": trap,
                "raw": answer[:200]
            }

        os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
        with open(RESULTS_FILE, 'a') as f:
            f.write(json.dumps(result) + '\n')

        status = "✓" if result.get("correct") else ("📊" if result.get("type") == "calibration" else "✗")
        print(f"{status} {answer[:80]}")
    except Exception as e:
        if "429" in str(e):
            state["counts"][model] = 20
            print(f"⚠ 429 - model exhausted")
        else:
            print(f"❌ {str(e)[:80]}")

    save_state(state)

    # Summary
    if os.path.exists(RESULTS_FILE):
        lines = open(RESULTS_FILE).readlines()
        correct = sum(1 for l in lines if '"correct": true' in l)
        total = sum(1 for l in lines if '"correct":' in l and '"type": "calibration"' not in l)
        print(f"Running total: {correct}/{total} correct ({len(lines)} total tests)")

if __name__ == "__main__":
    main()
