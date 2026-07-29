import urllib.request, json
body = json.dumps({"query": "什么是注意力机制？", "documents": ["注意力机制是深度学习中的一种技术", "今天的天气很好", "Transformer模型使用了自注意力机制"]}).encode()
req = urllib.request.Request("http://localhost:18888/rerank", data=body, headers={"Content-Type": "application/json"})
r = json.load(urllib.request.urlopen(req))
for res in r["results"]:
    idx = res["index"]
    score = res["score"]
    text = res["text"][:40]
    print(f"  [{idx}] score={score:.4f}  {text}")
