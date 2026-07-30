"""Command-line interface for local agent workflows."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .engine import AgentEngine, AgentError
from .ollama_client import OllamaAgentModel
from .workflows import WORKFLOWS, get_workflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a bounded read-only Local AI Stack agent workflow")
    parser.add_argument("task", help="Investigation or diagnosis task")
    parser.add_argument("--workflow", choices=sorted(WORKFLOWS), default="workspace-investigate")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--max-steps", type=int, default=int(os.getenv("AGENT_MAX_STEPS", "8")))
    parser.add_argument("--json", action="store_true", help="Print answer and trace as JSON")
    args = parser.parse_args()
    try:
        engine = AgentEngine(OllamaAgentModel(args.model), args.workspace, get_workflow(args.workflow), max_steps=args.max_steps)
        result = engine.run(args.task)
    except (AgentError, ValueError, OSError) as error:
        print(f"Agent failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    if args.json:
        print(json.dumps({"answer": result.answer, "steps": result.steps, "trace": [event.__dict__ for event in result.trace]}, ensure_ascii=False, indent=2))
    else:
        for event in result.trace:
            print(f"[{event.step}] {event.action}: {event.summary}", file=sys.stderr)
        print(result.answer)


if __name__ == "__main__":
    main()
