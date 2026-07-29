# 🛠️ 安装指南 / Setup Guide

## Windows

### 1. 安装依赖

```powershell
# 安装 Docker Desktop
# https://www.docker.com/products/docker-desktop/

# 安装 Ollama
winget install Ollama.Ollama

# 安装 Python 3.11+
# https://www.python.org/downloads/
```

### 2. 下载模型

```powershell
ollama pull qwen3:8b      # 主模型（8B）
ollama pull nomic-embed-text:latest  # 向量模型
```

### 3. 启动 FastGPT

```powershell
docker compose -f docker/docker-compose.yml up -d
```

访问 http://localhost:3000，默认密码 `1234`

### 4. 创建知识库

1. 登录 FastGPT
2. 新建知识库 → 选择向量模型 `nomic-embed-text`
3. 上传文档或使用导入脚本

## Linux

```bash
# 安装 Docker & Ollama
curl -fsSL https://ollama.com/install.sh | sh
sudo apt install docker-compose

# 下载模型
ollama pull qwen3:8b

# 启动
bash scripts/setup.sh
```
