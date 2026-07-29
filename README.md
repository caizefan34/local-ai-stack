# Local AI Stack — Ollama + FastGPT + RAG

> **Enterprise-grade RAG. 100% local. 100% free.** No API keys, no cloud costs, no GPU required.

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-6366f1?style=for-the-badge&logo=github)](https://caizefan34.github.io/local-ai-stack/)
[![License](https://img.shields.io/badge/License-MIT-blue)]()
[![GitHub Stars](https://img.shields.io/github/stars/caizefan34/local-ai-stack?style=social)](https://github.com/caizefan34/local-ai-stack)

---

## Quick Start

### Windows
```powershell
git clone https://github.com/caizefan34/local-ai-stack.git
cd local-ai-stack
winget install Ollama.Ollama
ollama pull qwen3:8b && ollama pull nomic-embed-text:latest
docker compose -f docker/docker-compose.yml up -d
.\scripts\start-all.ps1
```

### Linux
```bash
git clone https://github.com/caizefan34/local-ai-stack.git
cd local-ai-stack && bash scripts/setup.sh
```

Visit **http://localhost:3000** — default password: `1234`

---

## Features

| Feature | Description |
|---------|-------------|
| 🆓 **100% Free** | Fully open-source, zero API costs |
| 🔒 **Privacy First** | All data processed locally |
| 🎯 **RAG + Reranker** | BGE reranker for +40% accuracy |
| 🧩 **Visual Knowledge Base** | FastGPT UI for document management |
| 🏋️ **LoRA Fine-tuning** | PEFT + TRL pipeline, fits 8GB VRAM |
| 🌐 **Multi-Model** | Qwen3, LLaMA, Mistral — switch via config |
| 💻 **Windows First** | PowerShell one-click setup |

## Project Structure

```
local-ai-stack/
├── config/              FastGPT & OpenCode configs
├── docker/              Docker Compose (w/ resource limits)
├── docs/                Documentation & GitHub Pages site
├── knowledge-base/      Import tools (GitHub, CC Switch)
├── lora-finetune/       LoRA training pipeline
│   ├── scripts/         collect_data, train, export
│   └── data/            Training datasets
├── models/              Ollama Modelfiles
├── reranker/            BGE Reranker FastAPI service
├── scripts/             Setup, start, automation
│   └── automation/      Health checks, config updaters
└── tests/               E2E tests & evaluation
```

## What's Included

| Module | Description |
|--------|-------------|
| FastGPT v4.8.9 | Visual RAG platform with workflow engine |
| PostgreSQL + pgvector | Vector database (HNSW, pgHNSWEfSearch=200) |
| MongoDB + Redis | Session & cache storage |
| Ollama + Qwen3-8B | Local LLM inference (32K context window) |
| BGE Reranker v2 M3 | +40% retrieval accuracy |
| LoRA Fine-tuning | PEFT + TRL pipeline, QLoRA 4-bit |
| OpenCode Config | Pre-configured AI coding assistant |

## Automation Scripts

| Script | Purpose |
|--------|---------|
| `scripts/automation/check_fastgpt.py` | Health check |
| `scripts/automation/fastgpt_login.py` | Automated login |
| `scripts/automation/update_fastgpt_config.py` | Config updater |
| `scripts/automation/prepare_lora_data.py` | Collect training data from Codex/CC Switch |
| `knowledge-base/sync_github_to_fastgpt.py` | Sync GitHub repos to knowledge base |
| `knowledge-base/ccswitch_extract.py` | Extract CC Switch conversations |

## Running Tests

```bash
# Verify all services are running
python tests/e2e_test.py

# Evaluate model accuracy
python tests/evaluate.py --model qwen3-8b-stable
```

## LoRA Fine-tuning

```bash
# 1. Collect training data from Codex sessions
python scripts/automation/prepare_lora_data.py --source codex --max 300

# 2. Train with QLoRA (needs ~7GB VRAM)
cd lora-finetune
python scripts/train.py --quant 4bit --epochs 3

# 3. Merge and export to Ollama
python scripts/merge_and_export.py
ollama create my-model -f outputs/lora-adapter/Modelfile
```

## Configuration

1. Copy `.env.example` to `.env` and adjust settings
2. Edit `config/fastgpt-config.json` for RAG parameters
3. Edit `config/opencode-config.json` for IDE integration
4. Run `docker compose -f docker/docker-compose.override.yml down-up` for resource limits

See [docs/optimization-guide.md](docs/optimization-guide.md) for detailed tuning.

## Tech Stack

| Layer | Choice |
|-------|--------|
| LLM | Qwen3-8B (MIT license) |
| Embedding | nomic-embed-text |
| Reranker | BGE-Reranker-v2-M3 |
| RAG Platform | FastGPT v4.8.9 |
| Vector DB | pgvector |
| Training | PEFT + TRL (HuggingFace) |

## License

MIT License © 2026 [caizefan34](https://github.com/caizefan34)
