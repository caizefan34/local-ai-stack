# Desktop Dashboard

An authenticated, responsive dashboard for monitoring and controlling your Local AI Stack.

## Features

- Real-time service status (Ollama, FastGPT, Reranker, Docker)
- Role-gated Start/Stop and knowledge-base sync actions
- Knowledge Base sync trigger
- Metrics overview (models, datasets, documents)
- Auto-refresh every 15 seconds

## Usage

Create an administrator and serve the dashboard locally:

```bash
python -m pip install -r control_plane/requirements.txt
python -m control_plane bootstrap-admin --username admin
python -m control_plane serve
# Open http://127.0.0.1:18080/
```

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
