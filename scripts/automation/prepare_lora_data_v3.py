import sys, json, os, random
sys.stdout.reconfigure(encoding="utf-8")

def extract_text(content):
    """Handle content which can be string or array of {type, text}"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                texts.append(item.get("text", item.get("content", "")))
        return "\n".join(texts)
    return str(content)

qa_pairs = []
dirs = [
    (os.path.expanduser("~/.codex/archived_sessions"), True),
    (os.path.expanduser("~/.codex/sessions"), False),
]

for base_dir, is_archive in dirs:
    if not os.path.isdir(base_dir):
        continue
    files = []
    for root, dirs2, filenames in os.walk(base_dir):
        for f in filenames:
            if f.endswith(".jsonl"):
                files.append(os.path.join(root, f))
    
    for fp in files:
        sz = os.path.getsize(fp)
        if sz < 500:
            continue
        with open(fp, "r", encoding="utf-8", errors="replace") as fh:
            try:
                lines = fh.readlines()
            except:
                continue
        
        messages = []
        for line in lines:
            try:
                d = json.loads(line)
                if d.get("type") == "response_item":
                    payload = d.get("payload", {})
                    role = payload.get("role", "")
                    raw_content = payload.get("content", "")
                    content = extract_text(raw_content).strip()
                    if role in ("user", "assistant") and content and len(content) > 20:
                        messages.append({"role": role, "content": content[:3000]})
            except:
                pass
        
        # Create Q&A pairs
        for i in range(len(messages) - 1):
            if messages[i]["role"] == "user" and messages[i+1]["role"] == "assistant":
                user_msg = messages[i]["content"]
                asst_msg = messages[i+1]["content"]
                if len(user_msg) > 30 and len(asst_msg) > 30:
                    qa_pairs.append({
                        "instruction": user_msg[:3000],
                        "input": "",
                        "output": asst_msg[:3000]
                    })

print(f"Extracted {len(qa_pairs)} Q&A pairs")

# Deduplicate and sample
seen = set()
unique = []
for p in qa_pairs:
    h = p["instruction"][:100]
    if h not in seen:
        seen.add(h)
        unique.append(p)

# Sort by response length (quality heuristic), take top 300
unique.sort(key=lambda x: len(x["output"]), reverse=True)
unique = unique[:300]

random.shuffle(unique)

out_dir = os.path.expanduser("~/local-model-lab/lora-finetune/data")
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "train.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f"Saved {len(unique)} unique training samples")
for s in unique[:3]:
    print(f"  Q: {s['instruction'][:100]}...")
    print(f"  A: {s['output'][:100]}...")
    print()
