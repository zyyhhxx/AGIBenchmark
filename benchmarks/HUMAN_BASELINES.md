# Human Baseline Reference Data

## Metacognition Track

### Benchmark 1: Retrospective Confidence Calibration
- **ECE (Expected Calibration Error)**: 0.10–0.20 (Lichtenstein et al., 1982)
- **Human score (1 - ECE)**: 0.80–0.90
- **Notes**: Humans typically show slight overconfidence. Domain expertise improves calibration. Weather forecasters and professional poker players achieve ECE ≈ 0.05–0.10.

### Benchmark 2: Feeling-of-Knowing (FOK)
- **Gamma correlation**: 0.25–0.55 (Nelson, 1984; Schwartz & Metcalfe, 2011)
- **Typical gamma**: ~0.40 for general knowledge FOK
- **ECE**: ~0.15–0.25 (prospective judgments less calibrated than retrospective)
- **AUC**: 0.65–0.80
- **Notes**: FOK is harder than retrospective confidence. Humans access partial information (familiarity, related knowledge) to form FOK. Accuracy improves with domain expertise.
- **Key finding**: FOK resolution (discrimination) is more diagnostic than calibration

### Benchmark 3: Judgment-of-Learning (JOL)
- **Gamma correlation**: 0.40–0.90 (Nelson & Dunlosky, 1991)
- **Immediate JOL gamma**: 0.40–0.60
- **Delayed JOL gamma**: 0.80–0.95 (the "delayed JOL effect")
- **Notes**: Delayed JOLs are dramatically more accurate because they're based on retrieval attempts rather than recency/fluency. Our benchmark uses immediate JOLs (during/right after study).
- **Overconfidence**: Humans typically overestimate learning by 20-30% for new associations.

### Benchmark 4: Error Detection
- **d' (sensitivity)**: 1.5–3.0 (Yeung & Summerfield, 2012)
- **Hit rate (detecting errors)**: 0.60–0.85
- **False alarm rate**: 0.10–0.25
- **Error localization**: ~60-80% when error detected
- **Notes**: Error detection depends heavily on domain expertise. Math errors easier to catch than logical fallacies. Self-generated errors harder to detect than others' errors.
- **Confidence**: Moderate overconfidence in error judgments (ECE ≈ 0.15)

### Benchmark 5: Metacognitive Monitoring During Learning
- **Gamma (self-assessment vs. actual)**: 0.30–0.60
- **Dunning-Kruger pattern**: Low performers overestimate (bias +15-25%), high performers slightly underestimate (bias -5-10%)
- **Calibration improves with learning**: As people learn more, their self-assessment becomes more accurate.
- **Notes**: This is a novel benchmark design. Human baselines extrapolated from JOL literature applied to incremental learning contexts.

## Learning Track

### Benchmark 6: Learning Curves
- **Power law exponent**: 0.3–0.5 (Newell & Rosenbloom, 1981)
- **Sample efficiency**: Humans typically reach 80% on simple rule systems within 5-10 examples
- **Asymptotic performance**: 85-95% for well-defined rule systems
- **Notes**: The power law of practice is one of the most robust findings in learning psychology. Deviations from power law shape may indicate qualitatively different learning mechanisms.

### Benchmark 7: Near vs. Far Transfer
- **Near transfer retention**: 70-90% of original performance
- **Far transfer retention**: 20-50% of original performance
- **Transfer ratio (far/near)**: 0.25–0.60
- **Notes**: Transfer is one of the hardest achievements in learning. Most educational interventions fail to produce far transfer. Surface similarity drives near transfer; structural similarity drives far transfer.
- **Key reference**: Barnett & Ceci (2002) meta-analysis

### Benchmark 8: Proactive & Retroactive Interference
- **Retroactive interference**: 10-30% accuracy drop (Underwood, 1957)
- **Proactive interference**: 5-15% learning rate reduction
- **AB-AC paradigm**: Learning similar associations produces maximal interference
- **Notes**: Interference increases with similarity between materials. Our benchmark uses similar rule systems to maximize the effect.

### Benchmark 9: Curriculum Sensitivity
- **Easy→hard advantage**: 5-15% over random ordering (Rohrer & Taylor, 2007)
- **Interleaving advantage**: 10-20% on delayed tests (but 5-10% disadvantage on immediate tests)
- **Notes**: Curriculum effects are well-established but context-dependent. The benefit of interleaving over blocking increases with practice.

## Reference Summary Table

| Benchmark | Primary Metric | Human Range | Interpretation |
|-----------|---------------|-------------|----------------|
| Calibration | 1 - ECE | 0.80–0.90 | Score > 0.85 = human-level |
| FOK | Gamma | 0.25–0.55 | Score > 0.40 = typical human |
| JOL | Gamma | 0.40–0.90 | Score > 0.60 = good learner |
| Error Detection | d' | 1.5–3.0 | d' > 2.0 = good detector |
| Learning Monitoring | Gamma | 0.30–0.60 | Score > 0.45 = self-aware learner |
| Learning Curves | Exponent | 0.3–0.5 | Presence of curve = genuine learning |
| Transfer | Far/Near ratio | 0.25–0.60 | Ratio > 0.40 = good generalizer |
| Interference | Accuracy drop | 10–30% | Drop < 15% = robust memory |
| Curriculum | Effect size | 5–15% | Effect > 0 = genuine sensitivity |

## Methodology for Collecting Baselines

For competition submission, we cite published human baselines from the references above. If time permits:
1. Run the FOK and calibration benchmarks as surveys on human participants (5-10 volunteers)
2. Use existing human performance data from cited papers
3. Compare model scores against the reference ranges

All human baseline ranges are clearly cited with primary sources in COGNITIVE_RATIONALE.md.
