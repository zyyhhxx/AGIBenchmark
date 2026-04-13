# Structured Output Retry Bias

## Issue

18 of 26 notebooks use Kaggle Benchmarks' `schema=` parameter for structured JSON output. When a model's response fails to parse (e.g., DeepSeek-R1 wrapping output in `<think>` tags), the framework:

1. Sends the **full failed response** (including reasoning traces) back as a system message
2. Re-asks the same question with the parse error context
3. The model sees its own previous reasoning and can self-correct

This gives thinking models (DeepSeek-R1, etc.) a systematic advantage:
- **Extra reasoning context** — the model sees its own chain-of-thought from the failed attempt
- **Self-correction opportunity** — it can refine its answer on retry
- **Free-form fallback** — if JSON still fails, raw text is used, which may match `check_answer()` more loosely

Models that parse correctly on the first attempt (e.g., Claude) get none of these benefits.

## Evidence

DeepSeek-R1 on False Belief (Theory of Mind):
- **Local (Bedrock)**: 0.708
- **Kaggle (with retries)**: 1.000
- Nearly every response triggered a retry due to `<think>` tags

Claude Opus 4.6 on the same benchmark:
- **Local**: 0.583
- **Kaggle**: 0.583
- Zero retries (all first-attempt parses)

## Fix

Replace the retry pattern:
```python
# BEFORE (retry on failure = second LLM call)
try:
    response = llm.prompt(prompt, schema=MySchema)
    answer = response.answer
except Exception:
    answer = llm.prompt(prompt)  # <-- second call with retry context

# AFTER (single call, strip think tags, parse locally)
raw = llm.prompt(prompt)
cleaned = _strip_think(raw)
try:
    parsed = json.loads(re.search(r'\{.*\}', cleaned, re.DOTALL).group())
    answer = str(parsed.get("answer", cleaned))
except Exception:
    answer = cleaned  # use cleaned text, no retry
```

## Affected Notebooks (18/26)

| Notebook | Schema Calls | Retry Patterns |
|----------|-------------|----------------|
| exec_func_crt | 1 | 2 |
| exec_func_nback | 1 | 1 |
| learning_curriculum | 1 | 1 |
| learning_curves | 2 | 3 |
| learning_interference | 1 | 1 |
| learning_transfer | 3 | 5 |
| metacog_calibration | 1 | 2 |
| metacog_control | 2 | 3 |
| metacog_epistemic_humility | 1 | 2 |
| metacog_error_detection | 1 | 1 |
| metacog_fok | 2 | 4 |
| metacog_jol | 4 | 6 |
| metacog_learning_monitoring | 1 | 1 |
| social_cog_emotional_prosody | 1 | 1 |
| social_cog_false_belief | 3 | 3 |
| social_cog_pragmatic | 1 | 1 |
| social_cog_sarcasm | 1 | 1 |

**Unaffected:** All 4 Attention notebooks, exec_func_task_switch, exec_func_tol, exec_func_wcst, metacog_canary, metacog_epistemic_revision.

## Status

- [x] `social_cog_false_belief` — fixed
- [ ] Remaining 17 notebooks — pending
