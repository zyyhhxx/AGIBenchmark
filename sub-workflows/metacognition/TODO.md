# TODO — AGI Benchmark Task Queue

## In Progress

## Queue

**SUBMISSION-CRITICAL (Priority 1)**
- [x] Add pip install cells to all 27 notebooks: ensure `!pip install kaggle-benchmarks` + deps in cell 0 [1 cycle]
- [ ] Batch upload Metacognition track notebooks (8) to Kaggle Community Benchmarks platform [1 cycle]
- [ ] Batch upload Learning track notebooks (4) to Kaggle [1 cycle]
- [ ] Batch upload Attention track notebooks (4) to Kaggle [1 cycle]
- [ ] Batch upload Executive Functions track notebooks (4) to Kaggle [1 cycle]
- [ ] Batch upload Social Cognition track notebooks (3) + sub-metric notebooks (3) + submission overview to Kaggle [1 cycle]
- [ ] Run Metacognition benchmarks against GPT-4o on Kaggle platform, record scores, verify outputs parse correctly [1 cycle]
- [ ] Run Learning + Attention benchmarks against GPT-4o on Kaggle, record scores [1 cycle]
- [ ] Run Executive Functions + Social Cognition benchmarks against GPT-4o on Kaggle, record scores [1 cycle]
- [ ] Cross-validate top-5 benchmarks against Claude 3.5 Sonnet + Gemini 1.5 Pro — check for model-specific scoring anomalies [2 cycles]

**QUALITY & POLISH (Priority 2)**
- [ ] Create per-track results summary: compile frontier model scores into `results/FRONTIER_MODEL_RESULTS.md` with pass/fail thresholds [1 cycle]
- [ ] Review notebook markdown cells: ensure title, cognitive science rationale, interpretation guide in each [1 cycle]
- [ ] Verify contamination canary notebook works end-to-end on Kaggle [1 cycle]
- [ ] Update SUBMISSION_NARRATIVE.md with actual frontier model results (replace mock data) [1 cycle]
- [ ] Final pass on all 5 DESIGN.md files: ensure they match actual implementation [1 cycle]
- [ ] Review submission_overview.ipynb: verify it references all 24 benchmarks correctly [1 cycle]
- [ ] Git tag `v1.0-submission` and push final clean commit [1 cycle]

**ROBUSTNESS (Priority 3 — if time permits)**
- [ ] Stress-test 3 weakest benchmarks (vigilance, curriculum, instruction_update) with adversarial responses [1 cycle]
- [ ] Add timeout/retry logic to notebooks: wrap LLM calls with try/except + 3-retry [1 cycle]
- [ ] Verify all data/ directories contain required stimuli files, no hardcoded absolute paths [1 cycle]

**NEW HIGH-IMPACT BENCHMARKS (Priority 4 — only if core submission is solid)**
- [ ] Implement "Cognitive Reflection Test" (CRT) benchmark for Executive Functions (Frederick 2005) [2 cycles]
- [ ] Implement "Epistemic Humility" benchmark for Metacognition: unanswerable questions, measure confabulation vs uncertainty [2 cycles]
- [ ] Implement "Emotional Prosody in Text" benchmark for Social Cognition: emotional tone shift detection in dialogues [2 cycles]

