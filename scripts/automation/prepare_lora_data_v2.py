import sys, json, os, random
sys.stdout.reconfigure(encoding="utf-8")

qa_pairs = []

# Read from Codex session JSONL files
dirs = [
    os.path.expanduser("~/.codex/archived_sessions"),
    os.path.expanduser("~/.codex/sessions"),
]

for base_dir in dirs:
    if not os.path.isdir(base_dir):
        continue
    for root, dirs2, files in os.walk(base_dir):
        for f in files:
            if not f.endswith(".jsonl"):
                continue
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp)
            if sz < 500:
                continue
            with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
            
            # Extract messages in order
            messages = []
            for line in lines:
                try:
                    d = json.loads(line)
                    if d.get("type") == "response_item":
                        payload = d.get("payload", {})
                        role = payload.get("role", "")
                        content = payload.get("content", "")
                        if role in ("user", "assistant") and content and len(content) > 30:
                            messages.append({"role": role, "content": content})
                except:
                    pass
            
            # Create Q&A pairs from consecutive user-assistant turns
            for i in range(len(messages) - 1):
                if messages[i]["role"] == "user" and messages[i+1]["role"] == "assistant":
                    user_msg = messages[i]["content"]
                    asst_msg = messages[i+1]["content"]
                    # Filter out very short or system-like responses
                    if len(user_msg) > 50 and len(asst_msg) > 50:
                        qa_pairs.append({
                            "instruction": user_msg[:3000],
                            "input": "",
                            "output": asst_msg[:3000]
                        })

print(f"Extracted {len(qa_pairs)} Q&A pairs from conversations")

# Sample high-quality ones (prioritize pairs with longer responses)
qa_pairs.sort(key=lambda x: len(x["output"]), reverse=True)
qa_pairs = qa_pairs[:300]

# Save
out_dir = os.path.expanduser("~/local-model-lab/lora-finetune/data")
out_file = os.path.join(out_dir, "train.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(qa_pairs, f, ensure_ascii=False, indent=2)

print(f"Saved {len(qa_pairs)} training samples")
print()
for s in qa_pairs[:3]:
    print(f"Q: {s['instruction'][:100]}...")
    print(f"A: {s['output'][:100]}...")
    print()
