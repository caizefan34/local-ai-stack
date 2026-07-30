"""Local AI Stack MCP server using the official Python SDK."""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from . import core


mcp = FastMCP("local-ai-stack")


@mcp.tool()
def stack_health() -> dict:
    """Check whether Ollama, the reranker, and FastGPT are reachable."""
    return core.stack_health()


@mcp.tool()
def list_local_models() -> list[dict]:
    """List models currently installed in the local Ollama instance."""
    return core.list_models()


@mcp.tool()
def generate_local(prompt: str, model: str = core.DEFAULT_MODEL, temperature: float = 0.1, max_tokens: int = 512) -> str:
    """Generate text with a local Ollama model."""
    return core.generate(prompt, model=model, temperature=temperature, max_tokens=max_tokens)


@mcp.tool()
def rerank_documents(query: str, documents: list[str], top_k: int | None = None) -> list[dict]:
    """Rerank documents with the local BGE reranker."""
    return core.rerank(query, documents, top_k=top_k)


@mcp.resource("local-ai://configuration")
def configuration() -> str:
    """Read the non-secret endpoints, default model, and safety limits."""
    return json.dumps(core.public_configuration(), indent=2)


@mcp.prompt()
def review_code(code: str, focus: str = "correctness, security, and tests") -> str:
    """Create a structured local code-review prompt."""
    return f"Review the following code for {focus}. Return prioritized findings with concrete fixes.\n\n{code}"


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

