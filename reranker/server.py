from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn, torch, os, time, logging
from transformers import AutoModelForSequenceClassification, AutoTokenizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger('reranker')

app = FastAPI(title='Local Reranker - BGE')
MODEL_NAME = os.getenv('RERANKER_MODEL', 'BAAI/bge-reranker-v2-m3')
RERANKER_PORT = int(os.getenv('RERANKER_PORT', '18888'))
MAX_DOCUMENTS = int(os.getenv('RERANKER_MAX_DOCUMENTS', '256'))
model = None
tokenizer = None
device = 'cpu'

class ReRankInput(BaseModel):
    query: str = Field(min_length=1, max_length=8192)
    documents: List[str] = Field(min_length=1, max_length=MAX_DOCUMENTS)
    top_k: Optional[int] = Field(default=None, gt=0, le=MAX_DOCUMENTS)

class FastGPTReRankInput(BaseModel):
    query: str = Field(min_length=1, max_length=8192)
    passages: List[str] = Field(min_length=1, max_length=MAX_DOCUMENTS)

@app.on_event('startup')
async def load_model():
    global model, tokenizer, device
    device = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')
    log.info(f'Loading {MODEL_NAME} on {device}...')
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, trust_remote_code=True,
        torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
        low_cpu_mem_usage=True
    )
    model = model.to(device)
    model.eval()
    
    # Warmup
    log.info('Warming up...')
    try:
        inputs = tokenizer([['warmup', 'test document']], padding=True, truncation=True, return_tensors='pt', max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            model(**inputs)
        log.info('Warmup complete')
    except Exception as e:
        log.warning(f'Warmup failed (non-critical): {e}')
    
    log.info(f'Reranker ready on {device} in {time.time()-t0:.1f}s')

def _rerank(query: str, texts: List[str]):
    if model is None:
        raise HTTPException(503, 'Model not loaded yet - try again in a few seconds')
    if not texts:
        return []
    if len(texts) > MAX_DOCUMENTS:
        raise HTTPException(413, f'Too many documents; maximum is {MAX_DOCUMENTS}')
    pairs = [[query, doc] for doc in texts]
    with torch.no_grad():
        inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        scores = model(**inputs).logits.squeeze(-1).tolist()
    if isinstance(scores, float):
        scores = [scores]
    return scores

@app.post('/rerank')
def rerank(input: ReRankInput):
    t0 = time.time()
    scores = _rerank(input.query, input.documents)
    top_k = input.top_k or len(input.documents)
    indexed = sorted(
        [{'index': i, 'score': round(s, 4), 'text': input.documents[i]} for i, s in enumerate(scores)],
        key=lambda x: x['score'], reverse=True
    )[:top_k]
    log.info(f'Reranked {len(input.documents)} docs in {time.time()-t0:.3f}s, top score: {indexed[0]["score"] if indexed else 0}')
    return {'results': indexed}

@app.post('/rerank_fastgpt')
def rerank_fastgpt(input: FastGPTReRankInput):
    t0 = time.time()
    scores = _rerank(input.query, input.passages)
    log.info(f'FastGPT rerank: {len(input.passages)} docs in {time.time()-t0:.3f}s')
    return {'results': [{'index': i, 'relevance_score': round(float(s), 4)} for i, s in enumerate(scores)]}

@app.get('/health')
def health():
    return {
        'status': 'ok' if model is not None else 'loading',
        'model': MODEL_NAME,
        'device': str(model.device) if model else 'loading',
        'uptime': time.time() - health.start_time if hasattr(health, 'start_time') else 0
    }
health.start_time = time.time()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=RERANKER_PORT, log_level='info')
