# TODO — AGI Benchmark Task Queue

## In Progress

## Queue
- [ ] Create comprehensive results dashboard notebook: aggregate scores across all benchmarks and model families into a single visualization notebook with radar charts by cognitive track [1 cycle]
- [ ] Final pre-submission audit: verify all notebooks run independently on Kaggle, all @kbench.task decorators follow SDK conventions, all scores are in [0,1] range, all have docstrings [1 cycle]
- [ ] Test metacognition benchmarks against frontier models [1 cycle]
- [ ] Cross-validate across model families [1 cycle]
- [ ] Polish competition writeup with results [1 cycle]
- [ ] Create comprehensive Kaggle submission notebook [1 cycle]

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
- [x] Generate Kaggle notebooks for metacognitive control, epistemic revision, and instruction update benchmarks
