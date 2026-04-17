# Can Large Language Models Read Between the Lines? Benchmarking Social Cognition Across Theory of Mind, Pragmatics, Sarcasm, and Emotional Prosody

## Problem Statement

Social cognition — the ability to interpret beliefs, intentions, and emotions of others — is foundational to human intelligence. It encompasses theory of mind, pragmatic inference, non-literal language comprehension, and affective signal interpretation. These capacities emerge early in human development and are prerequisites for effective communication, cooperation, and social reasoning.

Current LLM evaluations emphasize factual recall, logical reasoning, and code generation, yet largely neglect the social-cognitive abilities that underpin natural human interaction. When benchmarks do test social cognition, they typically assess only first-order belief attribution or surface-level sentiment, failing to probe the higher-order recursive reasoning and contextual sensitivity that characterize genuine social understanding. **How well do current language models track nested beliefs, recover intended meaning from what is *not* said, detect sarcasm without explicit cues, and infer emotional states from paralinguistic descriptions?**

## Task & Benchmark Construction

| Task | Construct | Tier Weights | Key References |
|------|-----------|-------------|----------------|
| **False Belief (ToM)** | Higher-order belief attribution (5 orders) | T1: 0.05, T2: 0.05, T3: 0.10, T4: 0.60, T5: 0.20 | Wimmer & Perner (1983); Perner & Wimmer (1985); Kinderman et al. (1998) |
| **Pragmatic Inference** | Gricean implicature understanding | Direct: 0.15, Indirect: 0.35, Complex: 0.50 | Grice (1975); Searle (1975); Sperber & Wilson (1986) |
| **Sarcasm Detection** | Non-literal language comprehension | Obvious: 0.05, Contextual: 0.15, Subtle: 0.80 | Gibbs (1986); Shamay-Tsoory et al. (2005) |
| **Emotional Prosody** | Paralinguistic/affective signal interpretation | Single tier | Scherer (1986); Barrett et al. (2019); Gross (2015) |

### Key Design Choices

**False Belief** extends classic paradigms (Wimmer & Perner, 1983; Baron-Cohen et al., 1985) to 5th-order belief attribution, following evidence that human recursive mentalizing capacity peaks around the 4th–5th order (Kinderman et al., 1998; Dunbar, 1998). Tier weights concentrate 80% of the score on 4th- and 5th-order items, where models must track chains such as "A thinks B thinks C thinks D thinks X." Scenarios include perspective confusion traps designed to penalize shallow pattern matching.

**Pragmatic Inference** tests Gricean implicature (Grice, 1975) with complex multi-layer implicatures carrying half the total weight. The scoring formula — per-tier intended accuracy minus 0.1 times the literal trap rate — penalizes models that default to literal interpretations, consistent with the distinction between what is said and what is meant (Horn, 1984; Brown & Levinson, 1987).

**Sarcasm Detection** weights 80% of the score on subtle sarcasm requiring integration of speaker expectations and situational incongruity, with no explicit lexical markers. This reflects findings that sarcasm comprehension relies on theory of mind and affective processing rather than surface cues (Shamay-Tsoory et al., 2005).

**Emotional Prosody** requires inferring emotional states from text descriptions of vocal tone, facial expressions, and situational context — testing whether models can process paralinguistic information presented verbally, drawing on dimensional models of emotion (Scherer, 1986) and constructionist frameworks (Barrett et al., 2019).

**Contamination resistance:** All scenarios are original compositions, not sourced from published test batteries. Higher-order belief scenarios use novel character configurations. Sarcasm items avoid well-known examples. The weighted emphasis on the hardest tiers reduces the benefit of memorized patterns.

## Dataset

All items are original compositions targeting specific cognitive constructs. False Belief includes 34 scenarios distributed across five orders. Pragmatic Inference and Sarcasm Detection each employ three-tier item sets with original conversational scenarios. Emotional Prosody uses multi-cue vignettes describing vocal, facial, and situational information. No copyrighted datasets or published test batteries are reproduced.

## Results, Insights, and Conclusions

We evaluated 6 models on the [Kaggle Community Benchmarks platform](https://www.kaggle.com/benchmarks/ianstudy/social-cognition), spanning frontier (Claude Opus 4.6, GPT-5.4, DeepSeek-R1, Gemini 2.5 Pro, Gemini 2.5 Flash) and small (Gemma 3 1B):

| Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score) |
|------|------|-----|-------|-------------------|---------------------|
| Sarcasm Detection | 0.914 | 0.126 | 0.348 | Gemini 2.5 Pro (1.00) | Gemma 3 1B (0.65) |
| False Belief (ToM) | 0.612 | 0.179 | 0.538 | GPT-5.4 (0.83) | Gemma 3 1B (0.30) |
| Pragmatic Inference | 0.541 | 0.165 | 0.534 | Claude Opus 4.6 (0.75) | Gemma 3 1B (0.21) |
| Emotional Prosody | 0.357 | 0.136 | 0.439 | Claude Opus 4.6 (0.57) | Gemma 3 1B (0.13) |

**Overall ranking:** Claude Opus 4.6 (0.731) > GPT-5.4 (0.706) > DeepSeek-R1 (0.682) > Gemini 2.5 Flash (0.599) > Gemini 2.5 Pro (0.596) > Gemma 3 1B (0.323).

