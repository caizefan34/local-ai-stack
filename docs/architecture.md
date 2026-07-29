# 🏗️ 架构详解 / Architecture Deep Dive

## 数据流

```
用户提问 → FastGPT
  ├─ 意图识别（小模型 0.6B）
  ├─ 查询扩展（改写优化）
  ├─ 向量检索（nomic-embed → pgvector）
  │    └─ BGE Reranker 重排序
  ├─ 上下文组装
  └─ LLM 生成回答（Qwen3-8B via Ollama）
```

## 组件说明

### FastGPT (v4.8.9)

- 知识库管理：支持文档上传、QA 拆分、向量化
- 工作流编排：可视化拖拽搭建 AI 工作流
- 对话管理：多轮对话、上下文管理

### PostgreSQL + pgvector

- 向量搜索引擎
- HNSW 索引加速
- 支持精确和近似最近邻搜索

### BGE Reranker

- Cross-encoder 架构
- 对向量检索结果二次排序
- 支持中英文混合

### Ollama

- 本地 LLM 推理引擎
- OpenAI 兼容 API
- 支持模型导入导出

## 网络拓扑

```
浏览器 (3000) ←→ FastGPT Container
                        ↓
              PostgreSQL (5432)
              MongoDB (27017)
              Redis (6379)
                        ↓
              Ollama Host (11434)
              Reranker Host (18888)
```
