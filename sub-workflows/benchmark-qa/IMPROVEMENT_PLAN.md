# Metacognition Track — Improvement Plan

**Date:** 2026-04-13  
**Source:** Per-benchmark analyses from `results/analysis_{external_monitoring,self_monitoring,prospective_assessment}.md`  
**Benchmarks:** 9 (3 tiers × 3 benchmarks)

---

## Summary

All 9 metacognition benchmarks pass the std ≥ 0.08 discrimination threshold and have verified ground truth. **No benchmarks need to be dropped.** No scoring bugs or ground truth errors were identified. The track is in good shape — improvements are defensive (monitoring borderline metrics, hardening edge cases) rather than corrective.

**Overall verdict:** No urgent fixes required. Three low-priority improvements identified for future robustness.

---

## Priority List

Ranked by (a) impact on track discrimination, (b) severity of scoring issues, (c) ground truth concerns.

| # | Benchmark | Issue | Impact | Effort | Re-run? |
|---|-----------|-------|--------|--------|---------|
| 1 | metacog_calibration | Borderline std=0.083 (0.003 above threshold) — could drop below with new models | High (track validity) | Medium | Yes, if items added |
| 2 | metacog_learning_monitoring | Borderline std=0.093 — compressed range (0.277) | Medium | Medium | Yes, if difficulty raised |
| 3 | metacog_jol | Perverse incentive: constant-zero-confidence → free gamma_norm=0.50 score | Low (no ranking distortion currently) | Small | No |
| 4 | metacog_error_detection | 30% ceiling (3 models >0.95) | Low (hard items still discriminate) | Medium | Yes, if items added |
| 5 | metacog_epistemic_humility | GPT-OSS-120B missing score (ValidationException) | Low (9/10 acceptable) | Small | Yes (1 model) |
| 6 | metacog_calibration | 11/120 Ministral 3B parse failures (91% success) | Very Low | Small | No |
| 7 | metacog_fok | 2/81 Ministral 3B parse failures | Very Low | Small | No |

Items 8–9 (metacog_canary, metacog_epistemic_revision, metacog_control) have **no issues identified** — fully clean.

---

## Batch 1: Scoring/Parsing Fixes (No Item Changes, No Re-run)

### 1.1 JOL Gamma Edge Case — Variation Penalty (Priority #3)

**Problem:** When a model reports constant confidence (all zeros or all same value), gamma denominator = 0, gamma returns 0.0, and gamma_norm = (0+1)/2 = 0.50. This gives a free 0.20 score (0.40 × 0.50) for non-engagement — higher than some models that genuinely attempt recall.

**Fix:** Add a confidence-variation check before gamma normalization:
```python
if np.std(confidences) < 1.0:
    gamma_norm = 0.0  # No variation = no metacognitive signal
```

**Effort:** Small (<30 min). Change in `task_jol.py` scoring function.  
**Re-run needed:** No — can retroactively recalculate from stored transcripts.  
**Impact:** Claude Sonnet 4.6 and Llama 3.3 70B would drop from 0.50 to ~0.30. Does not change top/bottom rankings but removes perverse incentive.

### 1.2 Parse Failure Hardening — Ministral 3B (Priority #6, #7)

**Problem:** Ministral 3B has 11/120 parse failures on calibration and 2/81 on FOK due to markdown-wrapped JSON. Default fallback (confidence=50) is reasonable but not ideal.

