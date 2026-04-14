# Analysis: learning_curves

## Step 1: Aggregate Stats

| Metric | Value |
|--------|-------|
| Models | 10/10 |
| Mean | 0.5592 |
| Std | 0.0962 |
| Range | 0.2489 |
| Min | 0.4409 (Nova Pro) |
| Max | 0.6898 (Claude Opus 4.6) |

**Known from KNOWLEDGE:** curves v3 std=0.127 was the Phase 1 figure; current Phase 2 run shows std=0.0962 (slightly lower, still passes).

## Step 2: Score Distribution

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 0.6898 |
| GPT-OSS-120B | 0.6866 |
| Claude Sonnet 4.6 | 0.6854 |
| Qwen3 Next 80B | 0.5836 |
| DeepSeek-R1 | 0.5705 |
| Llama 4 Maverick 17B | 0.5473 |
| Ministral 3B | 0.4782 |
| GLM 4.7 | 0.4562 |
| Llama 3.3 70B | 0.4532 |
| Nova Pro | 0.4409 |

**Distribution shape:** Roughly continuous — top 3 cluster at ~0.69, middle 3 at 0.55–0.58, bottom 4 at 0.44–0.48. No hard ceiling or floor.

**std=0.0962 (≥0.08 ✅)** — passes threshold. Weakest discriminator of the 4 learning benchmarks (range=0.2489).

## Step 3: Model Discrimination

- **Delta (max−min):** 0.2489 — modest
- **Top cluster:** Claude Opus/Sonnet/GPT-OSS within 0.005 of each other — these models are functionally equivalent on learning curves
- **Bottom cluster:** GLM 4.7/Llama 3.3/Nova Pro within 0.016 — also functionally equivalent
- **260 questions per model** — large item count provides stable estimates

## Step 4: Q&A Review (5 models)

**Models reviewed:** Claude Opus (highest), Nova Pro (lowest), DeepSeek-R1 (mid), Ministral 3B (mid-low), Llama 3.3 70B (low)

- **Claude Opus 4.6:** 260 questions, 1568s (~26 min). Clean parsed answers. Score=0.6898 reflects strong but imperfect rule learning across difficulty progression.
- **Nova Pro:** 260 questions, 410s. Clean parsing. Score=0.4409 — struggles with steep/far-transfer items.
- **DeepSeek-R1:** 260 questions, 1982s (~33 min). Clean parsing. Mid-range score (0.5705) despite being a reasoning model.
- **Ministral 3B:** 260 questions, 880s. **79/260 parse issues** — model frequently outputs JSON objects instead of strings, backtick-wrapped responses, or dict-style answers. Despite parse issues, score=0.4782 is mid-range, suggesting the parser recovers many malformed responses.
- **Llama 3.3 70B:** 260 questions, 345s (fastest). Clean parsing. Low score=0.4532 despite clean parsing — genuine learning difficulty.

**Parsing concern:** Ministral 3B has 30% parse issue rate on this benchmark. The parser is handling many of them (score is non-zero), but some correct answers may be scored as wrong due to malformed JSON. This likely depresses Ministral's score by ~0.05–0.10.

**Think-tag leakage:** None detected.

## Step 5: Ground Truth Validation

- **Rule systems:** Multiple systems at increasing difficulty — SymbolTransform (easy→hard) plus structural transfer and positional/stateful systems for hard tier
- **Generated via:** `generate_symbol_system()`, `generate_structural_transfer()`, `generate_positional_system()`, `generate_stateful_system()` — all deterministic with fixed seeds
- **Verified:** Train system test items: `★ ★ □ ◇ ○ ○` → `▽ ▽ ▽ ▽ ○ ○` (correct by rule application including exception)
- **Far transfer:** `blix(8, 9)` = double 8 + 9 = 25 ✅
- **Composite scoring:** 0.20×standard + 0.50×far_transfer + 0.30×steep — heavily weights transfer and steep learning, which is appropriate for measuring genuine learning curves

**No ground truth errors found.**

## Step 6: Recommendation

**KEEP AS-IS**

Rationale:
- std=0.0962 passes ≥0.08 threshold
- 10/10 model coverage, 0 failures
- Ground truth is correct by construction (procedural generation)
- Score distribution is continuous with meaningful separation
- 260-item benchmark provides high statistical power

**Advisory for future iteration:**
- Ministral 3B parse issue rate (30%) is the highest of any model on any learning benchmark — applying backtick fence stripping (as done for metacog benchmarks) could improve score accuracy by ~0.05
- Range=0.2489 is relatively compressed — consider adding difficulty-4 rule systems (as done for learning_monitoring) to spread the top cluster
