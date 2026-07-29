# Local AI Stack — Ollama + FastGPT + RAG

> Run a production-grade RAG application on your laptop. Free, private, no GPU required.

## Quick Start

### Windows
`powershell
git clone https://github.com/caizefan34/local-ai-stack.git
cd local-ai-stack
winget install Ollama.Ollama
ollama pull qwen3:8b && ollama pull nomic-embed-text:latest
docker compose -f docker/docker-compose.yml up -d
.\scripts\start-all.ps1
`

### Linux
`ash
git clone https://github.com/caizefan34/local-ai-stack.git
cd local-ai-stack && bash scripts/setup.sh
`

Visit **http://localhost:3000** to start using FastGPT.

## Project Structure

`
local-ai-stack/
├── config/                    FastGPT & OpenCode configs
├── docker/                    Docker Compose for FastGPT stack
├── docs/                      Documentation & GitHub Pages site
├── knowledge-base/            Import tools (GitHub, CC Switch)
├── lora-finetune/             LoRA training pipeline
│   ├── scripts/               collect_data, train, export
│   └── data/                  Training datasets
├── models/                    Ollama Modelfiles
├── reranker/                  BGE Reranker FastAPI service
├── scripts/                   Setup, start, automation utilities
│   └── automation/            FastGPT health checks, config updaters
└── tests/                     E2E tests & evaluation
`

## What's Included

| Module | Description |
|--------|-------------|
| FastGPT v4.8.9 | Visual RAG platform with workflow engine |
| PostgreSQL + pgvector | Vector database |
| MongoDB + Redis | Session & cache storage |
| Ollama + Qwen3-8B | Local LLM inference |
| BGE Reranker v2 M3 | +40% retrieval accuracy |
| LoRA Fine-tuning | PEFT + TRL pipeline, fits 8GB VRAM |
| OpenCode Config | Pre-configured AI coding assistant |

## Automation Tools

| Script | Purpose |
|--------|---------|
| scripts/automation/check_fastgpt.py | Health check |
| scripts/automation/fastgpt_login.py | Automated login |
| scripts/automation/update_fastgpt_config.py | Config updater |
| scripts/automation/find_opencode.py | OpenCode discovery |
| scripts/automation/prepare_lora_data.py | Collect training data from Codex/CC Switch |
| knowledge-base/sync_github_to_fastgpt.py | Sync GitHub repos to knowledge base |
| knowledge-base/import_ccswitch_logs.py | Import CC Switch conversation logs |

## Configuration

1. Copy .env.example to .env and adjust settings
2. Edit config/fastgpt-config.json for RAG parameters
3. Edit config/opencode-config.json for IDE integration

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