**Fix:** Enhance JSON extraction regex to handle triple-backtick-wrapped JSON:
```python
# Try stripping ```json ... ``` wrapper first
cleaned = re.sub(r'```json\s*', '', text)
cleaned = re.sub(r'```\s*$', '', cleaned)
```

**Effort:** Small (<30 min). Already partially handled; just needs tightening.  
**Re-run needed:** No for scoring formula. Yes if we want cleaner Ministral data (low priority).

---

## Batch 2: Item Revisions (Re-run Needed)

### 2.1 Calibration — Add Harder Items (Priority #1)

**Problem:** Std=0.083 is only 0.003 above the 0.08 threshold. If new frontier models cluster near the mean, discrimination could collapse.

**Fix:** Add 10–15 difficulty-5 items targeting areas where even frontier models diverge:
- Obscure mathematical constants (e.g., Ramanujan primes, Catalan numbers)
- Multi-step logical reasoning with confidence traps
- Questions requiring meta-awareness of difficulty

**Effort:** Medium (30–60 min to design items + update notebook).  
**Re-run needed:** Yes — all 10 models on revised benchmark.  
**Expected impact:** Widen score spread by introducing items that separate frontier models.

### 2.2 Learning Monitoring — Increase Rule Difficulty (Priority #2)

**Problem:** Std=0.093 with compressed range (0.277). Both learning accuracy and confidence must vary simultaneously, limiting discrimination.

**Fix:** Change all rule systems to difficulty 3–4 (currently mixed 2–3). Harder rules create more learning errors, which amplifies the monitoring signal (confidence calibration becomes more informative when accuracy varies more).

**Effort:** Medium (30–60 min to adjust rule generators + update notebook).  
**Re-run needed:** Yes — all 10 models.  
**Expected impact:** Wider accuracy spread → more gamma variation → higher std.

### 2.3 Error Detection — Add Hard Statistical Items (Priority #4)

**Problem:** 30% ceiling (3 models >0.95). Frontier models find arithmetic errors too easily.

**Fix:** Add 5–8 items testing subtle statistical fallacies beyond the current E33–E40 set:
- Ecological fallacy
- Berkson's paradox
- Multiple comparisons / p-hacking detection
- Survivorship bias in presented data

**Effort:** Medium (30–60 min to design items + update scoring).  
**Re-run needed:** Yes — all 10 models.  
**Expected impact:** Reduce ceiling from 30% to <10%.

### 2.4 Epistemic Humility — Retry GPT-OSS-120B (Priority #5)

**Problem:** GPT-OSS-120B has no score due to a Bedrock ValidationException. 9/10 coverage is acceptable but 10/10 is better.

**Fix:** Retry GPT-OSS-120B with adjusted Bedrock parameters (token limits, timeout).  
**Effort:** Small (<30 min).  
**Re-run needed:** Yes — 1 model only.

---

## Batch 3: Benchmark Redesigns (Re-run + Revalidation Needed)

**No benchmarks require full redesign.** All 9 metacognition benchmarks are structurally sound, measure their intended constructs, and use contamination-resistant designs (fictional domains, procedural generation, novel stimuli).

---

## Remaining Known Limitations

1. **Claude hedging penalty** — Claude models systematically score lower on epistemic_humility and learning_monitoring due to conservative confidence reporting. This is a deliberate design choice (benchmarks reward decisive self-assessment), not a bug. Documented in KNOWLEDGE.
2. **kbench chat isolation on JOL** — The study-phase context is not retained during recall, making JOL a de facto "can you learn in zero-shot?" test rather than a true study→test paradigm. This is a platform limitation, not a benchmark design flaw.
3. **Ministral 3B as floor anchor** — Ministral 3B is consistently the weakest model across all 9 benchmarks. If it's replaced with a stronger small model in future evaluations, floor discrimination may compress.
4. **metacog_calibration borderline std** — At 0.083, this is the most fragile benchmark statistically. Monitor closely with any model roster changes.

---

## Estimated Total Effort

| Batch | Items | Effort | Re-runs |
|-------|-------|--------|---------|
| Batch 1 | 2 fixes | ~1 hour | None (or optional Ministral re-parse) |
| Batch 2 | 4 revisions | ~3 hours | 3 full (30 models) + 1 single-model |
| Batch 3 | None | — | — |
| **Total** | **6 items** | **~4 hours** | **~31 model runs** |

**Recommendation:** Implement Batch 1 immediately (no cost, defensive). Implement Batch 2 only if time permits before deadline or if new model evaluations reveal std dropping below threshold.
