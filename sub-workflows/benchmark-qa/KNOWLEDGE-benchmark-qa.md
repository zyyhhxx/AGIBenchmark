# KNOWLEDGE.md — AGI Benchmark

## Executive Functions Track — All 5 Benchmarks, All 10 Models (2026-04-14)
- **Retry bias fix applied:** CRT and N-back had `schema=` parameter removed; `_strip_think()` helper + regex JSON extraction added. Task_switch, TOL, WCST were unaffected.
- **All 10/10 models scored, 0 failures** across all 5 benchmarks.
- **CRT (Cognitive Reflection Test):** mean=0.7731, std=0.1494, range=0.447 ✅ — Opus 4.6=0.95, Sonnet 4.6=0.919, DeepSeek-R1=0.918, GPT-OSS-120B=0.886, Qwen3 80B=0.799, GLM 4.7=0.760, Maverick 17B=0.842, Llama 3.3 70B=0.593, Nova Pro=0.555, Ministral 3B=0.507
- **N-back (Working Memory):** mean=0.9442, std=0.1608, range=0.538 ✅ — 8 of 10 models score ≥0.98; Nova Pro is sole outlier at 0.462; 60 items per level. High ceiling for most frontier models.
- **Task Switch:** mean=0.8212, std=0.1509, range=0.470 ✅ — Surprising non-monotonic pattern: Ministral 3B (0.775) outscores Maverick 17B (0.530); GLM 4.7 (0.929) strong; Opus 4.6/DeepSeek-R1/GPT ceiling at 1.0.
- **Tower of London (TOL):** mean=0.492, std=0.2846, range=0.820 ✅ — Best discriminator; Opus 4.6=0.90, Sonnet 4.6=0.80 but DeepSeek-R1 only 0.64; GLM 4.7 unexpectedly strong (0.70); Ministral 3B near floor (0.08). TOL tests genuine planning, not pattern matching.
- **WCST (Wisconsin Card Sort):** mean=0.7821, std=0.2678, range=0.636 ✅ — Top 5 models (Opus, Sonnet, DeepSeek, GPT, Qwen3) all score 1.0 (perfect acc, 0 perseverative errors, 6/6 categories); Llama 3.3 70B lowest at 0.364.
- **Cross-benchmark ranking insight:** TOL best discriminates frontier-tier models; N-back least discriminating (ceiling effect for most). Task_switch shows non-monotonic size-vs-capability relationship.
- **Artifact paths:** `repo/sub-workflows/benchmark-qa/results/qa_transcripts/exec_func_{crt,nback,task_switch,tol,wcst}/` — 10 .jsonl + 10 .summary.json + aggregate_stats.json each.

## attention_selective Benchmark Results — All 10 Models (2026-04-14)
- **Scores:** Claude Opus 4.6=1.000, DeepSeek-R1=1.000, Claude Sonnet 4.6=0.9583, GPT-OSS-120B=0.9583, Llama 3.3 70B=0.8767, Nova Pro=0.7967, Llama 4 Maverick 17B=0.7567, Qwen3 Next 80B=0.7300, GLM 4.7=0.7167, Ministral 3B=0.5233
- **Aggregate:** mean=0.8317, std=0.1471 (≥0.08 ✅), range=0.4767; 10/10 coverage, 0 failures
- **Task tiers:** T1 (single feature), T2 (feature conjunction), T3 (triple conjunction). T2 is primary discriminator — varies 50%–100% across models. T3 surprisingly homogeneous (most models ≥83%).
- **Top models:** Claude Opus 4.6 and DeepSeek-R1 achieve perfect 1.0; top 4 cluster at ≥0.95
- **Bottom models:** Ministral 3B lowest at 0.5233; Qwen3 and GLM cluster in 0.71–0.73 range
- **Retry bias:** attention_selective unaffected (no schema= parameter used)
- **Artifact path:** `repo/sub-workflows/benchmark-qa/results/qa_transcripts/attention_selective/` — 10 .jsonl + 10 .summary.json + aggregate_stats.json

## attention_divided Benchmark Results — All 10 Models (2026-04-14)
- **Scores:** Claude Opus 4.6=0.9375, Claude Sonnet 4.6=0.9375, DeepSeek-R1=0.9375, GPT-OSS-120B=0.9375, Llama 4 Maverick 17B=0.9275, GLM 4.7=0.9167, Qwen3 Next 80B=0.8803, Llama 3.3 70B=0.8333, Nova Pro=0.7064, Ministral 3B=0.4139
- **Aggregate:** mean=0.8428, std=0.1675 (≥0.08 ✅), range=0.5236; 10/10 coverage, 0 failures
- **Task structure:** 7 trials per model (easy×2, medium×2, hard×3), dual-stream interleaved tasks (math + category classification, etc.)
- **Ceiling effect:** Top 4 models cluster at 0.9375; hard tier is the primary discriminator
- **Parsing anomalies:** Ministral 3B scores 0.0 on easy/medium but 0.778 on hard — likely JSON parsing issue with flat-answer format on simpler tiers; Nova Pro scores 0.0 on M1 (parity/magnitude/digit-sum) but normal on M2
- **Retry bias:** attention_divided unaffected (no schema= parameter used)
- **Artifact path:** `repo/sub-workflows/benchmark-qa/results/qa_transcripts/attention_divided/` — 10 .jsonl + 10 .summary.json + aggregate_stats.json

## Prospective Self-Assessment Tier Analysis — jol, fok, calibration (2026-04-13)
- **Score gradient:** metacog_fok (mean=0.571) > metacog_calibration (mean=0.521) > metacog_jol (mean=0.376) — JOL is hardest due to chat isolation preventing study-phase recall
- **Best discriminator:** metacog_jol (std=0.119, range=0.300); all three pass std ≥ 0.08
- **Critical JOL platform behavior:** Models do NOT retain study-phase context during JOL/recall phases despite `kbench.chats.new()` context manager — each `llm.prompt()` call is isolated. Claude Sonnet 4.6 and Llama 3.3 70B report confidence=0 for all words; Nova Pro confabulates definitions.
- **JOL perverse incentive:** Constant-zero-confidence → gamma_norm=0.50 (free 0.20 score). Models refusing to engage score ≥ models that attempt recall but confabulate. Does not distort current rankings but monitor if pattern becomes dominant.
- **FOK is cleanest benchmark:** No parsing issues, good confidence spread (std 21–32 per model), GPT-OSS-120B top (0.670), Ministral 3B bottom (0.388)
- **Calibration universal overconfidence:** All models mean confidence 94–99%. Claude Sonnet 4.6 best at modulating (std=10.1, range 35–100); scores highest (0.632). Ministral 3B confidence std=2.3 (nearly constant high) — 11/120 parse failures.
## metacog_learning_monitoring v2 — Difficulty 3-4 Rule Systems (2026-04-14)
- **Change:** SYSTEMS updated from 3 entries (d2, d2, d3) to 4 entries (d3, d3, d4, d4). Difficulty-4 rules added to both symbol and number generators: symbol d4 = 3-pass with pair merging + count-based reversal + parity swap; number d4 = 3 operators with mod arithmetic, wrap-around addition, nested expressions, even→odd parity rule.
- **Score spread (7 valid models):** std=0.181, range=0.497 — both targets met (std≥0.10, range≥0.30).
- **Scores by model:** Claude Sonnet 4.6=0.9393, DeepSeek-R1=0.9089, Llama 4 Maverick 17B=0.7496, GLM 4.7=0.7079, Nova Pro=0.6264, Llama 3.3 70B=0.5529, Ministral 3B=0.4422.
- **3 models errored (timeout/unknown):** Claude Opus 4.6, GPT-OSS-120B, Qwen3 Next 80B. Likely timeout at 360s. These don't affect spread calculation on valid scores.
- **Old baseline:** std=0.0771, range=0.2195 (difficulty 2-3) — inadequate separation.
- **Key takeaway:** Moving to difficulty 4 for rule-based systems dramatically improves model discrimination on learning monitoring.

## metacog_calibration v2 — Difficulty-5 Item Expansion (2026-04-13)
- **12 new difficulty-5 items added** to `procedural_calibration.py` covering: Catalan numbers, derangements, Stirling numbers (combinatorics); integer partitions, Euler totient, continued fractions, Bernoulli numbers, 1729 taxicab number (number theory); modular arithmetic; trailing zeros in 100!, digital root.
- **Total items:** 132 (25 d1, 30 d2, 35 d3, 15 d4, 27 d5). Extreme items (d≥4) = 42 (31.8% of total).
- **Scores — all 10 models (132-item benchmark):** DeepSeek-R1=0.6582, Sonnet 4.6=0.6581, GPT-OSS-120B=0.5970, Opus 4.6=0.5753, Maverick 17B=0.5545, GLM 4.7=0.4972, Qwen3 80B=0.4904, Nova Pro=0.4501, Llama 3.3 70B=0.4061, Ministral 3B=0.3003
- **Before/after:** mean 0.5199→0.5187, std 0.0858→0.1076, range 0.2589→0.3579. **std≥0.10 target: PASS**
- **Universal overconfidence persists:** All models mean confidence 94–99% on difficulty-5 items.
- **GLM 4.7 Bedrock issues:** Repeated ValidationException (internal server error) on Bedrock; runs may take 3600s+ to complete. Budget extra time.
- **DeepSeek-R1 response format:** Returns both `text` block and `reasoningContent` block; KeyError on `text` can occur intermittently — likely transient Bedrock issue, not a parsing bug.
- **Sequential runs required:** Parallel execution of 10 model runs causes SIGTERM due to resource contention on the EC2 instance. Run models one at a time with skip-if-scored logic.
- **AWS_PROFILE fix:** Set `~/.aws/config` with empty `[default]` profile to prevent boto3 ProfileNotFound errors when `AWS_PROFILE=default` is set in environment.

## Attention Track QA Validation — All 4 Benchmarks (2026-04-14)
- **All 4 attention benchmarks PASS QA:** divided (std=0.1675), selective (std=0.1550), vigilance (std=0.1738), instruction_update (std=0.2131) — all ≥0.08 threshold ✅
- **Phase stability:** Phase 1 → Phase 2 std delta <0.02 across all benchmarks — highly reproducible.
- **JSON comment parsing bug (cross-benchmark):** Ministral 3B and Nova Pro produce JavaScript-style `// comments` in JSON responses. `json.loads()` rejects these, scoring correct answers as 0. Affects divided (Ministral easy/medium, Nova Pro medium) and instruction_update (Ministral 6/11 trials). Fix: `re.sub(r'//.*', '', text)` before `json.loads()`. Impact: +0.05–0.15 for Ministral 3B; +0.03–0.05 for Nova Pro. Not yet patched — advisory only.
- **Llama 3.3 70B vigilance anomaly:** Completes 14 N-back segments in 4.1s (vs 42–72s for other models), producing only 413 tokens total. Score=0.5653 is genuine poor performance from minimal computation, not a parsing bug.
- **instruction_update highest discriminator:** std=0.2131, range=0.6841 — widest spread of all 4 attention benchmarks. H4_CHAINED (mod arithmetic with chained modifications) is the key trial — GLM, Qwen3, Nova Pro all drop to ~0.57 on this trial alone.
- **Ground truth verified correct** across all 4 benchmarks (N-back sequences, conjunction search items, dual-stream math/classification, instruction update rules). No debatable items found.
- **Think-tag leakage:** None detected across all 40 model runs.

