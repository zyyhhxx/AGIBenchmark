### Can AI Systems Understand Minds? A 4-Task Social Cognition Benchmark Suite

### Team
Yiyang Zeng (Independent researcher)

### Problem Statement

Social cognition — the ability to process, interpret, and respond to social information — enables humans to navigate the complexities of interpersonal interaction. Central to social cognition is Theory of Mind (ToM): the capacity to attribute mental states (beliefs, desires, intentions) to others and predict their behavior accordingly (Baron-Cohen, Leslie & Frith, 1985). Equally important are pragmatic language abilities — understanding what speakers *mean* beyond what they literally *say* (Grice, 1975) — and the detection of social signals such as sarcasm, irony, and emotional tone.

Current LLM social cognition evaluations typically test first- or second-order false belief scenarios that frontier models now pass trivially. These tests were designed to detect ToM *deficits* in young children, not to measure the upper range of social cognitive sophistication. We need benchmarks that probe the limits of AI social understanding: higher-order recursive belief tracking, nuanced pragmatic inference, and paralinguistic cue interpretation.

This benchmark suite asks: **Can frontier models track nested beliefs, decode pragmatic meaning, detect sarcasm, and interpret emotional subtext?**

### Task & Benchmark Construction

We constructed 4 tasks spanning the major dimensions of social cognition:

| Task | Construct | Protocol |
|------|-----------|----------|
| **False Belief (ToM)** | Higher-order belief attribution | 34 scenarios across 5 orders of ToM (1st through 5th); 4th-order carries 60% weight to target genuine recursive belief tracking (Baron-Cohen et al., 1985; Perner & Wimmer, 1985) |
| **Pragmatic Inference** | Gricean implicature | 3-tier pragmatic interpretation: direct implicature (0.15 weight), indirect/contextual (0.35), complex multi-layer (0.50); measures understanding beyond literal meaning (Grice, 1975) |
| **Sarcasm Detection** | Non-literal language | Identify sarcastic vs. sincere utterances in context, with varying degrees of contextual support and speaker intent markers |
| **Emotional Prosody** | Paralinguistic interpretation | Infer emotional states from text descriptions of vocal prosody, facial expressions, and situational context; measures social-emotional signal integration |

**Difficulty calibration:** False belief scenarios scale from trivial 1st-order (Sally-Anne style) to 5th-order divergent belief chains. The 60% weight on 4th-order ensures that ceiling performance on easy items doesn't inflate scores. Pragmatic inference similarly concentrates weight (50%) on complex multi-layer implicatures requiring integration of context, speaker goals, and social norms.

**Contamination resistance:** False belief uses novel scenarios with original character names and situations — not reproductions of Sally-Anne or other classic paradigms. Pragmatic inference items are original compositions testing Gricean maxim violations in novel contexts.

### Dataset

Items are constructed with deterministic parameters. Per-task counts: false belief (34 scenarios: 4×T1, 4×T2, 6×T3, 12×T4, 8×T5), pragmatic inference (30 items across 3 tiers), sarcasm detection (20 items), emotional prosody (20 items).

**Scoring:** False belief uses tier-weighted accuracy (0.05×T1 + 0.05×T2 + 0.10×T3 + 0.60×T4 + 0.20×T5). Pragmatic inference composites per-tier score (intended accuracy − 0.1 × literal trap rate). Sarcasm uses normalized accuracy. Emotional prosody uses accuracy across emotion categories.

