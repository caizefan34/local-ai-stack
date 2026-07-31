"""Allowlisted operational actions. No caller-supplied command is executed."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess


class ActionError(RuntimeError):
    pass


def _compose_project() -> str:
    """Return the Compose project owning the running FastGPT stack, if any."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "fastgpt-pg", "--format", "{{index .Config.Labels \"com.docker.compose.project\"}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def run_action(name: str, root: Path) -> str:
    root = root.resolve()
    env_file = root / ".env"
    if not env_file.is_file():
        env_file = root / ".env.example"
    compose_file = root / "docker" / "docker-compose.yml"
    project = _compose_project()
    project_args = [f"--project-name={project}"] if project else []
    if name == "start-all":
        command = ["powershell", "-File", str(root / "scripts" / "start-all.ps1")] if os.name == "nt" else ["docker", "compose", *project_args, "--env-file", str(env_file), "-f", str(compose_file), "up", "-d"]
    elif name == "stop-all":
        command = ["docker", "compose", *project_args, "--env-file", str(env_file), "-f", str(compose_file), "down"]
    elif name == "sync-kb":
        sync = root / "knowledge-base" / "sync" / "run-kb-sync.sh"
        command = ["wsl", "bash", str(sync)] if os.name == "nt" else ["bash", str(sync)]
    else:
        raise ActionError("Unknown action")
    if not command[-1] or (name == "sync-kb" and not Path(command[-1]).is_file()):
        raise ActionError("Required action script was not found")
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ActionError(str(error)) from error
    output = (result.stdout + result.stderr).strip()
    if result.returncode:
        raise ActionError(output[-4000:] or f"Action exited with {result.returncode}")
    return output[-4000:] or "Action completed"