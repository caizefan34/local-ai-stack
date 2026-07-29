"""Deterministic local model selection for code-assistant clients.

FastGPT workflows can call this script (or copy its rules) before selecting an
Ollama model. Keeping the classifier deterministic makes routing explainable
and avoids spending a model request just to choose another model.
"""
from __future__ import annotations

import argparse
import json
import re


CODE_MODEL = "qwen2.5-coder:7b"
COMPLETION_MODEL = "qwen2.5-coder:1.5b"
GENERAL_MODEL = "qwen3:8b"

CODE_PATTERNS = (
    r"```",
    r"\b(def|class|function|import|from|const|let|var|async|await)\b",
    r"\b(traceback|stack trace|exception|syntaxerror|typeerror|bug|linter|lint)\b",
    r"\b(python|javascript|typescript|java|rust|golang|sql|regex)\b",
    r"(写代码|编写代码|修复.{0,8}(bug|错误)|报错|代码补全|单元测试|函数|类)",
)
CODE_RE = re.compile("|".join(CODE_PATTERNS), re.IGNORECASE)


def classify(text: str) -> str:
    """Return ``code`` only when an explicit code signal is present."""
    return "code" if CODE_RE.search(text or "") else "general"


def choose_model(text: str, completion: bool = False) -> dict[str, str]:
    task = classify(text)
    if task == "code":
        model = COMPLETION_MODEL if completion else CODE_MODEL
    else:
        model = GENERAL_MODEL
    return {"task": task, "model": model, "reason": "explicit_code_signal" if task == "code" else "general_dialogue"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Route a prompt to a local Ollama model")
    parser.add_argument("text", help="Prompt or editor context to classify")
    parser.add_argument("--completion", action="store_true", help="Prefer the low-latency code completion model")
    print(json.dumps(choose_model(parser.parse_args().text, parser.parse_args().completion), ensure_ascii=False))


if __name__ == "__main__":
    main()
