# Analysis: learning_transfer

## Step 1: Aggregate Stats

| Metric | Value |
|--------|-------|
| Models | 10/10 |
| Mean | 0.786 |
| Std | 0.2259 |
| Range | 0.650 |
| Min | 0.35 (Ministral 3B) |
| Max | 1.0 (Claude Opus/Sonnet/DeepSeek-R1/GPT-OSS) |

**Known from KNOWLEDGE:** transfer delta=0.65 confirmed. Best discriminator among learning benchmarks.

## Step 2: Score Distribution

| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 1.000 |
| Claude Sonnet 4.6 | 1.000 |
| DeepSeek-R1 | 1.000 |
| GPT-OSS-120B | 1.000 |
| Llama 4 Maverick 17B | 0.880 |
| GLM 4.7 | 0.810 |
| Qwen3 Next 80B | 0.750 |
| Nova Pro | 0.550 |
| Llama 3.3 70B | 0.520 |
| Ministral 3B | 0.350 |

**Distribution shape:** Smooth gradient from 1.0 to 0.35 with a natural break at 0.55 (Nova Pro). 4 models at ceiling (1.0), but remaining 6 spread well (0.35–0.88).

**std=0.2259 (≥0.08 ✅)** — strongest discriminator in the learning track.

## Step 3: Model Discrimination

- **Ceiling effect:** 4/10 models at 1.0 (40%) — significant but tolerable since remaining 6 models spread well
- **Clean tier structure:** Perfect (1.0) → Strong (0.75–0.88) → Weak (0.35–0.55) — three natural clusters
- **Transfer scales with model capability:** The 4 perfect-score models are all frontier-class; medium models (Maverick, GLM, Qwen3) cluster in 0.75–0.88; smaller/weaker models (Nova Pro, Llama 3.3, Ministral) in 0.35–0.55
- **Known from KNOWLEDGE:** "transfer scales cleanly with model size" — confirmed in this run

## Step 4: Q&A Review (5 models)

**Models reviewed:** Claude Opus (highest=1.0), Ministral 3B (lowest=0.35), Nova Pro (mid-low=0.55), GLM 4.7 (mid=0.81), Qwen3 (mid=0.75)

- **Claude Opus 4.6:** 15 questions, perfect score. Clean parsed answers for all tiers (identical, near, far).
- **Ministral 3B:** 15 questions, **10/15 parse issues (67%)**. This is the most severe parsing rate of any model on any benchmark.
  - Dominant failure: outputs `{"answer": {"⬟", "⬟", "⬡"...}}` (set notation) or `{"answer": {"key": "val"...}}` (dict mapping) instead of answer strings
  - Q011–Q015 (far transfer, number domain): cleaner parsing, suggesting the number domain prompts elicit better-formatted responses
  - **Score impact:** With 67% parse failure rate, Ministral's true score could be 0.45–0.55 rather than 0.35. The model's ranking would likely stay at bottom but gap would narrow.
- **Nova Pro:** 15 questions, clean parsing. Score=0.55 — struggles on far transfer (number system).
- **GLM 4.7:** 15 questions, clean parsing. Score=0.81 — handles near transfer well, weaker on far.
- **Qwen3:** 15 questions, clean parsing. Score=0.75 — similar pattern to GLM.

**Think-tag leakage:** None detected.

## Step 5: Ground Truth Validation

- **Transfer structure verified:**
  - Identical tier (5 items): same symbol system, new test items — baseline
  - Near tier (5 items): same domain (symbols), different surface features — tests structural generalization
  - Far tier (5 items): different domain (number operations), structurally analogous rules — tests deep transfer
- **Rule mappings verified:**
  - Train: □→⬟, ◇→⬡, ★→▽, EXCEPTION: □◇→▽▽
  - Near: ○→⬟, □→▽, △→⬡, EXCEPTION: ○□→⬟⬟ (same structure, different symbols) ✅
  - Far: blix(x,y)=2x+y, quex(x,y)=(x+y)%10, zorp(x,y)=|x-y|+1 — structurally analogous operations ✅
- **Test items hand-checked:**
  - Train: `★ ★ □ ◇ ○ ○` → `▽ ▽ ▽ ▽ ○ ○` (exception fires on □◇) ✅
  - Far: `blix(8, 9)` = 2×8+9 = 25 ✅
  - Far: `blix(3, 7)` = 2×3+7 = 13 ✅
- **Scoring:** 0.30×identical + 0.35×near + 0.35×far — appropriately weights transfer over baseline

**No ground truth errors found.**

## Step 6: Recommendation

**KEEP AS-IS**

Rationale:
- std=0.2259 — strongest discriminator in the learning track, well above threshold
- 10/10 coverage, 0 failures
- Ground truth verified correct (both symbol and number domains)
- Score distribution shows clean capability gradient
- Transfer mapping is structurally sound (symbol→symbol near, symbol→number far)

**Advisory for future iteration:**
- Ministral 3B parse failure rate (67%) is extreme. Backtick stripping + answer-string normalization should be applied. True score likely ~0.10 higher.
- 4 models at ceiling (1.0) — consider adding "extreme transfer" tier (e.g., symbol→natural language rules) to separate top models.
