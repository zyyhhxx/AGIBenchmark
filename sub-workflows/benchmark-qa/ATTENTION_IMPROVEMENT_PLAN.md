# Attention Track — Improvement Plan

**Date:** 2026-04-15  
**Deadline:** 2026-04-16  
**Time Budget:** ~12 hours  
**Benchmarks:** 4 (attention_divided, attention_selective, attention_vigilance, attention_instruction_update)

---

## Executive Summary

All 4 attention benchmarks pass the std ≥ 0.08 threshold, but **ceiling clusters are the dominant problem**: 6/10 models tied on divided, 4/10 on selective, 2/10 on vigilance, and 5/10 on instruction_update. The current code already contains improvements that were never re-run (T4 tier for selective, H6-H8 trials for instruction_update). These in-code improvements, combined with targeted new additions and a parsing fix, should substantially improve discrimination.

**Key finding:** Code-on-disk diverges from scored results. The current task files include T4 items (selective) and H6-H8 trials (instruction_update) that were added after the last scoring run. Re-running with existing code is itself a major improvement.

**Approach:** Modeled on the metacognition track improvements — add harder items targeting frontier model separation, fix parsing bugs, and increase weight on discriminating tiers.

---

## Priority List (Ranked by Expected Impact / Effort)

| # | Benchmark | Issue | Expected Δstd | Effort | Re-run? |
|---|-----------|-------|---------------|--------|---------|
| 1 | attention_instruction_update | 5 models tied at 0.9833; H6-H8 already in code | +0.02–0.06 | **Zero** (re-run only) | Yes |
| 2 | attention_selective | 4 models at ceiling; T4 tier already in code | +0.01–0.04 | **Zero** (re-run only) | Yes |
| 3 | attention_divided | 6 models at 0.92-0.94; parsing fix in code | +0.01–0.03 | **Zero** (re-run only) | Yes |
| 4 | attention_instruction_update | Add 2 extreme trials beyond H8 | +0.02–0.05 | ~45 min | Yes (bundled w/ #1) |
| 5 | attention_divided | Add 2 extreme+ trials (5+ rules) | +0.01–0.03 | ~30 min | Yes (bundled w/ #3) |
| 6 | attention_vigilance | 2 models at 1.0; add 8-back condition | +0.01–0.02 | ~30 min | Yes |
| 7 | attention_selective | Add 4 T4 "extreme" items with 7+ constraints | +0.01–0.03 | ~45 min | Yes (bundled w/ #2) |

**Total estimated time:** ~2.5 hours code changes + 2 hours re-runs (4 benchmarks × 30 min) + 1 hour validation = ~5.5 hours  
**Buffer:** ~6.5 hours for debugging, re-runs if improvements fail, or additional iterations

---

## Batch 0: Re-Run Existing Code (No Changes Needed)

These improvements are **already implemented in the task files** but have never been scored. Re-running alone is the highest-ROI action.

### 0.1 attention_instruction_update — Hard Trials H6-H8 (Already in Code)

**Current state:** Scores based on 5 hard trials (H1-H5). Code now has 8 hard trials (H1-H8):
- **H6_DEEP_CHAIN:** 5-phase chained number rule system (20 items) — mod 5 → +2 → negate if prime → ×4 → +10 if even
- **H7_CONDITIONAL:** Conditional rules with phase swap and 5-letter override (16 items)
- **H8_INTERLEAVE:** 4-phase cycling rules with modification (R1 → R2 → R1' → R2', 16 items)

**Expected impact:** H6 is substantially harder than H4 (5 phases vs 3, more complex composition). Should break the 0.9833 ceiling cluster by introducing items where frontier models diverge on deep rule chaining. H7 and H8 add conditional branching and interleaving — distinct cognitive demands.

**Risk:** If frontier models also ace H6-H8, the ceiling remains. Mitigation: add extreme items (Batch 2, Priority #4).

### 0.2 attention_selective — Tier 4 Items (Already in Code)

**Current state:** Scores based on 3 tiers (T1/T2/T3, weights 0.08/0.22/0.70 effective). Code now has 4 tiers:
- **T4 (Quadruple-conjunction):** 6 items requiring 5-7 simultaneous constraints with near-miss edge cases
  - T4_01: 6-criteria student filtering
  - T4_02: 5-criteria recipe filtering with allergen logic
  - T4_03: 6-criteria apartment search
  - T4_04: 5-criteria stock screening
  - T4_05: 7-criteria server compliance
  - T4_06: 6-criteria candidate filtering

**Weight structure:** 0.08 × T1 + 0.22 × T2 + 0.35 × T3 + 0.35 × T4

**Expected impact:** T4 items require tracking 5-7 independent dimensions with near-miss distractors engineered to fail on exactly one criterion. This should separate frontier models (Opus, DeepSeek, Sonnet, GPT-OSS) that currently score 0.95-1.0 on the 3-tier version. Analogous to how metacog_error_detection's statistical fallacy items broke a 30% ceiling.

### 0.3 attention_divided — JSON Comment Stripping (Already in Code)

**Current state:** `extract_json()` already includes `re.sub(r"//.*", "", raw)` for comment stripping, plus backtick fence handling. This wasn't present during the scored runs.

**Expected impact:**
- Ministral 3B: ~0.41 → ~0.55-0.60 (recovers 4-6 trials from parse failures)
- Nova Pro: ~0.71 → ~0.74-0.76 (recovers 1-2 trials)
- Net effect on std: slight compression (weaker models improve), but ceiling cluster remains untouched
- This is a correctness fix, not a discrimination improvement

### 0.4 attention_vigilance — No Code Changes Pending

Current code matches what was scored. Re-run not needed unless new changes are made.

---

## Batch 1: New Item Additions (Code Changes Required)

### 1.1 attention_instruction_update — Add 2 Extreme Trials (Priority #4)

**Problem:** Even with H6-H8, the 0.9833 ceiling may persist if frontier models handle 5-phase chains. Need trials that combine MULTIPLE challenge types simultaneously.

**Proposed trials:**

**H9_RECURSIVE_OVERRIDE** (18 items):
```
- Phase 1 (items 1-4): Classify number as PRIME/COMPOSITE
- Phase 2 (items 5-8): Previous answer becomes the input. If previous answer was PRIME, double the number; if COMPOSITE, halve it (round down). Then classify result as PRIME/COMPOSITE.
- Phase 3 (items 9-12): REVERT to Phase 1 rules, BUT: if the number's digit sum is even, apply the OPPOSITE classification (PRIME→COMPOSITE, COMPOSITE→PRIME)
- Phase 4 (items 13-18): Apply Phase 2 modification to Phase 3 results. Additionally: if item position is odd, swap PRIME↔COMPOSITE in the final answer.
```
*Why this works:* Requires maintaining 4 simultaneous rule modifications, each building on the last. The recursive dependency (output of one phase feeds into the next) prevents shortcutting. Position-dependent swaps add an orthogonal dimension.

**H10_AMBIGUITY_RESOLUTION** (16 items):
```
- Phase 1 (items 1-4): Apply Rule A (word length) and Rule B (first letter position) simultaneously. Report both.
- Phase 2 (items 5-8): Rules CONFLICT. When A says SHORT and B says FIRST-HALF, report "CONFLICT". Otherwise report the Rule A answer.
- Phase 3 (items 9-12): Add Rule C (vowel count). Report the rule with the MAJORITY vote (if 2/3 agree, report that answer; if all 3 disagree, report "AMBIGUOUS").
- Phase 4 (items 13-16): Remove Rule B. Apply Rules A and C, but if they AGREE, report the OPPOSITE of their agreement.
```
*Why this works:* Forces simultaneous multi-rule evaluation with conflict detection and meta-reasoning about rule agreement. The "opposite of agreement" in Phase 4 is a high-order reversal that should trip up models that lock into a pattern.

**Weight adjustment:** Redistribute to 0.10 × easy + 0.20 × medium + 0.70 × hard. This increases the discriminating tier's influence.

**Effort:** ~45 minutes (design items, compute ground truth, add to HARD_TRIALS array)  
**Expected impact:** std 0.21 → 0.24-0.28. Should break the 5-model ceiling cluster.

### 1.2 attention_divided — Add 2 Extreme+ Trials (Priority #5)

**Problem:** Even extreme trials (4 rules) may not discriminate among the 6 models at 0.92-0.94. Need trials with 5-6 rules and cross-stream contradictions.

**Proposed trials:**

**X4_CONFLICTING_STREAMS** (12 items, 3 streams with rule conflicts):
```
Three streams share the SAME numbers but apply CONTRADICTORY rules:
- Stream A: Is the number divisible by the number of streams active so far (cumulative)?
- Stream B: Apply the PREVIOUS stream's rule to the NEXT stream's number
- Stream C: Report what Stream A WOULD answer if the number were doubled

Items rotate A→B→C. The cross-referencing makes it impossible to process streams independently.
```

**X5_META_STREAM** (15 items, 4 streams + meta-rule):
```
Streams A/B/C as before, plus:
- Stream D (meta): For each set of 3 consecutive items (one from each stream), report how many streams gave the SAME answer. If 0 or 1 streams agree, respond "DIVERGENT". If 2+, respond "CONVERGENT".
```

**Weight adjustment:** Increase extreme weight to 0.40 (from 0.35), reduce easy to 0.10.

**Effort:** ~30 minutes  
**Expected impact:** std 0.1675 → 0.19-0.22. Cross-stream referencing tests genuine divided attention (not just parallel single-stream processing).

### 1.3 attention_vigilance — Add 8-Back Condition (Priority #6)

**Problem:** 2 models (DeepSeek, GPT-OSS) at perfect 1.0. Current max is 6-back.

**Proposed change:**
1. Add 8-back condition (60 items) with higher near-miss rate (0.22)
2. Adjust weights: 3-back 0.20, 4-back 0.25, 6-back 0.25, 8-back 0.30

**Why this works:** 8-back requires tracking context 8 positions back, far exceeding typical working memory. The sequence must be long enough that even systematic models can't simply store all prior items. With confusable letter pairs, the false-alarm rate at 8-back should separate DeepSeek and GPT-OSS (which may have different internal context management strategies).

**Effort:** ~30 minutes (modify vigilance_stimuli.py, add VIGILANCE_8BACK, update task weights)  
**Expected impact:** std 0.1738 → 0.18-0.20. Modest improvement — the primary goal is breaking the 2-model perfect ceiling.

### 1.4 attention_selective — Add 4 Harder T4 Items (Priority #7)

**Problem:** Even with existing T4 items (6 items, 5-7 constraints each), some frontier models may still ace them. Need 7+ constraint items with deliberately ambiguous near-misses.

**Proposed items:**

**T4_07:** 8-criteria employee benefits eligibility (tenure, department, performance, salary band, full-time, no probation, manager approval, training completion) — 15 candidates, 3-4 correct
**T4_08:** 7-criteria scientific paper filtering (year, journal tier, citation count, methodology, sample size, field, open access) — 12 papers, 2-3 correct
**T4_09:** 8-criteria military unit deployment readiness (personnel strength, equipment status, training score, morale rating, supply level, location, weather clearance, command authorization) — 10 units, 2 correct
**T4_10:** 7-criteria investment opportunity screening (ROI, risk rating, minimum investment, sector, geographic region, liquidity, ESG score) — 12 opportunities, 3 correct

**Key design principle:** Each item should have 2-3 "near-misses" that fail on exactly ONE obscure criterion (e.g., an employee who meets 7/8 criteria but is on probation — easy to miss in a wall of data).

**Effort:** ~45 minutes  
**Expected impact:** std 0.155 → 0.17-0.19 (T4 already has 0.35 weight, adding 4 harder items shifts the T4 mean downward for mid-tier models).

---

## Batch 2: Weight Rebalancing (Bundled with Re-runs)

If re-runs show that existing improvements didn't sufficiently break ceilings:

### 2.1 attention_instruction_update — Increase Hard Weight
- Current: 0.15E + 0.25M + 0.60H
- Proposed: 0.10E + 0.15M + 0.75H
- Rationale: Easy and medium are saturated. Increasing hard weight amplifies the discriminating tier.

### 2.2 attention_divided — Increase Extreme Weight
- Current: 0.15E + 0.20M + 0.30H + 0.35X
- Proposed: 0.10E + 0.15M + 0.25H + 0.50X
- Rationale: 6-model ceiling is entirely in easy/medium tiers. Extreme tier is the only discriminator.

### 2.3 attention_selective — Increase T4 Weight
- Current: 0.08T1 + 0.22T2 + 0.35T3 + 0.35T4
- Proposed: 0.05T1 + 0.15T2 + 0.30T3 + 0.50T4
- Rationale: T4 is designed to break the frontier ceiling. Higher weight means T4 performance dominates ranking.

---

## Execution Plan (Ordered by Priority)

### Phase A: Re-Run Existing Code (Highest ROI, ~2 hours)

| Step | Action | Time |
|------|--------|------|
| A1 | Re-run attention_instruction_update (with H6-H8) | 30 min |
| A2 | Re-run attention_selective (with T4) | 30 min |
| A3 | Re-run attention_divided (with parsing fix) | 30 min |
| A4 | Evaluate results — compute new std/range | 15 min |
| A5 | Decision gate: which benchmarks still need improvement? | 15 min |

### Phase B: Implement New Items (Conditional on Phase A, ~2.5 hours)

Only for benchmarks that still have problematic ceilings after Phase A re-runs.

| Step | Action | Time |
|------|--------|------|
| B1 | Add H9, H10 to instruction_update (if ceiling persists) | 45 min |
| B2 | Add X4, X5 to divided (if ceiling persists) | 30 min |
| B3 | Add 8-back to vigilance (if DeepSeek/GPT-OSS still at 1.0) | 30 min |
| B4 | Add T4_07-10 to selective (if ceiling persists) | 45 min |
| B5 | Re-run modified benchmarks | 2 hours |

### Phase C: Weight Rebalancing (Conditional on Phase B, ~1 hour)

| Step | Action | Time |
|------|--------|------|
| C1 | Adjust weights for any benchmark still at problematic std | 15 min |
| C2 | Final re-run | 30 min |
| C3 | Validate and document results | 15 min |

---

## Expected Outcomes

| Benchmark | Current std | After Phase A | After Phase B | Target |
|-----------|------------|---------------|---------------|--------|
| attention_divided | 0.1675 | 0.16-0.17 | 0.19-0.22 | ≥0.18 |
| attention_selective | 0.1550 | 0.17-0.20 | 0.19-0.22 | ≥0.18 |
| attention_vigilance | 0.1738 | 0.1738 (no change) | 0.18-0.20 | ≥0.18 |
| attention_instruction_update | 0.2131 | 0.22-0.26 | 0.24-0.28 | ≥0.22 |

**Conservative estimate:** Phase A alone should improve discrimination on 3/4 benchmarks. Phase B targets the remaining gaps.

---

## Risk Mitigation

1. **If H6-H8 don't break instruction_update ceiling:** The trials may be within reach of all frontier models. H9/H10 use recursive and meta-reasoning patterns that are structurally harder. Fallback: weight rebalancing (Phase C).

2. **If T4 items are too hard (all models score poorly):** Would compress std rather than improve it. Mitigation: check that at least 2-3 models score ≥0.6 on T4 items. If all models crater, reduce T4 weight.

3. **If 8-back is impossible for all models:** Both DeepSeek and GPT-OSS would score similarly poorly, maintaining the ceiling at a lower level but not breaking the tie. Mitigation: if both drop equally, skip 8-back and accept the 2-model ceiling (it's less problematic than the 5-6 model ceilings on other benchmarks).

4. **Re-run failures or timeouts:** Some models may time out on harder items (observed in metacognition with 3 timeouts on difficulty-4 rules). Mitigation: monitor first 2-3 models during re-run, adjust timeout if needed.

---

## Parallels to Metacognition Improvements

| Pattern | Metacognition | Attention |
|---------|--------------|-----------|
| Add harder items to break ceiling | calibration: +12 d5 items → std 0.086→0.108 | instruction_update: H6-H8 (in code) + H9-H10 (proposed) |
| Increase procedural difficulty | learning_monitoring: rules d2-3→d3-4 → std 0.077→0.181 | vigilance: add 8-back condition |
| Fix parsing bugs | backtick stripping for Ministral 3B | JSON comment stripping (already in code) |
| Target ceiling clusters | error_detection: +7 hard items → ceiling 30%→0% | selective T4, instruction_update extreme trials |
| Weight rebalancing | N/A (not needed for metacog) | Shift weight to discriminating tiers (Phase C) |

---

## Files to Modify

| File | Changes |
|------|---------|
| `benchmarks/attention/task_instruction_update.py` | Add H9, H10 trials; adjust weights (Phase B/C) |
| `benchmarks/attention/task_divided.py` | Add X4, X5 trials; adjust weights (Phase B/C) |
| `benchmarks/attention/task_vigilance.py` | Add 8-back condition; adjust weights (Phase B/C) |
| `benchmarks/attention/data/vigilance_stimuli.py` | Add VIGILANCE_8BACK generation (Phase B) |
| `benchmarks/attention/task_selective.py` | Add T4_07-10 items (Phase B) |

---

## Decision Gates

1. **After Phase A:** If all 4 benchmarks have std ≥ 0.18 and no ceiling cluster ≥5 models → STOP. Ship as-is.
2. **After Phase B:** If all 4 benchmarks improved → STOP. If any regressed → investigate and potentially revert.
3. **After Phase C:** Final validation. All benchmarks must maintain std ≥ 0.08 (floor) and ideally ≥ 0.15 (target).

---

## Estimated Total Effort

| Phase | Code Time | Re-run Time | Total |
|-------|-----------|-------------|-------|
| Phase A (re-run existing) | 0 min | 2 hours | 2 hours |
| Phase B (new items) | 2.5 hours | 2 hours | 4.5 hours |
| Phase C (weights) | 15 min | 30 min | 45 min |
| Validation + documentation | — | — | 1 hour |
| **Total** | **2.75 hours** | **4.5 hours** | **~8.25 hours** |

Fits within the 12-hour budget with ~3.75 hours buffer for debugging and iteration.

---

## Recommendation

**Execute Phase A immediately.** The in-code improvements (T4 selective, H6-H8 instruction_update, parsing fixes) are zero-effort and should meaningfully improve 3/4 benchmarks. Evaluate results at the Phase A decision gate before committing to Phase B additions.

Phase B priority order if needed: instruction_update H9-H10 > divided X4-X5 > selective T4_07-10 > vigilance 8-back.
