#!/bin/bash
set -e
cd /home/ubuntu/.openclaw/workspace-agi-bench/repo

# Missing social_cog_emotional_prosody: Opus, Sonnet, GLM, GPT-OSS, Qwen3
# Missing metacog_error_detection: Opus, Sonnet, DeepSeek, Nova Pro, Qwen3
# Missing learning_curves: ALL 10

# social_cog_emotional_prosody missing models
for model in "anthropic.claude-opus-4-6-v1" "anthropic.claude-sonnet-4-6" "zai.glm-4.7" "openai.gpt-oss-120b-1:0" "qwen.qwen3-next-80b-a3b"; do
  echo "--- social_cog_emotional_prosody / $model ---"
  timeout 300 .venv/bin/python3 scripts/run_benchmark_bedrock.py --model "$model" --benchmark social_cog_emotional_prosody 2>&1 | grep -E "Score:|ERROR|FAILED|saved" || echo "TIMEOUT/FAIL: $model"
  sleep 2
done

# metacog_error_detection missing models
for model in "anthropic.claude-opus-4-6-v1" "anthropic.claude-sonnet-4-6" "deepseek.r1-v1:0" "amazon.nova-pro-v1:0" "qwen.qwen3-next-80b-a3b"; do
  echo "--- metacog_error_detection / $model ---"
  timeout 300 .venv/bin/python3 scripts/run_benchmark_bedrock.py --model "$model" --benchmark metacog_error_detection 2>&1 | grep -E "Score:|ERROR|FAILED|saved" || echo "TIMEOUT/FAIL: $model"
  sleep 2
done

# learning_curves ALL models
for model in "anthropic.claude-opus-4-6-v1" "anthropic.claude-sonnet-4-6" "deepseek.r1-v1:0" "zai.glm-4.7" "openai.gpt-oss-120b-1:0" "meta.llama3-3-70b-instruct-v1:0" "meta.llama4-maverick-17b-instruct-v1:0" "mistral.ministral-3-3b-instruct" "amazon.nova-pro-v1:0" "qwen.qwen3-next-80b-a3b"; do
  echo "--- learning_curves / $model ---"
  timeout 900 .venv/bin/python3 scripts/run_benchmark_bedrock.py --model "$model" --benchmark learning_curves 2>&1 | grep -E "Score:|ERROR|FAILED|saved" || echo "TIMEOUT/FAIL: $model"
  sleep 2
done

echo "ALL DONE"
