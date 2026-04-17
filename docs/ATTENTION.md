# Do Large Language Models Exhibit Human-Like Attentional Control?

## Problem Statement

Attention is a foundational pillar of human cognition — the mechanism by which organisms select, sustain, and flexibly redirect processing resources (Posner, 1980). Experimental psychology has decomposed attention into distinct constructs: selective filtering, divided allocation across concurrent tasks, sustained vigilance, and flexible updating of attentional priorities.

As large language models achieve sophisticated performance on reasoning benchmarks, a critical question emerges: do these systems exhibit the attentional control mechanisms that scaffold human cognition? This track operationalizes four well-established attentional constructs as text-based tasks grounded in the experimental paradigms that originally defined them. **Do LLMs exhibit the functional signatures of attentional control: robust filtering, graceful degradation under load, sustained accuracy over time, and flexible rule switching?**

## Task & Benchmark Construction

| Task | Construct | Theoretical Basis |
|------|-----------|-------------------|
| **Selective Attention** | Attentional filtering via conjunction search | Feature Integration Theory (Treisman & Gelade, 1980) |
| **Divided Attention** | Multi-stream interference | Multiple Resource Theory (Wickens, 2002; Pashler, 1994) |
| **Sustained Vigilance** | Sustained attention + working memory | Vigilance decrement (Mackworth, 1948; Kirchner, 1958) |
| **Instruction Update** | Cognitive flexibility | Task-switching (Rogers & Monsell, 1995; Monsell, 2003) |

### Key Design Choices

**Selective Attention** presents arrays of multi-feature items varying in color, shape, size, pattern, and border. Difficulty scales with features shared between targets and distractors, following the similarity gradient of Duncan and Humphreys (1989): pop-out conditions yield near-ceiling performance, while triple-conjunction conditions demand effortful search consistent with Guided Search theory (Wolfe, 1994).

**Divided Attention** requires simultaneous monitoring of three concurrent streams, each governed by stream-specific rules. Difficulty increases through cross-stream interference, operationalizing capacity limits (Kahneman, 1973) and structural interference when tasks compete for shared resources (Navon & Gopher, 1979). Human baselines show 10–30% dual-task cost on analogous paradigms.

**Sustained Vigilance** adapts the n-back paradigm (Kirchner, 1958) with 140-item sequences using 3-back (weight 0.55) and 4-back (weight 0.45) conditions. Near-miss confusable letter distractors (B/D/P, M/N/L) demand fine-grained discrimination. Target rate decreases across the sequence, inducing vigilance decrement (Warm, Parasuraman, & Matthews, 2008; Parasuraman & Davies, 1977).

**Instruction Update** changes rules mid-sequence with contradictory updates and catch trials. The hard tier (weighted 0.60) introduces rule reversals probing switch costs and perseveration (Monsell, 2003; Meiran, 1996).

**Scoring:**
- **Selective Attention:** Tier-weighted accuracy across pop-out through multi-conjunction conditions
- **Divided Attention:** Tier-weighted accuracy (0.20×easy + 0.30×medium + 0.50×hard)
- **Sustained Vigilance:** 0.35×accuracy + 0.35×sensitivity + 0.15×vigilance resistance + 0.15×(1 − false alarm rate)
- **Instruction Update:** Tier-weighted accuracy (0.15×easy + 0.25×medium + 0.60×hard)

**Contamination resistance:** All stimuli are procedurally generated with randomized feature combinations, sequence orderings, and rule sets. N-back sequences use novel letter arrangements with controlled similarity neighborhoods. No published stimulus batteries are reproduced.

## Dataset

The benchmark is fully synthetic and self-contained. Each task generates trials through parameterized procedures controlling difficulty, stimulus properties, and trial counts. All generation is deterministic given a seed, enabling full reproducibility. No copyrighted materials are used.

## Results, Insights, and Conclusions

