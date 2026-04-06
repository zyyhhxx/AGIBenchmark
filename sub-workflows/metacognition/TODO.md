# TODO — AGI Benchmark Task Queue

## In Progress
- [ ] Update notebook generator for all 12 benchmarks [1 cycle]

## Queue
- [ ] Test metacognition benchmarks against frontier models [1 cycle]
- [ ] Cross-validate across model families [1 cycle]
- [ ] Polish competition writeup with results [1 cycle]
- [ ] Create comprehensive Kaggle submission notebook [1 cycle]

## Done
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
