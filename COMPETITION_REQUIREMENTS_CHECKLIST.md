# Competition Requirements Checklist
**Generated:** 2026-04-10 | **Deadline:** April 16, 2026

## Competition Requirements (from Kaggle overview page)

The competition requires **three deliverables**:
1. **A Kaggle Benchmark** (collection of CB tasks)
2. **A discussion thread writeup** with 7 required sections
3. **Model results** run via CB platform

**Scoring:** 85% expert judges + 15% community upvotes

---

## Deliverable 1: Kaggle Benchmark (CB Tasks)

| Requirement | Status | Notes |
|-------------|--------|-------|
| CB tasks registered on platform | ❌ MISSING | No tasks registered yet — BLOCKS submission |
| Benchmark collection created | ❌ MISSING | Must group tasks into a collection |
| Tasks use `@kbench.task` decorator | ✅ PRESENT | All 29 notebooks have decorators |
| Tasks are self-contained notebooks | ✅ PRESENT | All validated via `nbconvert` |
| Notebooks are public on Kaggle | ⚠️ WEAK | ~20 still private; must toggle before CB registration |
| Ghost notebooks cleaned up | ❌ MISSING | ~70 ghost entries need deletion |

## Deliverable 2: Discussion Thread Writeup (7 Required Sections)

### Cross-reference: SUBMISSION_NARRATIVE.md

| Required Section | Status | Location in Narrative | Quality |
|-----------------|--------|----------------------|---------|
| **Problem Statement** | ✅ PRESENT | Section 1 (Overview) | Strong — clear framing of cognitive abilities gap |
| **Task & benchmark construction** | ✅ PRESENT | Section 2 (Track Summaries) + Section 3 (Design Principles) | Strong — all 29 tasks described with rationale |
| **Dataset provenance, columns, data types** | ✅ PRESENT | Section 4 (Dataset Design & Provenance) | **Fixed** — includes provenance, item schema, response schemas, licensing |
| **Technical details** | ✅ PRESENT | Section 6 (Technical Implementation) + Section 3 (Design Principles) | Good — SDK, scoring, contamination hardening |
| **Results, insights, conclusions** | ✅ PRESENT | Section 7 (full results) | **Strong** — Claude Sonnet 4 full suite + 10-model cross-validation + Gemini spot tests |
| **Organizational affiliations** | ✅ PRESENT | Section 10 | **Fixed** — "Independent submission" |
| **References & citations** | ✅ PRESENT | Section 9 | Strong — 20+ references, all cited in text |

### Cross-reference: KAGGLE_DISCUSSION_DRAFT.md

| Required Section | Status | Notes |
|-----------------|--------|-------|
| Problem Statement | ✅ PRESENT | "The Problem with Current Benchmarks" section |
| Task & benchmark construction | ✅ PRESENT | Track overview table + spotlight benchmarks |
| Dataset provenance | ⚠️ WEAK | Mentions procedural generation but no schema/column details |
| Technical details | ✅ PRESENT | SDK, scoring, contamination |
| Results, insights, conclusions | ✅ PRESENT | Cross-model results section with tables |
| Organizational affiliations | ❌ MISSING | Not in discussion draft |
| References & citations | ✅ PRESENT | Listed at bottom |
| Benchmark link | ⚠️ PLACEHOLDER | `[link to CB benchmark]` needs replacement |

## Deliverable 3: Model Results

| Requirement | Status | Notes |
|-------------|--------|-------|
| At least 1 model run on CB platform | ✅ PRESENT | 17 models run (per IAN_TODO_v2) |
| Results documented in writeup | ✅ PRESENT | 10-model × 26-benchmark score matrix in SUBMISSION_NARRATIVE |
| Cross-model comparison | ✅ PRESENT | Three-tier pattern, discriminatory power analysis |

## Deliverable 4: Community Engagement (15% of score)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Discussion thread posted | ✅ PRESENT | Already posted |
| Thread is compelling/polished | ⚠️ WEAK | Good content but needs: actual benchmark link, organizational affiliation |
| Invites discussion/feedback | ✅ PRESENT | Ends with call-to-action |
| Cross-model results included | ✅ PRESENT | 10-model findings section |

---

## Summary

| Category | Present | Missing | Weak |
|----------|---------|---------|------|
| CB Platform | 2 | 4 | 0 |
| Narrative (7 sections) | 7 | 0 | 0 |
| Discussion Draft (7 sections) | 5 | 1 | 1 |
| Model Results | 3 | 0 | 0 |
| Community Engagement | 3 | 0 | 1 |
| **Total** | **20** | **5** | **2** |

---

## Action Items

### CRITICAL (Blocks Submission)
1. **Register CB tasks** — Ian must register 26–29 tasks on Kaggle Benchmarks platform (~60 min)
2. **Create benchmark collection** — Group all tasks into a Benchmark (~5 min)
3. **Make all notebooks public** — ~20 notebooks still private (~10 min)
4. **Delete ghost notebooks** — ~70 ghost entries cluttering code page (~10 min)

### HIGH (Affects Score)
5. **Add organizational affiliation to discussion draft** — Add "Independent submission" line
6. **Replace benchmark link placeholder** — Update `[link to CB benchmark]` in discussion thread
7. **Add dataset schema details to discussion draft** — Brief mention of item schema (id, question, answer, confidence fields) for completeness

### MEDIUM (Polish)
8. **Consider adding dataset provenance summary to discussion draft** — The narrative has full details (Section 4) but the discussion post only mentions procedural generation in passing
9. **Engage with community** — Reply to comments, upvote other good submissions, participate in discussions to build visibility

### LOW (Won't Block)
10. **Fix flagged benchmarks** — attention_vigilance (ceiling), exec_func_tol (scoring), canary (floor)
11. **Clean up repo root JSON artifacts** — 47 `.task.json` / `.run.json` files

---

## Previously Flagged Items (from KNOWLEDGE.md)

| Item | Status |
|------|--------|
| Dataset provenance section missing | ✅ **FIXED** — Section 4 added to SUBMISSION_NARRATIVE.md |
| Organizational affiliation missing | ✅ **FIXED** — Section 10 added to SUBMISSION_NARRATIVE.md ("Independent submission") |
| Discussion draft polish for upvotes | ⚠️ Needs benchmark link + affiliation added |

---

*All critical path items are Ian-manual actions on the Kaggle web UI. Estimated total: ~87 min for MUST-DO items.*
