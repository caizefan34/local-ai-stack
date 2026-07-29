from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

app = FastAPI(title="Local Reranker")
model_name = "BAAI/bge-reranker-v2-m3"
model = None
tokenizer = None

class ReRankInput(BaseModel):
    query: str
    documents: List[str]
    top_k: Optional[int] = None

class ReRankOutput(BaseModel):
    results: List[dict]

class FastGPTReRankInput(BaseModel):
    query: str
    passages: List[str]

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, trust_remote_code=True)
    model.to(device) if device == "cuda" else model
    model.eval()
    print(f"[Reranker] Loaded on {device}")

def _rerank(query: str, texts: List[str]):
    if model is None:
        raise HTTPException(503, "Model not loaded")
    pairs = [[query, doc] for doc in texts]
    with torch.no_grad():
        inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors="pt", max_length=512)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        scores = model(**inputs).logits.squeeze(-1).tolist()
    if isinstance(scores, float):
        scores = [scores]
    return scores

@app.post("/rerank", response_model=ReRankOutput)
def rerank(input: ReRankInput):
    scores = _rerank(input.query, input.documents)
    top_k = input.top_k or len(input.documents)
    indexed = sorted(
        [{"index": i, "score": round(s, 4), "text": input.documents[i]} for i, s in enumerate(scores)],
        key=lambda x: x["score"], reverse=True
    )[:top_k]
    return ReRankOutput(results=indexed)

@app.post("/rerank_fastgpt")
def rerank_fastgpt(input: FastGPTReRankInput):
    scores = _rerank(input.query, input.passages)
    return {"results": [{"index": i, "relevance_score": round(float(s), 4)} for i, s in enumerate(scores)]}

@app.get("/health")
def health():
    return {"status": "ok", "model": model_name, "device": str(model.device) if model else "loading"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=18888)
