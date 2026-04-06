# TODO — AGI Benchmark Task Queue

## In Progress

## Queue
- [ ] Implement Executive Functions: Wisconsin Card Sort analogue — generate 30 card stimuli with 3 sorting dimensions (color/shape/number), model must infer active sorting rule from feedback, rule switches silently after 10 correct, measure perseveration errors and set-shifting speed [2 cycles]
- [ ] Implement Executive Functions: Tower of London planning benchmark — generate 15 goal states at 3/4/5-move optimal depths, model plans move sequences, score = optimal_moves / actual_moves averaged across items [1 cycle]
- [ ] Implement Executive Functions: Task-switching benchmark — alternating rule sets (odd/even vs. greater/less than 5) every N trials, measure switch cost (accuracy drop on switch trials vs. repeat trials) across 40 trials [1 cycle]
- [ ] Implement Executive Functions: Working memory N-back analogue — present sequences of 60+ items, model must identify when current item matches the one N steps back, vary N from 1 to 3, measure d-prime per N level [1 cycle]
- [ ] Write Executive Functions DESIGN.md with cognitive science rationale (Miyake et al. 2000 unity/diversity framework), scoring rubrics, and shortcut resistance notes for all 4 exec function benchmarks [1 cycle]
- [ ] Generate self-contained Kaggle notebooks for all 4 Executive Functions benchmarks using existing notebook template pattern [1 cycle]
- [ ] Implement Social Cognition: False-belief Theory of Mind benchmark — 20 Sally-Anne style scenarios with 1st-order and 2nd-order belief attribution, include reality/memory control questions, score = belief accuracy minus control accuracy to isolate ToM [1 cycle]
- [ ] Implement Social Cognition: Pragmatic inference benchmark — 30 items testing Gricean maxims (scalar implicature, indirect requests, irony/understatement), model must identify speaker's intended meaning vs. literal meaning [1 cycle]
- [ ] Implement Social Cognition: Sarcasm detection in context — 40 utterances with rich conversational context (20 sarcastic, 20 sincere), model rates sincerity 0-100, measure AUC discrimination and calibration [1 cycle]
- [ ] Write Social Cognition DESIGN.md with cognitive science rationale (Premack & Woodruff 1978, Grice 1975, Baron-Cohen et al. 1985) and generate Kaggle notebooks for all 3 social cognition benchmarks [1 cycle]
- [ ] Run all 12 existing benchmarks end-to-end with mock LLM responses (always-confident, always-uncertain, random, perfect) to validate scoring pipelines produce sensible score distributions [2 cycles]
- [ ] Expand FOK question bank from 40 to 80+ questions by adding procedurally generated reasoning questions (novel syllogisms, multi-step arithmetic) that cannot be contaminated [1 cycle]
- [ ] Add adversarial shortcut probes to attention benchmarks: inject 10 items per benchmark where surface heuristics (position bias, length correlation) point to wrong answers, verify discrimination holds [1 cycle]
- [ ] Implement contamination canary system: embed 5 fabricated "facts" in FOK/calibration questions, verify no model recognizes them, serving as proof stimuli are novel [1 cycle]
- [ ] Implement "metacognitive control" benchmark (NEW): model reads a long passage, must choose which 3 of 10 sections to re-read before answering 5 questions, measure whether re-read choices correlate with question-relevant sections vs. random selection [2 cycles]
- [ ] Implement "epistemic revision" benchmark (NEW): teach model 10 rules with examples, then present 3 contradicting observations, model must identify which rules changed and state updated rules — tests belief revision rather than just accumulation [2 cycles]
- [ ] Split composite-score benchmarks into separate @kbench.task functions for each sub-metric (e.g., fok_gamma, fok_ece, fok_auc as separate leaderboard entries) [1 cycle]
- [ ] Create cross-benchmark correlation analysis: run all benchmarks on same model and measure inter-benchmark correlations to verify they measure distinct constructs (discriminant validity) [1 cycle]
- [ ] Add difficulty-stratified calibration analysis to metacog benchmarks: compute ECE separately for easy/medium/hard questions, verify calibration degrades on harder items [1 cycle]
- [ ] Run sensitivity analysis on learning curve benchmark: vary training examples (5, 10, 20, 40) and verify scores differentiate meaningfully and show expected power-law shape [1 cycle]
- [ ] Write competition overview narrative (2-page submission summary): 5 tracks, 19+ benchmarks, key innovations, differentiation from existing submissions [1 cycle]
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
