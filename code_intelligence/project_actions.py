"""Prepare project changes locally; execution always requires --confirm."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def require_confirm(args: argparse.Namespace, description: str) -> None:
    if args.confirm:
        return
    print(f"Preview: {description}")
    raise SystemExit("Re-run the exact command with --confirm to make this change")


def main() -> None:
    parser = argparse.ArgumentParser(description="Confirmed local project operations")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--confirm", action="store_true", help="Required before a mutation is executed")
    commands = parser.add_subparsers(dest="action", required=True)
    commit = commands.add_parser("commit", help="Create a local Git commit")
    commit.add_argument("--message", required=True)
    create = commands.add_parser("create-file", help="Create a UTF-8 text file inside the workspace")
    create.add_argument("--path", required=True)
    create.add_argument("--content", required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        parser.error(f"Not a workspace: {workspace}")
    if args.action == "commit":
        require_confirm(args, f"git commit in {workspace} with message: {args.message!r}")
        subprocess.run(["git", "commit", "-m", args.message], cwd=workspace, check=True)
    else:
        target = (workspace / args.path).resolve()
        if workspace not in target.parents:
            parser.error("--path must stay inside --workspace")
        require_confirm(args, f"create {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(args.content, encoding="utf-8")
        print(f"Created {target}")


if __name__ == "__main__":
    main()
