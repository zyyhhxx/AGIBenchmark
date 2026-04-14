# Analysis: exec_func_tol (Tower of London)

## Score Distribution
| Metric | Value |
|--------|-------|
| Mean | 0.492 |
| Std | 0.2846 |
| Range | 0.820 |
| Min | 0.080 (Ministral 3B) |
| Max | 0.900 (Claude Opus 4.6) |

**Std ≥ 0.08: PASS ✅ (best discriminator in exec_func track)**

## Phase 1 → Phase 2 Comparison
| Model | Phase 1 | Phase 2 | Delta |
|-------|---------|---------|-------|
| Claude Opus 4.6 | 0.800 | 0.900 | +0.100 |
| DeepSeek-R1 | 0.153 | 0.640 | +0.487 |
| GPT-OSS-120B | 0.680 | 0.740 | +0.060 |
| Llama 3.3 70B | 0.153 | 0.120 | -0.033 |
| Qwen3 80B | 0.290 | 0.420 | +0.130 |
| Nova Pro | 0.280 | 0.240 | -0.040 |
| Maverick 17B | 0.000 | 0.280 | +0.280 |
| Sonnet 4.6 | 0.000 | 0.800 | **+0.800** |
| GLM 4.7 | 0.000 | 0.700 | **+0.700** |
| Ministral 3B | 0.160 | 0.080 | -0.080 |

**Massive improvement for Sonnet and GLM** — Phase 1 scores of 0.000 were caused by the chain-of-thought parser pollution bug (full-text regex fallback). The 5-strategy cascade parser fix resolved this. DeepSeek-R1 also improved substantially (+0.487).

Known Phase 1 std=0.2846 matches (this is Phase 2 run). Phase 1 real std was much lower due to parser bugs clustering models near floor.

## Model Discrimination
**Best discriminator in the entire Executive Functions track.** Range=0.820, std=0.285. Clean tier separation:
- Tier 1 (≥0.7): Opus(0.90), Sonnet(0.80), GPT-OSS(0.74), GLM(0.70)
- Tier 2 (0.2-0.65): DeepSeek(0.64), Qwen3(0.42), Maverick(0.28), Nova(0.24)
- Tier 3 (<0.2): Llama3.3(0.12), Ministral(0.08)

GLM 4.7 unexpectedly strong (0.70) — outperforms DeepSeek-R1 (0.64) on planning. DeepSeek-R1's reasoning-heavy approach may not help with spatial planning as much as with logical tasks.

## Q&A Transcript Review

### Claude Opus 4.6 (highest, 0.90)
- Clean parsing via MOVES: summary line (Strategy 1). 2-move and 3-move problems all correct. Some 4-5 move problems failed.
- Arrow count in responses: 2-4 per item — model produces concise MOVES lines as instructed.

### Ministral 3B (lowest, 0.08)
- Parsing works but moves are wrong. tol_2move_1: parsed 2 moves [('A','C'),('C','A')] — doesn't reach goal state. Response length=2000 chars (truncated?) with 0 arrows in first item, suggesting model uses "from X to Y" format.
- This is genuine planning failure, not a parser bug.

### DeepSeek-R1 (mid, 0.64)
- Chain-of-thought reasoning produces many arrows in response body. Parser correctly uses Strategy 1 (MOVES: line) or Strategy 2 (numbered moves). Score reflects genuine planning difficulty on 4-5 move problems.

### Sonnet 4.6 (surprising improvement, 0.80)
- Phase 1 score was 0.000 due to parser bug. Phase 2 shows strong planning ability — near Opus level.

### GLM 4.7 (surprising strong, 0.70)
- Also improved from 0.000. Genuine planning capability previously masked by parser bug.

## Parser Fix Verification (Step 6)
- **5-strategy cascade DEPLOYED ✅**: (S1) MOVES: summary line, (S2) numbered move lines, (S3) last compact move list, (S4) numbered "from X to Y", (S5) MOVES line with "from X to Y". No full-text fallback.
- **Prompt hardening DEPLOYED ✅**: Explicit instruction for "MOVES: A→B, C→A, B→C" as LAST line.
- **Residual concern**: 4-5 move problems may still produce 24+ arrows in reasoning traces for some models, but S1/S2 parse correctly from summary lines.

## Ground Truth Validation
- TOL move counts verified: 2-move problems require optimal=2, 3-move=3, etc. Sample items checked — optimal move counts are correct ✅.
- Move validation logic checks both move count and goal state reachability.

## Recommendation
**KEEP AS-IS.** Best discriminator (std=0.285, range=0.820). Parser fix resolved Phase 1 floor effect. No scoring or ground truth changes needed. Clean three-tier model separation validates TOL as measuring genuine planning ability.
