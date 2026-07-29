#!/usr/bin/env python3
"""Test the BGE reranker service."""
import urllib.request, json

body = json.dumps({
    "query": "attention mechanism in transformers",
    "documents": [
        "Attention is a key component of Transformer models.",
        "The weather is nice today.",
        "Self-attention allows models to weigh input token importance."
    ]
}).encode()
req = urllib.request.Request("http://localhost:18888/rerank",
    data=body, headers={"Content-Type": "application/json"})
r = json.load(urllib.request.urlopen(req, timeout=30))
print("Reranker results:")
for res in r["results"]:
    idx = res["index"]
    score = res["score"]
    text = res["text"][:50]
    print(f"  [{idx}] score={score:.4f}  {text}")
