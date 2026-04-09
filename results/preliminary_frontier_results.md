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
