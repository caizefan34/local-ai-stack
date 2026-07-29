"""Create AST-aware code chunks and a local import dependency graph.

The output is JSON so it can be embedded by any local model or uploaded to a
FastGPT knowledge base. No source code leaves the selected directory.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path


CODE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".java"}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}
MAX_FILE_BYTES = 1_000_000
JS_IMPORT_RE = re.compile(r"(?:import\s+(?:.+?\s+from\s+)?|require\s*\()['\"]([^'\"]+)['\"]")
JS_SYMBOL_RE = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][\w$]*)", re.MULTILINE)


def _source(node: ast.AST, source: str) -> str:
    return ast.get_source_segment(source, node) or ""


def _called_names(node: ast.AST) -> list[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)
    return sorted(names)


def _python_chunks(path: Path, source: str) -> tuple[list[dict], list[str]]:
    tree = ast.parse(source, filename=str(path))
    imports: list[str] = []
    chunks: list[dict] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append("." * node.level + (node.module or ""))

    def add_chunk(node: ast.AST, name: str, kind: str, parent: str | None = None) -> None:
        code = _source(node, source)
        if not code:
            return
        chunks.append({
            "file": str(path),
            "language": "python",
            "kind": kind,
            "name": name,
            "parent": parent,
            "signature": code.splitlines()[0].strip(),
            "docstring": ast.get_docstring(node) or "",
            "imports": sorted(set(imports)),
            "calls": _called_names(node),
            "code": code,
        })

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add_chunk(node, node.name, "function")
        elif isinstance(node, ast.ClassDef):
            add_chunk(node, node.name, "class")
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    add_chunk(member, member.name, "method", node.name)
    return chunks, sorted(set(imports))


def _generic_chunks(path: Path, source: str) -> tuple[list[dict], list[str]]:
    imports = sorted(set(JS_IMPORT_RE.findall(source)))
    symbols = list(JS_SYMBOL_RE.finditer(source))
    chunks: list[dict] = []
    for index, match in enumerate(symbols):
        end = symbols[index + 1].start() if index + 1 < len(symbols) else len(source)
        code = source[match.start():end].strip()
        chunks.append({
            "file": str(path), "language": path.suffix.lstrip("."), "kind": "symbol",
            "name": match.group(1), "parent": None, "signature": code.splitlines()[0],
            "docstring": "", "imports": imports, "calls": [], "code": code,
        })
    return chunks, imports


def index_directory(root: Path) -> dict:
    root = root.resolve()
    chunks: list[dict] = []
    dependencies: list[dict] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in CODE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts) or path.stat().st_size > MAX_FILE_BYTES:
            continue
        try:
            source = path.read_text(encoding="utf-8")
            file_chunks, imports = _python_chunks(path, source) if path.suffix == ".py" else _generic_chunks(path, source)
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        relative = str(path.relative_to(root))
        for chunk in file_chunks:
            chunk["file"] = relative
        chunks.extend(file_chunks)
        dependencies.extend({"source": relative, "target": target} for target in imports if target)
    return {"version": 1, "root": str(root), "chunks": chunks, "dependencies": dependencies}


def main() -> None:
    parser = argparse.ArgumentParser(description="Index a codebase by AST functions/classes and imports")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, default=Path("code-index.json"))
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error(f"Not a directory: {args.directory}")
    output = index_directory(args.directory)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Indexed {len(output['chunks'])} chunks and {len(output['dependencies'])} dependencies: {args.output}")


if __name__ == "__main__":
    main()
