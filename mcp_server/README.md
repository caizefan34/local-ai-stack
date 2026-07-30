# Local AI Stack MCP server

The MCP server exposes the local stack to MCP-compatible clients over stdio. It does not open a network listener.

## Install and run

```bash
python -m pip install -r mcp_server/requirements.txt
python -m mcp_server.server
```

Example client configuration:

```json
{
  "mcpServers": {
    "local-ai-stack": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/absolute/path/to/local-ai-stack",
      "env": {
        "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
        "RERANKER_BASE_URL": "http://127.0.0.1:18888",
        "FASTGPT_BASE_URL": "http://127.0.0.1:3000"
      }
    }
  }
}
```

Available tools:

- `stack_health`
- `list_local_models`
- `generate_local`
- `rerank_documents`

The server also provides the `local-ai://configuration` resource and a `review_code` prompt. No passwords or `.env` contents are exposed.

