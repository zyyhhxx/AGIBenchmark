# AGI Benchmark Goals — Phase 2 (Post-Submission QA)

> Updated: 2026-04-13

Phase 1 (notebook creation, Kaggle upload, initial model runs) is complete.
Phase 2 focuses on rigorous validation before finalizing writeups and results.

---

## Step 1: Full Model Evaluation (10 models × 26 benchmarks)

Run all benchmarks against the 10 local models, **one benchmark at a time** to pace LLM calls and avoid rate limits.

**Requirements:**
- Every question and response for all models must be **recorded** (full Q&A logs, not just scores)
- After each benchmark completes across all models, **review**:
  - Scores and distributions (do they spread? ceiling/floor effects?)
  - The actual Q&A transcripts — do model responses match what the scoring function rewards/penalizes?
  - Edge cases: are there questions where the "correct" answer is debatable?
  - Parsing issues: do any models' responses fail to parse correctly, inflating/deflating scores?

**Models:**
1. Claude Opus 4.6
2. Claude Sonnet 4.6
3. DeepSeek-R1
4. GPT-OSS-120B
5. Llama 3.3 70B
6. Llama 4 Maverick 17B
7. Nova Pro
8. Ministral 3B
9. Qwen3 Next 80B
10. GLM 4.7

**Order:** Run one benchmark at a time across all 10 models before moving to the next.

---

## Step 2: Per-Benchmark Analysis

For each of the 26 benchmarks, write an analysis covering:

1. **Score distribution** — mean, std, range, ceiling/floor effects
2. **Model discrimination** — does the benchmark separate models meaningfully?
3. **Q&A review findings** — specific examples of:
   - Correct scoring (model got it right, score reflects it)
   - Incorrect scoring (model gave a reasonable answer but scored 0, or vice versa)
   - Parsing artifacts (structured output failures, think-tag issues, etc.)
4. **Ground truth validity** — are the "correct" answers actually correct? Any debatable items?
5. **Recommendation** — keep as-is, revise items, adjust scoring, or drop

---

## Step 3: Improvement Plans

Based on Step 2 findings, write an improvement plan **per track**:

- **Attention** (4 benchmarks)
- **Executive Functions** (5 benchmarks)
- **Learning** (4 benchmarks)
- **Metacognition** (9 benchmarks)
- **Social Cognition** (4 benchmarks)

Each plan should cover:
- Which benchmarks need item revision, scoring changes, or removal
- Priority order (fix high-impact issues first)
- Estimated effort per fix
- Whether re-running models is needed after fixes

---

## Step 4: Execute Improvement Plans

Implement the fixes identified in Step 3, track by track.

**For each fix:**
- Document what was changed and why (link to Step 2 analysis)
- Record before/after: old scoring behavior vs new
- If items were revised, added, or removed — note the diff
- If scoring logic changed — explain the rationale
- If re-running models is required — re-run and compare old vs new scores

**Deliverable per track:** An `IMPROVEMENT_LOG.md` in each track's writeup directory documenting:
- Actions taken
- Items changed (with IDs)
- Scoring changes (with formulas)
- Re-run results (if applicable)
- Remaining known limitations

---

## Known Issues to Address

- **Retry bias**: 18/26 notebooks give thinking models a retry advantage (see `docs/RETRY_BIAS_ISSUE.md`). Fix all before re-running.
- **Stale writeup data**: Writeup audit found 23 issues (see `docs/writeup_audit.txt`). Fix after Step 2 analysis is complete.
