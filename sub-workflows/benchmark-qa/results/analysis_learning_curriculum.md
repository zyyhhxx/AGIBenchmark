# Analysis: learning_curriculum

## Step 1: Aggregate Stats

| Metric | Value |
|--------|-------|
| Models | 10/10 |
| Mean | 0.644 |
| Std | 0.0975 |
| Range | 0.300 |
| Min | 0.46 (Qwen3 Next 80B) |
| Max | 0.76 (Llama 3.3 70B) |

## Step 2: Score Distribution

| Model | Score |
|-------|-------|
| Llama 3.3 70B | 0.76 |
| Claude Opus 4.6 | 0.70 |
| Claude Sonnet 4.6 | 0.70 |
| Llama 4 Maverick 17B | 0.70 |
| GPT-OSS-120B | 0.70 |
| GLM 4.7 | 0.70 |
| Ministral 3B | 0.68 |
| Nova Pro | 0.52 |
| DeepSeek-R1 | 0.52 |
| Qwen3 Next 80B | 0.46 |

**Distribution shape:** Bimodal — 6 models cluster at 0.68–0.76 (top group), 3 models at 0.46–0.52 (lower group). No ceiling or floor effect.

**std=0.0975 (≥0.08 ✅)** — passes threshold but is the weakest of the 4 learning benchmarks.

## Step 3: Model Discrimination

- **Delta (max−min):** 0.30 — adequate but compressed
- **Top cluster:** 6 models within 0.08 of each other (0.68–0.76) — weak discrimination among frontier models
- **Surprising findings:**
  - Llama 3.3 70B scores highest (0.76) despite being mid-tier on other learning benchmarks — curriculum sensitivity may favor specific architectural features
  - DeepSeek-R1 (0.52) is surprisingly low — reasoning model performs poorly on curriculum ordering sensitivity
  - Ministral 3B (0.68) outperforms Nova Pro (0.52) and DeepSeek-R1 (0.52) — non-monotonic size-capability relationship

## Step 4: Q&A Review (5 models)

**Models reviewed:** Llama 3.3 70B (highest), Qwen3 (lowest), DeepSeek-R1 (surprising), Ministral 3B (mid), Claude Opus 4.6 (mid-high)

- **Llama 3.3 70B:** 20 questions, 5.0s duration — extremely fast inference. Parsed answers are clean JSON strings. No parsing artifacts.
- **Qwen3 Next 80B:** 20 questions, 32.1s. Clean parsed answers. Low score reflects genuine curriculum insensitivity — model shows similar accuracy regardless of example ordering.
- **DeepSeek-R1:** 20 questions, 71.1s. Clean parsing. Low score (0.52) is genuine — reasoning model overthinks simple rule application and shows minimal ordering effect.
- **Ministral 3B:** 20 questions, 52.7s. 1/20 parse issue (minor). Score of 0.68 is surprisingly strong — small model benefits from curriculum structure.
- **Claude Opus 4.6:** 20 questions, 124.1s. Clean parsing. Steady 0.70 score.

**Parsing issues:** Minimal (1/100 across 5 models). No scoring artifacts detected.
**Think-tag leakage:** None detected.

## Step 5: Ground Truth Validation

- **Rule system:** SymbolTransform-curriculum_v2 (difficulty=2), generated via `generate_symbol_system()` with deterministic seed
- **Rules verified:** Replace ◇→▽, △→⬟, ○→★, EXCEPTION pattern for adjacent symbols
- **Test items:** Generated programmatically from the rule system — answers are deterministic and correct by construction
- **Scoring formula:** 0.40 × max_accuracy + 0.30 × sensitivity + 0.30 × optimal_ordering_bonus
  - max_accuracy: best accuracy across curriculum orderings
  - sensitivity: variance in accuracy across orderings
  - optimal_ordering_bonus: whether easy→hard ordering performs best

**No ground truth errors found.** Rule system is procedurally generated with verified outputs.

## Step 6: Recommendation

**KEEP AS-IS**

Rationale:
- std=0.0975 passes the ≥0.08 threshold
- 10/10 model coverage with no errors
- Ground truth is correct by construction
- Parsing is clean across all models
- The compressed top cluster (6 models at 0.68–0.76) is a limitation but reflects genuine similarity in curriculum sensitivity among frontier models
- This is the only benchmark measuring curriculum ordering effects — the construct is valuable even with moderate discrimination

**Advisory for future iteration:**
- Consider increasing rule difficulty to d3 to spread the top cluster
- The scoring formula's sensitivity component (0.30 weight) could be increased to reward models that genuinely show different learning curves under different orderings
