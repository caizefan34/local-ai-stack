"""
Data Collection Tool - Import training data from multiple sources

Usage:
  python scripts/collect_data.py

Supported sources:
  1. JSON file import (standard format)
  2. CSV file import
  3. Manual Q&A pair input
  4. FastGPT API export
  5. Markdown conversation extract
"""
import json, os, sys, csv, glob
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "train.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    # Merge with existing data
    existing = []
    if os.path.exists(OUTPUT_FILE):
        existing = load_json(OUTPUT_FILE)
    all_data = existing + data
    # Deduplicate by instruction
    seen = set()
    unique = []
    for item in all_data:
        key = item.get("instruction", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved {len(data)} new records to {OUTPUT_FILE}")
    print(f"    Total after dedup: {len(unique)}  records")
    return unique

def convert_ccswitch_format(raw_data):
    """Parse CC Switch export format"""
    converted = []
    for item in raw_data:
        # Support multiple key names
        q = item.get("query") or item.get("question") or item.get("user") or item.get("prompt") or ""
        a = item.get("answer") or item.get("response") or item.get("assistant") or item.get("completion") or ""
        if isinstance(q, list):
            q = " ".join(q)
        if isinstance(a, list):
            a = " ".join(a)
        if q.strip() and a.strip():
            converted.append({"instruction": q.strip(), "output": a.strip()})
    return converted

def main():
    print("=" * 60)
    print("Training Data Collection Tool")
    print("=" * 60)
    print()
    print("Supported input formats:")
    print("  1. JSON file (standard Alpaca format)")
    print("  2. JSON file (CC Switch / ChatGPT export)")
    print("  3. CSV file (query,answer columns)")
    print("  4. Plain text conversation logs")
    print("  5. FastGPT dialogue log import")
    print()
    path = input("Input file path (drag file here): ").strip().strip("'\"")

    if not os.path.exists(path):
        print(f"[ERR] File not found: {path}")
        return

    ext = os.path.splitext(path)[1].lower()
    data = []

    if ext == ".json":
        raw = load_json(path)
        # Auto-detect format
        if isinstance(raw, list):
            if raw and "messages" in raw[0]:
                # ShareGPT format
                for item in raw:
                    msgs = item.get("messages", [])
                    user = [m for m in msgs if m.get("role") == "user"]
                    asst = [m for m in msgs if m.get("role") == "assistant"]
                    for u, a in zip(user, asst):
                        data.append({"instruction": u["content"], "output": a["content"]})
            elif raw and "instruction" in raw[0]:
                data = raw  # Standard Alpaca
            else:
                data = convert_ccswitch_format(raw)
        print(f"  Parsed {len(data)} Q&A pairs")

    elif ext == ".csv":
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                q = row.get("query") or row.get("question") or row.get("user") or ""
                a = row.get("answer") or row.get("response") or row.get("assistant") or ""
                if q.strip() and a.strip():
                    data.append({"instruction": q.strip(), "output": a.strip()})
        print(f"  Parsed {len(data)} Q&A pairs")

    elif ext == ".txt" or ext == ".md":
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        lines = text.strip().split("\n\n")
        for block in lines:
            lines_b = block.strip().split("\n")
            q = ""
            a = ""
            for line in lines_b:
                if line.startswith("Q:") or line.startswith("Q:") or line.startswith("User:"):
                    q = line.split(":", 1)[1].strip()
                elif line.startswith("A:") or line.startswith("A:") or line.startswith("AI:") or line.startswith("Assistant:"):
                    a = line.split(":", 1)[1].strip()
            if q and a:
                data.append({"instruction": q, "output": a})
        print(f"  Parsed {len(data)} Q&A pairs")
    else:
        print(f"[ERR] Unsupported file format: {ext}")
        return

    if data:
        # Show preview of first 3 items
        print()
        print("Preview first 3 items:")
        for i, item in enumerate(data[:3]):
            print(f"  [{i+1}] Q: {item['instruction'][:60]}...")
            print(f"       A: {item['output'][:60]}...")
            print()
        confirm = input("Confirm import? (Y/n): ").strip().lower() or "y"
        if confirm == "y":
            save_data(data)
        else:
            print("Cancelled")
    else:
        print("[WARN] No valid Q&A pairs found")
        print("  Supported format examples:")
        print('  [{"instruction": "question", "output": "answer"}]')
        print('  [{"query": "question", "answer": "answer"}]')
        print('  CSV: query,answer')

if __name__ == "__main__":
    main()