**Insight 1 — Emotional Prosody is the hardest unsolved frontier.** With a mean of 0.357, even the best model (Claude Opus 4.6 at 0.57) falls far short of reliable affective inference. This aligns with Barrett et al.'s (2019) constructionist view that emotion recognition requires contextual integration rather than simple category matching — a capacity current architectures evidently lack.

**Insight 2 — Sarcasm detection is approaching saturation for frontier models.** Three models exceed 0.99 (Gemini 2.5 Pro at 1.00, Gemini 2.5 Flash at 0.99, GPT-5.4 at 0.99), and the task mean of 0.914 is the highest across all four tasks. The 0.80 weight on subtle sarcasm means these scores reflect genuine contextual reasoning, not keyword detection. The gap to Gemma 3 1B (0.65) confirms this capacity correlates with model scale, consistent with the role of theory of mind in sarcasm processing (Shamay-Tsoory et al., 2005).

**Insight 3 — No single model dominates across all social-cognitive dimensions.** Claude Opus leads pragmatics (0.75) and prosody (0.57), GPT-5.4 leads ToM (0.83), and Gemini 2.5 Pro achieves perfect sarcasm (1.00). This fragmentation suggests social cognition is not a unitary capability that scales uniformly but depends on training data composition and fine-tuning emphasis.

**Insight 4 — GPT-5.4 exhibits a striking dissociation between mentalizing and pragmatics.** Its ToM score of 0.83 is the highest by a clear margin, yet its pragmatic inference score of 0.56 is mid-range. This mirrors findings in developmental psychology where belief attribution and conversational implicature follow distinct developmental trajectories (Miller, 2009; Perner & Wimmer, 1985), suggesting these models may acquire social-cognitive components independently.

**Insight 5 — The Gemini models reveal a possible training data signature.** Gemini 2.5 Pro and Flash both achieve near-perfect sarcasm (1.00 and 0.99) yet score notably lower on ToM (0.53 and 0.58). This pattern — high surface-level social language performance with weak recursive mentalizing — is consistent with exposure to abundant labeled sarcasm data without corresponding emphasis on higher-order belief reasoning.

**Insight 6 — 4th-order ToM weighting prevents ceiling effects.** The task mean of 0.612 with std = 0.179 provides strong discriminative power. Without the heavy 4th-order weighting (0.60), lower-order items alone would push most frontier models near ceiling, collapsing meaningful distinctions. This validates the design informed by Dunbar's (1998) social brain hypothesis and Kinderman et al.'s (1998) work on recursive mentalizing limits.

**Average cross-benchmark std = 0.152**, confirming meaningful model separation across social-cognitive dimensions. The 2.3× ratio between top (0.731) and bottom (0.323) demonstrates that the suite discriminates effectively even with a limited model roster.

## References

- Baron-Cohen, S., Leslie, A. M. & Frith, U. (1985). Does the autistic child have a "theory of mind"? *Cognition*, 21(1), 37–46.
- Barrett, L. F. et al. (2019). Emotional expressions reconsidered. *Psychological Science in the Public Interest*, 20(1), 1–68.
- Brown, P. & Levinson, S. C. (1987). *Politeness: Some Universals in Language Usage*. Cambridge University Press.
- Dunbar, R. I. M. (1998). The social brain hypothesis. *Evolutionary Anthropology*, 6(5), 178–190.
- Gibbs, R. W. (1986). On the psycholinguistics of sarcasm. *Journal of Experimental Psychology: General*, 115(1), 3–15.
- Grice, H. P. (1975). Logic and conversation. In P. Cole & J. L. Morgan (Eds.), *Syntax and Semantics 3: Speech Acts* (pp. 41–58). Academic Press.
- Gross, J. J. (2015). Emotion regulation: Current status and future prospects. *Psychological Inquiry*, 26(1), 1–26.
- Horn, L. R. (1984). Toward a new taxonomy for pragmatic inference. In D. Schiffrin (Ed.), *Meaning, Form, and Use in Context* (pp. 11–42). Georgetown University Press.
- Kinderman, P., Dunbar, R. I. M. & Bentall, R. P. (1998). Theory-of-mind deficits and causal attributions. *British Journal of Psychology*, 89(2), 191–204.
- Miller, S. A. (2009). Children's understanding of second-order mental states. *Psychological Bulletin*, 135(5), 749–773.
- Perner, J. & Wimmer, H. (1985). "John thinks that Mary thinks that…" *Journal of Experimental Child Psychology*, 39(3), 437–471.
- Scherer, K. R. (1986). Vocal affect expression: A review and a model for future research. *Psychological Bulletin*, 99(2), 143–165.
- Searle, J. R. (1975). Indirect speech acts. In P. Cole & J. L. Morgan (Eds.), *Syntax and Semantics 3: Speech Acts* (pp. 59–82). Academic Press.
- Shamay-Tsoory, S. G., Tomer, R. & Aharon-Peretz, J. (2005). The neuroanatomical basis of understanding sarcasm and its relationship to social cognition. *Neuropsychology*, 19(3), 288–300.
- Sperber, D. & Wilson, D. (1986). *Relevance: Communication and Cognition*. Blackwell.
- Wimmer, H. & Perner, J. (1983). Beliefs about beliefs: Representation and constraining function of wrong beliefs. *Cognition*, 13(1), 103–128.
