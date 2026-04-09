# Preliminary Frontier Model Results

## Gemini 2.5 Flash — CRT (Cognitive Reflection Test)

**Date:** 2026-04-09 06:00 UTC  
**Method:** Direct API calls with chain-of-thought prompting  
**Quota:** Free tier (very limited — 3 items tested)

### Classic CRT Items (Frederick, 2005)

| # | Item | Correct | Trap | Model Answer | Result |
|---|------|---------|------|-------------|--------|
| 1 | Bat & ball ($1.10 total, bat costs $1 more) | $0.05 | $0.10 | $0.05 | ✓ Correct |
| 2 | 100 machines, 100 widgets (if 5 machines → 5 widgets in 5 min) | 5 minutes | 100 minutes | 5 | ✓ Correct |
| 3 | Lily pads doubling (48 days to cover lake) | 47 days | 24 days | 47 | ✓ Correct |

**Result: 3/3 correct (100%)**

### Analysis
- Gemini 2.5 Flash solves all classic CRT items correctly when allowed to reason step-by-step
- This is consistent with the hypothesis that chain-of-thought enables "System 2" override
- Human accuracy on these items: 30-48% (Frederick 2005)
- **Key question:** Do our procedurally generated CRT variants (novel number parameters, novel problem structures) still fool frontier models? The classic items may be in training data.

### Implications for Our Benchmark
1. **Contamination concern:** Classic CRT items are widely known — models may have memorized them
2. **Our procedural variants are critical:** We use novel numbers/structures specifically to test genuine reasoning vs memorization
3. **Chain-of-thought matters:** Without CoT, models may perform closer to human levels
4. **Need to test without step-by-step prompt:** Our actual benchmark doesn't encourage CoT explicitly

### Next Steps
- Run full CRT benchmark with our 20 procedurally generated items (needs billing)
- Test with and without chain-of-thought prompting
- Compare across models (GPT-4o, Claude, DeepSeek-R1)

## Additional Spot Checks (Gemini 2.5 Flash)

| Test | Expected | Model Response | Verdict |
|------|----------|---------------|----------|
| Stroop (ink color) | RED | RED | ✓ Correct |
| Epistemic humility (fabricated substance) | "I don't know" | "I don't know" | ✓ Good epistemic humility |
| 2nd-order ToM (Mary thinks John will look...) | Green cupboard | Green cupboard | ✓ Correct |
| Calibration (47th digit of pi, confidence) | Low (~10-30) | 100 | ✗ Overconfident! |

**Key finding:** Gemini 2.5 Flash shows **overconfidence on unknowns** (100% confidence for the 47th digit of pi) but correctly expresses uncertainty for fabricated items. This suggests models may have domain-specific calibration — confident about things that *seem* knowable (pi digits) but appropriately humble about clearly fabricated items. Our benchmark suite tests both dimensions.

## FOK Confidence Ratings (Pre-answer)

| Question Type | Question | Confidence | Analysis |
|---------------|----------|-----------|----------|
| Easy factual | Capital of France? | 100 | Appropriate — universally known |
| Hard procedural | 347 × 283? | 100 | Potentially overconfident — depends if model can compute |

**Observation:** Model gives 100% confidence for all questions tested, including computation. This suggests possible calibration issues that our FOK benchmark (with its 81-item bank across 9 difficulty categories) would expose more clearly.

## Additional Cognitive Tests

| Domain | Test | Expected | Model Response | Verdict |
|--------|------|----------|---------------|---------|
| Sarcasm Detection | "Oh great, another Monday meeting..." | YES (sarcastic) | YES | ✓ |
| Pragmatic Inference | "Some students passed" → implies not all? | YES (Gricean) | NO (logical) | ✗ Literal bias |
| Set-Shifting (WCST) | Match RED CIRCLE by color (not shape) | B (Red Square) | B | ✓ |

### Key Insight: Literal Bias in Pragmatic Inference
Gemini 2.5 Flash interprets "some" logically (compatible with "all") rather than pragmatically (implying "not all"). This demonstrates the **literal bias** that our pragmatic inference benchmark is designed to detect. In human conversation, "some of the students passed" almost always implies not all did — this is Grice's maxim of quantity. The model's literal interpretation suggests a gap in social cognition that our benchmark suite would quantify across 25 pragmatic inference items.

This finding alone justifies our Social Cognition track — it reveals a measurable cognitive difference between human and model pragmatic reasoning.

## Deeper Cognitive Tests

| Domain | Test Description | Result | Score |
|--------|-----------------|--------|-------|
| Epistemic Revision | Correct belief after contradiction (Zorblatt Chemistry) | Correctly updated all 3 derivations | ✓ 3/3 |
| N-back (2-back) | 7-item sequence, identify 2-back matches | 5/5 correct | ✓ 100% |

### Epistemic Revision Analysis
Gemini 2.5 Flash successfully performs belief revision in our Zorblatt Chemistry scenario:
- Correctly applies the original rule (Flox + Brine → Zorb)
- Correctly overrides Rule 2 with the correction (Zorb is heat-stable)
- Correctly infers downstream consequences (Zorb doesn't become Glimmer, so can't dissolve in Pax)

This suggests strong epistemic revision capabilities for Gemini. However, our full benchmark uses 10 rules with 3 contradictions and 10 transfer questions — a much more demanding test that may reveal limitations in complex multi-rule reasoning.

### N-back Analysis
Perfect 2-back performance on a 7-item sequence. This is a short sequence; our full benchmark uses 60-item sequences at N=1, 2, and 3, which is much more demanding and likely to show working memory limitations.
