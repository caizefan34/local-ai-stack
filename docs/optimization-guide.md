# ⚡ 性能优化指南 / Optimization Guide

## 1. RAG 检索优化

### Reranker 二次排序

启用 reranker 后，检索流程变为：
1. 向量检索 Top 20 → 2. Reranker 重排 → 3. 取 Top 5

```json
{
  "reRankModels": [{
    "requestUrl": "http://host.docker.internal:18888/rerank_fastgpt",
    "name": "BGE Reranker v2 M3",
    "model": "bge-reranker-v2-m3"
  }]
}
```

### Chunk 大小优化

| 场景 | 推荐 Chunk 大小 |
|------|----------------|
| 技术文档 / 代码 | 800-1000 字 |
| 对话记录 | 500-800 字 |
| 长文章 | 1000-1200 字 |

### pgHNSWEfSearch

配置项 `pgHNSWEfSearch` 控制向量索引搜索精度：
- 默认值：80（平衡）
- 推荐：200（高精度）
- 最高：400（最高精度，略慢）

## 2. 模型推理优化

### Ollama 配置

```
# 设置并发参数
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
```

### 量化选择

| 量化 | 模型大小 | 8GB 显卡 | 性能 |
|------|---------|---------|------|
| Q4_K_M | ~5.2 GB | ✅ 可运行 | 推荐平衡 |
| Q3_K_M | ~4.0 GB | ✅ 流畅 | 速度优先 |
| Q8_0 | ~8.0 GB | ❌ 超显存 | 精度最高 |

## 3. LoRA 微调优化

### 参数推荐

| 硬件 | 批次大小 | LoRA 秩 | 梯度累积 |
|------|---------|---------|---------|
| 8GB 显卡 | 1 | 8 | 4 |
| 12GB 显卡 | 2 | 16 | 2 |
| 24GB 显卡 | 4 | 32 | 1 |
