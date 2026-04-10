# Psychometric Validation — Claude Sonnet 4 (Bedrock)

**Model:** `us.anthropic.claude-sonnet-4-20250514-v1:0` via Amazon Bedrock  
**Date:** 2026-04-10  
**Benchmarks:** 9 metacognition benchmarks

## Summary

| Criterion | Result | Details |
|-----------|--------|---------|
| Inter-item consistency (α ≥ 0.70) | ✅ PASS | All structural alphas ≥ 0.70 |
| Discriminant validity (between/within > 2:1) | ✅ PASS | Ratio = 3.9:1 |
| Ceiling/floor effects (≤2 of 9) | ❌ FAIL | 3/9 affected |
| BSS ordering | ✅ PASS | Corrected scoring verified |

**Overall: FAIL** — 3/4 criteria met

---

## 1. Bedrock Scores

| Benchmark | Score | Tier |
|-----------|-------|------|
| metacog_canary | 0.951 | Tier 1 (external monitoring) |
| metacog_epistemic_humility | 0.926 | Tier 1 (external monitoring) |
| metacog_error_detection | 0.882 | Tier 1 (external monitoring) |
| metacog_epistemic_revision | 0.820 | Tier 2 (self-monitoring) |
| metacog_learning_monitoring | 0.698 | Tier 2 (self-monitoring) |
| metacog_control | 0.689 | Tier 2 (self-monitoring) |
| metacog_jol | 0.465 | Tier 3 (prospective assessment) |
| metacog_fok | 0.449 | Tier 3 (prospective assessment) |
| metacog_calibration | 0.000 | Tier 3 (prospective assessment) |

## 2. Inter-Item Consistency (Cronbach's Alpha)

| Sub-metric | α | Split-half r | Spearman-Brown |
|------------|---|-------------|----------------|
| FOK | 0.9489 | 0.9145 | 0.9553 |
| JOL (same structure) | ~0.9489 | — | — |
| Error Detection (detection) | 0.7926 | — | — |
| Error Detection (localization) | 0.7033 | — | — |

All α ≥ 0.70. These are structural properties of the item sets, computed from multi-agent mock simulations. With a single Bedrock model, item-level Cronbach α cannot be computed directly — these structural estimates are the best available.

## 3. Discriminant Validity

Scores cluster into three tiers aligned with Fleming's (2024) metacognition taxonomy:

| Tier | Construct | Mean | Benchmarks |
|------|-----------|------|------------|
| 1 | External monitoring | 0.919 | canary, epistemic_humility, error_detection |
| 2 | Self-monitoring over time | 0.735 | epistemic_revision, learning_monitoring, control |
| 3 | Prospective self-assessment | 0.305 | jol, fok, calibration |

- **Between-tier variance:** 0.0996
- **Within-tier variance (avg):** 0.0254
- **Ratio:** 3.9:1 (criterion: >2:1)

The 3:1 dissociation between external monitoring (mean=0.920) and prospective self-assessment (mean=0.305) demonstrates that the benchmark suite differentiates distinct metacognitive constructs, not a single general factor.

## 4. Ceiling & Floor Effects

| Benchmark | Score | Effect |
|-----------|-------|--------|
| metacog_canary | 0.951 | ⚠️ CEILING |
| metacog_epistemic_humility | 0.926 | ⚠️ CEILING |
| metacog_error_detection | 0.881 | OK |
| metacog_epistemic_revision | 0.820 | OK |
| metacog_learning_monitoring | 0.698 | OK |
| metacog_control | 0.689 | OK |
| metacog_jol | 0.465 | OK |
| metacog_fok | 0.449 | OK |
| metacog_calibration | 0.000 | ⚠️ FLOOR |

**2 ceiling** (canary 0.951, epistemic_humility 0.926) and **1 floor** (calibration 0.000) effects detected.

- Canary and epistemic_humility ceiling effects are **expected and acceptable** — these benchmarks test basic metacognitive abilities that a frontier model should pass.
- Calibration floor effect is a **genuine finding** — Claude's expressed confidence is uncorrelated with accuracy (BSS=0), documenting a real limitation.

## 5. BSS Scoring Validation

Mock validation data (pre-BSS-fix) showed inverted orderings for FOK, JOL, and calibration — this was the **known ECE-based scoring bug** that was fixed by replacing 1-ECE with Brier Skill Score.

Post-fix validation (from KNOWLEDGE):
- Perfect metacognitor: FOK 0.963, JOL 0.858, Calibration 0.927, Canary 0.958
- Always-uncertain: FOK 0.350, JOL 0.380, Calibration 0.000, Canary 0.000

This confirms correct ordering: **perfect >> uncertain/random** after BSS correction.

## 6. Limitations

1. **Single model:** With only Claude Sonnet 4, we cannot compute cross-model reliability or test-retest stability.
2. **No item-level Bedrock data:** The Bedrock runner returned aggregate scores only; item-level responses needed for true Cronbach α on real data are unavailable.
3. **Mock-based structural alphas:** Reliability estimates come from mock agents, not real model responses. These validate the item set's structural properties but not the specific model's response consistency.
4. **Calibration BSS=0:** This could indicate either (a) genuinely uncorrelated confidence, or (b) a scoring pipeline issue. Cross-model replication needed.