We evaluated 9 models on the [Kaggle Community Benchmarks platform](https://www.kaggle.com/benchmarks/ianstudy/attention-track), spanning frontier (DeepSeek-R1, Gemini 2.5 Pro, Gemini 2.5 Flash, Claude Opus 4.6, GPT-5.4), mid-tier (GPT-5.4 Mini, GPT-5.4 Nano), and small models (Gemma 3 4B, Gemma 3 1B):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| Instruction Update | 0.776 | 0.301 | 0.931 | DeepSeek-R1 / Gemini Flash / Pro / Claude Opus (0.99) | Gemma 3 1B (0.06) |
| Selective Attention | 0.841 | 0.156 | 0.422 | DeepSeek-R1 (1.00) | Gemma 3 1B (0.58) |
| Divided Attention | 0.802 | 0.211 | 0.674 | DeepSeek-R1 / Gemini 2.5 Flash (0.94) | Gemma 3 1B (0.27) |
| Sustained Vigilance | 0.764 | 0.185 | 0.453 | DeepSeek-R1 / Gemini Flash / Pro (1.00) | Gemma 3 1B (0.55) |

**Overall ranking:** DeepSeek-R1 (0.982) > Gemini 2.5 Flash (0.976) > Gemini 2.5 Pro (0.974) > Claude Opus 4.6 (0.920) > GPT-5.4 (0.854) > GPT-5.4 Mini (0.800) > GPT-5.4 Nano (0.698) > Gemma 3 4B (0.596) > Gemma 3 1B (0.362).

**Insight 1 — Instruction Update is the strongest discriminator.** With std = 0.301 and range = 0.931, cognitive flexibility most sharply separates models. Gemma 3 1B's near-zero score (0.06) indicates complete failure to maintain and update rule representations — consistent with the finding that task switching requires active inhibition of prior task sets (Monsell, 2003). Four frontier models tie at 0.99, suggesting that once sufficient executive control capacity exists, the task saturates.

**Insight 2 — Sustained Vigilance reveals within-frontier dissociations.** Three models achieve perfect scores (1.00), yet Claude Opus drops to 0.82 and GPT-5.4 to 0.67. This mirrors human vigilance research: the decrement reflects sustained resource allocation over extended sequences, not raw ability (Warm et al., 2008). Models that maintain working memory across 140 items with decreasing target prevalence demonstrate the attentional persistence that Parasuraman and Davies (1977) identified as the core challenge.

**Insight 3 — Smaller models exhibit construct-specific dissociations.** GPT-5.4 Nano scores 0.86 on Selective Attention but only 0.63 on Instruction Update. Gemma 3 1B collapses on Instruction Update (0.06) and Divided Attention (0.27) yet maintains 0.55–0.58 on Selective Attention and Vigilance. These profiles mirror neuropsychological dissociations where selective attention is preserved while executive control is impaired, suggesting that different attentional constructs place qualitatively different demands on model architecture.

**Insight 4 — Divided Attention produces the clearest scale gradient.** Scores decline smoothly from 0.94 (DeepSeek-R1) to 0.27 (Gemma 3 1B) with minimal clustering, reflecting the graded interference predicted by Multiple Resource Theory (Wickens, 2002) as processing demands exceed available capacity.

**Insight 5 — Selective Attention is the most uniformly accessible construct.** It shows the highest mean (0.841) and lowest variability (std = 0.156). Even Gemma 3 1B achieves 0.58, suggesting that basic feature-based filtering — the pre-attentive mechanism of Feature Integration Theory (Treisman & Gelade, 1980) — is partially supported even in small models.

**Average cross-benchmark std = 0.213**, confirming effective model separation. The 2.7× ratio between the highest (0.982) and lowest (0.362) overall scores demonstrates that the suite discriminates across the full model spectrum, while the construct-specific dissociations confirm it captures meaningful architectural differences rather than a single capability dimension.

## References

- Duncan, J. & Humphreys, G. W. (1989). Visual search and stimulus similarity. *Psychological Review*, 96(3), 433–458.
- Kahneman, D. (1973). *Attention and Effort*. Prentice-Hall.
- Kirchner, W. K. (1958). Age differences in short-term retention. *Journal of Experimental Psychology*, 55(4), 352–358.
- Mackworth, N. H. (1948). The breakdown of vigilance during prolonged visual search. *Quarterly Journal of Experimental Psychology*, 1(1), 6–21.
- Meiran, N. (1996). Reconfiguration of processing mode prior to task performance. *Journal of Experimental Psychology: LMC*, 22(6), 1423–1442.
- Monsell, S. (2003). Task switching. *Trends in Cognitive Sciences*, 7(3), 134–140.
- Navon, D. & Gopher, D. (1979). On the economy of the human-processing system. *Psychological Review*, 86(3), 214–255.
- Parasuraman, R. & Davies, D. R. (1977). A taxonomic analysis of vigilance performance. In R. R. Mackie (Ed.), *Vigilance* (pp. 559–574). Plenum Press.
- Pashler, H. (1994). Dual-task interference in simple tasks. *Psychological Bulletin*, 116(2), 220–244.
- Posner, M. I. (1980). Orienting of attention. *Quarterly Journal of Experimental Psychology*, 32(1), 3–25.
- Rogers, R. D. & Monsell, S. (1995). Costs of a predictable switch. *Journal of Experimental Psychology: General*, 124(2), 207–231.
- Treisman, A. M. & Gelade, G. (1980). A feature-integration theory of attention. *Cognitive Psychology*, 12(1), 97–136.
- Warm, J. S., Parasuraman, R. & Matthews, G. (2008). Vigilance requires hard mental work and is stressful. *Human Factors*, 50(3), 433–441.
- Wickens, C. D. (2002). Multiple resources and performance prediction. *Theoretical Issues in Ergonomics Science*, 3(2), 159–177.
- Wolfe, J. M. (1994). Guided Search 2.0: A revised model of visual search. *Psychonomic Bulletin & Review*, 1(2), 202–238.
