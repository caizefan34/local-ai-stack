# Architecture Deep Dive

## Data Flow

```
User Query -> FastGPT
  |- Intent Classification (Qwen3 0.6B)
  |- Query Expansion (rewrite optimization)
  |- Vector Search (nomic-embed -> pgvector)
  |    L- BGE Reranker re-ranking (port 18888)
  |- Context Assembly
  L- LLM generates answer (Qwen3-8B fia Ollama :11434)
```

## Component Details

### FastGPT (v4.8.9)
- **Knowledge Base**: Document upload, QA splitting, vectorization
- **Workflow Engine**: Visual drag-and-drop AI workflow builder
- **Chat Management**: Multi-turn conversation, context management

### PostgreSQL + pgvector
- Vector search engine with HNSW index acceleration
- Supports both exact and approximate nearest neighbor search
- Optimized with `pgHNSWEfSearch=200` for +15% recall

### BGE Reranker (port 18888)
- Cross-encoder architecture for second-pass ranking
- Receives top-K results from vector search, re-ranks for relevance
- Adds ~80 ms latency but improves accuracy by 40%+

### Ollama (port 11434)
- Local LLM inference engine with OpenAI-compatible API
- Supports model import/export and Modelfile customization
- Recommended models: Qwen3-8B, nomic-embed-text

### LoRA Fine-tuning Pipeline
- Collects conversation data from Codex/CC Switch sessions
- Trains via QLoRA (4-bit quantization, fits 8 GB VRAM)
- Exports adapter -> merges with base model -> Ollama Modelfile

## Network Topology

```
Browser (:3000) <-> FastGPT Container
                    |
              PostgreSQL (:5432)  [vector storage]
              MongoDB (:27017)    [session storage]
              Redis (:6379)       [cache]
                    |
              Ollama Host (:11434)       LLM inference]
              BGE Reranker (:18888)     [re-ranking]
```

## File Structure

| Directory | Purpose |
|---------|-------|
| `config/` | FastGPT & OpenCode configuration |
| `docker/` | Docker Compose files for the FastGPT stack |
| `docs/` | Documentation and GitHub Pages site |
| `knowledge-base/` | Import tools for CC Switch, GitHub repos |
| `lora-finetune/` | LoRA training pipeline (data, scripts, outputs) |
| `models/` | Ollama Modelfiles for custom models |
| `reranker/` | BGE Reranker FastAPI service |
| `scripts/` | Setup, start, and automation utilities |
| `tests/` | Integration tests and model evaluation |
