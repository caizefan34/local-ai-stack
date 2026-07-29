import sys, json, pymongo, os, random
from bson.objectid import ObjectId
sys.stdout.reconfigure(encoding="utf-8")

client = pymongo.MongoClient("mongodb://localhost:27017/fastgpt?directConnection=true", serverSelectionTimeoutMS=5000)
db = client["fastgpt"]
kb_id = ObjectId("6a675d6c59fb544cd040db65")

# Extract Q&A pairs from knowledge base
qa_pairs = []
for d in db["dataset_datas"].find({"datasetId": kb_id, "a": {"$ne": ""}}).limit(200):
    q = d.get("q", "").strip()
    a = d.get("a", "").strip()
    if q and a and len(q) > 20 and len(a) > 20:
        qa_pairs.append({"instruction": q[:2000], "input": "", "output": a[:2000]})

print(f"Found {len(qa_pairs)} Q&A pairs with answers")

# Also generate from conversations (q has content, a is empty - these are chunks)
# We can pair consecutive chunks as pseudo Q&A
count = 0
for d in db["dataset_datas"].find({"datasetId": kb_id, "a": ""}).sort("_id", 1).limit(5000):
    q = d.get("q", "").strip()
    if q and len(q) > 100 and count < 150:
        # Use chunks that look like Q&A (contain question patterns)
        if any(x in q[:200].lower() for x in ["?", "如何", "怎么", "什么", "为什么", "怎样", "是否", "能否", "what", "how", "why", "can"]):
            qa_pairs.append({"instruction": q[:2000], "input": "", "output": "Based on the above information: " + q[:1000]})
            count += 1

print(f"Generated {len(qa_pairs)} total training samples")

# Filter to max 200 high-quality samples, mix sources
random.shuffle(qa_pairs)
qa_pairs = qa_pairs[:200]

# Save
out_dir = os.path.expanduser("~/local-model-lab/lora-finetune/data")
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "train.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(qa_pairs, f, ensure_ascii=False, indent=2)

print(f"Saved {len(qa_pairs)} samples to {out_file}")

# Show samples
for s in qa_pairs[:3]:
    print(f"  INSTR: {s['instruction'][:80]}...")
    print(f"  OUT: {s['output'][:80]}...")
    print()