**Provenance:** All scenarios are original compositions. No standard ToM test batteries (e.g., Happé's Strange Stories, Faux Pas test) are reproduced verbatim.

### Technical Details

All tasks use the `kaggle-benchmarks` SDK with `@kbench.task` decorators. Key design decisions:

- **False belief (v5 design):** Earlier versions (v1–v4) showed ceiling effects (mean > 0.90) because text-based false belief is effectively reading comprehension for LLMs. The v5 redesign concentrates on 4th-order recursive belief tracking (A thinks B thinks C thinks D thinks X), where models must maintain a belief stack 4 levels deep. The critical discriminating feature is *perspective confusion traps* — scenarios where models answer what X actually thinks instead of what Y thinks X thinks.
- **Pragmatic inference (v2 design):** Original flat design scored 0.824–1.000 (std ≈ 0.061). The v2 redesign introduces literal trap rate scoring that penalizes models choosing literal interpretations of clearly non-literal utterances, weighted toward complex multi-layer items.
- **Sarcasm:** Context-dependent detection requires integration of speaker expectations, situational incongruity, and pragmatic markers — not just keyword matching.
- **kbench caching pitfall:** Module-level `.run()` calls fired during import with DummyLLM, caching invalid results. Fixed with `__name__` guards and cache clearing.

### Results, Insights, and Conclusions

We evaluated 10 models via Amazon Bedrock:

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| False Belief (ToM) | 0.710 | 0.178 | 0.623 | Llama 4 (1.00) | GPT-OSS-120B (0.38) |
| Pragmatic Inference | 0.733 | 0.220 | 0.652 | GPT-OSS-120B (0.96) | Nova Pro (0.30) |
| Sarcasm Detection | 0.839 | 0.141 | 0.481 | GLM 4.7 (0.95) | Llama 4 (0.46) |
| Emotional Prosody | 0.808 | 0.049 | 0.172 | Qwen3 80B (0.86) | Ministral 3B (0.69) |

**Insight 1 — No model dominates social cognition.** Unlike other tracks where Claude Opus or DeepSeek-R1 consistently lead, social cognition shows varied top performers: Llama 4 leads ToM, GPT-OSS-120B leads pragmatics, GLM 4.7 leads sarcasm, Qwen3 leads prosody. This suggests social cognitive abilities are shaped by training data composition (cultural exposure, dialogue data) rather than raw model scale.

**Insight 2 — ToM difficulty scales non-linearly with order.** Models show near-perfect 1st–3rd order performance but diverge sharply at 4th order. The most common failure mode is "perspective confusion" — answering what a character actually believes rather than what another character *thinks* they believe. This mirrors developmental findings where children master 1st-order ToM years before higher-order reasoning (Perner & Wimmer, 1985).

**Insight 3 — Pragmatic inference shows surprising inversions.** GPT-OSS-120B (0.96) dramatically outperforms Claude Opus (0.87) on pragmatic inference, while Nova Pro (0.30) collapses to near-floor. This wide range (0.652) suggests that conversational pragmatics — understanding speaker intent, Gricean maxim violations, and social context — varies dramatically across model families in ways not predicted by scale alone.

**Insight 4 — Sarcasm and prosody reveal a dissociation.** Llama 4 Maverick scores 0.46 on sarcasm (worst) but 0.82 on emotional prosody (near-top). Conversely, GLM 4.7 leads sarcasm (0.95) but scores below average on prosody (0.77). This double dissociation suggests sarcasm detection (requiring integration of incongruity, context, and speaker intent) taps different social-cognitive resources than emotional state inference.

**Average cross-benchmark std = 0.147**, demonstrating good overall discrimination. Pragmatic inference (std = 0.220) and false belief (std = 0.178) are the strongest discriminators.

### Organizational Affiliations

Independent submission — no organizational affiliation.

### References & Citations

- Baron-Cohen, S., Leslie, A. M. & Frith, U. (1985). Does the autistic child have a "theory of mind"? *Cognition*, 21(1), 37–46.
- Grice, H. P. (1975). Logic and conversation. In P. Cole & J. Morgan (Eds.), *Syntax and Semantics 3: Speech Acts* (pp. 41–58). Academic Press.
- Perner, J. & Wimmer, H. (1985). "John thinks that Mary thinks that…": Attribution of second-order beliefs by 5- to 10-year-old children. *Journal of Experimental Child Psychology*, 39(3), 437–471.
- Premack, D. & Woodruff, G. (1978). Does the chimpanzee have a theory of mind? *Behavioral and Brain Sciences*, 1(4), 515–526.
- Sperber, D. & Wilson, D. (1986). *Relevance: Communication and Cognition*. Blackwell.
- Happé, F. G. E. (1994). An advanced test of theory of mind. *Journal of Autism and Developmental Disorders*, 24(2), 129–154.
- Gibbs, R. W. (2000). Irony in talk among friends. *Metaphor and Symbol*, 15(1–2), 5–27.
