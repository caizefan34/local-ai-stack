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

To install a desktop shortcut with the dragon mascot icon, run once:

```powershell
.\desktop-app\install-shortcut.ps1
```

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

## Native Desktop App (Electron)

The repository now ships a native Electron desktop shell (`desktop-app/electron/`) so the dashboard opens as a real desktop application instead of a browser tab:

- Custom dark splash screen with the mascot, then a frameless 1360x860 application window with a Codex-style top bar (drag to move, minimize / maximize / close)
- One-click tabs in the top bar: `控制台` (control plane, port 18080) and `FastGPT` (port 3000), plus back / forward / reload
- `Local AI Stack` shortcut opens the control plane; `AI Desktop` shortcut opens FastGPT directly (`--fastgpt`)
- Automatically starts the control plane when it is not running (no duplicate instances)
- Single-instance lock, external links open in the default browser
- Desktop shortcuts `Local AI Stack` and `AI Desktop` point here

First run installs the Electron runtime automatically (~100 MB). In China, if the download fails, run once with the mirror:

```powershell
$env:ELECTRON_MIRROR = "https://npmmirror.com/mirrors/electron/"
npm install --save-dev electron@latest
```

Recreate/update the desktop shortcuts:

```powershell
.\desktop-app\electron\install-shortcuts.ps1
```

The legacy browser-mode launcher (`.\desktop-app\launch.ps1`) is kept as a fallback.
