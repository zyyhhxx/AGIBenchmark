### Can AI Systems Focus? A 4-Task Attention Benchmark Suite

### Team
Yiyang Zeng (Independent researcher)

### Problem Statement

Attention — the ability to selectively focus cognitive resources, sustain vigilance over time, and divide processing across concurrent demands — is a cornerstone of human cognition (Posner, 1980). Despite its centrality, LLM evaluations rarely test attentional mechanisms directly. Standard benchmarks conflate attention with knowledge: a model that "attends" to the right context may simply be retrieving memorized associations rather than dynamically allocating processing resources.

Human attention research distinguishes at least three core constructs: *selective attention* (filtering relevant from irrelevant information; Treisman & Gelade, 1980), *divided attention* (managing multiple concurrent information streams; Pashler, 1994), and *sustained attention/vigilance* (maintaining focus over extended sequences; Wickens, 2002). These constructs have distinct neural substrates and failure modes in humans — do they dissociate in AI systems as well?

This benchmark suite asks: **Can frontier models selectively filter, divide, and sustain their attention across competing cognitive demands?**

### Task & Benchmark Construction

We constructed 4 tasks, each targeting a distinct attentional construct grounded in the cognitive psychology literature:

| Task | Construct | Protocol |
|------|-----------|----------|
| **Selective Attention** | Feature-based filtering | Identify targets among distractors varying in similarity; measures resistance to interference (Treisman & Gelade, 1980) |
| **Divided Attention** | Multi-stream processing | Process 2–3 concurrent information streams with varying levels of cross-stream interference; 3 difficulty tiers (Pashler, 1994; Kahneman, 1973) |
| **Sustained Attention (Vigilance)** | Temporal maintenance | N-back task (3-back and 4-back) with confusable letter stimuli over 140 items; measures vigilance decrement and false alarm rate (Kirchner, 1958) |
| **Instruction Update** | Attentional set shifting | Follow rules that change mid-sequence with contradictory updates and catch trials; measures perseveration vs. flexible updating (Monsell, 2003; Meiran, 1996) |

**Difficulty tiering:** Divided attention uses weighted tiers (0.20 × easy + 0.30 × medium + 0.50 × hard) where hard trials present 3 streams in the same domain with conflicting rules. Vigilance uses 3-back (80 items) and 4-back (60 items) with near-miss letter distractors (e.g., B/D/P, M/N/L confusable pairs). Instruction update includes baseline, slow-switch, rapid-switch, and random-cue blocks.

**Contamination resistance:** All stimuli are procedurally generated with seeded randomness. N-back sequences use novel letter strings. No standard attention test batteries (e.g., TOVA, CPT) are reproduced.

### Dataset

Items are generated at evaluation time using deterministic random seeds. Per-task item counts: selective attention (20 trials), divided attention (24 trials across 3 tiers), vigilance (140 items across 2 n-back conditions), instruction update (40+ trials across 4 blocks).

**Scoring:** Selective attention uses normalized accuracy across difficulty levels. Divided attention composites tier-weighted accuracy. Vigilance combines accuracy (0.35), sensitivity/hit−FA (0.35), vigilance decrement resistance (0.15), and false alarm avoidance (0.15). Instruction update measures switch cost (accuracy drop from non-switch to switch trials).

**Provenance:** All stimuli are synthetically generated. No copyrighted materials or existing psychometric instruments are reproduced.

### Technical Details

All tasks use the `kaggle-benchmarks` SDK with `@kbench.task` decorators. Key implementation details:

- **Divided attention:** Each difficulty tier presents items in a single prompt with explicit stream labels. Cross-stream interference is induced by requiring different operations on overlapping data domains.
- **Vigilance (N-back):** Items presented as a continuous sequence in a single prompt. Model must identify which items match the item N positions back. Near-miss distractors (visually/phonologically similar letters) test genuine position tracking vs. familiarity heuristics.
- **Instruction update:** Rules are presented sequentially with contradictions. Catch trials (old rule suddenly reapplied) test whether models truly update or simply follow the most recent instruction.
- All tasks use `numpy` for scoring; regex-based response parsing handles variable output formats.

### Results, Insights, and Conclusions

We evaluated 10 models via Amazon Bedrock across all 4 attention benchmarks:

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| Divided Attention | 0.836 | 0.167 | 0.524 | DeepSeek-R1 (0.94) | Ministral 3B (0.41) |
| Instruction Update | 0.856 | 0.226 | 0.684 | Claude Opus (0.98) | Ministral 3B (0.30) |
| Selective Attention | 0.888 | 0.054 | 0.175 | Llama 4 (0.95) | Ministral 3B (0.78) |
| Vigilance (N-back) | 0.758 | 0.176 | 0.432 | DeepSeek-R1 (1.00) | Ministral 3B (0.57) |

**Insight 1 — Instruction update is the strongest discriminator.** With a range of 0.684 and std of 0.226, attentional set shifting most reliably separates model capability. Ministral 3B (0.30) shows severe perseveration on outdated rules, while frontier models (0.98) flexibly update. This aligns with Monsell's (2003) finding that set-shifting cost reflects executive control, not just attention.

**Insight 2 — Selective attention shows ceiling effects.** All 10 models score above 0.775, with std of only 0.054. Feature-based filtering in text is relatively easy for LLMs because they lack the perceptual interference channel that makes selective attention hard for humans (no Stroop-like color-word conflicts in text). This benchmark measures a real construct but may need multimodal stimuli to challenge frontier models.

**Insight 3 — Vigilance reveals a reasoning-model advantage.** DeepSeek-R1 (1.00) and GPT-OSS-120B (1.00) achieve perfect scores on N-back, while non-reasoning models average 0.71. Chain-of-thought reasoning may function as an "external working memory" that compensates for the sustained tracking demands of N-back. This parallels human findings that verbalization strategies improve vigilance (Helton & Russell, 2011).

**Insight 4 — Divided attention degrades with interference, not load.** The easy→medium→hard tier gradient is steeper for smaller models: Ministral 3B drops from 0.85 (easy, 2 non-conflicting streams) to 0.21 (hard, 3 conflicting streams), while Claude Opus maintains 0.90+. This mirrors Wickens' (2002) multiple resource theory — interference between similar-domain streams, not raw stream count, drives attention failure.

**Average cross-benchmark std = 0.156**, confirming the suite produces meaningful model separation across attentional constructs.

### Organizational Affiliations

Independent submission — no organizational affiliation.

### References & Citations

- Posner, M. I. (1980). Orienting of attention. *Quarterly Journal of Experimental Psychology*, 32(1), 3–25.
- Treisman, A. M. & Gelade, G. (1980). A feature-integration theory of attention. *Cognitive Psychology*, 12(1), 97–136.
- Wickens, C. D. (2002). Multiple resources and performance prediction. *Theoretical Issues in Ergonomics Science*, 3(2), 159–177.
- Pashler, H. (1994). Dual-task interference in simple tasks. *Psychological Bulletin*, 116(2), 220–244.
- Kahneman, D. (1973). *Attention and Effort*. Prentice-Hall.
- Kirchner, W. K. (1958). Age differences in short-term retention. *Journal of Experimental Psychology*, 55(4), 352–358.
- Monsell, S. (2003). Task switching. *Trends in Cognitive Sciences*, 7(3), 134–140.
- Meiran, N. (1996). Reconfiguration of processing mode prior to task performance. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 22(6), 1423–1442.
- Helton, W. S. & Russell, P. N. (2011). Working memory load and the vigilance decrement. *Experimental Brain Research*, 212(3), 429–437.
