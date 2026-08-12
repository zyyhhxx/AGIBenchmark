#!/usr/bin/env python3
"""Fix the scoring script to support multi-turn conversations within chat contexts."""

with open('scripts/run_benchmark_bedrock.py', 'r') as f:\n    content = f.read()\n\n# 1. Replace setup_kbench_mocks() to add ChatSession and ChatManager classes after it\nold_setup = '''def setup_kbench_mocks():
    """Patch kaggle_benchmarks for local execution."""
    import kaggle_benchmarks as kbench
    from unittest.mock import MagicMock

    class DummyLLM:
        def prompt(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'
        def __call__(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'

    kbench.llm = DummyLLM()
    if not hasattr(kbench, 'log'):
        kbench.log = lambda x: None

    class DummyChatCtx:
        def new(self, name=""):
            return self
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass

    if not hasattr(kbench, 'chats') or kbench.chats is None:
        kbench.chats = DummyChatCtx()
    elif not hasattr(kbench.chats, 'new'):
        kbench.chats = DummyChatCtx()'''

new_setup = '''def setup_kbench_mocks():
    """Patch kaggle_benchmarks for local execution."""
    import kaggle_benchmarks as kbench
    from unittest.mock import MagicMock

    class DummyLLM:
        def prompt(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'
        def __call__(self, *a, **kw): return '{"answer": "unknown", "confidence": 50}'

    kbench.llm = DummyLLM()
    if not hasattr(kbench, 'log'):
        kbench.log = lambda x: None

    # Chat context is set up per-run in run_one() with the actual LLM reference.
    # Install a no-op fallback here for early access.
    class DummyChatCtx:
        def new(self, name=""):
            return self
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass

    if not hasattr(kbench, 'chats') or kbench.chats is None:
        kbench.chats = DummyChatCtx()
    elif not hasattr(kbench.chats, 'new'):
        kbench.chats = DummyChatCtx()


class ChatSession:
    """Context manager for an isolated multi-turn chat.

    On enter: signals the LLM to start accumulating conversation history.
    On exit: signals the LLM to clear history (back to single-turn mode).
    """
    def __init__(self, llm, name=""):
        self._llm = llm
        self._name = name

    def __enter__(self):
        if hasattr(self._llm, '_start_chat'):
            self._llm._start_chat(self._name)
        return self

    def __exit__(self, *a):
        if hasattr(self._llm, '_end_chat'):
            self._llm._end_chat()


class ChatManager:
    """Manages isolated chat contexts, bridging kbench.chats.new() to the LLM."""
    def __init__(self, llm):
        self._llm = llm

    def new(self, name=""):
        return ChatSession(self._llm, name)'''

assert old_setup in content, "Could not find old setup_kbench_mocks"
content = content.replace(old_setup, new_setup)
print("  [1/4] Added ChatSession + ChatManager classes")

# 2. Replace the BedrockLLM class's __init__ and _call to support multi-turn
old_init_call = '''    class BedrockLLM:
        def __init__(self, max_retries=3, retry_delay=5):
            self._client = client
            self._model_id = model_id
            self._max_retries = max_retries
            self._retry_delay = retry_delay
            self._total_input_tokens = 0
            self._total_output_tokens = 0

        def _call(self, prompt, max_tokens=4096):
            last_err = None
            for attempt in range(self._max_retries + 1):
                try:
                    resp = self._client.converse(
                        modelId=self._model_id,
                        messages=[{'role': 'user', 'content': [{'text': prompt}]}],
                        inferenceConfig={'maxTokens': max_tokens, 'temperature': 0.0}
                    )
                    usage = resp.get('usage', {})
                    self._total_input_tokens += usage.get('inputTokens', 0)
                    self._total_output_tokens += usage.get('outputTokens', 0)
                    # Handle models that return reasoningContent before text
                    content = resp['output']['message']['content']
                    for block in content:
                        if 'text' in block:
                            return block['text']
                    # Fallback: if only reasoningContent, extract that
                    for block in content:
                        if 'reasoningContent' in block:
                            rt = block['reasoningContent']
                            if isinstance(rt, dict) and 'reasoningText' in rt:
                                return rt['reasoningText'].get('text', str(rt))
                            return str(rt)
                    return str(content)'''

new_init_call = '''    class BedrockLLM:
        def __init__(self, max_retries=3, retry_delay=5):
            self._client = client
            self._model_id = model_id
            self._max_retries = max_retries
            self._retry_delay = retry_delay
            self._total_input_tokens = 0
            self._total_output_tokens = 0
            # Multi-turn chat state
            self._in_chat = False
            self._chat_name = ""
            self._messages = []

        def _start_chat(self, name=""):
            """Begin a new isolated chat context (clears history)."""
            self._in_chat = True
            self._chat_name = name
            self._messages = []

        def _end_chat(self):
            """End the current chat context."""
            self._in_chat = False
            self._chat_name = ""
            self._messages = []

        def _call(self, prompt, max_tokens=4096):
            # Build messages: multi-turn within chat, single-turn outside
            if self._in_chat:
                self._messages.append({'role': 'user', 'content': [{'text': prompt}]})
                messages = list(self._messages)
            else:
                messages = [{'role': 'user', 'content': [{'text': prompt}]}]

            last_err = None
            for attempt in range(self._max_retries + 1):
                try:
                    resp = self._client.converse(
                        modelId=self._model_id,
                        messages=messages,
                        inferenceConfig={'maxTokens': max_tokens, 'temperature': 0.0}
                    )
                    usage = resp.get('usage', {})
                    self._total_input_tokens += usage.get('inputTokens', 0)
                    self._total_output_tokens += usage.get('outputTokens', 0)
                    # Handle models that return reasoningContent before text
                    content = resp['output']['message']['content']
                    response_text = None
                    for block in content:
                        if 'text' in block:
                            response_text = block['text']
                            break
                    if response_text is None:
                        # Fallback: if only reasoningContent, extract that
                        for block in content:
                            if 'reasoningContent' in block:
                                rt = block['reasoningContent']
                                if isinstance(rt, dict) and 'reasoningText' in rt:
                                    response_text = rt['reasoningText'].get('text', str(rt))
                                else:
                                    response_text = str(rt)
                                break
                    if response_text is None:
                        response_text = str(content)

                    # Append assistant response to chat history
                    if self._in_chat:
                        self._messages.append({'role': 'assistant', 'content': [{'text': response_text}]})

                    return response_text'''

assert old_init_call in content, "Could not find old BedrockLLM init+call"
content = content.replace(old_init_call, new_init_call)
print("  [2/4] Replaced BedrockLLM.__init__ and _call with multi-turn support")

# 3. Add cleanup on error (after the last 'raise last_err' in _call)
old_except_end = '''                    else:
                        raise last_err'''

new_except_end = '''                    else:
                        # On failure within a chat, remove the user msg we added
                        if self._in_chat and self._messages and self._messages[-1]['role'] == 'user':
                            self._messages.pop()
                        raise last_err'''

# Only replace the FIRST occurrence (inside _call)
content = content.replace(old_except_end, new_except_end, 1)
print("  [3/4] Added error cleanup for chat messages")

# 4. In run_one(), after setup_kbench_mocks(), install ChatManager
old_run_one = '''    setup_kbench_mocks()

    # Re-import to pick up fresh data modules'''

new_run_one = '''    setup_kbench_mocks()

    # Install chat manager that bridges kbench.chats.new() to the actual LLM
    import kaggle_benchmarks as _kbench
    _kbench.chats = ChatManager(llm)

    # Re-import to pick up fresh data modules'''

assert old_run_one in content, "Could not find old run_one pattern"
content = content.replace(old_run_one, new_run_one)
print("  [4/4] Installed ChatManager in run_one()")

with open('scripts/run_benchmark_bedrock.py', 'w') as f:\n    f.write(content)\n\nprint("\nDone! Multi-turn chat support added to scoring script.")
