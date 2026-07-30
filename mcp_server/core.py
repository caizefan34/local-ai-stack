"""Dependency-free clients used by the Local AI Stack MCP server."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
RERANKER_BASE_URL = os.getenv("RERANKER_BASE_URL", "http://127.0.0.1:18888").rstrip("/")
FASTGPT_BASE_URL = os.getenv("FASTGPT_BASE_URL", "http://127.0.0.1:3000").rstrip("/")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
REQUEST_TIMEOUT = float(os.getenv("LOCAL_AI_REQUEST_TIMEOUT", "60"))
MAX_PROMPT_CHARS = int(os.getenv("MCP_MAX_PROMPT_CHARS", "50000"))
MAX_DOCUMENTS = int(os.getenv("MCP_MAX_DOCUMENTS", "64"))


class LocalAIError(RuntimeError):
    """A user-facing local service error."""


def _request_json(url: str, payload: dict[str, Any] | None = None, timeout: float | None = None) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"} if body else {},
        method="POST" if body else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout or REQUEST_TIMEOUT) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read(512).decode("utf-8", errors="replace").strip()
        raise LocalAIError(f"{url} returned HTTP {error.code}: {detail or error.reason}") from error
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise LocalAIError(f"Could not call {url}: {error}") from error


def _probe(url: str, json_response: bool = False) -> dict[str, Any]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=min(REQUEST_TIMEOUT, 5)) as response:
            detail = json.load(response) if json_response else {"http_status": response.status}
            return {"ok": response.status < 500, **detail}
    except Exception as error:  # Health output should include every service.
        return {"ok": False, "error": str(error)}


def stack_health() -> dict[str, Any]:
    return {
        "ollama": _probe(f"{OLLAMA_BASE_URL}/api/tags", json_response=True),
        "reranker": _probe(f"{RERANKER_BASE_URL}/health", json_response=True),
        "fastgpt": _probe(f"{FASTGPT_BASE_URL}/"),
    }


def list_models() -> list[dict[str, Any]]:
    result = _request_json(f"{OLLAMA_BASE_URL}/api/tags")
    return [
        {"name": item.get("name", ""), "size": item.get("size", 0), "modified_at": item.get("modified_at", "")}
        for item in result.get("models", [])
    ]


def generate(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.1, max_tokens: int = 512) -> str:
    prompt = str(prompt).strip()
    if not prompt:
        raise ValueError("prompt must not be empty")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ValueError(f"prompt exceeds {MAX_PROMPT_CHARS} characters")
    if not 0 <= temperature <= 2:
        raise ValueError("temperature must be between 0 and 2")
    if not 1 <= max_tokens <= 4096:
        raise ValueError("max_tokens must be between 1 and 4096")
    result = _request_json(
        f"{OLLAMA_BASE_URL}/api/generate",
        {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": temperature, "num_predict": max_tokens}},
    )
    return str(result.get("response", ""))


def rerank(query: str, documents: list[str], top_k: int | None = None) -> list[dict[str, Any]]:
    query = str(query).strip()
    if not query:
        raise ValueError("query must not be empty")
    if not documents or len(documents) > MAX_DOCUMENTS:
        raise ValueError(f"documents must contain between 1 and {MAX_DOCUMENTS} items")
    if top_k is not None and not 1 <= top_k <= len(documents):
        raise ValueError("top_k must be between 1 and the number of documents")
    result = _request_json(f"{RERANKER_BASE_URL}/rerank", {"query": query, "documents": documents, "top_k": top_k})
    return list(result.get("results", []))


def public_configuration() -> dict[str, Any]:
    return {
        "ollama_base_url": OLLAMA_BASE_URL,
        "reranker_base_url": RERANKER_BASE_URL,
        "fastgpt_base_url": FASTGPT_BASE_URL,
        "default_model": DEFAULT_MODEL,
        "request_timeout_seconds": REQUEST_TIMEOUT,
        "limits": {"max_prompt_chars": MAX_PROMPT_CHARS, "max_documents": MAX_DOCUMENTS},
    }

