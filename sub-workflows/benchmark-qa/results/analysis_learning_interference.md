# Analysis: learning_interference

## Step 1: Aggregate Stats

| Metric | Value |
|--------|-------|
| Models | 10/10 |
| Mean | 0.9191 |
| Std | 0.1276 |
| Range | 0.4500 |
| Min | 0.55 (Ministral 3B) |
| Max | 1.0 (Claude Opus/Sonnet/GPT-OSS) |

**Known from KNOWLEDGE:** interference v3 std=0.280 was the Phase 1 3-model figure; current 10-model run shows std=0.1276 (lower, as expected with more models filling the middle).

## Step 2: Score Distribution

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 1.000 |
| Claude Sonnet 4.6 | 1.000 |
| GPT-OSS-120B | 1.000 |
| DeepSeek-R1 | 0.979 |
| Llama 4 Maverick 17B | 0.970 |
| Llama 3.3 70B | 0.930 |
| Qwen3 Next 80B | 0.930 |
| GLM 4.7 | 0.930 |
| Nova Pro | 0.902 |
| Ministral 3B | 0.550 |

**Distribution shape:** Heavy ceiling — 3 models at perfect 1.0, 6 more in 0.90–0.98. Ministral 3B is the sole outlier at 0.55. Without Ministral, std would drop to ~0.035 (non-discriminating).

**std=0.1276 (≥0.08 ✅)** — passes threshold, but discrimination is driven almost entirely by one model.

## Step 3: Model Discrimination

- **Ceiling effect:** 3/10 models at 1.0 (30%), 9/10 above 0.90 — strong ceiling
- **Delta (max−min):** 0.45 — large, but misleading since only Ministral 3B is far from the cluster
- **Without Ministral 3B:** range=0.098, std≈0.035 — would fail ≥0.08 threshold
- **Context-length fix:** max_examples reduced from 6→4 for hard tier (≥2 distractors) is deployed. No context-length errors found in Ministral 3B transcript (0 grep matches). Fix is working correctly.

## Step 4: Q&A Review (5 models)

**Models reviewed:** Claude Opus (highest=1.0), Ministral 3B (lowest=0.55), Nova Pro (mid-low=0.902), DeepSeek-R1 (near-ceiling=0.979), GLM 4.7 (mid=0.93)

- **Claude Opus 4.6:** 30 questions, perfect score. All parsed answers are clean strings matching expected outputs.
- **Ministral 3B:** 30 questions, 5/30 parse issues (17%). Malformed responses include:
  - Q004: Output is a JSON dict mapping symbols instead of a string sequence
  - Q008: Dict-style mapping + self-correction narrative after JSON
  - Q012: Set notation `{"▽", "△", "△"}` instead of sequence
  - Q014: Dict mapping
  - Q021: Dict mapping + appended reasoning
  These parse failures likely contribute 3–5 incorrectly scored items (~0.10–0.17 score impact).
- **Nova Pro:** Clean parsing. Score=0.902 reflects occasional confusion on hard tier (2 distractors).
- **DeepSeek-R1:** Clean parsing. Near-perfect (0.979) — one error on hard tier.
- **GLM 4.7:** Clean parsing. 0.93 — consistent performance across tiers.

**Think-tag leakage:** None detected.

## Step 5: Ground Truth Validation

- **Three difficulty tiers:** Easy (d=1, 1 dissimilar distractor), Medium (d=2, 1 similar distractor), Hard (d=3, 2 similar distractors + interleaved examples)
- **Rule systems verified:**
  - Easy target: Replace □→★, △→⬡, ○→▽. Test: `□ □ △ ○ ○ ○` → `★ ★ ⬡ ▽ ▽ ▽` ✅
  - Easy distractor: Replace ◇→▽, △→⬟, □→★ — different mapping, creates potential confusion on shared symbols (△, □)
  - Medium/Hard: Higher difficulty rules with exception patterns
- **Scoring formula:** Per tier: 0.30×control + 0.70×interference_accuracy. Composite: 0.15×easy + 0.35×medium + 0.50×hard
- **Interference controls:** Distractors are co-present in same prompt (not across turns) — this is the correct design per KNOWLEDGE

**No ground truth errors found.** Rule systems are procedurally generated and verified.

## Step 6: Recommendation

**KEEP AS-IS**

Rationale:
- std=0.1276 passes ≥0.08 threshold
- 10/10 coverage, 0 failures
- Context-length fix deployed and working (no errors for Ministral 3B)
- Ground truth correct by construction
- The v3 design (distractors co-present in same prompt) is the correct interference paradigm

**Structural limitation (documented, not actionable now):**
- Ceiling effect: 9/10 models score ≥0.90. Discrimination relies entirely on Ministral 3B.
- If Ministral 3B were removed from the model roster, this benchmark would fail std ≥ 0.08.
- **Advisory for future iteration:** Add difficulty-4 tier with 3+ distractors and conflicting exception rules to separate frontier models.

**Ministral 3B parse issue advisory:**
- 5/30 items (17%) have malformed JSON (dict-style instead of string). Backtick fence stripping + dict-to-string normalization could recover 2–3 items, improving Ministral score by ~0.07–0.10. Not score-critical since Ministral is already correctly identified as the weakest model.
