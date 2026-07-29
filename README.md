# Local AI Stack — Ollama + FastGPT + RAG

> **Enterprise-grade RAG. 100% local. 100% free.** No API keys, no cloud costs, no GPU required. Windows + Linux + WSL.

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-6366f1?style=for-the-badge)](https://caizefan34.github.io/local-ai-stack/)
[![License](https://img.shields.io/badge/License-MIT-blue)]()
[![GitHub Stars](https://img.shields.io/github/stars/caizefan34/local-ai-stack?style=social)](https://github.com/caizefan34/local-ai-stack)

<p align="center">
  <img src="docs/og-image.svg" alt="Local AI Stack" width="100%">
</p>
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)]()
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)]()

---

## Prerequisites

- Windows 10/11, Linux, or macOS with WSL2
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

### Linux / WSL
```bash
git clone https://github.com/caizefan34/local-ai-stack.git
cd local-ai-stack && bash scripts/setup.sh
```

Then open **http://localhost:3000** (default password: "1234")

---

## Features

| Feature | Description |
|---|---|
| 100% Free | Fully open-source, zero API costs |
| Privacy First | All data processed locally |
| RAG + Reranker | BGE reranker boosts accuracy by 40% |
| Visual Knowledge Base | FastGPT UI for document management |
| LoRA Fine-Tuning | PEFT + TRL pipeline, fits 8GB VRAM |
| Multi-Model Support | Qwen3, LLaMA, Mistral |
| One-Click Setup | PowerShell + Bash automation |
| **Knowledge Base Auto-Sync** | **Automatically sync folders → FastGPT (weekly)** |
| **Desktop Dashboard** | **Real-time service monitor with live status** |

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
| **Desktop Dashboard** | **HTML dashboard with service monitoring** |
| **KB Auto-Sync Pipeline** | **WSL scripts for automated knowledge base syncing** |

## Knowledge Base Auto-Sync

Automatically sync your local documents, course materials, and research papers into FastGPT.

```bash
# Sync Windows folders to WSL
cd knowledge-base/sync
python3 sync-from-windows.py

# Full weekly sync
bash fastgpt-weekly-sync.sh
```

**Windows Scheduled Task** (run as Admin):
```powershell
.\scripts\setup_kb_sync_task.ps1
```

Scheduled: **Every Sunday at 03:00**

### Import Tools

```bash
# Import a paper (auto-extracts metadata)
python3 knowledge-base/sync/add_paper.py paper.pdf

# Clone and import a GitHub repo
python3 knowledge-base/sync/add_github.py https://github.com/user/repo

# Import course materials
python3 knowledge-base/sync/add_course.py lecture1.pdf lecture2.pptx
```

## Desktop Dashboard

Open the real-time dashboard to monitor and control your stack:

```powershell
start desktop-app/dashboard.html
```

Or serve via Python: `python -m http.server 8080` then visit `http://localhost:8080/desktop-app/dashboard.html`

**Features:**
- Live service status (Ollama, FastGPT, Reranker, Docker)
- One-click Start/Stop all services
- Knowledge Base sync trigger
- Auto-refresh every 15 seconds

## Project Structure

```
local-ai-stack/
├── config/              FastGPT & OpenCode configs
├── docker/              Docker Compose (with resource limits)
├── docs/                Documentation & GitHub Pages site
├── knowledge-base/      Import tools (GitHub, CC Switch)
│   └── sync/            Auto-sync pipeline (WSL scripts)
├── lora-finetune/       LoRA training pipeline
├── models/              Ollama Modelfiles
├── reranker/            BGE Reranker FastAPI service
├── scripts/             Setup, start, automation
│   └── automation/      Health checks, config updaters
├── desktop-app/         Desktop dashboard (HTML)
└── tests/               E2E tests & evaluation
```

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
| scripts/setup_kb_sync_task.ps1 | Install Windows scheduled task |
| knowledge-base/sync/sync-from-windows.py | Sync Windows folders to WSL |
| knowledge-base/sync/fastgpt-weekly-sync.sh | Full weekly sync orchestrator |

## Running Tests

```bash
python tests/e2e_test.py
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
