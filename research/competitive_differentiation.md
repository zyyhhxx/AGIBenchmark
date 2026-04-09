# Competitive Differentiation Analysis

## Our Unique Benchmarks (Not Seen in Other Submissions)

### Tier 1: Highly Unique
1. **Epistemic Revision** — No other submission tests belief updating under contradiction. Uses invented "Zorblatt Chemistry" rule system — completely contamination-proof.
2. **Metacognitive Control** — Tests strategic re-reading allocation. Novel adaptation of Nelson & Narens monitoring→control framework.
3. **Contamination Canary** — Meta-benchmark that detects data leakage. Only meta-evaluation tool we've seen in the competition.
4. **Epistemic Humility** — Tests confabulation rate on genuinely unanswerable questions. Most LLMs will expose weaknesses here.

### Tier 2: Strong Differentiation
5. **FOK (two-phase)** — Other FOK benchmarks exist (CASK competitor), but our two-phase protocol prevents post-hoc rationalization. Key differentiator: confidence BEFORE answering.
6. **CRT (procedural)** — CRT has been used before, but our procedurally generated variants with novel number parameters defeat memorization.
7. **Learning Curves** — Tests power-law fit of in-context learning. Unique approach to measuring learning dynamics.

### Tier 3: Good But Common
8. **False Belief ToM** — Well-known paradigm, several competitors have similar tests
9. **Stroop/Selective Attention** — Common paradigm, but our implementation with cognitive science controls is stronger
10. **WCST** — Well-studied paradigm, appears in other submissions

## Competitor Analysis: What We Know

### CASK (Darío Ávalos) — Most Threatening Competitor
- 17 models tested (we have 0 real results)
- Focus: context-aware sensitivity to knowledge (metacognition)
- Strong finding: Gemma collapses under misleading context
- Key result: DeepSeek-R1 shows +0.534 swing under misleading context
- **Our advantage:** We cover 5 tracks (they appear to cover 1-2). Our metacognition is deeper (9 benchmarks vs ~1-3). Our psychometric validation is more rigorous.
- **Their advantage:** Actual model results with 17 models. Real data > predictions.

### Executive Functions Suite (discussion/683441)
- 5 domains, 15 tasks, 27 models tested
- Attention shifting hit ceiling (3/4 models score 1.0)
- **Our advantage:** Our exec functions + attention benchmarks use different paradigms and difficulty calibration
- **Their advantage:** 27 model results

### General Landscape
- Most submissions focus on 1-2 tracks
- Few cover all 5 tracks comprehensively
- Most don't have psychometric validation
- Most use well-known paradigms without contamination resistance
- **Model results are the biggest differentiator** — we urgently need real results

## Recommendations
1. **Priority 1:** Get Gemini API billing enabled for frontier model results
2. **Priority 2:** Post discussion draft ASAP for upvote collection
3. **Priority 3:** Upload remaining notebooks via web UI
4. **Priority 4:** Submit to CB platform
