import os, json, logging
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from flask import Flask, request, jsonify
from sentence_transformers import CrossEncoder

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

MODEL_NAME = "BAAI/bge-reranker-v2-m3"

print(f"Loading reranker: {MODEL_NAME}...")
model = CrossEncoder(MODEL_NAME)
print("Reranker ready!")

@app.route("/rerank_fastgpt", methods=["POST"])
def rerank():
    data = request.get_json()
    query = data.get("query", "")
    passages = data.get("passages", [])

    if not query or not passages:
        return jsonify({"results": []})

    pairs = [[query, p] for p in passages]
    scores = model.predict(pairs).tolist()

    results = [
        {"index": i, "relevance_score": float(scores[i])}
        for i in range(len(passages))
    ]
    results.sort(key=lambda x: x["relevance_score"], reverse=True)

    return jsonify({"results": results})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=18888)
