# Local AI Stack — Ollama + FastGPT + RAG

> **Enterprise-grade RAG. 100% local. 100% free.** No API keys, no cloud costs, no GPU required.

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-6366f1?style=for-the-badge)](https://caizefan34.github.io/local-ai-stack/) [![License](https://img.shields.io/badge/License-MIT-blue)]() [![GitHub Stars](https://img.shields.io/github/stars/caizefan34/local-ai-stack?style=social)](https://github.com/caizefan34/local-ai-stack)

## Prerequisites

- Windows 10/11, Linux, or macOS
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- At least 8GB RAM (16GB recommended for LoRA training)
- 20GB free disk space

## Quick Start

### Windows
```powershell
git clone https://github.com/caizefan34/local-ai-stack.git
Set-Location local-ai-stack
winget install Ollama.Ollama
ollama pull qwen3:8b
ollama pull nomic-embed-text:latest
docker compose -f docker/docker-compose.yml up -d
.\scripts\start-all.ps1
```

### Linux
```bash
git clone https://github.com/caizefan34/local-ai-stack.git
cd local-ai-stack && bash scripts/setup.sh
```

Then open **http://localhost:3000** (default password: "1234")

## Features

| Feature | Description |
|---|---|
| 100% Free | Fully open-source, zero API costs |
| Privacy First | All data processed locally |
| RAG + Reranker | BGE reranker boosts accuracy by 40% |
| Visual Knowledge Base | FastGPT UI for document management |
| LoRA Fine-Tuning | PEFT + TRL pipeline, fits 8GB VRAM |
| Multi-Model Support | Qwen3, LLaMA, Mistral |
| One-Click Setup | PowerShell automation included |

## Project Structure

```
local-ai-stack/
--- config/\\ FastGPT & OpenCode configs
--- docker/\\ Docker Compose (with resource limits)
--- docs/\\ Documentation & GitHub Pages site
--- knowledge-base/\\ Import tools (GitHub, CC Switch)
--- lora-finetune/\\ LoRA training pipeline
--- models/\\ Ollama Modelfiles
--- reranker/\\ BGE Reranker FastAPI service
--- scripts/\\ Setup, start, automation
--- tests/\\ E2E tests & evaluation
```

## What's Included

| Module | Description |
|---|---|
| FastGPT v4.8.9 | Visual RAG platform with workflow engine |
| PostgreSQL + pgvector | Vector database (HNSW index) |
| MongoDB + Redis | Session and cache storage |
| Ollama + Qwen3-8B | Local LLM with 32K context window |
| BGE Reranker v2 M3 | Retrieval accuracy booster |
| LoRA Fine-Tuning | PEFT + TRL, QLoRA 4-bit |
| OpenCode Config | Pre-configured AI coding assistant |

## Automation Scripts

| Script | Purpose |
|---|---|
| scripts/automation/check_fastgpt.py | Health check all services |
| scripts/automation/fastgpt_login.py | Auto-login for config changes |
| scripts/automation/update_fastgpt_config.py | Deploy updated settings |
| scripts/automation/prepare_lora_data.py | Extract Q&A for training |
| scripts/automation/check_fastgpt_api.py | Verify API endpoints |
| scripts/automation/find_fastgpt_api.py | Discover API configuration |
| scripts/automation/find_opencode.py | Locate OpenCode integration |
| knowledge-base/sync_github_to_fastgpt.py | Sync GitHub repos to KB |
| knowledge-base/ccswitch_extract.py | Extract CC Switch conversations |

## Running Tests

```bash
# Verify services are running
python tests/e2e_test.py

# Evaluate model accuracy
python tests/evaluate.py --model qwen3-8b-stable
```

## Configuration

1. Copy `.env.example` to `.env` and adjust settings
2. Edit `config/fastgpt-config.json` for RAG parameters
3. Edit `config/opencode-config.json` for IDE integration
4. Review `docker/docker-compose.override.yml` for resource limits

See [docs/optimization-guide.md](docs/optimization-guide.md) for detailed tuning.

## Tech Stack

| Layer | Choice |
|---|---|
| LLM | Qwen3-8B (MIT license) |
| Embedding | nomic-embed-text |
| Reranker | BGE-Reranker-v2-M3 |
| RAG Platform | FastGPT v4.8.9 |
| Vector DB | pgvector (PostgreSQL) |
| Training | PEFT + TRL (HuggingFace) |

## License

MIT License © 2026 [caizefan34](https://github.com/caizefan34)
