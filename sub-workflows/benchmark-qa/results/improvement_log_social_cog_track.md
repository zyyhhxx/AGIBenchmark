# Improvement Log: Social Cognition Track

## Track Summary

All 4 social cognition benchmarks were reviewed and QA'd (benchmark-qa task 015).
3 benchmarks were KEEP AS-IS. 1 benchmark (sarcasm) required redesign.

**Final track status:** All 4 benchmarks PASS std ≥ 0.08 ✅

---

## Benchmark 1: social_cog_emotional_prosody — KEEP AS-IS

**Score distribution:**
| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 0.564 |
| Claude Sonnet 4.6 | 0.504 |
| Llama 4 Maverick 17B | 0.476 |
| Qwen3 Next 80B | 0.413 |
| GLM 4.7 | 0.370 |
| DeepSeek-R1 | 0.331 |
| Nova Pro | 0.259 |
| GPT-OSS-120B | 0.268 |
| Llama 3.3 70B | 0.301 |
| Ministral 3B | 0.266 |

**Stats:** mean=0.3549, std=0.0888, range=0.2958

**Verdict:** KEEP AS-IS — std=0.0888 ≥ 0.08 ✅. Hardest of the 4 benchmarks (mean=0.355).
Genuine frontier challenge — even top model Claude Opus only scores 0.564.
Inferring emotion from described vocal/physical cues remains difficult for all models.

**Rationale for no change:** Low mean reflects genuine task difficulty, not benchmark flaws.
No ground truth errors found. Parsing artifacts resolved by retry bias fix (schema= removed).

---

## Benchmark 2: social_cog_false_belief — KEEP AS-IS

**Score distribution:**
| Model | Score |
|-------|-------|
| Llama 3.3 70B | 0.8625 |
| Qwen3 Next 80B | 0.8625 |
| DeepSeek-R1 | 0.8000 |
| Claude Opus 4.6 | 0.7875 |
| GLM 4.7 | 0.7625 |
| Nova Pro | 0.7375 |
| Claude Sonnet 4.6 | 0.6875 |
| Llama 4 Maverick 17B | 0.6500 |
| GPT-OSS-120B | 0.6125 |
| Ministral 3B | 0.5625 |

**Stats:** mean=0.7069, std=0.1128, range=0.3000

**Verdict:** KEEP AS-IS — std=0.1128 ≥ 0.08 ✅. Mid-range scores with good discrimination.

**Key finding:** Claude Opus 4.6 fails 8/34 fourth-order ToM items (collapses nested belief chains
to ground truth). This is a genuine cognitive failure at 4th-order nested perspective, not a parsing
artifact. Consistent failure mode. Tier weights: 0.00/0.00/0.05/0.70/0.25 (code is authoritative).

---

## Benchmark 3: social_cog_pragmatic — KEEP AS-IS

**Score distribution:**
| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 0.8112 |
| Claude Sonnet 4.6 | 0.7003 |
| Nova Pro | 0.3601 |
| DeepSeek-R1 | 0.4559 |
| Llama 4 Maverick 17B | 0.5218 |
| GPT-OSS-120B | 0.4986 |
| Qwen3 Next 80B | 0.3827 |
| GLM 4.7 | 0.4503 |
| Llama 3.3 70B | 0.2356 |
| Ministral 3B | 0.2936 |

**Stats:** mean=0.4786, std=0.1622, range=0.5756

**Verdict:** KEEP AS-IS — std=0.1622 ≥ 0.08 ✅. Best discriminator of the 4 benchmarks (range=0.576).
3-tier design (direct 0.15 / indirect 0.35 / complex 0.50) works well.

**Key finding:** Llama 3.3 70B scores 0.236 on pragmatic vs 0.863 on false_belief — large intra-model
gap showing pragmatic inference harder than explicit ToM for smaller instruction-tuned models.

---

## Benchmark 4: social_cog_sarcasm — REVISED ✅

**Redesign:** Flat 40-item benchmark → 3-tier 85-item benchmark.

**Before (v1, 40 flat items):**
- mean=0.9772, std=0.0251, range=0.0891 — FAIL (std < 0.08)
- All models ≥0.909; trivially solved by all models including Ministral 3B

**After (v2, 85 items, 3-tier):**
| Model | Score |
|-------|-------|
| Claude Opus 4.6 | 0.9680 |
| Llama 3.3 70B | 0.9454 |
| GLM 4.7 | 0.9186 |
| Llama 4 Maverick 17B | 0.9184 |
| Claude Sonnet 4.6 | 0.8874 |
| Nova Pro | 0.8623 |
| DeepSeek-R1 | 0.8360 |
| GPT-OSS-120B | 0.8075 |
| Ministral 3B | 0.7162 |
| Qwen3 Next 80B | 0.6198 |

- **mean=0.8480, std=0.1034, range=0.3482** — PASS ✅ (4.1× std improvement)
- Weighted scoring: 0.05×tier1 + 0.15×tier2 + 0.80×tier3
- Tier 3 (subtle/deadpan/cultural): primary discriminator
- Hardest items: S45 (professional obligatory positivity), S46 (chef with impossible dietary restrictions)

See `improvement_log_social_cog_sarcasm.md` for full details.

---

## Track-Level Statistics

| Benchmark | mean | std | range | Status |
|-----------|------|-----|-------|--------|
| emotional_prosody | 0.355 | 0.089 | 0.296 | KEEP ✅ |
| false_belief | 0.707 | 0.113 | 0.300 | KEEP ✅ |
| pragmatic | 0.479 | 0.162 | 0.576 | KEEP ✅ |
| sarcasm (v2) | 0.848 | 0.103 | 0.348 | REVISED ✅ |

**Track average std: 0.117** (1.5× above 0.08 threshold) — all benchmarks healthy.

## QA Process

- Retry bias fix applied to all 4 benchmarks (schema= parameter removed)
- Phase 1 and Phase 2 runs completed for all benchmarks
- QA analysis files created: `results/analysis_social_cog_{benchmark}.md`
- Sarcasm redesign confirmed working via full 10-model re-run
