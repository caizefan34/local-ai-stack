"""Strict action schemas for the local agent loop."""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


class ActionValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ToolAction:
    tool: str
    arguments: dict[str, Any]
    summary: str
    type: str = "tool"


@dataclass(frozen=True)
class FinalAction:
    answer: str
    type: str = "final"


Action = ToolAction | FinalAction


def _decode_json(text: str) -> dict[str, Any]:
    value = text.strip()
    if value.startswith("```"):
        lines = value.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            value = "\n".join(lines[1:-1])
    try:
        result = json.loads(value)
    except json.JSONDecodeError as error:
        raise ActionValidationError(f"Model output is not valid JSON: {error.msg}") from error
    if not isinstance(result, dict):
        raise ActionValidationError("Action must be a JSON object")
    return result


def parse_action(text: str) -> Action:
    item = _decode_json(text)
    action_type = item.get("type")
    if action_type == "tool":
        if set(item) != {"type", "tool", "arguments", "summary"}:
            raise ActionValidationError("Tool action must contain only type, tool, arguments, and summary")
        if not isinstance(item["tool"], str) or not item["tool"].strip():
            raise ActionValidationError("tool must be a non-empty string")
        if not isinstance(item["arguments"], dict):
            raise ActionValidationError("arguments must be an object")
        if not isinstance(item["summary"], str) or not item["summary"].strip() or len(item["summary"]) > 240:
            raise ActionValidationError("summary must contain 1-240 characters")
        return ToolAction(item["tool"], item["arguments"], item["summary"].strip())
    if action_type == "final":
        if set(item) != {"type", "answer"}:
            raise ActionValidationError("Final action must contain only type and answer")
        if not isinstance(item["answer"], str) or not item["answer"].strip():
            raise ActionValidationError("answer must be a non-empty string")
        return FinalAction(item["answer"].strip())
    raise ActionValidationError("type must be 'tool' or 'final'")

