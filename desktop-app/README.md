# Desktop Dashboard

A lightweight HTML dashboard for monitoring and controlling your Local AI Stack.

## Features

- Real-time service status (Ollama, FastGPT, Reranker, Docker)
- One-click Start/Stop all services
- Knowledge Base sync trigger
- Metrics overview (models, datasets, documents)
- Auto-refresh every 15 seconds

## Usage

Open `dashboard.html` in any browser:

```bash
start desktop-app/dashboard.html
```

Or serve with Python:

```bash
cd local-ai-stack
python -m http.server 8080
# Open http://localhost:8080/desktop-app/dashboard.html
```

## Configuration

Copy `config.template.json` to `~/.ai-desktop/config.json` and adjust:

```json
{
  "syncTime": "03:00",
  "autoSync": true,
  "syncDay": "Sunday"
}
```
