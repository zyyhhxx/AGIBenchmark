# Tests

- **`test_harness.py`** — Mock LLM test harness for running benchmarks without API access. Provides a `MockLLM` that returns predictable responses, allowing validation of task logic, scoring formulas, and data pipelines offline.

```bash
python -m pytest tests/test_harness.py
```
