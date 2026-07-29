import json, os, sys, pymongo
from bson.objectid import ObjectId
sys.stdout.reconfigure(encoding="utf-8")

# Update FastGPT config.json
config_path = os.path.expanduser("~/local-model-lab/fastgpt/config.json")
with open(config_path, "r", encoding="utf-8-sig") as f:
    config = json.load(f)

# Fix model names
for m in config.get("llmModels", []):
    old = m.get("model", "")
    name = m.get("name", "")
    if old == "qwen3-8b-stable" or old == "qwen3-8b-stable:latest":
        m["model"] = "qwen3:8b"
        print(f"Fixed: {name}: {old} -> qwen3:8b")
    if old == "qwen3-1.7b-stable":
        m["model"] = "qwen3:1.7b"
        print(f"Fixed: {name}: {old} -> qwen3:1.7b")

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)
print("\nconfig.json updated!")

# Also update the OneAPI URL if needed
print("\nNext: Update OneAPI provider if needed")
print("Config now points to qwen3:8b")
