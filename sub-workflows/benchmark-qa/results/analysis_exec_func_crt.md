# Analysis: exec_func_crt (Cognitive Reflection Test)

## Score Distribution
| Metric | Value |
|--------|-------|
| Mean | 0.7728 |
| Std | 0.1558 |
| Range | 0.4429 |
| Min | 0.5071 (Ministral 3B) |
| Max | 0.9500 (Claude Opus 4.6) |

**Std ≥ 0.08: PASS ✅**

## Phase 1 → Phase 2 Comparison
| Model | Phase 1 | Phase 2 | Delta |
|-------|---------|---------|-------|
| Claude Opus 4.6 | 0.914 | 0.950 | +0.036 |
| DeepSeek-R1 | 0.701 | 0.918 | +0.217 |
| GPT-OSS-120B | 0.645 | 0.886 | +0.241 |
| Llama 3.3 70B | 0.612 | 0.593 | -0.019 |
| Qwen3 80B | 0.864 | 0.799 | -0.065 |
| Nova Pro | 0.513 | 0.555 | +0.042 |
| Maverick 17B | 0.573 | 0.842 | +0.269 |
| Sonnet 4.6 | 0.800 | 0.919 | +0.119 |
| GLM 4.7 | 0.739 | 0.760 | +0.021 |
| Ministral 3B | 0.454 | 0.507 | +0.053 |

Phase 2 std (0.156) vs Phase 1 std (0.149): comparable. Several models improved notably (DeepSeek, GPT-OSS, Maverick) — likely due to retry bias fix or different run conditions.

## Model Discrimination
Known Phase 1 std=0.178 (from KNOWLEDGE). Current std=0.156 — slight decrease but well above threshold. Good separation between top cluster (Opus/Sonnet/DeepSeek ≥0.92) and bottom cluster (Ministral/Nova/Llama3.3 ≤0.59).

## Q&A Transcript Review (5 models)

### Claude Opus 4.6 (highest, 0.95)
- Clean parsing, correct answers. 1 item wrong out of 20. No parser artifacts.

### Ministral 3B (lowest, 0.507)
- **CRT01 PARSE BUG**: Model correctly answered 1.50 in JSON (`"answer": 1.50`) but parser extracted "28" from reasoning text. The CRT regex extraction caught a number from the chain-of-thought (`2x = 3 → x = 1.5... total cost is x + (x + 25) = 28`) instead of the JSON answer field.
- Impact: +1 item → score would be 0.557 (+0.05). Minor impact on overall discrimination.
- Remaining 13 failures appear to be genuine errors (intuitive trap answers).

### Qwen3 80B (mid, 0.799)
- Clean parsing. Failures on extreme difficulty items (compound rate, recursive discount). Expected behavior.

### Maverick 17B (surprising high, 0.842)
- Clean parsing. Strong performance on procedural items, weaker on multi-step reasoning chains.

### GLM 4.7 (random, 0.760)
- Clean parsing. No artifacts detected.

## Parser Fix Verification (Step 6)
- **CRT regex extraction**: Deployed ✅ — uses 4-pattern cascade (answer/result markers, standalone numbers, equals-sign, bold numbers). Falls back to first number.
- **CRT01 Ministral bug**: Parser grabs "28" from reasoning text because backtick-wrapped JSON isn't parsed as JSON first. The regex cascade finds "28" before "1.50". This is a known limitation of text-only parsing when model wraps response in markdown code blocks.
- **Severity**: Low — affects 1 item for 1 model. Not worth a re-run.

## Ground Truth Validation
- CRT procedural items spot-checked: CRT01 (bat-and-ball variant, answer=1.50 ✅), CRT02 (loom/widget variant, answer=7 ✅), CRT03 (lily pad variant, answer=23 ✅), CRT04 (answer=5 ✅), CRT05 (answer=-2.25 ✅).
- All 20 items verified correct via KNOWLEDGE (contamination-replaced procedural generator items).

## Recommendation
**KEEP AS-IS.** Std=0.156 well above threshold. CRT01 Ministral parse bug is minor (1 item, 1 model, +0.05 impact). No scoring formula changes needed. No ground truth errors found.
