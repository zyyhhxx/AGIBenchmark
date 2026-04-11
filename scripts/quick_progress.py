#!/usr/bin/env python3
import json, os

models = [
    'anthropic.claude-opus-4-6-v1', 'deepseek.r1-v1_0', 'openai.gpt-oss-120b-1_0',
    'meta.llama3-3-70b-instruct-v1_0', 'meta.llama4-maverick-17b-instruct-v1_0',
    'amazon.nova-pro-v1_0', 'anthropic.claude-sonnet-4-6', 'zai.glm-4.7',
    'qwen.qwen3-next-80b-a3b', 'mistral.ministral-3-3b-instruct'
]

total_done = 0
for m in models:
    f = f'results/{m}.json'
    if os.path.exists(f):
        d = json.load(open(f))
        s = len(d.get('scores', {}))
        e = len(d.get('errors', {}))
        print(f'{m}: {s}/26 scored, {e} errors')
        if s == 26:
            total_done += 1
    else:
        print(f'{m}: MISSING')

print(f'\nComplete: {total_done}/10 models')
