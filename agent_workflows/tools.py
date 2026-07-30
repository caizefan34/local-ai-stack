"""Read-only workspace tools with path and output limits."""
from __future__ import annotations

from dataclasses import dataclass
import fnmatch
from pathlib import Path
from typing import Any, Callable


MAX_FILE_BYTES = 1_000_000
MAX_OUTPUT_CHARS = 50_000
DENIED_NAMES = {".git", ".env", ".env.local", ".env.production", "id_rsa", "id_ed25519", "credentials.json", "secrets.json"}
DENIED_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


class ToolError(RuntimeError):
    pass


def _bounded(value: Any) -> Any:
    text = str(value)
    if len(text) <= MAX_OUTPUT_CHARS:
        return value
    return text[:MAX_OUTPUT_CHARS] + "\n[output truncated]"


class WorkspaceTools:
    def __init__(self, workspace: Path):
        self.root = workspace.resolve(strict=True)
        if not self.root.is_dir():
            raise ToolError(f"Not a workspace directory: {workspace}")

    def _resolve(self, relative: str, *, directory: bool | None = None) -> Path:
        value = Path(str(relative or "."))
        if value.is_absolute():
            raise ToolError("Absolute paths are not allowed")
        candidate = (self.root / value).resolve(strict=True)
        try:
            candidate.relative_to(self.root)
        except ValueError as error:
            raise ToolError("Path resolves outside the workspace") from error
        relative_parts = candidate.relative_to(self.root).parts
        if any(part.lower() in DENIED_NAMES or part.lower().startswith(".env.") for part in relative_parts):
            raise ToolError("Sensitive paths are not available to agent tools")
        if candidate.suffix.lower() in DENIED_SUFFIXES:
            raise ToolError("Key and certificate files are not available to agent tools")
        if candidate.is_symlink():
            raise ToolError("Symbolic links are not available to agent tools")
        if directory is True and not candidate.is_dir():
            raise ToolError("Expected a directory")
        if directory is False and not candidate.is_file():
            raise ToolError("Expected a file")
        return candidate

    def list_files(self, path: str = ".", pattern: str = "*", limit: int = 100) -> dict[str, Any]:
        if not 1 <= limit <= 500:
            raise ToolError("limit must be between 1 and 500")
        base = self._resolve(path, directory=True)
        files: list[str] = []
        for candidate in sorted(base.rglob("*")):
            if len(files) >= limit:
                break
            if candidate.is_symlink() or not candidate.is_file():
                continue
            relative = candidate.relative_to(self.root)
            if any(part.lower() in DENIED_NAMES or part.lower().startswith(".env.") for part in relative.parts):
                continue
            if candidate.suffix.lower() in DENIED_SUFFIXES or not fnmatch.fnmatch(candidate.name, pattern):
                continue
            files.append(relative.as_posix())
        return {"files": files, "truncated": len(files) == limit}

    def read_file(self, path: str, start_line: int = 1, max_lines: int = 200) -> dict[str, Any]:
        if start_line < 1 or not 1 <= max_lines <= 500:
            raise ToolError("start_line must be positive and max_lines must be between 1 and 500")
        candidate = self._resolve(path, directory=False)
        if candidate.stat().st_size > MAX_FILE_BYTES:
            raise ToolError(f"File exceeds the {MAX_FILE_BYTES} byte limit")
        try:
            lines = candidate.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError as error:
            raise ToolError("Only UTF-8 text files can be read") from error
        selected = lines[start_line - 1:start_line - 1 + max_lines]
        return {"path": candidate.relative_to(self.root).as_posix(), "start_line": start_line, "content": _bounded("\n".join(selected)), "truncated": start_line - 1 + max_lines < len(lines)}

    def search_text(self, query: str, path: str = ".", pattern: str = "*", max_results: int = 50) -> dict[str, Any]:
        query = str(query)
        if not query or len(query) > 500:
            raise ToolError("query must contain 1-500 characters")
        if not 1 <= max_results <= 200:
            raise ToolError("max_results must be between 1 and 200")
        base = self._resolve(path, directory=True)
        results: list[dict[str, Any]] = []
        needle = query.casefold()
        for candidate in sorted(base.rglob("*")):
            if len(results) >= max_results:
                break
            if candidate.is_symlink() or not candidate.is_file() or candidate.stat().st_size > MAX_FILE_BYTES or not fnmatch.fnmatch(candidate.name, pattern):
                continue
            relative = candidate.relative_to(self.root)
            if any(part.lower() in DENIED_NAMES or part.lower().startswith(".env.") for part in relative.parts) or candidate.suffix.lower() in DENIED_SUFFIXES:
                continue
            try:
                for number, line in enumerate(candidate.read_text(encoding="utf-8").splitlines(), 1):
                    if needle in line.casefold():
                        results.append({"path": relative.as_posix(), "line": number, "text": line[:500]})
                        if len(results) >= max_results:
                            break
            except UnicodeDecodeError:
                continue
        return {"results": results, "truncated": len(results) == max_results}


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[..., dict[str, Any]]


class ToolRegistry:
    def __init__(self, workspace: Path):
        tools = WorkspaceTools(workspace)
        self._tools = {
            "list_files": ToolSpec("list_files", "List workspace files. Arguments: path?, pattern?, limit?", tools.list_files),
            "read_file": ToolSpec("read_file", "Read a UTF-8 workspace file. Arguments: path, start_line?, max_lines?", tools.read_file),
            "search_text": ToolSpec("search_text", "Search literal text. Arguments: query, path?, pattern?, max_results?", tools.search_text),
        }

    def descriptions(self) -> str:
        return "\n".join(f"- {item.name}: {item.description}" for item in self._tools.values())

    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        spec = self._tools.get(name)
        if not spec:
            raise ToolError(f"Unknown tool: {name}")
        try:
            return spec.handler(**arguments)
        except TypeError as error:
            raise ToolError(f"Invalid arguments for {name}: {error}") from error

