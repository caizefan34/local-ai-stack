"""Control-plane bootstrap and server command."""
from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path

import uvicorn

from .app import ROOT, create_app
from .store import Store


def main() -> None:
    parser = argparse.ArgumentParser(description="Local AI Stack authenticated control plane")
    parser.add_argument("--database", type=Path, default=Path(os.getenv("CONTROL_PLANE_DB", ROOT / "data" / "control-plane.sqlite3")))
    commands = parser.add_subparsers(dest="command", required=True)
    bootstrap = commands.add_parser("bootstrap-admin", help="Create the first dashboard administrator")
    bootstrap.add_argument("--username", default="admin")
    bootstrap.add_argument("--password", help="Password; omit to enter it securely")
    serve = commands.add_parser("serve", help="Run the authenticated dashboard")
    serve.add_argument("--host", default=os.getenv("CONTROL_PLANE_HOST", "127.0.0.1"))
    serve.add_argument("--port", type=int, default=int(os.getenv("CONTROL_PLANE_PORT", "18080")))
    args = parser.parse_args()
    if args.command == "bootstrap-admin":
        password = args.password or getpass.getpass("Administrator password: ")
        store = Store(args.database)
        store.initialize()
        store.create_user(args.username, password, "admin")
        print(f"Created administrator {args.username!r} in {args.database}")
        return
    uvicorn.run(create_app(args.database), host=args.host, port=args.port)


if __name__ == "__main__":
    main()

