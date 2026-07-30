# Multi-user access control

FastGPT has its own account and team management UI. Local AI Stack additionally protects the Dashboard control actions with a local control plane.

Create the first local administrator, then start the authenticated dashboard:

```powershell
python -m pip install -r control_plane/requirements.txt
python -m control_plane bootstrap-admin --username admin
python -m control_plane serve
```

Open `http://127.0.0.1:18080/` and sign in. The service defaults to loopback-only binding.

Roles:

- `viewer`: service health only;
- `operator`: health plus the allowlisted start, stop, and knowledge-base sync actions;
- `admin`: operator access plus user creation, role changes, and account disablement.

The Agent workbench is also administrator-only. It can inspect only the server-configured workspace through the bounded read-only tools; the Dashboard does not accept a workspace path from the browser. See [Agent workflows](agent-workflows.md) for workspace and model configuration.

Sessions use random bearer tokens stored only as SHA-256 digests in `data/control-plane.sqlite3`, expire after eight hours by default, and are invalidated when an account is disabled. The action endpoint has no command argument: only its fixed allowlist can run.

Use FastGPT's own UI to create chat users and teams. Do not expose this control plane publicly; for remote administration, keep it behind a VPN or authenticated reverse proxy and set `CONTROL_PLANE_HOST` deliberately.
