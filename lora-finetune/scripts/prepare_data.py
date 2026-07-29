"""
Convert FastGPT exported dialogue logs to LoRA training data format.

Usage:
  python scripts/prepare_data.py --input chat_logs.json --output data/train.json

Input format (FastGPT dialogue logs):
  [{"query": "user question", "answer": "model response"}, ...]

Output format: Alpaca JSON
"""
import json, os, sys, argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Convert dialogue data to training format")
    parser.add_argument("--input", "-i", required=True, help="Input dialogue log JSON")
    parser.add_argument("--output", "-o", default="data/train.json", help="Output training data JSON")
    parser.add_argument("--min-length", type=int, default=5, help="Minimum Q&A length")
    return parser.parse_args()

def main():
    args = parse_args()

    if not os.path.exists(args.input):
        print(f"[ERR] Input file not found: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        raw = json.load(f)

    train_data = []
    skipped = 0
    for item in raw:
        query = (item.get("query") or item.get("instruction") or "").strip()
        answer = (item.get("answer") or item.get("output") or "").strip()
        if len(query) < args.min_length or len(answer) < args.min_length:
            skipped += 1
            continue
        train_data.append({
            "id": f"qa-{len(train_data)+1:04d}",
            "instruction": query,
            "output": answer,
        })

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Conversion complete")
    print(f"    Input: {len(raw)} records")
    print(f"    Output: {len(train_data)} records")
    print(f"    Skipped: {skipped} (too short)")
    print(f"    File: {args.output}")

if __name__ == "__main__":
    main()
