# Metacognition Research Notes

## Nelson & Narens (1990) Framework

Core model: two interacting levels — **object-level** (cognition) and **meta-level** (monitoring/control).

### Monitoring processes (object → meta)
- **Ease-of-Learning (EOL)**: Pre-study judgment of how easy something will be to learn
- **Judgment-of-Learning (JOL)**: During/after study, prediction of future recall
- **Feeling-of-Knowing (FOK)**: After failed recall, prediction of future recognition
- **Confidence Judgments**: Post-answer certainty rating

### Control processes (meta → object)
- Allocation of study time
- Strategy selection
- Termination of study/search

### Key insight for benchmarking
The framework separates **monitoring accuracy** from **control effectiveness**. 
For LLMs, we can test monitoring (calibration between predicted and actual performance) 
and control (whether models adaptively adjust their behavior based on self-assessment).

## LLM Metacognition Literature (2024-2026)

### Key findings
1. **LLMs show limited but real metacognition** — can sometimes distinguish what they know vs. don't know
2. **Overconfidence is pervasive** — models tend to express high confidence even on incorrect answers
3. **Calibration varies by domain** — better on factual knowledge, worse on reasoning
4. **Scale design matters** — confidence scale granularity affects measured metacognitive sensitivity (meta-d')
5. **Prompting can elicit better metacognition** — telling models they may not know helps

### Methodological approaches
- **Matthews Correlation Coefficient ("Introspection Score")**: Correlation between model's delegate/answer choice and actual correctness
- **meta-d'**: Signal detection metric for metacognitive sensitivity  
- **ECE (Expected Calibration Error)**: Difference between confidence and accuracy across bins
- **Confidence-accuracy correlation**: Simple Pearson/Spearman between stated confidence and correctness

### Gaps we can exploit
- Most studies use simple factual QA — we can test metacognition on **reasoning tasks**
- Few studies examine **metacognitive control** (not just monitoring)
- Novel: test metacognition about **learning** (cross-embed with Learning track)
- Novel: test whether models can **predict difficulty for other models** (social metacognition analog)

## Benchmark Design Principles

1. **Separate monitoring from performance**: Model's task answer and metacognitive judgment must be independently scored
2. **Use diverse difficulty levels**: Need spread of easy/hard items for calibration analysis
3. **Avoid contamination**: Use novel stimuli where possible (procedurally generated)
4. **Multiple metacognitive measures**: FOK, JOL, confidence, error detection
5. **Shortcut resistance**: Models shouldn't be able to game metacognitive judgments without genuine self-knowledge