## Done
- [x] Update notebook generator for all 12 benchmarks
- [x] Read competition page, rules, and submission format
- [x] Read DeepMind paper "Measuring Progress Toward AGI: A Cognitive Taxonomy"
- [x] Understand kaggle-benchmarks SDK (cookbook, examples)
- [x] Download paper to drive/papers/
- [x] Strategic track selection → Metacognition (#1) + Learning (#2)
- [x] Design Feeling-of-Knowing (FOK) benchmark for LLMs → task_fok.py
- [x] Design Judgment-of-Learning (JOL) calibration benchmark → task_jol.py + jol_stimuli.py
- [x] Design error detection benchmark → task_error_detection.py + error_detection_chains.py
- [x] Design Learning track: learning curves → task_learning_curves.py + rule_systems.py
- [x] Design Learning track: near vs. far transfer → task_transfer.py
- [x] Design Learning track: proactive/retroactive interference → task_interference.py
- [x] Implement first benchmark using kaggle-benchmarks SDK patterns → all tasks use @kbench.task
- [x] Write cognitive science rationale for each benchmark → COGNITIVE_RATIONALE.md
- [x] Review existing Kaggle submissions for inspiration/gaps → research/competition_landscape.md
- [x] Cross-embed metacognitive probes within learning tasks → task_learning_monitoring.py
- [x] Design Learning track: curriculum sensitivity → task_curriculum.py
- [x] Document methodology thoroughly → METHODOLOGY.md
- [x] Test shortcut resistance → shortcut_analysis.py + added 4 more error chains
- [x] Add human baseline methodology / reference data → HUMAN_BASELINES.md
- [x] Benchmarks for Attention track → task_selective.py, task_vigilance.py, task_divided.py
- [x] Create Kaggle submission notebooks → 5 initial notebooks generated
- [x] Implement Executive Functions: WCST, Tower of London, Task-switching, N-back
- [x] Write Executive Functions DESIGN.md
- [x] Generate Kaggle notebooks for all 4 Executive Functions benchmarks
- [x] Implement Social Cognition: False-belief ToM, Pragmatic inference, Sarcasm detection
- [x] Write Social Cognition DESIGN.md + generate Kaggle notebooks
- [x] Run all 20 benchmarks end-to-end with mock LLM responses — all pass, no crashes, scores in [0,1]. Analysis in results/MOCK_VALIDATION_ANALYSIS.md
- [x] Expand FOK question bank from 43 to 81 questions — added procedural arithmetic, syllogisms, sequences, logic puzzles (contamination-resistant)
- [x] Add adversarial shortcut probes to attention benchmarks
- [x] Implement contamination canary system
- [x] Write competition overview narrative → SUBMISSION_NARRATIVE.md
- [x] Implement "metacognitive control" benchmark → task_metacognitive_control.py (2 passages, 10 sections each, strategic re-reading with 3-section budget)
- [x] Implement "epistemic revision" benchmark → task_epistemic_revision.py (Zorblatt Chemistry rule system, 10 rules, 3 contradictions, 10 transfer questions)
- [x] Split JOL sub-metrics → task_jol_submetrics.py (jol_gamma, jol_ece, jol_recall)
- [x] Split error detection sub-metrics → task_error_detection_submetrics.py (f1, localization, ece, gamma)
- [x] Implement attention-to-instruction-update benchmark → task_instruction_update.py (5 trials including 1 catch, task-switching paradigm)
- [x] Inter-rater reliability simulation → reliability_analysis.py (all α ≥ 0.70: FOK 0.95, error detection 0.79/0.70, attention 0.73)
- [x] Cross-benchmark correlation analysis → correlation_analysis.py (good discriminant validity: within-track r=0.37 vs between-track r=0.09)
- [x] Difficulty-stratified calibration analysis → stratified_calibration.py (ECE increases with difficulty: easy 0.26, hard 0.30)
- [x] Learning curve sensitivity analysis → sensitivity_analysis.py (current [0,2,4,8,12] config validated, monotonic, spread 0.37)
- [x] Create comprehensive results dashboard notebook (radar chart + heatmap + reliability/validity summary)
- [x] Final pre-submission audit: all 26 task files pass, all notebooks have .run() calls, all DESIGN.md present
- [x] Polish competition writeup (updated to 24 benchmarks, added psychometric validation section)
- [x] Create submission overview notebook
- [x] Generate sub-metric notebooks (JOL, FOK, error detection)
- [x] Fix missing .run() calls in exec functions + social cognition tasks
- [x] Generate Kaggle notebooks for metacognitive control, epistemic revision, and instruction update benchmarks
