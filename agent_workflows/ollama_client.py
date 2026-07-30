"""Ollama adapter for the strict agent action protocol."""
from __future__ import annotations

from mcp_server import core


class OllamaAgentModel:
    def __init__(self, model: str = core.DEFAULT_MODEL, max_tokens: int = 1024):
        self.model = model
        self.max_tokens = max_tokens

    def complete(self, prompt: str) -> str:
        return core.generate(prompt, model=self.model, temperature=0, max_tokens=self.max_tokens)

