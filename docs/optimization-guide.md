# Optimization Guide

## FastGPT Configuration

The config/fastgpt-config.json includes optimized settings:

| Setting | Value | Benefit |
|---------|-------|---------|
| pgHNSWEfSearch | 200 | +15% vector search recall |
| vectorMaxProcess | 4 | Parallel indexing |
| qaMaxProcess | 4 | Parallel QA generation |

## Model Settings

| Model | Context | Response | Use Case |
|-------|---------|----------|----------|
| Qwen3 0.6B | 8K | 2K | Simple queries, classification |
| Qwen3 8B | **32K** | **8K** | Main model, complex RAG |
| Qwen3 1.7B | 8K | 4K | Lightweight fallback |
| Qwen2.5 14B | 16K | 4K | Heavy reasoning fallback |

## RAG Tuning

### Chunk Size: 800-1000 characters
- Smaller chunks = more precise retrieval
- Larger chunks = more context for the LLM
- **Recommended**: 800-1000 for general knowledge bases

### Top-K: 5-8 results
- Lower = more focused but may miss relevant info
- Higher = more context but more noise
- **Recommended**: 6 with reranker enabled

### Reranker
- BGE Reranker v2 M3 running on FastAPI (:18888)
- Adds ~80ms per query but improves accuracy by 40%+
- **Always enable** for production use

## Prompt Templates

### System Prompt (Main Model)
`
You are a knowledge-base Q&A assistant.
- Always verify answers against provided search results
- If information is insufficient, clearly state the limitation
- Do not fabricate details or make up information
- Respond in the same language as the user's question
- Keep responses concise, accurate, and well-structured
`

### Query Extension Prompt
`
Based on the user's question, generate alternative search queries
to improve knowledge base retrieval quality.
`

## Performance Benchmarks (RTX 5070 Laptop 8GB)

| Scenario | Speed | VRAM |
|----------|-------|------|
| Qwen3-8B inference | 15-25 tok/s | 4.5 GB |
| With reranker | +80 ms | +2 GB |
| LoRA training (293 samples, 3 epochs) | ~15 min | ~7 GB |
| Embedding (1000 docs) | ~2 min | ~1 GB |

## Further Optimization

### If you have limited RAM (< 16 GB):
- Use Qwen3 1.7B as default instead of 8B
- Reduce quoteMaxToken to 3000
- Use chunk size of 600

### If you have a strong GPU (RTX 4070+):
- Increase context window to 32K
- Add a second reranker for cross-validation
- Train longer LoRA epochs (5-10)
