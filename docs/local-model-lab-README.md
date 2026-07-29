# Local Model Lab

用于记录本地 Ollama 模型的配置、基线评测和每轮优化结果。

## 当前环境
- 硬件：RTX 5070 Laptop 8GB、32GB RAM
- Ollama：v0.32.4，主模型 `qwen3-8b-stable`（Q4_K_M，8192 context，100% GPU）
- FastGPT：v4.8.9，集成 Qwen3 + BGE Reranker v2 M3
- OpenCode：v1.18.7，默认 `ollama/qwen3-8b-stable`
- Reranker：BAAI/bge-reranker-v2-m3（568M params，CPU 端口 18888）

## 连接信息
- FastGPT 页面：http://localhost:3000
- Ollama API：http://host.docker.internal:11434/v1
- Reranker API：http://localhost:18888/rerank_fastgpt（FastGPT 格式）

## 运行评测
```powershell
python /home/user\local-model-lab\evaluate.py qwen3-8b-stable
python /home/user\local-model-lab\reranker\test.py
```

## 启动方式
- Ollama 自动启动（服务）
- Reranker：`python /home/user\local-model-lab\reranker\server.py`
- FastGPT：`docker compose -p temp -f "/home/user\AppData\Local\Temp\fastgpt-docker-compose-v489.yml" up -d`
