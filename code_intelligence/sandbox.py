"""Run code in an ephemeral, network-isolated Docker container.

The project directory is mounted read-only. Generated files are limited to a
temporary in-container filesystem and the caller must explicitly choose the
command to run. This is intended for user-confirmed snippets and tests only.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def docker_command(workspace: Path, image: str, command: str, timeout: int) -> list[str]:
    workspace = workspace.resolve()
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "--pids-limit", "128", "--memory", "512m", "--cpus", "1",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=128m",
        "--mount", f"type=bind,src={workspace},dst=/workspace,readonly",
        "--workdir", "/workspace", image, "sh", "-lc", command,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a user-approved command in a locked-down Docker sandbox")
    parser.add_argument("--workspace", type=Path, required=True, help="Project directory mounted read-only")
    parser.add_argument("--image", default="python:3.12-alpine", help="Container image to use")
    parser.add_argument("--command", required=True, help="Command to execute inside the container")
    parser.add_argument("--timeout", type=int, default=30, help="Host-side timeout in seconds")
    args = parser.parse_args()
    if not args.workspace.is_dir():
        parser.error(f"Not a directory: {args.workspace}")
    if args.timeout < 1 or args.timeout > 300:
        parser.error("--timeout must be between 1 and 300 seconds")
    try:
        result = subprocess.run(docker_command(args.workspace, args.image, args.command, args.timeout), timeout=args.timeout)
    except FileNotFoundError:
        parser.error("Docker is required for sandbox execution")
    except subprocess.TimeoutExpired:
        raise SystemExit(f"Sandbox timed out after {args.timeout} seconds")
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
