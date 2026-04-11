#!/bin/bash
set -e
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo

BENCHMARKS="attention_selective social_cog_emotional_prosody metacog_error_detection learning_curves"
MODELS=(
  "anthropic.claude-opus-4-6-v1"
  "anthropic.claude-sonnet-4-6"
  "deepseek.r1-v1:0"
  "zai.glm-4.7"
  "openai.gpt-oss-120b-1:0"
  "meta.llama3-3-70b-instruct-v1:0"
  "meta.llama4-maverick-17b-instruct-v1:0"
  "mistral.ministral-3-3b-instruct"
  "amazon.nova-pro-v1:0"
  "qwen.qwen3-next-80b-a3b"
)

for bm in $BENCHMARKS; do
  echo "======== BENCHMARK: $bm ========"
  for model in "${MODELS[@]}"; do
    echo "--- $bm / $model ---"
    timeout 900 .venv/bin/python3 scripts/run_benchmark_bedrock.py --model "$model" --benchmark "$bm" 2>&1 || echo "FAILED: $bm / $model"
    sleep 2
  done
done

echo "ALL DONE"
