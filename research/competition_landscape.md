# Competition Landscape Analysis — April 6, 2026

## Key Findings from Kaggle Discussion Forums

### Existing Submissions (from search snippets)

1. **Metacognition — ECE Benchmark** (discussion/681964)
   - Someone built an ECE-based calibration benchmark
   - Found: "GPT-style models express 85% confidence on..." (truncated)
   - **Our differentiator**: We have 4 distinct metacognition tasks (calibration, FOK, JOL, error detection) vs their single ECE measure. Our FOK two-phase protocol is more cognitively grounded.

2. **Metacognition — 5-aspect benchmark** (discussion/683724)
   - Tests 5 distinct aspects of metacognition across Gemini 2.5, + other models
   - **Our differentiator**: Novel stimuli (invented words/rules), cognitive science framework (Nelson & Narens), two-phase FOK protocol

3. **Attention Benchmark — Vigilance & Injection Resistance** (discussion/683441)
   - 3 tasks: likely selective attention, vigilance (sustained), injection resistance
   - Expanded to 14 models. Vigilance ranges 0.00–1.00 across models (good discrimination!)
   - **Task 5: Proactive Interference** — overlaps with our interference benchmark
   - Attention shifting hit ceiling (3/4 models score 1.0) — hardened to v5

4. **Executive Functions** — Cognitive Control Suite (same discussion/683441)
   - 5 domains: inhibitory control, cognitive flexibility, working memory, planning, verbal/semantic
   - 15 tasks, 27 models

5. **Multi-dimensional scoring question** (discussion/687121)
   - Leaderboard is one float per task
   - Pattern: create separate outer tasks that each extract one score dimension
   - Can't return dict; need separate `@kbench.task` decorators

### Implications for Our Strategy

1. **Metacognition track is crowded** — need to stand out with:
   - Stronger cognitive science grounding (Nelson & Narens framework, citing specific literature)
   - Novel experimental paradigms (two-phase FOK, novel stimuli JOL)
   - Multiple metrics per benchmark (gamma, ECE, AUC)

2. **Learning track seems less contested** — focus here for better prize chances

3. **Technical: one float per task** — our composite scores are fine, but consider also submitting individual metric tasks

4. **Model discrimination is key** — benchmarks that produce 0.00–1.00 spread across models are valued. Need to ensure our benchmarks aren't ceiling/floor effects.

5. **Need to test on multiple models** — at minimum Gemini 2.5/3, Claude, DeepSeek

### Design Principles from Q&A (from search snippet)
- Cognitive faculties "interact, overlap, and build on one another"
- But evaluated on separate axes to build cognitive profiles
- Shortcuts and gaming resistance is important
- Need to show task truly measures intended cognitive ability

### What We Should Do
- [ ] Split composite scores into individual metric tasks for leaderboard
- [ ] Ensure difficulty calibration prevents ceiling/floor effects
- [ ] Write strong writeup connecting to cognitive science
- [ ] Test on 3+ frontier models to show discrimination
- [ ] Consider cross-embedding metacognitive probes in learning tasks (unique differentiator)
