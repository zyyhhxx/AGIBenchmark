# TODO — AGI Benchmark Task Queue

## In Progress
- [ ] Implement "metacognitive control" benchmark (NEW): model reads a long passage, must choose which 3 of 10 sections to re-read before answering 5 questions, measure whether re-read choices correlate with question-relevant sections vs. random selection [2 cycles]

## Queue
- [x] Add adversarial shortcut probes to attention benchmarks — 10 adversarial items added to selective attention (position bias, length correlation, authority bias)
- [x] Implement contamination canary system: already exists in task_canary.py with 5 fabricated facts, verified in mock validation
- [ ] Implement "epistemic revision" benchmark (NEW): teach model 10 rules with examples, then present 3 contradicting observations, model must identify which rules changed and state updated rules — tests belief revision rather than just accumulation [2 cycles]
- [ ] Split composite-score benchmarks into separate @kbench.task functions for each sub-metric (e.g., fok_gamma, fok_ece, fok_auc as separate leaderboard entries) [1 cycle] — FOK sub-metrics done, remaining: JOL, error detection
- [ ] Create cross-benchmark correlation analysis: run all benchmarks on same model and measure inter-benchmark correlations to verify they measure distinct constructs (discriminant validity) [1 cycle]
- [ ] Add difficulty-stratified calibration analysis to metacog benchmarks: compute ECE separately for easy/medium/hard questions, verify calibration degrades on harder items [1 cycle]
- [ ] Run sensitivity analysis on learning curve benchmark: vary training examples (5, 10, 20, 40) and verify scores differentiate meaningfully and show expected power-law shape [1 cycle]
- [x] Write competition overview narrative (2-page submission summary): 5 tracks, 20+ benchmarks, key innovations → SUBMISSION_NARRATIVE.md
- [ ] Implement attention-to-instruction-update benchmark: give initial task instructions, then mid-sequence update instructions subtly, measure adaptation speed and perseveration rate [1 cycle]
- [ ] Add inter-rater reliability simulation: for each benchmark, generate 100 synthetic response profiles and measure test-retest reliability (Cronbach's alpha) of the scoring function [1 cycle]
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