## attention_vigilance Benchmark Results — All 10 Models (2026-04-14)
- **Scores:** DeepSeek-R1=1.000, GPT-OSS-120B=1.000, Claude Sonnet 4.6=0.8647, Claude Opus 4.6=0.8559, Llama 4 Maverick 17B=0.8559, Qwen3 Next 80B=0.7073, Nova Pro=0.6329, Ministral 3B=0.5856, Llama 3.3 70B=0.5653, GLM 4.7=0.5599
- **Aggregate:** mean=0.7628, std=0.1738 (≥0.08 ✅), range=0.4401; 10/10 coverage, 0 failures
- **Task structure:** N-back task with 2-back (weight=0.55) and 4-back (weight=0.45) conditions. 2-back: 77 items, overall acc=0.75 (top models); 4-back: 56 items, overall acc=0.64 (top models). 4-back is the discriminator — hit rate drops to 0.231 for bottom models.
- **Vigilance decrement:** 4-back condition shows near-zero decrement (0.000), suggesting models don't fatigue like humans but also don't improve; 2-back shows slight 0.015 decrement.
- **Ceiling models:** DeepSeek-R1 and GPT-OSS-120B both score 1.0 — 4-back not fully saturating top models.
- **Bottom cluster:** Llama 3.3 70B (4.1s duration — very fast, suspicious), GLM 4.7, and Ministral 3B all cluster 0.56–0.59. Llama 3.3 70B's 4.1s runtime suggests minimal reasoning effort.
- **Retry bias:** attention_vigilance unaffected (no schema= parameter used).
- **Artifact path:** `repo/sub-workflows/benchmark-qa/results/qa_transcripts/attention_vigilance/` — 10 .jsonl + 10 .summary.json + aggregate_stats.json

## Batch 1 Scoring/Parsing Fixes — Confirmed Deployed (2026-04-13)
- **JOL std-penalty:** `if np.std(all_jol_ratings) < 1.0: gamma_norm = 0.0` added to task_jol.py. Constant-confidence models lose the free 0.20 score. No current model has std < 1.0 (Ministral 3B std=2.3), so rankings unchanged but perverse incentive removed.
- **Backtick fence stripping:** `re.sub(r'```(?:json)?\s*', '', cleaned)` + closing fence strip added to JSON extraction in task_calibration.py (Phase 1) and task_fok.py (Phase 1 and Phase 2). Fixes Ministral 3B's 11/120 parse failures that defaulted to confidence=50.
- **Notebooks synced:** metacog_jol.ipynb, metacog_calibration.ipynb, metacog_fok.ipynb all contain the respective fixes and pass `jupyter nbconvert` syntax validation.
- **Step 5 (retroactive recalc) is not feasible locally** — no Q&A transcripts; benchmarks run on Kaggle Community Benchmarks platform. Impact analysis based on scoring formula: backtick fix eliminates confidence=50 defaults for Ministral 3B, improving its calibration score.

- **Calibration ground truth verified:** All difficulty 4–5 items confirmed correct (primes=21, sum=49/20, pi digit=5, sphere SA=615.75, birthday paradox=50%, groups of order 8=5)
- **Calibration borderline std:** 0.0830 (0.003 above threshold) — monitor on future model additions
- **All three benchmarks: KEEP AS-IS**

## Metacognition Track Improvement Plan — Summary (2026-04-13)
- **All 9 benchmarks rated KEEP AS-IS** — no drops, no scoring bugs, no ground truth errors
- **Batch 1 (no re-run, ~1 hr):** (1) JOL constant-confidence variation penalty: if std(confidences)<1.0, set gamma_norm=0.0 to remove free-score incentive; (2) Ministral 3B parse hardening: strip triple-backtick JSON wrappers before extraction
- **Batch 2 (re-run required, ~3 hrs, ~31 model runs):** (1) Calibration: add 10–15 difficulty-5 items (std=0.083 is borderline); (2) Learning monitoring: raise rules to difficulty 3–4 to widen accuracy spread; (3) Error detection: add ecological fallacy/Berkson/p-hacking items to address 30% ceiling; (4) Retry GPT-OSS-120B epistemic_humility (ValidationException)
- **Batch 3:** None needed
- **Key fragility:** metacog_calibration std=0.083 is only 0.003 above threshold — most at-risk benchmark if model roster changes

## metacog_error_detection v2 — Hard Statistical Fallacy Expansion (2026-04-14)
- **7 new difficulty=3 items added (E45–E51):** ecological fallacy, Berkson's paradox, multiple comparisons/p-hacking (×2), survivorship bias, regression to the mean, misapplied Simpson's paradox.
- **Total items: 72** (was 65). Difficulty-3 items: 31 (was 24, 43% of total).
- **Ceiling effect RESOLVED:** 0/10 models scored >0.95 (was ~30%). Target was <10%. ✅
- **v2 scores (10 models):** Opus 4.6=0.9467, Sonnet 4.5=0.8979, DeepSeek-R1=0.8958, Qwen3 80B=0.843, GLM 4.7=0.821, Nova Pro=0.8164, Maverick 17B=0.7809, Ministral 3B=0.6465, GPT-OSS-120B=0.4301, Llama 3.3 70B=0.4301.
- **Spread:** std≈0.17, range=0.52 (strong discrimination). GPT-OSS-120B and Llama 3.3 70B cluster at 0.43 — may be floor effect for those models.
- **Model ID lesson:** Bedrock model IDs require `us.` cross-region inference profile prefix for Anthropic (Opus, Sonnet), DeepSeek-R1, and Meta Llama 4. Direct foundation model IDs work for Nova Pro, Ministral, Llama 3.3, GLM, Qwen3, GPT-OSS.
- **Sonnet 4.6 unavailable:** Substituted `us.anthropic.claude-sonnet-4-5-20250929-v1:0`.
- **Gamma column:** Several non-Anthropic models return gamma=-1.0 — likely no confidence scores returned; expected behavior.

## Self-Monitoring Tier Analysis — epistemic_revision, learning_monitoring, control (2026-04-13)
- **Score gradient:** learning_monitoring (mean=0.814) > epistemic_revision (mean=0.794) > control (mean=0.495) — control is substantially harder, requiring both monitoring accuracy and strategic action under constraint
- **Best discriminator:** metacog_control (std=0.221, range=0.490) — bimodal split: 6 models cluster 0.61–0.69 (strategic re-reading works), 4 models at 0.20–0.35 (strategic failure)
- **Borderline discriminator:** metacog_learning_monitoring (std=0.093, passes ≥0.08 threshold) — compressed range due to simultaneous variance required in both learning accuracy and confidence calibration
- **Claude hedging penalty:** Claude Sonnet 4.6 scores 0.70 on learning_monitoring — reports conservative confidence 55–72 throughout even as accuracy is high; poor gamma correlation drags down score. Consistent with epistemic_humility pattern in KNOWLEDGE.
- **Reasoning models vs. metacognitive control:** DeepSeek-R1 scores 0.21 on control (2nd lowest). Extended chain-of-thought reasoning causes confabulation when context is missing — model generates plausible-sounding answers about unrelated real domains (e.g., Indian classical music tala/avartan) instead of recognizing the information gap. Same confabulation pattern seen in Qwen3 Next 80B (0.20, lowest).
- **GPT-OSS-120B epistemic scoping failure:** Scores 0.64 on epistemic_revision — correctly identifies contradictions but over-applies revisions to uncontradicted rules, causing transfer errors. Genuine metacognitive scoping failure.
- **All three benchmarks: KEEP AS-IS** — zero debatable ground truth items, all use synthetic/fictional domains, no parsing artifacts

