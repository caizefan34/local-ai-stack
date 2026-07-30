"""Minimal LSP bridge for local inline code completion via Ollama.

Run with ``python code_intelligence/lsp_server.py`` and configure any editor's
LSP client to use stdio. It intentionally exposes only completion, so editors
keep ownership of file edits and command confirmation.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from collections import OrderedDict

try:
    from .router import COMPLETION_MODEL
except ImportError:  # Running directly as a stdio server.
    from router import COMPLETION_MODEL


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
MODEL = os.getenv("CODE_COMPLETION_MODEL", COMPLETION_MODEL)
DOCUMENTS: dict[str, str] = {}
COMPLETION_CACHE: OrderedDict[str, str] = OrderedDict()
MAX_CACHE_ENTRIES = 32


def read_message() -> dict | None:
    headers: dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line == b"\r\n":
            break
        key, value = line.decode("ascii").split(":", 1)
        headers[key.lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    return json.loads(sys.stdin.buffer.read(length))


def send_message(payload: dict) -> None:
    encoded = json.dumps(payload).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(encoded)}\r\n\r\n".encode("ascii") + encoded)
    sys.stdout.buffer.flush()


def completion_prompt(text: str, line: int, character: int) -> str:
    lines = text.splitlines()
    prefix = "\n".join(lines[:line] + ([lines[line][:character]] if line < len(lines) else []))
    return "Complete only the next code tokens. Do not explain.\n\n" + prefix[-12000:]


def apply_content_changes(text: str, changes: list[dict]) -> str:
    """Apply LSP full or ranged changes in the order received."""
    for change in changes:
        if "range" not in change:
            text = change.get("text", "")
            continue
        lines = text.splitlines(keepends=True)

        def offset(position: dict) -> int:
            line = min(max(position.get("line", 0), 0), len(lines))
            if line >= len(lines):
                return len(text)
            units = max(position.get("character", 0), 0)
            index = 0
            consumed = 0
            for index, character in enumerate(lines[line]):
                width = 2 if ord(character) > 0xFFFF else 1
                if consumed + width > units:
                    break
                consumed += width
                index += 1
                if consumed == units:
                    break
            else:
                index = len(lines[line])
            return sum(len(value) for value in lines[:line]) + index

        start = offset(change["range"]["start"])
        end = offset(change["range"]["end"])
        text = text[:start] + change.get("text", "") + text[end:]
    return text


def ollama_completion(prompt: str) -> str:
    if prompt in COMPLETION_CACHE:
        COMPLETION_CACHE.move_to_end(prompt)
        return COMPLETION_CACHE[prompt]
    data = json.dumps({"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.1, "num_predict": 160}}).encode("utf-8")
    request = urllib.request.Request(OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        completion = json.load(response).get("response", "")
    COMPLETION_CACHE[prompt] = completion
    if len(COMPLETION_CACHE) > MAX_CACHE_ENTRIES:
        COMPLETION_CACHE.popitem(last=False)
    return completion


def handle(message: dict) -> dict | None:
    method = message.get("method")
    params = message.get("params", {})
    if method == "initialize":
        return {"capabilities": {"textDocumentSync": {"openClose": True, "change": 1}, "completionProvider": {"triggerCharacters": [".", "(", " "]}}}
    if method == "textDocument/didOpen":
        document = params.get("textDocument", {})
        DOCUMENTS[document.get("uri", "")] = document.get("text", "")
        return None
    if method == "textDocument/didChange":
        document = params.get("textDocument", {})
        changes = params.get("contentChanges", [])
        uri = document.get("uri", "")
        DOCUMENTS[uri] = apply_content_changes(DOCUMENTS.get(uri, ""), changes)
        return None
    if method == "textDocument/didClose":
        DOCUMENTS.pop(params.get("textDocument", {}).get("uri", ""), None)
        return None
    if method == "textDocument/completion":
        document = params.get("textDocument", {})
        position = params.get("position", {})
        try:
            text = DOCUMENTS.get(document.get("uri", ""), "")
            suggestion = ollama_completion(completion_prompt(text, position.get("line", 0), position.get("character", 0)))
            return {"isIncomplete": False, "items": [{"label": "Local AI completion", "kind": 15, "insertText": suggestion}]}
        except (OSError, ValueError, urllib.error.URLError) as error:
            return {"isIncomplete": False, "items": [], "error": str(error)}
    return None


def main() -> None:
    while message := read_message():
        result = handle(message)
        if "id" in message and result is not None:
            send_message({"jsonrpc": "2.0", "id": message["id"], "result": result})


if __name__ == "__main__":
    main()
