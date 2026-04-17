# Scripts

Utilities for running and validating benchmarks.

- **`run_benchmark_bedrock.py`** — Run benchmarks against Amazon Bedrock models. Supports running individual benchmarks, entire tracks, or all 26 benchmarks across any Bedrock-hosted model.
  ```bash
  python scripts/run_benchmark_bedrock.py --model anthropic.claude-sonnet-4-6 --benchmark metacog_fok
  python scripts/run_benchmark_bedrock.py --model all --track metacognition
  python scripts/run_benchmark_bedrock.py --list
  ```

- **`validate_all_benchmarks.py`** — Validates all 26 benchmark task files: checks imports, data loading, function signatures, and scoring bounds. No API key needed.
  ```bash
  python scripts/validate_all_benchmarks.py
  ```

- **`verify_ground_truth.py`** — Independently recomputes expected outputs for learning benchmarks and verifies them against stored ground truth. Exits non-zero on any mismatch.
  ```bash
  python scripts/verify_ground_truth.py
  ```
