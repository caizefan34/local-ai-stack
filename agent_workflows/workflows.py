"""Named workflow policies and prompts."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Workflow:
    name: str
    purpose: str
    instructions: str


WORKFLOWS = {
    "workspace-investigate": Workflow(
        "workspace-investigate",
        "Investigate a codebase and return an evidence-backed report.",
        "Locate relevant files, inspect only what is needed, cite file paths and line numbers, and separate evidence from inference.",
    ),
    "code-diagnose": Workflow(
        "code-diagnose",
        "Diagnose a code problem without changing files.",
        "Trace the likely cause, inspect tests and callers, then return a minimal suggested fix and verification steps. Never claim that a change was applied.",
    ),
}


def get_workflow(name: str) -> Workflow:
    try:
        return WORKFLOWS[name]
    except KeyError as error:
        raise ValueError(f"Unknown workflow {name!r}; choose from {', '.join(WORKFLOWS)}") from error

