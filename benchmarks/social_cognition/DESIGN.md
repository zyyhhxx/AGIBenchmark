# Social Cognition Track — Design Document

## Cognitive Science Framework

Social cognition encompasses the mental processes involved in perceiving, interpreting, and responding to other people's mental states, intentions, and social signals. We focus on three core components:

1. **Theory of Mind (ToM)** — Attributing beliefs, desires, and intentions to others
2. **Pragmatic Inference** — Understanding what speakers mean beyond what they literally say
3. **Sarcasm Detection** — Integrating context with utterance to detect non-literal intent

These abilities are deeply interconnected: sarcasm detection requires ToM (understanding the speaker's actual belief) and pragmatic competence (recognizing conversational implicatures).

### Key References
- Premack, D., & Woodruff, G. (1978). Does the chimpanzee have a theory of mind? *Behavioral and Brain Sciences, 1*(4), 515–526.
- Baron-Cohen, S., Leslie, A. M., & Frith, U. (1985). Does the autistic child have a "theory of mind"? *Cognition, 21*(1), 37–46.
- Wimmer, H., & Perner, J. (1983). Beliefs about beliefs. *Cognition, 13*(1), 103–128.
- Grice, H. P. (1975). Logic and conversation. In *Syntax and Semantics* (Vol. 3, pp. 41–58).
- Gibbs, R. W. (1986). On the psycholinguistics of sarcasm. *Journal of Experimental Psychology: General, 115*(1), 3–15.
- Shamay-Tsoory, S. G., Tomer, R., & Aharon-Peretz, J. (2005). The neuroanatomical basis of understanding sarcasm. *Neuropsychology, 19*(3), 288.

---

## Benchmark 1: False-Belief Theory of Mind

### What it tests
**Belief attribution.** Can the model track what another agent believes, even when that belief is false (i.e., differs from reality)?

### Design
- 20 scenarios: 10 first-order, 10 second-order false beliefs
- **1st-order**: "Where will Sally look?" (Sally doesn't know the object moved)
- **2nd-order**: "Where does Mary think John will look?" (recursive mentalizing)
- 3 questions per scenario: belief, reality control, memory control
- Score isolates ToM from comprehension by subtracting control failures

### Scoring
| Metric | Weight | What it measures |
|--------|--------|-----------------|
| 1st-order (adjusted) | 0.30 | Basic belief attribution |
| 2nd-order (adjusted) | 0.40 | Recursive mentalizing |
| Control accuracy | 0.30 | Scenario comprehension |

Adjusted = belief_accuracy - max(0, 1 - control_accuracy)

### Shortcut Resistance
- Belief answer ALWAYS differs from reality → can't just answer "where is it"
- Control questions catch models that don't understand the scenario
- 2nd-order requires tracking TWO agents' beliefs
- Diverse scenarios prevent template matching

### Human Baselines
- 1st-order: ~95% (adults), ~50% (4-year-olds, pre-ToM)
- 2nd-order: ~80% (adults), ~35% (6-year-olds)
- Controls: ~98% (adults)

---

## Benchmark 2: Pragmatic Inference

### What it tests
**Understanding speaker intent beyond literal meaning.** Tests Gricean maxims and conversational implicatures.

### Design
- 20 items across 4 categories:
  - Scalar implicature (5): "some" → "not all"
  - Indirect requests (5): "It's cold in here" → "close the window"
  - Irony/sarcasm (5): Saying opposite of what you mean
  - Understatement (5): Minimizing significant events
- Each item has both intended and literal meaning patterns
- Model must identify the speaker's TRUE intended meaning

### Scoring
| Metric | Weight | What it measures |
|--------|--------|-----------------|
| Intended accuracy | primary | Correct identification of speaker intent |
| Literal trap rate | penalty (-0.1×) | Being fooled by surface meaning |

Score = intended_accuracy - 0.1 × literal_trap_rate

### Shortcut Resistance
- Each item has explicit literal vs. intended meaning distinction
- Diverse pragmatic types prevent single-strategy approach
- Rich context required for correct interpretation
- No simple keyword matching works across all types

### Human Baselines
- Adults: ~90-95% intended accuracy, ~2-5% literal trap rate
- Children (5-6): ~60-70% intended accuracy (developing pragmatic competence)

---

## Benchmark 3: Sarcasm Detection in Context

### What it tests
**Context-dependent sarcasm detection.** Can the model detect when utterances are sarcastic vs. sincere based on contextual cues?

### Design
- 40 items: 20 sarcastic, 20 sincere
- **Matched pairs**: Many sarcastic/sincere pairs share the SAME surface utterance
  - "Well, that was quick service!" → sarcastic (after 45-min wait) or sincere (after 2-min service)
- Model rates sincerity 0-100
- Signal detection analysis (AUC) + calibration

### Scoring
| Metric | Weight | What it measures |
|--------|--------|-----------------|
| AUC | 0.50 | Discrimination between sarcastic and sincere |
| 1 - Calibration error | 0.30 | Rating accuracy |
| Threshold accuracy | 0.20 | Binary classification at 50 |

### Shortcut Resistance
- Matched pairs force context reliance — same words, different intent
- 50/50 base rate prevents frequency shortcuts
- Continuous rating reveals calibration, not just binary classification
- Rich, diverse contexts prevent pattern matching

### Human Baselines
- Adults with context: ~95% AUC, ~90% threshold accuracy
- Without context: ~65% (near chance for matched pairs)

---

## Track-Level Design Notes

### Construct Validity
All three benchmarks tap into social cognition but at different levels:
- **False belief**: core mentalizing ability
- **Pragmatic inference**: language-mediated social reasoning
- **Sarcasm detection**: integrated social + linguistic processing

A model could theoretically score high on sarcasm detection via pattern matching without genuine ToM. The false-belief benchmark controls for this by requiring explicit belief tracking.

### Contamination Resistance
- All scenarios are original compositions (not from published test batteries)
- Matched sarcasm pairs prevent keyword-based shortcuts
- False-belief scenarios use diverse settings (not just Sally-Anne variations)
- Pragmatic items use real-world contexts requiring world knowledge

### Cultural Considerations
Current items are primarily Western-context. Future iterations should include cross-cultural pragmatic norms (directness varies by culture).

---

## Benchmark 4: Emotional Prosody in Text

### Cognitive Science Basis
- Emotional prosody perception (Scherer, 1986): detecting emotion from vocal/textual cues
- Text-based emotion recognition (Barrett et al., 2019)
- Emotion regulation detection (Gross, 2015)

### Design
1. Present multi-turn dialogues (6 with emotional tone shifts, 4 controls with no shift)
2. Shift types: friendly→hostile, professional→anxious, sympathetic→frustrated, neutral→excited, cheerful→melancholic, confident→defensive
3. Model must: detect shift presence, identify turn, label emotions before/after, identify trigger

### Metrics
- Shift detection accuracy (sensitivity)
- Emotion labeling accuracy (with synonym matching)
- Trigger identification quality
- False alarm rate on control dialogues

### Score formula
`0.40 * shift_detection + 0.30 * emotion_labeling + 0.20 * trigger_id + 0.10 * (1 - false_alarm)`

### Files
- `task_emotional_prosody.py`
