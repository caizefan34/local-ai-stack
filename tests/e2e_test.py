import urllib.request, json

body = json.dumps({"model":"qwen3-1.7b-stable","prompt":"What is 2+2? Output only the number.","stream":False,"think":False,"options":{"temperature":0,"num_predict":16}}).encode()
req = urllib.request.Request("http://localhost:11434/api/generate", data=body, headers={"Content-Type":"application/json; charset=utf-8"})
r = json.load(urllib.request.urlopen(req, timeout=30))
print("1.7B: [" + r["response"].strip() + "]", r["eval_count"], "tok", r["eval_duration"]/1e9, "s")

body = json.dumps({"model":"qwen3-8b-stable","prompt":"Python list comprehension syntax? Output just one line.","stream":False,"think":False,"options":{"temperature":0,"num_predict":32}}).encode()
req = urllib.request.Request("http://localhost:11434/api/generate", data=body, headers={"Content-Type":"application/json; charset=utf-8"})
r = json.load(urllib.request.urlopen(req, timeout=30))
print("8B: [" + r["response"].strip() + "]", r["eval_count"], "tok", r["eval_duration"]/1e9, "s")

body = json.dumps({"query":"machine learning","passages":["supervised learning requires labeled data","the weather is nice today","deep learning is a subset of machine learning"]}).encode()
req = urllib.request.Request("http://localhost:18888/rerank_fastgpt", data=body, headers={"Content-Type":"application/json"})
r = json.load(urllib.request.urlopen(req, timeout=30))
s = [(x["index"], round(x["relevance_score"],2)) for x in r["results"]]
print("Reranker:", s)

req = urllib.request.Request("http://localhost:3000/", method="GET")
try:
    urllib.request.urlopen(req, timeout=5)
    print("FastGPT: OK")
except:
    print("FastGPT: ERR")
