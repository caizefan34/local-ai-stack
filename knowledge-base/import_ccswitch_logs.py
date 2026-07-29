#!/usr/bin/env python3
"""Extract conversation data from Codex session logs for QA training."""
import os, json, glob

def extract_pairs(filepath: str) -> list[dict]:
    """Extract Q&A pairs from a Codex session file."""
    pairs = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        msgs = data.get("messages", [])
        for i in range(len(msgs) - 1):
            if msgs[i].get("role") == "user" and msgs[i+1].get("role") == "assistant":
                pairs.append({
                    "instruction": msgs[i].get("content", ""),
                    "output": msgs[i+1].get("content", ""),
                })
    except:
        pass
    return pairs

def main():
    search_paths = [
        os.path.expanduser("~/.codex/sessions/*.json"),
        os.path.expanduser("~/.codex/archived_sessions/*.json"),
    ]
    
    all_pairs = []
    seen = set()
    
    for pattern in search_paths:
        for f in glob.glob(pattern):
            pairs = extract_pairs(f)
            for p in pairs:
                key = p["instruction"][:100]
                if key not in seen:
                    seen.add(key)
                    all_pairs.append(p)
    
    print(f"Extracted {len(all_pairs)} unique Q&A pairs")
    
    output = "train_data.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_pairs, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output}")

if __name__ == "__main__":
    main()
