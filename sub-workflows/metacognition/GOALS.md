# GOALS.md — AGI Benchmark Hackathon (Final Submission)

## Active Goal
Submit **5 writeups** (one per track) to maximize prize chances. Deadline: **April 16, 2026** (11:59 PM UTC).

## ⛔ Hard Rules
- **DO NOT upload notebooks to Kaggle using the CLI or API.** Let the human handle all Kaggle uploads manually via the web UI.
- **Each writeup must not exceed 1,500 words.** Follow the required template exactly.
- **All notebooks MUST be self-contained.** No `from data.*` imports — data must be inlined in the notebook. Kaggle has no access to local modules.
- **No duplicate execution.** Each notebook must have exactly ONE `@kbench.task` definition and ONE `.run()` call. `if __name__ == "__main__"` guards do NOT work in Jupyter — `__name__` is always `"__main__"`.
- **Task docstrings must be < 255 characters.** Kaggle truncates task descriptions longer than 255 chars. Check ALL `@kbench.task` decorated functions.
- **Task names must be meaningful human-readable titles.** Not snake_case identifiers. E.g. "Contamination Canary" not "metacog_canary".
- Note: Rules say "one (1) Submission per Team" for Hackathons — unclear if per-track or total. Ian will verify on Kaggle whether multiple writeups are allowed. Plan for 5, fall back to 1 (metacognition) if restricted.

## Submission Requirements (from competition rules, verified 2026-04-11)

Full rules saved in `repo/COMPETITION_RULES.md`.

A valid submission = **Kaggle Writeup** + **attached Kaggle Benchmark**

### Kaggle Writeup
- Created via **"New Writeup"** button (NOT a Discussion post)
- Must select a **Track**
- ≤1,500 words — submissions over this limit may be penalized
- Must include a **cover image** (required to submit)
- Must click **"Submit"** button — drafts don't count
- Required template:
  ```
  ### Project Name
  ### Your Team
  ### Problem Statement
  ### Task & benchmark construction
  ### Dataset
  ### Technical details
  ### Results, insights, and conclusions
  ### Organizational affiliations
  ### References & citations
  ```

### Kaggle Benchmark (attached to writeup)
- Benchmark + tasks set to **private** (auto-publish after deadline)
- Attached via "Attachments" → "Add a link" → select benchmark

### Evaluation Criteria
| Criteria | Weight |
|----------|--------|
| Dataset quality & task construction | **50%** |
| Writeup quality | **20%** |
| Novelty, insights, discriminatory power | **30%** |

### Prizes
- 4 × $25,000 grand prizes (best across all tracks)
- 2 × $10,000 per track (14 unique winners total, no repeats)

---

## 🔴 PRIORITY 1: Notebook Consistency & Quality (ALL tracks)

These items apply to ALL 26+ notebooks across all 5 tracks. Complete before any other work.

### 1. Notebook implementations must match .py source files
- For every `benchmarks/<track>/task_*.py`, verify the corresponding `notebooks/*.ipynb` has identical task logic
- If the .py was updated (new items, new prompts, new scoring), the notebook MUST be updated to match
- Pay special attention to: canary (v3 items + new confidence prompt), calibration (v2 questions), error_detection (recently fixed)

### 2. No double benchmark runs in notebooks
- Each notebook must have exactly ONE `.run()` call
- Check ALL notebooks: `grep -c ".run("` in each code cell
- Common bug: `.run()` at end of task definition cell AND in a separate run cell
- The task .py files may have `task.run(llm=kbench.llm)` at module level — this must NOT appear in the notebook version

### 3. Task names must be meaningful human-readable titles
- All `@kbench.task(name=...)` must use human-readable names, not snake_case
- E.g. "Contamination Canary" not "metacog_canary", "Wisconsin Card Sorting" not "exec_func_wcst"
- Check BOTH .py files AND notebooks — they must match
- This was done on 2026-04-12 but verify no regressions from later commits

### 4. Task docstrings must be < 255 characters
- Kaggle truncates the `description` field (taken from the docstring under `@kbench.task`)
- Check ALL task functions across all tracks — count characters in the docstring
- If over 255, shorten to a concise single-sentence description
- This applies to both .py files and inlined notebook code

---

## 🔴 PRIORITY 2: Metacognition Architecture Improvements

These were identified in 2026-04-12 architectural review but NOT addressed by the previous workflow run.

### Canary → Demote to Pass/Fail Gate (NOT DONE)
- Canary measures factuality detection, not true metacognition
- All frontier models score ~0.99 — no discrimination at the top
- **Action:** Reframe in writeup as a pass/fail contamination gate, not a scored metacognitive benchmark
- Update `WRITEUP_METACOGNITION.md` to describe canary as infrastructure/validation, not a core benchmark
- The fabrication-detection construct is subsumed by Calibration + Epistemic Humility

### Error Detection → Redesign Harder (NOT DONE — only std tuned)
- std was raised from 0.077 → 0.097 via parameter tuning, but architectural changes were NOT made
- **Action:** Add subtle errors (locally valid but globally inconsistent), clean chains with NO errors (tests false positive rate), multi-error chains (0/1/2/3 errors)
- Update both .py and notebook

### Epistemic Revision → Redesign Harder (NOT DONE)
- std=0.102 passes threshold, but no deeper redesign was done
- **Action:** Add ambiguous evidence, conflicting sources with different reliability, cases where NOT revising is correct
- Tests genuine belief evaluation vs. reflexive compliance

### Learning Monitoring → Redesign or Merge (NOT DONE)
- std=0.081 barely passes, overlaps with JOL
- **Action:** If time permits, redesign with adversarial learning material + interference tasks. Otherwise merge into JOL and drop as separate benchmark.

### NEW: Ease of Learning (EOL) — Stretch Goal
- Biggest gap in Nelson & Narens monitoring timeline (pre-encoding monitoring)
- Present tasks of varying difficulty, model predicts difficulty BEFORE engaging, score prediction accuracy
- **Action:** Implement only if all Priority 1 and 2 items are done

---

## 🟡 PRIORITY 3: Writeup Polish

- Update all 5 writeups to reflect any benchmark changes made in Priority 1-2
- Ensure canary is reframed as gate in metacognition writeup
- Verify all writeups are ≤ 1,500 words
- Verify all cover images exist

---

## Target Models (Amazon Bedrock)
| # | Model | Model ID |
|---|-------|----------|
| 1 | Claude Opus 4.6 | anthropic.claude-opus-4-6-v1 |
| 2 | Claude Sonnet 4.6 | anthropic.claude-sonnet-4-6-v1 |
| 3 | DeepSeek-R1 | deepseek.r1-v1:0 |
| 4 | GLM 4.7 | zai.glm-4.7 |
| 5 | GPT-OSS-120B | openai.gpt-oss-120b-1:0 |
| 6 | Llama 3.3 70B | meta.llama3-3-70b-instruct-v1:0 |
| 7 | Llama 4 Maverick 17B | meta.llama4-maverick-17b-instruct-v1:0 |
| 8 | Ministral 3B | mistral.ministral-3-3b-instruct |
| 9 | Nova Pro | amazon.nova-pro-v1:0 |
| 10 | Qwen3 Next 80B | qwen.qwen3-next-80b-a3b |

## Competition Timeline
- March 17, 2026 — Start
- **April 16, 2026** — Final Submission Deadline (11:59 PM UTC)
- April 17 – May 31, 2026 — Judging Period
- June 1, 2026 — Anticipated Results
