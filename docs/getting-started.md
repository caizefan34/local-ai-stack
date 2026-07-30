# Local AI Stack: one-click setup

This is the shortest path from a fresh checkout to the local desktop control plane.

## Prerequisites

- Windows 10/11 with Docker Desktop, Ollama, and Python 3.10+
- 8 GB RAM minimum; 16 GB recommended
- Internet access for the first image and model downloads

Install Docker Desktop, Ollama, and Python first. Then run the guided setup once:

```powershell
git clone https://github.com/caizefan34/local-ai-stack.git
cd local-ai-stack
.\scripts\setup.ps1
```

For coding models, use `.\scripts\setup.ps1 -CodeMode`.

## Daily use

Run `.\desktop-app\install-shortcut.ps1` once to create the **Local AI Stack** desktop shortcut. After that, double-click the desktop icon. It starts the local control plane and opens an independent Edge/Chrome application window. If no Chromium browser is installed, it opens the default browser instead.

The repository also includes [`Start Local AI Stack.cmd`](../Start%20Local%20AI%20Stack.cmd) as a portable fallback when the shortcut has not been installed.

On the first visit, create the administrator in the browser. This replaces the old command-line bootstrap step. The setup endpoint is automatically disabled after the first account is created.

The Dashboard provides:

- service health for Ollama, FastGPT, and the reranker;
- start/stop and knowledge-base actions for operators;
- allowlisted Ollama model downloads;
- user and role management for administrators.

## Optional integrations

Start the local MCP server for an MCP-compatible client:

```powershell
python -m mcp_server.server
```

Run a bounded, read-only workspace investigation:

```powershell
python -m agent_workflows "List the top-level Python modules" --workspace . --model qwen3:8b
```

The desktop launcher does not install Docker or Ollama and does not expose the database ports. Keep `BIND_ADDRESS` and `DATABASE_BIND_ADDRESS` set to `127.0.0.1` unless a firewall and authenticated reverse proxy protect remote access.

## Troubleshooting

- If the window does not open, run `python -m control_plane serve` and open `http://127.0.0.1:18080` manually.
- If model downloads fail, verify `ollama list` and that Ollama is running on port 11434.
- If knowledge-base sync returns an error, configure `KB_WINDOWS_SOURCE` and `KB_WINDOWS_REF_SOURCE` and ensure the source folders exist.
- For account, model, and remote-access details, read [multi-user access](multi-user-access.md), [model manager](model-manager.md), and [production hardening](production-hardening.md).
