# Desktop Dashboard

An authenticated, responsive dashboard for monitoring and controlling your Local AI Stack.

## Features

- Real-time service status (Ollama, FastGPT, Reranker, Docker)
- Role-gated Start/Stop and knowledge-base sync actions
- Knowledge Base sync trigger
- Metrics overview (models, datasets, documents)
- Auto-refresh every 15 seconds

## Usage

For a one-click desktop-style window on Windows, run:

```powershell
.\desktop-app\launch.ps1
```

You can also double-click [`Start Local AI Stack.cmd`](../Start%20Local%20AI%20Stack.cmd) in the repository root. It launches the same desktop window without opening a terminal.

The launcher starts the local control plane when needed and opens the dashboard in Edge/Chrome App mode. It falls back to the default browser if neither browser is installed. It does not install or modify Docker/Ollama.

For a browser-only launch, use `.\desktop-app\launch.ps1 -BrowserOnly`.

Serve the dashboard locally. On the first visit, the browser shows a one-time form for creating the administrator; no separate bootstrap command is required:

```bash
python -m pip install -r control_plane/requirements.txt
python -m control_plane serve
# Open http://127.0.0.1:18080/
```

The dashboard then guides you through service checks, allowlisted model downloads, service actions, and user management according to the signed-in user's role.

Do not open `dashboard.html` directly: it needs the authenticated control-plane API. See [`docs/multi-user-access.md`](../docs/multi-user-access.md) for user roles and remote-access guidance.

## Configuration

Copy `config.template.json` to `~/.ai-desktop/config.json` and adjust:

```json
{
  "syncTime": "03:00",
  "autoSync": true,
  "syncDay": "Sunday"
}
```