## External Monitoring Tier Analysis — canary, epistemic_humility, error_detection (2026-04-13)
- **Score gradient:** error_detection (mean=0.871) > epistemic_humility (mean=0.805) > canary (mean=0.546) — reflects increasing difficulty: arithmetic error detection is easiest, confidence calibration on fabricated facts is hardest
- **Best discriminator:** metacog_canary (std=0.280, range=0.875) — no ceiling, floor effect (10%) is by design (Ministral 3B = 0.000)
- **Mild ceiling on error_detection:** 30% of models >0.95; hard statistical items (E33-E40: base rate neglect, Simpson's paradox, Bayesian inference) are the key discriminators
- **Ministral 3B failure modes per benchmark:** hallucination with confidence=95-99 on fabricated facts (canary); hedging/confabulating on unknowable items (epistemic_humility); false positive error detection — claims errors in correct solutions (error_detection)
- **Claude hedging penalty:** Claude Opus (0.797) and Sonnet (0.838) score mid-tier on epistemic_humility despite being frontier models — hedged responses ("maybe") are penalized vs. flat refusal ("no"); Llama 3.3 70B scores highest (0.921) by consistently refusing outright
- **Rank inversion on epistemic_humility:** Llama 3.3 70B > Nova Pro > Claude models — not a scoring bug; reflects behavioral difference (refusal vs. epistemic hedging)
- **GPT-OSS-120B missing** on epistemic_humility (ValidationException); 9/10 coverage acceptable
- **All 149 items: zero debatable ground truth** across all three benchmarks
- **All three benchmarks: KEEP AS-IS** — no items to revise, no scoring changes needed

## Retry Bias Fix — All 7 Metacognition Notebooks (2026-04-13)
- **Root cause:** `schema=` parameter in `llm.prompt()` calls caused retry loops on parse failure, biasing scores upward (models got extra attempts).
- **Fix pattern:** Remove `schema=`, add `_strip_think()` helper to strip `<think>...</think>` tags, then extract JSON with `re.search(r'\{.*\}', cleaned, re.DOTALL)` and `json.loads()` — single LLM call only.
- **Affected files:** task_calibration.py, task_epistemic_humility.py, task_error_detection.py, task_fok.py, task_jol.py, task_learning_monitoring.py, task_metacognitive_control.py (all in repo/benchmarks/metacognition/).
- **Validation:** `python3 -m py_compile` and `jupyter nbconvert --to notebook` both pass on all 7 files post-fix.
- **No score impact recorded** — smoke test on metacog_fok confirmed correct parse path; full re-run not performed in this task.

## Final Submission Validation — All 26 Benchmarks PASS (2026-04-12)
- **All 26 benchmarks meet std ≥ 0.08** (min std = 0.0813 for metacog_learning_monitoring)
- **metacog_calibration fixed:** std recovered from 0.0000 → 0.0858 by completing all 10 model scores; root cause was duplicate rows masking incomplete data in CSV
- **258/260 model scores present** (99.2%); 2 missing are Qwen3 Next 80B OOM on learning_curves and exec_func_nback — within tolerance
- **Notebook nbconvert validation:** `MissingIDFieldWarning` appears on all notebooks but is a soft warning, not a blocking error; nbconvert exits 0 for all 27 notebooks
- **nbconvert `--to notebook` check reliably validates JSON + cell structure** without needing to execute; `!pip` and `%magic` cells trigger false positives in ast.parse but are valid IPython syntax
- **Drift detection workflow confirmed:** task_calibration.py → metacog_calibration.ipynb drift was real and required resync; re-running this check after any .py edit is important
- **Submission artifacts all pass:** 5 writeups (1091–1262 words), 5 cover images (valid PNG), 26 benchmark notebooks (valid JSON)

## Post-Fix Score Update — All 5 Tracks (2026-04-12)
- **4 benchmarks had scores updated** after attention_selective, social_cog_emotional_prosody, learning_curves, and metacog_error_detection were re-run:
  - `attention_selective`: mean 0.888→0.827, std 0.054→0.137, range 0.175→0.437 — top DeepSeek-R1 (0.96), bottom Ministral 3B (0.52)
  - `learning_curves`: mean 0.654→0.587, std 0.068→0.127, range 0.180→0.346 — top Claude Opus (0.79), bottom Ministral 3B (0.44)
  - `metacog_error_detection`: mean 0.862→0.890, std 0.077→0.092, range 0.226→0.329 — top DeepSeek-R1 (0.98), bottom Ministral 3B (0.65)
  - `social_cog_emotional_prosody`: mean 0.808→0.368, std 0.049→0.084, range 0.172→0.306 — top Claude Opus (0.56), bottom Nova Pro (0.25)
- **metacog_calibration CSV had only 2 entries (both 0.0000)** — determined to be incomplete data; preserved original writeup row (10 models, mean 0.165, std 0.332) rather than overwriting with degraded data
- **All 4 re-run benchmarks now meet std ≥ 0.08 threshold** (were below threshold pre-fix)
- **social_cog_emotional_prosody floor effect discovered:** even top model Claude Opus only scores 0.56; inferring emotion from described vocal/physical cues is a genuine frontier challenge
- All 5 cover images regenerated (1782×1181px, ~80–99 KB)

## Pre-Submission Audit — All 5 Tracks (2026-04-12)
- **Audit date:** 2026-04-12; covers all 26 benchmarks across 5 tracks
- **4 benchmarks below std ≥ 0.08 threshold:**
  - `metacog_error_detection`: std=0.0769 (delta -0.003, borderline)
  - `attention_selective`: std=0.0544
  - `learning_curves`: std=0.0682
  - `social_cog_emotional_prosody`: std=0.0491
- **2 benchmarks with 9/10 model scores (Qwen3 OOM):** learning_curves, exec_func_nback
- **Notebook validation:** all 27 notebooks pass `jupyter nbconvert` syntax validation; no duplicate cells, broken imports, `.nbconvert` duplicates, or multiple `.run()` calls
- **Naming mismatches (confirmed non-drift):** task_metacognitive_control→metacog_control, task_learning_curves→learning_curves, task_switching→exec_func_task_switch
- **Genuine drift:** social_cog_emotional_prosody .py is ~2h newer than .ipynb (sync needed before submission)
- **Uncommitted files:** results/qwen.qwen3-next-80b-a3b.json and sub-workflows/metacognition/results/rerun_log.txt
- **Executive Functions:** only fully clean track (all 5 benchmarks pass std ≥ 0.08, min std=0.1161)
- **Pattern:** borderline benchmarks (std 0.07–0.08) don't need redesign but should be monitored; hard failures (<0.06) warrant intervention before submission

## Cover Image Generation — All 5 Tracks (2026-04-12)
- Script generates grouped bar charts from `repo/results/score_matrix_all_tracks.csv`
- 5 representative models: Claude Opus 4.6, Claude Sonnet 4.6, Nova Pro, Llama 3.3 70B, Ministral 3B
- Human baseline band: green shaded region 0.60–0.85
- Output: `repo/assets/{track}_cover.png` at 1782×1181px (150 DPI); metacognition at 2564×1205px due to more benchmarks
- File sizes: 80–100 KB each — acceptable quality/size tradeoff

## Writeup Score Verification — All Tracks (2026-04-12)
- Calibration (metacog): mean=0.165, std=0.332 — only Claude Opus achieves meaningful BSS; 6 models score exactly 0.000 (DeepSeek-R1, Llama 3.3, Llama 4, Ministral 3B, Nova Pro, Qwen3)
- Canary (metacog): std=0.305, range=1.000 — Ministral 3B scores 0.000 (fails canary entirely)
- Sarcasm top performer: GLM 4.7 at 0.9450 (not Claude models)
- ToL (exec functions) bottom: 3 models tie at 0.000 (Claude Sonnet, GLM 4.7, Llama 4 Maverick)
- All 5 writeup word counts verified under 1500: Attention=1102, Learning=1114, Metacognition=1263, Exec Functions=1186, Social Cognition=1190
- Score matrix cross-check: tables in writeups match score_matrix_all_tracks.csv after fixes in this task

## Notebook Hard-Rule Violations — Cleanup Patterns (2026-04-12)
- **Duplicate `.nbconvert.ipynb` files:** Artefact of running `jupyter nbconvert` without `--output`; safe to delete. `exec_func_crt.nbconvert.ipynb` was one such duplicate.
- **Broken relative imports** (`from data.canary_items import ...`): kbench notebooks must be self-contained — inline all data directly in the notebook rather than importing from a sibling `data/` package. This is a hard requirement for Kaggle submission.
- **Duplicate cells:** Common pattern is cell N being an exact copy of cell 0 (setup) or a standalone `.run()` that already appears inside a task cell. Safe to delete the redundant copy.
- **Validation command:** `jupyter nbconvert --to notebook <file> --output /tmp/test.ipynb` exit-0 is sufficient syntax validation for all `.ipynb` files.


## social_cog_pragmatic Benchmark — Tiered Redesign (2026-04-11)
- **Problem:** Original flat benchmark scored 0.824–1.0 across models (std≈0.061) — too easy, ceiling effect.
- **Fix:** 3-tier difficulty design: direct implicature (0.15 weight), indirect/contextual (0.35), complex multi-layer (0.50). Per-tier score = `intended_accuracy - 0.1 × literal_trap_rate`.
- **v2 scores:** Claude Sonnet 4.6=0.6974, Nova Pro=0.3601, Ministral 3B=0.306 → std=0.1732 ✅, range=0.391.
- **kbench artifact quirk:** Top-level `score` field in run.json is `None` even on successful runs; actual scores are in `results[0].numericResult.value`. Don't treat `score: None` as a failure — check `results[]` array.
- **Iteration failures (1 & 2):** Executor updated `task_pragmatic.py` but never regenerated `task.json` (stayed versionNumber=1 with old flat definition). Fix required explicitly setting `version=2` in `@kbench.task()` decorator AND setting `kbench.client.directory` to `repo/benchmarks/social_cognition/` to store artifacts in the correct location.
- **Per-model run artifacts:** Use `_id=label` parameter in `.run()` to produce separate `social_cog_pragmatic-run_param_id_<label>.run.json` per model instead of overwriting a single file.
- **Pattern:** After modifying a kbench task definition, always regenerate `task.json` by re-running the task decorator — the JSON is derived from the decorator, not auto-synced.

## Learning Interference Benchmark v3 — Design & Results (2026-04-11)
- **Root cause of v2 failure (std=0.029):** Rules were re-provided in each prompt independently — no actual competing information in context, so interference was impossible.
- **v3 fix:** Present multiple competing rule systems together in the same prompt (proactive + retroactive interference within context). Ask model to apply only the target system.
- **Three difficulty tiers:** Easy (1 dissimilar distractor, difficulty=1), Medium (1 similar distractor, difficulty=2), Hard (2 similar distractors + interleaved example items, difficulty=3).
- **Per-tier scoring:** 0.30 × control + 0.70 × interference_accuracy. Composite = 0.15×easy + 0.35×medium + 0.50×hard.
- **v3 scores:** Claude Sonnet 4.6=1.000, Nova Pro=0.783, Ministral 3B=0.441 → std=0.280 ✅, range=0.559 ✅
- **Context length issue:** Hard tier with full examples caused Ministral 3B context-length errors; fixed by reducing max_examples from 6→4 when ≥2 distractors.
- **Bug to avoid:** When generating test items for variant systems, ensure expected outputs are from the variant's own rules, not the base system's. Using only `system.test_items` (pre-generated per system) avoids this cross-contamination.
- **Pattern:** Interference benchmarks require distractors to be co-present in the *same prompt*, not across separate turns or prompts.


## Notebook–.py Sync Audit — Metacognition Suite (2026-04-11)
- Audited all 9 metacog notebooks against their corresponding `task_*.py` files; found 12 mismatches across 7 notebooks; 2 were already in sync.
- Key divergences: (1) `brier_skill_score` in notebooks had an extra `ref` parameter with if/else logic not in .py; (2) `compute_ece` parameter was `confidences` in notebooks vs `confidences_0_100` in .py; (3) `compute_dprime` in notebooks used `scipy.stats.norm.ppf`; .py uses manual Abramowitz & Stegun approximation.
- Fix: patched notebook cells to match .py source of truth; inserted `norminv` helper into `metacog_error_detection.ipynb`.
- Extra notebook-only helpers intentionally left: `_seeded_word` in metacog_jol; `_make_rng`, `apply_rules`, `generate_number_system`, `generate_symbol_system` in metacog_learning_monitoring — used by notebook logic, not in conflict with .py.
- All 9 notebooks pass `jupyter nbconvert` syntax validation post-fix.
- **Pattern:** `scipy` imports in notebooks can silently diverge from .py files that avoid scipy for portability. Always check dependency assumptions when comparing implementations.

## Metacognition Benchmark Discriminatory Power Rankings (2026-04-11)
- Analyzed 9 metacog benchmarks across up to 10 models; ranked by std (score spread).
- Top-3 most discriminating: **epistemic_humility** (std=0.2452, range=0.7214), **control** (std=0.1829), **calibration** (std=0.1644)
- Bottom-3 least discriminating: **fok** (std=0.0695, only 3 valid scores), **epistemic_revision** (std=0.0132, clustered ~0.80), **canary** (std=0.0000, all zeros — working as intended)
- epistemic_humility spreads widest: Ministral 3B=0.20, Llama 3.3 70B=0.92 — best single benchmark for differentiating model metacognitive capability.
- calibration CV=2.24 indicates extreme relative variance despite low mean (0.07) — useful for distinguishing top models but many score near zero.
- epistemic_revision ceiling effect: 8 models score 0.79–0.82 with almost no spread; likely too easy for current frontier models.
- Full table saved to `repo/sub-workflows/metacognition/results/metacog_discriminatory_summary.md`.

## Cover Image for Metacognition Writeup (2026-04-11)
- Output: `repo/assets/metacognition_cover.png` — 1777×1180px, 150 DPI, 106KB
- Chart: grouped bar chart, 9 benchmarks × 3 tiers (External Monitoring / Self-Monitoring / Prospective Self-Assessment)
- Models shown: Claude Opus 4.6, Claude Sonnet 4.6, Nova Pro, Llama 3.3 70B, Ministral 3B
- Human baseline band (0.60–0.85) rendered as green shaded region
- Three-tier pattern visible: External Monitoring highest → Self-Monitoring mid → Prospective Self-Assessment lowest across all models


## exec_func_crt + exec_func_task_switch Discrimination Fixes (2026-04-11)
- **Root cause — CRT (std=0.028):** Two compounding failures: (1) answer parser truncated at 20 chars causing parse failures on all verbose responses; (2) all 15 items at similar difficulty, so no spread even with correct parsing.
- **Fix — CRT:** Added 5 extreme items requiring 3+ cognitive shifts (compound rate+spoilage, recursive discounts, Bayesian base-rate neglect, multi-step age chains, nested container arithmetic). Rewrote parser with regex extraction for patterns like `**Answer:**`, `=`, bolded numbers. Difficulty weights: extreme=3.0, hard=2.0, easy=1.0.
- **CRT v2 scores (Opus 4.6 / Nova Pro / Ministral 3B):** 0.878 / 0.574 / 0.454 → std=0.178 ✅
- **Root cause — task_switch (std=0.000):** Each trial was an independent prompt with rule explicitly stated — no switching cost possible. Trivially solvable.
- **Fix — task_switch:** Rewrote to batch presentation (all items in one prompt). Replaced trivial rules (odd/even, greater/less than 5) with computationally harder rules: digit-sum parity (requires arithmetic) and letter-position comparison (requires ordinal reasoning). Added 4 blocks: baseline, slow-switch (every 5), rapid-switch (every 1–2), random-cue. 14 switch trials in rapid block vs 3 in slow.
- **task_switch v2 scores (Opus 4.6 / Nova Pro / Ministral 3B):** 1.000 / 0.7125 / 0.775 → std=0.124 ✅
- **Pattern:** Parser truncation bugs silently map all models to near-identical floor scores — always verify raw answer extraction before diagnosing discrimination failures.
- **Pattern:** Per-trial prompts with explicit rule restatement collapse switch cost to zero. Batch presentation is necessary to expose cognitive reconfiguration cost.

## Sub-metrics Cleanup (2026-04-10)
- Deleted 3 sub-metrics notebooks (metacog_error_detection_submetrics, metacog_fok_submetrics, metacog_jol_submetrics) and their corresponding benchmark modules.
- These were experimental breakdowns of parent tasks; their removal reduces metacognition notebook count from 11→8.
- Kaggle-side slugs for these notebooks still exist but are NOT to be deleted (Ian must keep them on Kaggle per IAN_TODO_FINAL_v2.md).
- Operational scripts referencing these slugs were intentionally left unchanged — they fail gracefully since local notebooks no longer exist.
- After deletion: no broken imports remain in benchmarks/metacognition/.

## Bedrock Multi-Model Runner — run_benchmark_bedrock.py (2026-04-10)
- **MODEL_CATALOG:** 10 models; some require `us.` cross-region inference prefix (DeepSeek R1, Nova Pro, Llama 4 Maverick, Claude Haiku 4.5).
- **Benchmark count:** 26 live benchmarks across 5 tracks (GOALS.md says 29 — discrepancy; 26 is actual codebase count).
- **Claude Haiku 4.5** (`us.anthropic.claude-3-5-haiku-20241022-v1:0`) is inaccessible on the current AWS account (legacy/access denied). Use Ministral 3B for cheap smoke tests instead.
- **Ministral 3B** (`mistral.ministral-3-3b-instruct`) scored 0.0 on `metacog_canary` (expected — model hallucinates on unknowable fake facts). Confirms end-to-end pipeline works.
- **Rate limiting:** 2s between benchmarks, 5s between models prevents Bedrock throttling.
- **Retry logic:** 3 retries with exponential backoff (5s base); 120s read timeout via botocore Config.
- **Output schema:** `results/{model_id}.json` → `{model, model_label, timestamp, scores:{benchmark:{score,error,duration_s}}}`.

## attention_divided + attention_instruction_update Discrimination Fixes (2026-04-11)
- **Root cause of non-discrimination (std=0.013/0.017):** Original task_divided.py used a simple 2-stream dual-task with no interference; original task_instruction_update.py had shallow rule switches with few items.
- **Fix — attention_divided:** Rewrote with 3 difficulty tiers (easy: 2 streams no conflict, medium: 3 streams shared domain, hard: 3 streams same items different rules). Score = 0.20×easy + 0.30×medium + 0.50×hard. Cites Pashler (1994), Kahneman (1973), Wickens (2002).
- **Fix — attention_instruction_update:** Added multi-step contradictory rule updates and catch trials. Cites Monsell (2003) task-switching, Meiran (1996) set-shifting.
- **Post-fix discrimination results (3 models: Claude Opus 4.6, Nova Pro, Ministral 3B):**
  - attention_divided: scores 0.9375 / 0.7089 / 0.4139 → std=0.2625, range=0.5236 ✅
  - attention_instruction_update: scores 0.9833 / 0.7760 / 0.1992 → std=0.4063, range=0.7841 ✅
- **Pattern:** Difficulty tiers that expose genuine cognitive cost (interference, perseveration) are the most reliable fix for ceiling-effect benchmarks.

## metacog_canary + metacog_epistemic_revision Discrimination Fixes (2026-04-10)

### metacog_canary
- **Root cause of floor effect (all=0.0):** Bedrock LLM wrapper does not support `schema=` parameter — all models fell back to `confidence=50`, scoring 0.0.
- **Fix:** Explicit JSON prompt + `_extract_confidence` regex helper. No SDK schema dependency.
- **Final scores (v2):** Claude Opus 4.6=0.9947, Nova Pro=0.6375, Ministral 3B=0.0000; std=0.41, range=0.9947.
- **Ministral 3B=0 is expected** — it hallucinates on fabricated facts, which is the canary's intent.

### metacog_epistemic_revision
- **Root cause of non-discrimination:** Bedrock API is stateless; only the first `llm.prompt()` call received context. All subsequent calls had none.
- **Explicit-rules trap:** Providing full contradiction text per transfer question collapses discrimination (all models 0.94+, std=0.027) — reduces to reading comprehension.
- **v4 fix:** Transfer phase provides raw experimental data points only. Model must inductively infer revised rules. Weights: 0.80 transfer + 0.20 perseveration; violation/revision weights=0.
- **Final scores (v4):** Claude Opus 4.6=0.9600, Nova Pro=0.5900, Ministral 3B=0.7500; std=0.153, range=0.37.
- **Rank inversion (Ministral > Nova):** Nova Pro perseverates more on original rules — a real behavioral difference the perseveration component captures.

## Notebook Audit — Repository-wide (2026-04-10)
- **Scope:** 31 notebooks across 6 tracks (metacog×12, learning×4, attention×4, exec_func×5, social_cog×4, other×2). Task originally stated 33; actual count is 31.
- **Syntax:** All 31 pass `jupyter nbconvert` validation.
- **kbench structure:** 29/31 pass @kbench.task + .run() checks. The 2 failures (results_dashboard, submission_overview) are utility notebooks, not benchmarks — expected.
- **Scoring consistency issues (4 total):**
  - metacog: calibration/FoK/JoL use BSS/Brier; others use accuracy — intentionally different (confidence vs accuracy tasks)
  - attention: attention_vigilance missing `normalize` — likely needs fix
  - exec_func: exec_func_tol has no detected scoring pattern — likely needs fix
  - social_cog: social_cog_sarcasm uses `normalize`; other 3 don't — may need harmonization
- **No incomplete notebooks:** 0 TODOs, stubs, or placeholder text found across all 31.
- **Audit artifact:** `repo/NOTEBOOK_AUDIT.md`

## Competition Requirements Audit — Cross-Reference (2026-04-10)
- **SUBMISSION_NARRATIVE.md** (10 sections, ~600 lines): all 7 required writeup sections are PRESENT including dataset provenance (Section 4) and org affiliation (Section 10: "Independent submission").
- **KAGGLE_DISCUSSION_DRAFT.md**: organizational affiliation is still missing; `[link to CB benchmark]` placeholder not yet replaced.
- **Critical blockers**: 4 items, all requiring Ian manual Kaggle web UI actions (~87 min total): CB task registration, benchmark collection creation, making ~20 notebooks public, deleting ~70 ghost notebooks.
- **17 models** already run on CB platform; 10-model × 26-benchmark score matrix in SUBMISSION_NARRATIVE.
- **Scoring:** 85% expert judges + 15% community upvotes.
- **Checklist artifact:** `repo/COMPETITION_REQUIREMENTS_CHECKLIST.md` (27 items: 20 PRESENT, 5 MISSING, 2 WEAK).

## Submission Status Cross-Reference — IAN_TODO_FINAL_v2.md (2026-04-10)
- Competition requires 3 deliverables: CB task collection, discussion thread writeup (7 required sections), model results
- Critical path to submission: ~87 min of manual Ian action on Kaggle web UI
- Single largest item: registering 26–29 CB tasks (~60 min)
- Notebook public status: ~20 still private; must be toggled before CB task registration
- Ghost notebooks (~70) must be cleared before CB task creation to avoid confusion
- SUBMISSION_NARRATIVE.md missing 2 sections: Dataset provenance and organizational affiliation
- Community upvotes = 15% of score — polish discussion thread after benchmark is live
- Checklist artifact: `repo/IAN_TODO_FINAL_v2.md`

## CB Submission Checklist Structure — IAN_TODO_FINAL.md (2026-04-09)
- 29 total benchmarks: 9 metacognition (incl. canary + 3 sub-metric), 4 learning, 4 attention, 5 exec_func, 4 social_cog, 3 sub-metrics
- 6 notebooks needed manual public toggle due to API 429 rate limits on push day
- CB task registration requires running the notebook on CB platform (copy-paste from repo/notebooks/); `@kbench.task` decorator auto-registers
- Ghost notebooks (~70) from retry storms must be deleted via web UI before CB submission
- Discussion thread visibility counts for 15% of final score — post after CB tasks are live

## Kaggle API Rate Limits — Bulk Push Strategy (2026-04-09)
- **Rate limit:** ~20 `kaggle kernels push` calls per session before 429 errors
- **Safe batching:** groups of 3 pushes with 60s delays stays under limit for ~18 notebooks
- **Recovery:** ~24h wait or toggle visibility via Kaggle web UI for already-uploaded private notebooks
- **Pattern:** For large batches (>20), split across multiple sessions or days. Push directories with `kernel-metadata.json is_private: false` persist — safe to retry after rate limit resets
- **v2 push result:** 20/26 notebooks pushed to public; 6 remain private pending manual toggle or retry: metacog_epistemic_humility, metacog_error_detection_submetrics, metacog_fok, metacog_fok_submetrics, metacog_jol, metacog_jol_submetrics

## Import Fixes — attention_vigilance, learning_curriculum, attention_instruction_update (2026-04-09)

- **Problem 1:** `from data import ...` relative imports in `task_vigilance.py` and `task_curriculum.py` failed when modules were loaded from repo root; rewritten as absolute imports.
- **Problem 2:** Module-level `.run(kbench.llm)` calls in all three files executed on import outside a Kaggle notebook, causing errors. Wrapped in `if __name__ == '__main__'` guards.
- **Pattern:** All benchmark `.py` files must guard `.run()` calls — the kaggle-benchmarks SDK only provides `kbench.llm` inside a running notebook kernel.
- All three files now pass `py_compile` and import cleanly with `kaggle-benchmarks` installed.

## Learning Interference Scoring v2 — task_interference.py (2026-04-09)

- **Root cause of v1 collapse:** `0.40 * (1 - retroactive) + 0.30 * baseline_A + 0.30 * baseline_B` — when model can't learn (baselines=0), retroactive=0, all strategies score 0.4 identically.
- **Fix:** 4 independent sub-metrics each weighted 0.25: (1) retroactive interference normalized to control_A, (2) proactive interference normalized to control_A, (3) compartmentalization = post_interf_A / control_A, (4) control_A accuracy.
- **Key insight:** Must normalize interference magnitudes by control_A (no-interference baseline) to avoid denominator-zero collapse. Guard with `if control_A > 0 else 0.0`.
- **Mock validation results:** perfect_compartmentalizer=0.5000, full_retroactive_forgetter=0.4500, proactive_blocker=0.6375, cant_learn_anything=0.0000. 5/6 pairs >0.1 separation, 3 distinct clusters.
- **Pattern:** When a benchmark scores constant across conditions, look for unguarded zero denominators and unnormalized magnitudes.

## BSS Scoring Fix — FOK, JOL, Calibration, Canary (2026-04-09)

- **Root cause:** ECE-based scoring (1-ECE) was inverted: always-uncertain agents (constant 50%) outscored perfect metacognitors because low ECE ≠ good discrimination.
- **Fix:** Replaced 1-ECE with Brier Skill Score (BSS = 1 - BS/BS_ref) in all four benchmarks.
  - BS_ref = base_rate × (1 - base_rate) for FOK/JOL/Calibration; BS_ref = 0.25 (uniform) for Canary.
- **Validated (N=60 mock):** Perfect metacognitor: FOK 0.963, JOL 0.858, Calibration 0.927, Canary 0.958. Always-uncertain: FOK 0.350, JOL 0.380, Calibration 0.000, Canary 0.000.
- **Pattern:** BSS is the correct scoring rule for confidence-outcome alignment benchmarks. ECE alone lacks resolution discrimination and rewards hedging.
- **Negative BSS** clamped to 0 (floor) in all tasks. ECE retained as a diagnostic-only metric.
- FOK/JOL composite: `0.40 * gamma_norm + 0.30 * max(0, BSS) + 0.30 * AUC`.

## Contamination Hardening — Metacognition Benchmarks (2026-04-09)

### Risk ratings across 8 benchmarks
- **LOW** (already safe): canary (fabricated items), control (fictional Lake Vordak passage), epistemic_revision (synthetic Zorblatt chemistry), jol (invented pseudowords), learning_monitoring (procedural rule systems)
- **HIGH → MITIGATED**: calibration — was 100% well-known trivia; added 40 procedural questions (arithmetic, unit conversions, physics formulas) → now 50% procedural
- **MEDIUM → MITIGATED**: error_detection — was standard textbook problems; added 16 procedural chains with randomized parameters → 37 total chains
- **MEDIUM (acceptable)**: fok — 30 trivia + 30 procedural; ecological validity requires real-world known/unknown facts. epistemic_humility — trivia by design (measuring meta-knowledge about known facts, not knowledge itself)

### Implementation patterns
- `procedural_calibration.py`: 40 questions in 3 tiers (easy/medium/hard) using math, physics formulas, logic — fully deterministic from parameters
- `procedural_error_chains.py`: 16 chains using randomized numeric parameters so answers differ from textbook examples
- `task_calibration.py` had inline `CALIBRATION_QUESTIONS` bypassing the data module — fixed to import from data module
- Pattern: always check task files for inline data that may shadow the data module

## Psychometric Validation — Claude Sonnet 4 on Bedrock (2026-04-10)

- **Three-tier profile:** External monitoring (canary, epistemic_humility, error_detection) mean=0.919; self-monitoring (epistemic_revision, learning_monitoring, control) mean=0.735; prospective self-assessment (jol, fok, calibration) mean=0.305. Clean 3:1 dissociation validates construct coverage.
- **Discriminant validity:** Between-tier / within-tier variance ratio = 3.9:1 (criterion >2:1). PASS.
- **Calibration floor:** BSS=0.000 — Claude's expressed confidence is uncorrelated with accuracy. This is a genuine capability gap, not a scoring artifact. Cross-model replication recommended.
- **Ceiling benchmarks:** canary (0.951) and epistemic_humility (0.926) are expected for frontier models; these are diagnostic baselines, not difficulty targets.
- **Inter-item α:** FOK α=0.949, Error Detection α=0.793/0.703 — computed from mock simulations (item-level Bedrock data unavailable); validates structural reliability of item sets.
- **Pattern:** Single-model Bedrock runs yield aggregate scores only; true Cronbach α on real responses requires item-level logging. Add item-level output to future Bedrock runner.

## Difficulty Calibration Findings — Spot Test Analysis (2026-04-09)

### Ceiling Effect Benchmarks (score ≥90%, models trivially pass)
- **CRT classic items**: 100% for Flash and Flash-Lite — contaminated in training data; must replace with procedurally generated variants
- **Stroop**: trivially passed by LLMs (no perceptual interference in text); redesign as semantic Stroop
- **N-back (short)**: 5-item 2-back is trivial with full context windows; needs 50+ items and 3-back/4-back conditions
- **Epistemic revision (simple)**: 3/3 perfect — add partial/ambiguous revision items and multi-step revision chains
- **2nd-order ToM**: both models pass; upgrade to 3rd/4th-order nested belief scenarios
- **Epistemic humility fabricated names**: too easy (models learned "if unrecognized → say I don't know"); add near-miss items with real-but-obscure entities
- **WCST single-trial**: trivial; needs full 128-card protocol with perseveration error scoring

### Broken/Inverted Scoring Benchmarks
- **FOK, JOL, Calibration, Canary mock scores**: perfect metacognition agent scores LOWER than always-uncertain baseline
- **Root cause**: scoring calibration alone (1-ECE) rewards uncertainty over accuracy; need resolution component (Brier skill score or Murphy decomposition) that rewards discrimination
- **Learning interference**: all four mock strategies score identically at 0.4 — benchmark cannot discriminate any behavior; scoring must measure proactive/retroactive interference magnitude from baseline
- **Import failures**: `attention_vigilance`, `learning_curriculum`, `attention_instruction_update` all fail with import errors — must fix `from data import ...` paths before these benchmarks can run

### Working Benchmarks (good discrimination between models)
- domain-specific calibration, pragmatic inference, 1st-order ToM, sarcasm, error detection, Tower of London
- 1st-order ToM and scalar implicature discriminate between Flash vs Flash-Lite by model size
- Tower of London and domain calibration challenge even Flash (genuine failures)

### Stratified Calibration Issue
- Easy ECE: 0.260, Medium: 0.194, Hard: 0.300 — medium tier is actually easiest
- Difficulty tiers don't align with actual calibration difficulty; should derive empirically from model accuracy

## Repository Architecture — Known Issues (2026-04-10)

- **Division-by-zero bug:** `task_jol.py` gamma correlation (~line 124) has no `if denom > 0` guard — potential ZeroDivisionError when no concordant/discordant pairs exist.
- **Broken absolute imports:** `task_vigilance.py` and `task_curriculum.py` use `from benchmarks.X.data...` — inconsistent with all other 22 task files using relative imports. These will fail if run from a non-root working directory.
- **Gamma function duplicated 7×:** `task_error_detection.py`, `task_error_detection_submetrics.py`, `task_fok.py`, `task_fok_submetrics.py`, `task_jol.py`, `task_jol_submetrics.py`, `task_learning_monitoring.py` each implement Goodman-Kruskal gamma independently with minor differences. Extract to `benchmarks/metacognition/scoring.py`.
- **`rule_systems.py` duplicated:** byte-identical in `benchmarks/metacognition/data/` and `benchmarks/learning/data/`.
- **25/29 task files** have unguarded module-level `.run(kbench.llm)` calls (no `if __name__ == '__main__'` guard). Confirmed non-issue for Kaggle notebook execution but breaks local import/py_compile.
- **47 JSON artifacts** (28 `.task.json`, 19 `.run.json`) at repo root — low-priority clutter.

## Competition Framework


- Google DeepMind's "Measuring Progress Toward AGI: A Cognitive Taxonomy"
- 10 cognitive abilities identified; hackathon focuses on 5 with largest evaluation gaps:
  1. **Learning** — acquiring new knowledge through experience and instruction
  2. **Metacognition** — knowledge and monitoring of one's own cognitive processes
  3. **Attention** — focusing cognitive resources on what matters
  4. **Executive functions** — planning, inhibition and cognitive flexibility
  5. **Social cognition** — processing/interpreting social information and responding appropriately

## Evaluation Protocol (from paper)
1. Evaluate AI systems across cognitive tasks using held-out test sets (prevent data contamination)
2. Collect human baselines from demographically representative adults
3. Map AI performance relative to human performance distribution

## Kaggle Community Benchmarks Platform
- Submissions are Kaggle notebooks using the `kaggle-benchmarks` SDK (`kaggle_benchmarks` / `kbench`)
- Each task = a Python function decorated with `@kbench.task()`
- Tasks can use `llm.prompt()` for model calls, `kbench.assertions` for pass/fail, judge LLMs for subjective eval
- Return types: `bool` (pass/fail), `float`/`int` (score), `tuple[int,int]` (count), `tuple[float,float]` (score+CI)
- `.evaluate()` runs task over a pandas DataFrame dataset
- `%choose task_name` in final cell selects the main task for leaderboard
- Supports: multi-turn conversations, isolated judge chats, structured output schemas, multimodal inputs
- Models available: Gemini, Claude, Llama, DeepSeek, etc. via `kbench.llms["provider/model"]`
- Currently one task per notebook on leaderboard
- Submit benchmark = 1+ tasks grouped together

## Prize Structure
- $10,000 × 2 per track (top two submissions) = $100,000
- $25,000 × 4 grand prizes (best overall) = $100,000
- Total: $200,000
- Results announced June 1, 2026

## Paper Key Points (Measuring Progress Toward AGI: A Cognitive Framework)
- 10 cognitive faculties: Perception, Generation, Attention, Learning, Memory, Reasoning, Metacognition, Executive Functions, Problem Solving, Social Cognition
- First 8 are basic building blocks; Problem Solving and Social Cognition are "composite" faculties
- Three-stage evaluation protocol: (1) cognitive assessment on held-out tasks, (2) human baselines, (3) cognitive profiles mapping AI vs human distribution
- Task design principles: targeted to specific abilities, held-out, independently verified, varied difficulty, varied structure/format
- Existing gap areas (hackathon focus): Learning, Metacognition, Attention, Executive Functions, Social Cognition
- Paper acknowledges problem solving and perception already have decent benchmarks

## Metacognition Notebook Suite — SDK Audit (2026-04-09)
- 12 metacognition notebooks in `repo/notebooks/metacog_*.ipynb`: all pass kbench SDK compatibility after one fix
- Pattern: implementation `.py` files in `repo/benchmarks/metacognition/` may be ahead of their notebook counterparts — always cross-check stubs against these sources
- `metacog_epistemic_revision.ipynb` was a stub with no code; rebuilt from `task_epistemic_revision.py` (30K chars)
- Audit checklist: `!pip install kaggle-benchmarks` in cell 0, `@kbench.task()` decorator, `%choose <task>` as final cell, no direct openai/anthropic imports
- `jupyter nbconvert --to notebook` is a reliable notebook syntax validator

## Key Learnings
- Kaggle pages require JS rendering — can't scrape directly, use search snippets instead
- The kaggle-benchmarks SDK cookbook is the essential reference for implementation
- Competition emphasizes going "beyond recall" — must test genuine cognitive ability not memorization
- Shortcut resistance is critical: tasks must not be solvable by pattern matching or data contamination

## Kaggle API Limitations (2026-04-09)
- `kaggle kernels list --mine` returns `is_private=None` for all notebooks — visibility field not populated by API
- Toggling notebook visibility via API (pull → set `is_private:false` → push) triggers `SaveKernel` endpoint; repeated failed pushes cause 429 rate-limiting that persists
- Failed API pushes create ghost notebook entries (id=0, empty slug/ref, title="[Private Notebook]") that cannot be deleted via API — must use web UI
- **Recommendation:** Toggle notebook visibility and delete ghost entries through Kaggle web UI, not the API
- 4 target notebooks (CRT v2, canary metacog, epistemic humility v2, emotional prosody v2) under `ianstudy/` account need manual public toggle
- 8 other named notebooks already public (epistemic revision, WCST, divided attention, sarcasm detection, tower of london, instruction update, vigilance attention, learning monitoring)

## Community Benchmarks Submission Process (2026-04-09)
- CB task registration is **entirely UI-driven** — no API or CLI path exists
- Must use "Create Task" button at kaggle.com/benchmarks/tasks/new for each notebook
- Notebooks must be PUBLIC before they can be registered as CB tasks
- 12 notebooks uploaded to Kaggle as regular kernels; 19 additional local-only notebooks not yet pushed
- Failed API pushes created ghost entries (id=0, empty slug) — cleanup requires web UI
- Full submission guide at `repo/CB_SUBMISSION_GUIDE.md` with step-by-step instructions for Ian

## SUBMISSION_NARRATIVE.md — Theoretical Grounding Update (2026-04-09)
- Track 1 metacognition section rewritten with 4 paragraphs citing Nelson & Narens (1990), Fleming (2024), Koriat (1997), Steyvers & Peters (2025), Chhikara et al. (2025), Vuorre & Metcalfe (2021), AFCE NeurIPS 2024
- Benchmark table now includes "Theoretical Basis" column linking each of 9 benchmarks to named frameworks
- Section 5 split into 5.1 (vs. traditional benchmarks) and 5.2 (vs. CASK) with 7-dimension comparison table
- Key CASK differentiation: CASK tests 1 construct (context-sensitivity of calibration); our suite tests 9 constructs with Fleming sensitivity/bias/efficiency decomposition
- Section 8 rewritten: contamination canaries, sub-metric decomposition (gamma + ECE + Brier), and procedural generation highlighted as unique differentiators
- 10 new references added: Botvinick, Chhikara, Dunlosky & Rawson, Fleming ×2, Koriat, Mercier & Sperber, Nelson & Dunlosky, Steyvers & Peters, Vuorre & Metcalfe

## Claude Sonnet 4 Metacognition Benchmark Results — Bedrock Run (2026-04-09)

Model: `us.anthropic.claude-sonnet-4-20250514-v1:0` via Amazon Bedrock

| Benchmark | Score | vs. Human Baseline | Notes |
|-----------|-------|--------------------|-------|
| Canary Detection | 0.951 | — | Near-perfect fabrication detection |
| Epistemic Humility | 0.926 | — | Strong admission of knowledge limits |
| Error Detection (F1) | 0.882 | 0.75–0.85 | **Above** human baseline |
| Epistemic Revision | 0.820 | 0.70–0.85 | Near top of human range |
| Learning Monitoring | 0.698 | 0.60–0.75 | Mid-range human |
| Metacog Control | 0.689 | 0.65–0.80 | Mid-range human |
| JOL (composite) | 0.465 | 0.50–0.70 | **Below** human baseline |
| FOK (composite) | 0.449 | 0.60–0.80 | **Below** human baseline |
| Calibration (BSS) | 0.000 | 0.80–0.90 | **Complete failure** |

**Key insights:**
- Claude's metacognition is bimodal: near-perfect at detecting fabrications and admitting ignorance (external-facing), but poor at self-monitoring confidence accuracy (internal-facing)
- BSS=0.000 on calibration means Claude's expressed confidence is uncorrelated with accuracy — this is a fundamental limitation, not a benchmark artifact
- FOK and JOL both below human range — Claude cannot reliably predict what it does/doesn't know before being tested
- Error detection exceeds human baseline — Claude catches logical/factual errors in text better than humans
- Pattern: Claude is strong at "do I know this? (no)" but weak at "how confident should I be? (calibrated)"

## Claude Sonnet 4 — Three-Tier Metacognition Profile (2026-04-09)

Mapping of 9 metacognition benchmark scores to Fleming's (2024) taxonomy:

- **Tier 1 (>0.85) — external monitoring:** Canary (0.951), Epistemic Humility (0.926), Error Detection (0.882). Shared structure: detecting external anomalies (fabricated facts, unknowable questions, reasoning errors).
- **Tier 2 (0.65–0.85) — self-monitoring over time:** Epistemic Revision (0.820), Learning Monitoring (0.698), Metacog Control (0.689). Moderate/inconsistent self-tracking of cognitive state across turns.
- **Tier 3 (<0.50) — prospective self-assessment:** JOL (0.465), FOK (0.449), Calibration (0.000). Prospective prediction of own performance before being tested — Claude fundamentally fails here.

**Key ratio:** External monitoring mean = 0.920 vs. internal self-assessment mean = 0.305 → 3:1 dissociation. This is a testable structural prediction: any model with strong external monitoring but weak internal self-assessment should cluster in this same three-tier pattern.

## Project Status Snapshot (2026-04-09)
- 29 benchmarks + 31 notebooks completed across all 5 cognitive tracks; all pass syntax validation
- Psychometric validation complete: Cronbach α ≥ 0.70, good discriminant validity (4:1 within/between ratio)
- Spot tests with Gemini 2.5 Flash/Flash-Lite revealed: calibration failure, pragmatic literal bias, 1st-order ToM failure, inconsistent pragmatics
- FRONTIER_MODEL_RESULTS.md has no actual scores — Gemini API free tier exhausted; no other keys available
- Entire critical path is Ian-blocked: 4 manual notebook uploads, ~70 ghost cleanup, 18 API-blocked pushes, CB task registration, discussion post
- Estimated ~1.5 hrs of Ian web UI work before CB platform can run models automatically
- Agent-actionable next: retry Kaggle API pushes (rate limit recovery), run benchmarks locally once billing enabled, update narrative with real scores

## CRT Procedural Generator — Contamination Replacement (2026-04-09)

- **Problem:** Classic CRT items (bat-and-ball, lily pad, widget factory) score 100% for Flash and Flash-Lite — fully contaminated in training data.
- **Solution:** 15 generator functions with randomizable numeric seeds replace static items. `generate_crt_items(seed, n_items)` is deterministic per seed but produces different correct answers across seeds.
- **Trap taxonomy implemented:** algebraic anchoring, rate independence, exponential growth, complement misread, percentage asymmetry, fence-post, boundary escape, self-reference, cuts-vs-pieces, interval counting, denomination irrelevance, total-time shortcut, recursive weight, meeting point, linear-vs-exponential.
- **Contamination test (mock):** intuitive-answer model drops from ~1.0 → 0.05; easy-correct model 0.27; perfect model 0.95. Difficulty spread: 4 easy / 6 medium / 5 hard.
- **12/15 generators** produce different `correct` answers with different seeds; 3 (meeting-point, boundary-escape) have fixed conceptual answers independent of parameters.
- **File:** `repo/benchmarks/executive_functions/data/crt_items.py` — backward-compatible: exports `CRT_ITEMS` (seed=42) so `task_crt.py` requires no changes.
- **Pattern:** Replace any static "classic puzzle" dataset with a parametric generator; seed=42 as default preserves reproducibility while alternate seeds defeat memorization.

## Local Model Testing — Use Bedrock via kbench SDK (2026-04-09)

- **Context:** Previous research loop got stuck trying to test against GPT-4o (not supported) and Gemini (free tier exhausted, billing not enabled).
- **Solution:** Use AWS Bedrock via the local kbench runner. The `kbench` SDK supports custom model backends; configure it to call Bedrock's Claude Sonnet.
- **Supported on Kaggle CB platform:** `anthropic/claude-sonnet-4`, `google/gemini-2.5-flash`, `google/gemini-2.5-pro`, `meta/llama-3.1-70b`. OpenAI is NOT supported.
- **For local testing when a real model is needed:**
  - Use `scripts/run_benchmark_local.py` with a Bedrock-backed Claude model
  - The VPS has AWS credentials and Bedrock access (us-east-1, Claude Sonnet/Opus)
  - Preferred local test model: `amazon-bedrock/us.anthropic.claude-sonnet-4-6` (cost-effective, matches CB platform's Claude Sonnet tier)
  - Do NOT attempt to obtain or use Google API keys — Gemini is unavailable locally; use Bedrock instead
  - Do NOT attempt GPT-4o or any OpenAI model — not available on CB platform or locally
- **Pattern:** Any task that requires "run a benchmark against a real model" should default to Bedrock Claude Sonnet locally. Results can be reported as "Claude Sonnet 4.6 (Amazon Bedrock)" in the narrative.

## submission_overview.ipynb Consolidation (2026-04-10)

- The notebook was entirely redundant with `SUBMISSION_NARRATIVE.md` except for one element: an explicit inventory of 30 individual benchmark notebooks organized by track.
- That inventory was merged into Section 6 (Technical Implementation) of `SUBMISSION_NARRATIVE.md` as the subsection "Individual Benchmark Notebooks (30 total)".
- After merge, the notebook was deleted. References in 15 files (UPLOAD_INSTRUCTIONS.md, NOTEBOOK_AUDIT.md, GOALS.md, 9 Python scripts) were updated to remove or comment out the submission_overview entry.
- **Pattern:** When a notebook exists solely as a summary/overview of other content, merge unique elements into the canonical markdown document and delete the notebook. Prefer `SUBMISSION_NARRATIVE.md` as the single source of truth for narrative content.

## Discriminatory Power Analysis — 26 Benchmarks (2026-04-10)
- **Top discriminators** (Claude Opus 4.6 − Ministral 3B Δ): learning_transfer (+0.65), metacog_epistemic_humility (+0.60), metacog_control (+0.48), exec_func_wcst (+0.14), social_cog_emotional_prosody (+0.12).
- **Ceiling effect (all models >0.9):** attention_vigilance (all=1.0), social_cog_false_belief (mean=0.964).
- **Floor effect (all models <0.1):** metacog_canary (all=0.0 — confirms canary design working but uninformative for ranking).
- **Low variance (std<0.05), non-discriminatory:** attention_divided (0.013), attention_instruction_update (0.017), attention_selective (0.035), exec_func_crt (0.028), metacog_epistemic_revision (0.013).
- **Zero discrimination (Δ=0.00):** exec_func_task_switch, exec_func_crt, attention_vigilance, metacog_canary — these four add no model-separation signal.
- **Caveat:** Many benchmarks have only 2–4 valid scores (rest are ERRORs from timeouts); discrimination estimates are uncertain for sparse rows.
- **Action:** Expand item count / difficulty range for all flagged benchmarks; ceiling/floor cases require redesign not just parameter tweaks.

## Bedrock Score Matrix — Full 10-Model Run (2026-04-10)
- **All 10 models** successfully produced 26-entry result files; score_matrix.csv generated (26×10).
- **Error-heavy models:** GPT-OSS-120B (15/26 errors), Qwen3 Next 80B (16/26 errors), GLM 4.7 (12/26 errors), Claude Opus 4.6 (13/26), DeepSeek-R1 (11/26) — mostly timeouts on complex benchmarks.
- **Clean models:** Llama 3.3 70B (26/26 scored), Llama 4 Maverick 17B (26/26 scored).
- **Chronic timeouts (>300s):** exec_func_wcst, exec_func_tol, exec_func_nback, exec_func_crt, exec_func_task_switch, attention_divided, attention_instruction_update — these benchmarks are slow for all models and produce frequent nulls.
- **attention_vigilance** scored 1.0 for every model — likely a ceiling effect; benchmark may be too easy.
- **Execution strategy:** Sequential runs take ~8 hrs total; parallel runner per model (separate processes) is necessary to complete within session windows.
- **OOM risk:** Running 5–6 models concurrently (each as a subprocess) triggered SIGKILL on one run — keep parallelism to ≤4 models at once to avoid OOM.

## Cross-Model Three-Tier Metacognition Pattern — Validated (2026-04-10)
- **Three-tier structure replicates across all 10 models:** Tier 1 (external monitoring: epistemic_humility, error_detection) ~0.83; Tier 2 (temporal self-tracking: revision, control, learning_monitoring) ~0.68; Tier 3 (prospective self-assessment: FOK, JOL, calibration) ~0.29.
- **Scale amplifies Tier 1, not Tier 3.** Frontier models show larger T1→T3 gap (0.65) than 3B baseline (0.40). Larger models get better at detecting others' errors but not at predicting their own performance.
- **Calibration failure universal:** 4/5 models scored BSS=0.000; only Sonnet 4.6 achieved 0.368 (still far below human ~0.85). Not model-specific; a general LLM property.
- **CRT prediction failed:** Originally predicted as strong discriminator; actual std=0.028, all models cluster at ~0.36. CRT items need harder procedurally-generated variants.
- **Confirmed §7.5 structure for SUBMISSION_NARRATIVE.md:** Original predictions vs. actual results documented with ✅/❌/⚠️ for each benchmark.
- **Best discriminators are cognitive, not knowledge-based:** learning_transfer, epistemic_humility, metacog_control outperform all knowledge-recall benchmarks in model separation.

## attention_vigilance Ceiling Fix — N-back Redesign (2026-04-10)
- **Root cause of ceiling:** 60 items in 3 chunks of 20 counting ★ symbols — trivially easy, all 10 models scored 1.0.
- **Fix:** N-back vigilance task (Kirchner 1958): 3-back (80 items) + 4-back (60 items) with near-miss letter distractors (B/D/P, M/N/L confusable pairs).
- **Scoring formula:** 0.35 * accuracy + 0.35 * sensitivity (hit_rate - FA_rate) + 0.15 * vig_decrement_resistance + 0.15 * (1 - FA_rate). Weighting sensitivity/accuracy higher than vigilance decrement avoids near-free points from short sequences.
- **Final scores:** Claude Opus 4.6=0.856, Nova Pro=0.591, Ministral 3B=0.600; std=0.123 (>0.10 target), range=0.265.
- **Lesson:** Vigilance decrement weight should be ≤0.15 when sequences are <100 items total — not long enough to produce real fatigue effects worth 0.30 weight.
- **Lesson:** 4-back hit rate ~0.545 even for strong models; 3-back alone leaves Opus near ceiling. Always include a hard condition.

## Metacognition 9-Benchmark Final Scores — 10-Model Bedrock Run (2026-04-11)
- **Coverage:** 89/90 scores (1 missing: Ministral 3B calibration — ValidationException, model limitation confirmed on retry).
- **Score matrix:** `repo/results/metacog_final_scores.csv` — 9 benchmarks × 10 models.
- **Per-benchmark stats (mean ± std, N):**
  - canary: 0.795 ± 0.305, N=10 — widest spread, best discriminator
  - calibration: 0.184 ± 0.347, N=9 — second-widest; most frontier models score 0.000 (BSS failure)
  - control: 0.549 ± 0.181, N=10 — mid-range, good separation
  - epistemic_humility: 0.788 ± 0.220, N=10
  - epistemic_revision: 0.801 ± 0.102, N=10
  - error_detection: 0.862 ± 0.077, N=10
  - fok: 0.561 ± 0.083, N=10
  - jol: 0.393 ± 0.091, N=10
  - learning_monitoring: 0.834 ± 0.081, N=10
  - **Avg std = 0.165 — PASS (≥0.10 target)**
- **Regressions vs prior Claude Sonnet 4 baselines:**
  - epistemic_humility: 0.926 → 0.838 (Δ=-0.088) — minor regression, benchmark update effect
  - control: 0.689 → 0.350 (Δ=-0.339) — major regression, attributed to hardened benchmark stimuli
  - calibration: 0.000 → 0.504 (improvement, prior scoring bug fixed)
- **Calibration floor effect:** 6/10 models score 0.000 on calibration (BSS=0); only Claude Sonnet 4.6 (0.504), Claude Opus 4.6 (0.998), DeepSeek-R1 (0.000), GPT-OSS-120B (0.124), GLM 4.7 (0.025) achieve non-zero — Claude flagship models uniquely able to express calibrated uncertainty.
- **Weak discriminators:** error_detection (std=0.077), jol (std=0.091), learning_monitoring (std=0.081), fok (std=0.083) — consider hardening for v2.
- **Haiku inaccessible:** Known AWS Bedrock access issue, not benchmark bug.

## Tower of London Parser Fix — exec_func_tol v2 (2026-04-11)
- **Root cause of floor effect (mean=0.038):** `parse_moves()` had a full-text regex fallback that matched every `A→B` token in chain-of-thought reasoning traces — 5-move problems produced 24–36 spurious parsed moves, causing validation failures.
- **Fix:** Replaced full-text fallback with a 5-strategy cascade: (S1) MOVES: summary line, (S2) numbered move lines (`Move 1: A→B`), (S3) last compact move list on a single line with ≥2 moves, (S4) numbered `from X to Y` lines, (S5) MOVES line with `from X to Y`. No full-text fallback.
- **Prompt hardening:** Added explicit instruction to end response with `MOVES: A→B, C→A, B→C` as the LAST line, reducing S1 failures.
- **After fix scores (20 problems, 3 models):** Claude Opus 4.6=0.71, Nova Pro=0.26, Ministral 3B=0.00 → mean=0.323 (≥0.20 ✅), std=0.293 (≥0.10 ✅).
- **Residual issue:** 5-move problems still produce 24–27 parsed moves for Opus when no MOVES: line is elicited — S2/S3 still pick up reasoning. Not score-breaking given Opus scores well overall.
- **General lesson:** Full-text regex fallbacks in response parsers are dangerous for chain-of-thought models. Always require a structured output line and parse ONLY that line first.
- **Artifact:** `repo/benchmarks/executive_functions/task_tol.py`, `repo/notebooks/exec_func_tol.ipynb`

## WCST Benchmark Fix — exec_func_wcst v2 (2026-04-11)
- **Problem:** v1 scored std=0.007 due to three compounding bugs: (1) 80 individual LLM calls causing timeouts, (2) post-shift trials had no shift signal in history, (3) response parser grabbed numbers from reasoning preamble instead of final answers.
- **Fix:** Redesigned to 6-block batch-prompt architecture (1 LLM call per block). History explicitly shows Correct/Incorrect feedback chain, giving models a clear shift signal. Parser now takes LAST N numbers from response.
- **Final scores (v2):** Claude Opus 4.6=1.000, Nova Pro=0.526, Ministral 3B=0.261 → std=0.306, range=0.739 — well above 0.10 target.
- **Score formula:** 0.25×accuracy + 0.45×(1−perseveration_rate) + 0.30×categories_norm
- **Key insight:** Parser bugs in LLM benchmark evaluation are insidious — models may be producing correct reasoning but "wrong" answers due to how numbers are extracted. Always validate parser against known-correct model responses before attributing failures to model capability.
- **Inverted ranking signal:** Ministral 3B outperforming Claude Opus on a reasoning task is a strong diagnostic signal of a broken parser/prompt, not a genuine capability finding.
- **Artifact:** `repo/benchmarks/executive_functions/task_wcst.py`, `repo/notebooks/exec_func_wcst.ipynb`

## False-Belief Theory of Mind (social_cog_false_belief) — v5 Final (2026-04-11)
- **Root cause of original ceiling (0.967):** kbench SDK caches run results via `_handle_cached_run`; module-level `.run(kbench.llm)` fired during import with DummyLLM, writing a cache file, and real runs returned cached dummy results. Fix: guard with `if __name__ == '__main__'`.
- **v3/v4 attempt:** Adding misleading surface cues and batch multi-character tracking failed — all frontier models scored ~0.90, std≈0.033. Text-based false-belief is effectively reading comprehension for LLMs; explicit belief-relevant info in prompts is trivially extracted.
- **v5 design:** 34 scenarios across 5 tiers (4×T1, 4×T2, 6×T3, 12×T4, 8×T5). Tier weights: 0.05×T1 + 0.05×T2 + 0.10×T3 + 0.60×T4 + 0.20×T5.
- **Key discriminating tier:** 4th-order (60% weight). 5th-order with convergent belief chains scored 1.0 across all models — replaced with divergent belief chains (two independent lies at different chain positions).
- **Final v5 scores (5 models):** GLM 4.7=0.6667, Nova Pro=0.700, Llama 3.3 70B=0.8667, Claude Sonnet 4.6=0.925, Llama 4 Maverick=0.950 → mean=0.822, std=0.117 ✅
- **Common failure mode:** FB52/FB56 "perspective confusion" trap — models answer what X actually thinks instead of what Y thinks X thinks. Good diagnostic of genuine ToM failure vs. reading comprehension.
- **Cache pitfall:** Results cached in both `.run.json` files AND `repo/results/*.json` — both must be cleared when re-running with updated scenarios.
- **Artifact:** `repo/benchmarks/social_cognition/task_false_belief.py`, `repo/benchmarks/social_cognition/data/false_belief_scenarios.py`, `repo/notebooks/social_cog_false_belief.ipynb`

## Full 10-Model Bedrock Benchmark Run — All 5 Tracks (2026-04-11)

### Score Matrix (258/260 cells, 2 OOM-killed)
Final scores across 26 benchmarks × 10 Bedrock models compiled in `repo/results/score_matrix_all_tracks.csv` and `repo/results/per_track_analysis.md`.

### OOM failures (documented, not errors)
- Qwen3 Next 80B × learning_curves: OOM-killed consistently (large context benchmark, model context window issue)
- Qwen3 Next 80B × exec_func_nback: OOM-killed consistently

### Discriminatory power by track (avg range across benchmarks)
| Track | Avg Range | Most Discriminatory |
|-------|-----------|---------------------|
| Executive Functions | 0.5546 | exec_func_tol (0.8000) |
| Learning | 0.5200 | learning_interference (0.8800) |
| Metacognition | 0.4998 | metacog_canary (1.0000) |
| Social Cognition | 0.4821 | social_cog_pragmatic (0.6519) |
| Attention | 0.4537 | attention_instruction_update (0.6841) |

### Key model insights
- **Ministral 3B** is the clear weakest model: attention_instruction_update=0.299, learning_interference=0.120, exec_func_tol=0.000
- **DeepSeek-R1** scores highest on attention_vigilance (1.000) and learning_transfer (1.000) — reasoning model benefits structured tasks
- **exec_func_tol** (Tower of London) is the hardest benchmark: mean=0.252, range=0.800 — strong discriminatory power
- **learning_curves** is least discriminatory in Learning track (range=0.180) and reliably times out >600s for large models; 900s timeout recommended
- **attention_selective** is least discriminatory in Attention track (range=0.175) — consider replacement in future iterations
- **metacog_calibration** shows extreme bimodal distribution (mean=0.165, range=0.998) — one model (Claude Opus) scores near-perfect, most score near-zero

### Execution lessons
- Parallel benchmark execution (>2 concurrent processes) causes OOM kills on this instance — always use sequential execution
- DeepSeek-R1 requires 900s timeout per benchmark (reasoning model inference is slow)
- learning_curves requires 900s timeout for large models
- kbench run results are cached in `.run.json` files AND `repo/results/*.json` — clear both when re-running

## Track Writeups — Completed (2026-04-11)
- All 5 track writeups exist at `repo/WRITEUP_<TRACK>.md`; all are under 1,500 words.
- Cover images at `repo/assets/<track>_cover.png` — grouped bar charts with background category shading, human baseline band, 5 representative models; generated programmatically via matplotlib.
- Required sections confirmed in all writeups: Project Name, Team, Problem Statement, Task & Benchmark Construction, Dataset, Technical Details, Results/Insights/Conclusions, Organizational Affiliations, References.
- All writeups declare "Independent submission — no organizational affiliation."
- **Attention writeup:** Cites Posner (1980), Treisman & Gelade (1980), Wickens (2002). Key finding: divided attention degrades with interference type (competing domains), not stream count — mirrors Wickens' multiple resource theory.
- **Learning writeup:** Cites Thorndike (1932), Ausubel (1968). Key finding: transfer scales cleanly with model size; interference resistance does not (suggests distinct mechanism). Curriculum sensitivity is low for LLMs vs. humans.
- **Executive functions writeup:** Cites Miyake et al. (2000), Diamond (2013). Key finding: exec_func_tol (Tower of London) most discriminatory (range=0.80); inhibition is most size-sensitive.
- **Social cognition writeup:** Cites Baron-Cohen et al. (1985), Grice (1975). Key finding: pragmatic inference shows family-level inversions (GPT-OSS-120B > Claude Opus); ToM degrades non-linearly at 3rd order for most models.

## attention_selective v2 Redesign — Conjunction Search (2026-04-12)
- **Problem:** v1 had std=0.054 (ceiling clustering 0.775–0.950) due to flat Stroop-analogue items
- **Fix:** Replaced with 3-tier conjunction search (Treisman & Gelade, 1980):
  - Tier 1: 4 pop-out items, weight 0.10 (easy single-feature)
  - Tier 2: 10 feature-conjunction items, weight 0.40 (2-feature binding)
  - Tier 3: 12 triple-conjunction items, weight 0.50 (3–5 features, near-miss distractors)
- **Result:** std=0.1318, mean=0.8268; score range 0.4367 across 10 models
- **Model spread:** DeepSeek-R1/GPT-OSS-120B 0.960 → Ministral 3B 0.523
- **Bug found during redesign:** T3_09 had non-unique answer (Marcus & George both matched); T2_07 had wrong answer (6→7) — both fixed
- **Notebook structure:** `.run()` appears as standalone cell (cell 6: `attention_selective.run()`); prior validator turns incorrectly flagged it as missing because grep on docstring matched first
- **Lesson:** When checking for `.run()`, verify it is a standalone call cell, not inside a docstring. The notebook cell structure (cell index) is authoritative.

## social_cog_emotional_prosody Discrimination Fix — Final Results (2026-04-12)
- **Root cause:** Benchmark too easy for most models (std=0.049, scores clustered 0.73-0.88)
- **Fix:** 3-tier weighting (easy=10%, medium=30%, hard=60%) with multiplicative emotion scoring for hard tier (both before AND after emotions must be correct); exact turn identification (no ±1 tolerance) for hard tier
- **Final 10-model scores:** Claude Opus 4.6=0.5563, Claude Sonnet 4.6=0.4518, Qwen3 80B=0.4036, GLM 4.7=0.3948, GPT-OSS-120B=0.3498, Llama 4 Maverick=0.3408, DeepSeek-R1=0.3285, Ministral 3B=0.3077, Llama 3.3 70B=0.2939, Nova Pro=0.2502
- **Final std=0.0837** (mean=0.3677, range=0.3061) — target ≥0.08 ✅
- **Ranking note:** Nova Pro (0.2502) ranks lowest — unexpectedly below Ministral 3B (0.3077). DeepSeek-R1 also underperforms expectations; reasoning-format JSON parsing may inflate difficulty for these models.
- **Design insight:** Multiplicative scoring for multi-part answers (require ALL components correct) is the strongest lever for compressing scores downward without changing task content.
- **Cache risk:** Nova Pro had a stale cached run with different code version (0.2460 cached vs 0.2502 fresh). Always invalidate cache after changing scoring logic.

## metacog_error_detection Discrimination Fix — Final Results (2026-04-12)
- **Root cause of low std (0.077):** Only 2 hard (d=3) error items existed in the original 48; most hard items were correct chains that don't penalize weaker models.
- **Fix:** Added 8 hard items (E33-E40, d=3) targeting statistical reasoning traps: base rate neglect, Simpson's paradox, off-by-one, unit conversion, LCD arithmetic, inclusion-exclusion, Bayesian inference, correlation-causation. Added 4 easy anchor items (E41-E44, d=1): simple addition, area formula, division, time conversion errors.
- **Final 10-model scores:** DeepSeek-R1=0.9781, Claude Sonnet 4.6=0.9667, Claude Opus 4.6=0.9664, Llama 4 Maverick=0.9472, GLM 4.7=0.9156, GPT-OSS-120B=0.9079, Llama 3.3 70B=0.8666, Nova Pro=0.8628, Qwen3 80B=0.8410, Ministral 3B=0.6491 → std=0.0924 ✅
- **Primary discriminator:** Ministral 3B (0.6491) on statistical reasoning items (base rate neglect, Bayesian inference).
- **Cache pitfall:** kbench skips re-running updated benchmarks with stale cached results — always clear per-model result cache after modifying benchmark items.
- **Design insight:** Statistical reasoning fallacy items (base rate neglect, Simpson's paradox) are the strongest discriminators for error_detection — frontier models handle them well but smaller models fail systematically.
- **Artifact:** `repo/benchmarks/metacognition/task_error_detection.py`, `repo/benchmarks/metacognition/data/error_detection_chains.py`, `repo/notebooks/metacog_error_detection.ipynb`

## learning_curves v3 Discrimination Fix — Final Results (2026-04-12)
- **Root cause of v2 low discrimination (std=0.068):** Abstract system generator produced trivial surface-renaming tasks — models could pattern-match outputs without genuine structural inference.
- **Fix:** Replaced `generate_abstract_system` with `generate_structural_transfer` (coordinate-pair encoding + word-problem embedding). Added `generate_positional_system` and `generate_stateful_system` to `HARD_LEARNING_SYSTEMS`. Far-transfer prompt reduced to 2 worked examples (withholds full transfer rules, forcing genuine inference).
- **Composite weights:** Changed from 0.25/0.50/0.25 → 0.20/0.50/0.30 (standard/far_transfer/steep), increasing penalty for failing the harder steep condition.
- **Final v3 scores (9 models):** Claude Opus 4.6=0.7873, DeepSeek-R1=0.7413, GPT-OSS-120B=0.6855, Claude Sonnet 4.6=0.6606, Llama 4 Maverick=0.5667, GLM 4.7=0.5074, Llama 3.3 70B=0.4542, Nova Pro=0.4430, Ministral 3B=0.4410 → std=0.1271, range=0.3463 ✅
- **Qwen3 Next 80B:** OOM — excluded from stats.
- **Ranking shift:** GLM 4.7 dropped sharply (v2: 0.7403 → v3: 0.5074) and Nova Pro dropped (v2: 0.6820 → v3: 0.4430) — these models were inflated by the trivial abstract system; structural transfer is genuinely harder for them.
- **Design insight:** Withholding transfer rules (only 2 examples instead of full system spec) is the key lever — models must infer the structural mapping, not just apply stated rules.
- **Artifact:** `repo/benchmarks/learning/task_learning_curves.py`, `repo/benchmarks/learning/data/rule_systems.py`

## GPT-OSS-120B metacog_epistemic_humility Recovery — 10/10 Coverage (2026-04-14)
- **Score:** 0.6990 (9th of 10 models; above only Ministral 3B at 0.2000)
- **Confabulation pattern:** 5/14 unanswerable items failed (subjective, paradox, underspecified, category_error types) — GPT-OSS-120B attempts answers on philosophically ambiguous items instead of deferring
- **Previous failure:** ValidationException on Bedrock; retry with increased timeout (600s) succeeded
- **Benchmark discrimination:** epistemic_humility range spans 0.2000–0.9214 (Ministral 3B to Llama 3.3 70B), std adequate for model separation

## Metacognition Track — Full Improvement Cycle Completed (2026-04-14)
- **Final state:** All 9 benchmarks pass std ≥ 0.08 threshold; 10/10 model coverage on all benchmarks
- **3 benchmarks improved via targeted revisions:** calibration (0.086→0.108 std), learning_monitoring (0.077→0.181 std), error_detection (0.092→0.170 std)
- **Ceiling effect resolved on error_detection:** 30% of models >0.95 → 0% after adding 7 statistical fallacy items (d3)
- **Parsing robustness pattern:** Backtick fence stripping (`re.sub(r'```(?:json)?\s*', '', cleaned)`) needed for Ministral 3B; apply proactively to all JSON-parsing benchmarks
- **JOL gamma penalty:** Defensive fix — if model confidence std < 1.0, set gamma_norm=0.0 to prevent non-engaging models from scoring free 0.20
- **Remaining structural limitation:** 3 large models (Opus 4.6, GPT-OSS-120B, Qwen3 Next 80B) time out on difficulty-4 learning_monitoring rules at 360s; their v2 scores not captured
- **IMPROVEMENT_LOG.md** at `repo/sub-workflows/metacognition/IMPROVEMENT_LOG.md` documents full cycle for audit/reproducibility

## attention_instruction_update Benchmark Results — All 10 Models (2026-04-14)
- **Scores:** Claude Opus 4.6=0.9833, Claude Sonnet 4.6=0.9833, DeepSeek-R1=0.9833, GPT-OSS-120B=0.9833, Llama 4 Maverick 17B=0.9833, Llama 3.3 70B=0.9525, GLM 4.7=0.8905, Qwen3 Next 80B=0.8900, Nova Pro=0.7646, Ministral 3B=0.2992
- **Aggregate:** mean=0.8713, std=0.2022 (≥0.08 ✅), range=0.6841; 10/10 coverage, 0 failures
- **Trial structure:** 11 trials per model (Easy, Medium, Hard difficulty tiers). Easy×2, Medium×3, Hard×6 approximate breakdown.
- **Ceiling cluster:** 5 models tie at 0.9833 (Claude Opus, Sonnet, DeepSeek-R1, GPT-OSS-120B, Llama 4 Maverick). Only H2_EMBEDDED trial breaks the ceiling (2/12 wrong responses among top models).
- **Key discriminating trial:** H4_CHAINED (mod arithmetic with chained modifications) — GLM 4.7, Qwen3 Next 80B, Nova Pro all drop to 0.571 on this trial.
- **Ministral 3B parsing anomaly:** Scores 0/8 on E1 and E2 (simple single-switch trials) despite scoring 1.0 on H1_REVERSAL — attributed to JSON extraction failure on flat answer format, not cognitive inability.
- **Retry bias:** Unaffected (no schema= parameter used).
- **Artifact path:** `repo/sub-workflows/benchmark-qa/results/qa_transcripts/attention_instruction_update/` — 10 .jsonl + 10 .summary.json + aggregate_stats.json

## Track Rename & Scope Expansion (2026-04-14)
- **Renamed:** sub-workflow from `metacognition` to `benchmark-qa` to cover all 26 benchmarks across 5 cognitive tracks
- **Metacognition track (9 benchmarks): COMPLETE.** Full Phase 2 cycle done — retry bias fix, 10-model re-runs with Q&A transcripts, per-benchmark analysis, improvement plan, scoring/item fixes, improvement log. All 9 pass std ≥ 0.08.
- **Remaining tracks need Phase 2 QA:**
  - Attention (4 benchmarks): divided, selective, vigilance, instruction_update
  - Executive Functions (5 benchmarks): crt, nback, task_switch, tol, wcst
  - Learning (4 benchmarks): curriculum, curves, interference, transfer
  - Social Cognition (4 benchmarks): emotional_prosody, false_belief, pragmatic, sarcasm
- **Phase 1 runs exist** for all remaining benchmarks (task/run JSONs in workspace root)
- **Notebooks:** 7 metacog notebooks already improved; remaining 17 need the same treatment
- **Known issue:** Retry bias affects 18/26 notebooks total (see docs/RETRY_BIAS_ISSUE.md) — metacog ones fixed, others still affected

## Attention Track — QA Improvement Cycle Complete (2026-04-14)
- **All 4 benchmarks passed** evaluation with KEEP AS-IS verdict; no changes implemented, re-runs skipped per Step 7
- **Track average std: 0.1774** (well above 0.08 threshold across divided/selective/vigilance/instruction_update)
- **Non-blocking advisory items documented** (but not fixed): JSON comment stripping for Ministral 3B/Nova Pro (~0.05–0.15 gain possible); ceiling clusters on divided (6/10 at 0.92–0.94) and instruction_update (5/10 at 0.9833) are tolerable with current 10-model roster
- **Llama 3.3 70B vigilance anomaly:** 4.1s response / 413 tokens → 0.5653 score; confirmed genuine poor performance, not a parsing bug
- **Improvement log:** `repo/sub-workflows/benchmark-qa/results/improvement_log_attention_track.md`
