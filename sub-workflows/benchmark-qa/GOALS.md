# AGI Benchmark Goals — Phase 2 (Post-Submission QA)

> Updated: 2026-04-14

Phase 1 (notebook creation, Kaggle upload, initial model runs) is complete.
Phase 2 focuses on rigorous validation before finalizing writeups and results.

**Metacognition track (9 benchmarks): COMPLETE.** Full QA cycle done — see KNOWLEDGE and archived IMPROVEMENT_LOG.md.

## Remaining Work: 4 Tracks × 3 Tasks Per Benchmark

For each of the 17 remaining benchmarks across 4 tracks, create exactly 3 tasks:

### Attention (4 benchmarks)
- `attention_divided`
- `attention_selective`
- `attention_vigilance`
- `attention_instruction_update`

### Executive Functions (5 benchmarks)
- `exec_func_crt`
- `exec_func_nback`
- `exec_func_task_switch`
- `exec_func_tol`
- `exec_func_wcst`

### Learning (4 benchmarks)
- `learning_curriculum`
- `learning_curves`
- `learning_interference`
- `learning_transfer`

### Social Cognition (4 benchmarks)
- `social_cog_emotional_prosody`
- `social_cog_false_belief`
- `social_cog_pragmatic`
- `social_cog_sarcasm`

---

## Task 1: Run Benchmark (per benchmark)

Run the benchmark against all 10 models with detailed Q&A transcript logging.

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

**Requirements:**
- Every question and response for all models must be **recorded** (full Q&A logs, not just scores)
- Save Q&A transcripts to `results/qa_transcripts/{benchmark_name}/{model_id}.jsonl` with fields: question_id, prompt, response, parsed_answer, correct_answer, score
- Save per-model summary scores to `results/qa_transcripts/{benchmark_name}/{model_id}.summary.json`
- Run models sequentially (one at a time) to avoid resource contention
- Use 300s timeout per model, 900s for DeepSeek-R1
- Fix retry bias first if this benchmark is affected (see `docs/RETRY_BIAS_ISSUE.md`)
- Compute and record: mean, std, range across all 10 models

---

## Task 2: Evaluate Results (per benchmark)

Analyze the Q&A transcripts and scores from Task 1.

**Requirements:**
1. **Score distribution** — mean, std, range, ceiling/floor effects
2. **Model discrimination** — does the benchmark separate models meaningfully? (target: std ≥ 0.08)
3. **Q&A review** — review 5 transcripts (highest, lowest, mid-range, surprising, random model). Document:
   - Correct scoring examples
   - Incorrect scoring examples (model gave reasonable answer but scored 0, or vice versa)
   - Parsing artifacts (structured output failures, think-tag issues)
4. **Ground truth validity** — are the "correct" answers actually correct? Flag debatable items with IDs
5. **Recommendation** — for each issue found: keep as-is, revise specific items (list IDs), adjust scoring formula, or drop
6. Save analysis to `results/analysis_{benchmark_name}.md`

---

## Task 3: Implement Improvements and Re-run (per benchmark)

Execute all improvements identified in Task 2, then re-run the benchmark.

**Requirements:**
1. Implement all recommended fixes (scoring changes, item revisions, difficulty adjustments)
2. Update both the `.py` task file and the corresponding `.ipynb` notebook
3. Validate notebook passes `jupyter nbconvert --to notebook` syntax check
4. Re-run the benchmark against all 10 models with the fixes applied
5. Compare before/after: old std vs new std, old range vs new range
6. Document all changes in `results/improvement_log_{benchmark_name}.md`:
   - What was changed and why
   - Items added/modified/removed (with IDs)
   - Scoring formula changes
   - Before/after score comparison
   - Remaining known limitations
7. If Task 2 found no issues (benchmark already passes all criteria), document that and skip re-run

---

## Known Issues to Address

- **Retry bias**: 18/26 notebooks give thinking models a retry advantage (see `docs/RETRY_BIAS_ISSUE.md`). Fix affected benchmarks in Task 1 before running.
- **Sequential runs required**: Parallel execution causes SIGTERM due to resource contention. Run models one at a time.
- **GLM 4.7 Bedrock issues**: Repeated ValidationException; budget extra time.
- **DeepSeek-R1 response format**: Returns both `text` and `reasoningContent` blocks; handle KeyError on `text`.

## Success Criteria

All 26 benchmarks pass:
- std ≥ 0.08 (model discrimination)
- No scoring bugs
- No ground truth errors
- 10/10 model coverage (or documented reason for exclusion)
- Ceiling effects addressed (no more than 10% of models above 0.95)
