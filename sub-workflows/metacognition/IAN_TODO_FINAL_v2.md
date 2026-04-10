# 🚨 IAN'S FINAL SUBMISSION CHECKLIST v2
**Updated:** 2026-04-10 | **Deadline: April 16, 2026 (6 days left)**

---

## Competition Submission Requirements (from Kaggle)

The competition requires **three deliverables**:

1. **A Kaggle Benchmark** (collection of tasks) on the Community Benchmarks platform
2. **A discussion thread writeup** linked to the benchmark, covering:
   - Problem Statement
   - Task & benchmark construction
   - Dataset provenance, columns, and data types
   - Technical details
   - Results, insights, and conclusions
   - Organizational affiliations
   - References & citations
3. **Model results** — benchmarks run against models via the CB platform ($50/day, $500/month quota)

---

## Status Summary

| Area | Status |
|------|--------|
| Benchmarks implemented (code) | ✅ 29/29 complete |
| Notebooks validated (syntax) | ✅ 31/31 pass |
| Notebooks uploaded to Kaggle | ⚠️ ~26 uploaded, many still private |
| CB tasks registered | ❌ Not started |
| CB benchmark collection created | ❌ Not started |
| Discussion thread posted | ✅ Done (needs benchmark link update) |
| Models run on CB platform | ✅ 17 models run |
| Writeup (SUBMISSION_NARRATIVE.md) | ✅ Complete with citations |

---

## MUST-DO (Blocks Submission)

### 1. Make ALL notebooks public (~10 min)
**Why:** Notebooks must be public before they can be registered as CB tasks.

Per `KAGGLE_KERNELS.md`, these are still **private**:
- Error Detection, Error Det Sub-metrics
- Learning Monitoring, Metacognitive Control, Epistemic Revision
- Vigilance, Divided Attention, Instruction Update
- Task Switching, N-Back, WCST, Tower of London
- False Belief ToM, Sarcasm Detection

Plus the 6 rate-limited ones from `IAN_TODO_FINAL.md`:
- Epistemic Humility, FOK, FOK Sub-metrics, JOL, JOL Sub-metrics, Error Detection Sub-metrics

**Action:** Go to each notebook → Settings → Make Public → Save.
~20 notebooks need toggling. Budget 10 min.

### 2. Delete ghost notebooks (~10 min)
**Why:** ~70 ghost entries from API retry storms clutter the code page and may confuse CB task creation.

**Action:** https://www.kaggle.com/ianstudy/code → delete any "[Private Notebook]", blank, or duplicate entries.

### 3. Register all benchmarks as CB tasks (~60 min)
**Why:** This IS the submission. Without CB tasks, there is no entry.

**Action for each of 26–29 notebooks:**
1. Go to https://www.kaggle.com/benchmarks → "+ Create" → "Create Task"
2. Copy-paste all code cells from corresponding `repo/notebooks/*.ipynb`
3. Run the notebook — `@kbench.task` decorator auto-registers
4. Verify task appears on benchmarks page

See `IAN_TODO_FINAL.md` Phase 3 for the full notebook-by-notebook table (still accurate).

### 4. Create the Benchmark collection (~5 min)
**Why:** Tasks must be grouped into a Benchmark for submission.

**Action:**
1. https://www.kaggle.com/benchmarks/new
2. Name: **"Cognitive Abilities Benchmark Suite — Measuring AGI"**
3. Add all 26 core tasks (or all 29 including sub-metrics)
4. Paste description from `repo/SUBMISSION_NARRATIVE.md` Section 1 (Overview)

### 5. Update discussion thread with benchmark link (~2 min)
**Why:** The writeup must link to the benchmark. Discussion thread is already posted but has a `[link to CB benchmark]` placeholder.

**Action:** Edit the existing discussion post → replace placeholder with actual benchmark URL from step 4.

---

## SHOULD-DO (Improves Score)

### 6. Verify writeup covers all required sections (~15 min)
`SUBMISSION_NARRATIVE.md` is the writeup. Cross-check it has:

| Required Section | Status | Notes |
|-----------------|--------|-------|
| Problem Statement | ✅ Section 1 | Clear framing |
| Task & benchmark construction | ✅ Section 2 | All 29 tasks described |
| Dataset provenance/columns/types | ⚠️ Weak | Add a section on data sources — procedural generators, trivia sources, stimuli provenance |
| Technical details | ✅ Sections 5, 8 | Scoring, contamination hardening |
| Results, insights, conclusions | ✅ Section with Claude results | Could add more models if CB platform results are available |
| Organizational affiliations | ❌ Missing | Add a brief line (independent researcher, university, etc.) |
| References & citations | ✅ 20+ references | Strong |

**Action:** Add a "Dataset" section describing stimuli provenance (procedural generators, trivia sources). Add organizational affiliation. ~15 min.

### 7. Add more CB model results to writeup (~10 min)
**Why:** "Results, insights, and conclusions" is a scored section. Currently only Claude Sonnet results are documented.

**Action:** After CB platform runs complete (step 3), pull results for Gemini, Llama, DeepSeek etc. and add a cross-model comparison table to the narrative. This is what makes the writeup compelling.

### 8. Polish discussion thread for upvotes (~10 min)
**Why:** Community upvotes count for **15% of final score**.

**Action:** After benchmark is live, edit discussion post to include:
- Actual model results (not just Claude)
- A compelling visualization or table
- Invite discussion/feedback

---

## NICE-TO-HAVE (Won't Block, Minor Improvement)

### 9. Create per-track sub-benchmarks (~15 min)
Instead of one 29-task benchmark, create 5 track-specific benchmarks (metacognition, learning, attention, exec functions, social cognition). Makes the cognitive profile structure more visible to judges.

### 10. Fix known code issues (~20 min)
From `NOTEBOOK_AUDIT.md`:
- `attention_vigilance` missing `normalize` in scoring
- `exec_func_tol` has no detected scoring pattern
- Gamma function duplicated 7× across metacog files (extract to shared module)

These don't block submission but could cause unexpected scores on the CB platform.

### 11. Clean up repo root JSON artifacts (~5 min)
47 `.task.json` and `.run.json` files at repo root. Cosmetic cleanup.

---

## Recommended Order of Operations

| Step | What | Est. Time | Priority |
|------|------|-----------|----------|
| 1 | Delete ghost notebooks | 10 min | MUST |
| 2 | Make all notebooks public | 10 min | MUST |
| 3 | Register 26–29 CB tasks | 60 min | MUST |
| 4 | Create benchmark collection | 5 min | MUST |
| 5 | Update discussion thread link | 2 min | MUST |
| 6 | Add dataset section + affiliation to writeup | 15 min | SHOULD |
| 7 | Update writeup with CB model results | 10 min | SHOULD |
| 8 | Polish discussion for upvotes | 10 min | SHOULD |
| | **Total MUST-DO** | **~87 min** | |
| | **Total with SHOULD-DO** | **~122 min** | |

---

## Quick Verification After Submission

- [ ] All 26+ tasks visible at https://www.kaggle.com/benchmarks (under your profile)
- [ ] Benchmark collection exists and contains all tasks
- [ ] At least 1 model run triggered and completed on CB
- [ ] Discussion thread has working benchmark link
- [ ] Discussion thread has real model results (not just placeholder)
- [ ] Writeup covers all 7 required sections (problem, construction, dataset, technical, results, affiliation, references)
