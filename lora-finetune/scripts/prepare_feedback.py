"""Convert explicitly approved JSONL feedback into reviewed LoRA candidates.

Negative feedback is useful only when it contains a human correction. The
generated JSON is an input for human review, not a direct deployment artifact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def convert(source: Path) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {number}") from exc
        if item.get("approved") is not True:
            continue
        prompt = str(item.get("prompt", "")).strip()
        rating = item.get("rating")
        answer = str(item.get("correction") if rating == "down" else item.get("response", "")).strip()
        if prompt and answer:
            candidates.append({"id": f"feedback-{number:04d}", "instruction": prompt, "output": answer})
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare approved code feedback for human review")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"Feedback file not found: {args.input}")
    candidates = convert(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Prepared {len(candidates)} review candidates: {args.output}")


if __name__ == "__main__":
    main()
