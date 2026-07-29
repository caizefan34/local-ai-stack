"""Store explicitly approved code-assistant feedback for later fine-tuning."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Record approved local code-assistant feedback")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--response", required=True)
    parser.add_argument("--rating", choices=("up", "down"), required=True)
    parser.add_argument("--correction", default="", help="Human-corrected answer for negative feedback")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--output", type=Path, default=Path("lora-finetune/data/feedback.jsonl"))
    parser.add_argument("--approved", action="store_true", help="Required: confirms this content may be retained for training")
    args = parser.parse_args()
    if not args.approved:
        parser.error("Feedback is not stored until --approved is provided")
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "prompt": args.prompt,
        "response": args.response,
        "rating": args.rating,
        "correction": args.correction,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Stored approved feedback in {args.output}")


if __name__ == "__main__":
    main()
