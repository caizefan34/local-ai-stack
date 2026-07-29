# Local AI Stack
> **Production-grade RAG. 100% local. 100% free. No GPU required.** 
Build a private AI knowledge base on your laptop with zero cloud costs.

<p align="center">
<a href="https://github.com/caizefan34/local-ai-stack"><img src="https://img.shields.io/github/stars/caizefan34/local-ai-stack?style=for-the-badge&logo=github&color=6366f1" alt="Stars"></a> <a href="https://caizefan34.github.io/local-ai-stack/"><img src="https://img.shields.io/badge/GitHub%20Pages-Live-6366f1?style=for-the-badge" alt="Pages"></a> <a href="https://github.com/caizefan34/local-ai-stack/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"></a></p>

<p align="center">
  <img src="docs/og-image.svg" alt="Local AI Stack" width="100%">
</p>

<p align="center">
<a href="#-quick-start">Quick Start</a> . <a href="#-features">Features</a> . <a href="#-demo">Demo</a> . <a href="#-use-cases">Use Cases</a> . <a href="https://caizefan34.github.io/local-ai-stack/">GitHub Pages</a></p>

---

## ✨ Why Local AI Stack?

Most RAG solutions are either:
- **Cloud-dependent** (OpenAI, Claude) - costs, privacy risks, rate limits
- **Complex to set up** - Kubernetes, multiple services, days of configuration
- **GPU-hungry** - requires expensive hardware

This stack solves all three:
- ✅ **100% offline** - No API keys, no data leaves your machine
- ✅ **One-command setup** - Docker Compose + PowerShell/Bash
- ✅ **Runs on 8GB RAM / CPU** - No GPU required (GPU just makes it faster)
- ✅ **Fine-tune your model** - LoRA training pipeline included

## ⚡ Quick Start

Get your AI knowledge base running in under 5 minutes:

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

Open **http://localhost:3000** (default password: 1234)

---

## ✨ Features

<table>
<tr><td width="50%"><h3>🔒 Privacy First</h3><p>All data processed locally. No API calls. Your documents never leave your machine.</p></td>
<td width="50%"><h3>🎹 Production RAG</h3><p>Visual workflow engine with reranker that boosts accuracy by 40%. BGE-Reranker-v2-M3 included.</p></td></tr>
<tr><td><h3>💪 LoRA Fine-Tuning</h3><p>PEFT + TRL pipeline. Fine-tune Qwen3-8B on 8GB VRAM with QLoRA. Turn your conversations into a custom model.</p></td>
<td><h3>🔄 Auto-Sync Pipeline</h3><p>Weekly sync from Windows folders to FastGPT. Import papers, courses, and GitHub repos automatically.</p></td></tr>
<tr><td><h3>💻 Desktop Dashboard</h3><p>Real-time service monitor with one-click controls. Check status, start/stop services, trigger KB sync.</p></td>
<td><h3>🌐 Multi-Model</h3><p>Switch between Qwen3, LLaMA, Mistral via config. 4 models pre-configured for different workloads.</p></td></tr>
</table>

## 🎬 Demo

### Service Dashboard
Monitor all services in real time:

```
⚫ ollama    ✔️ online     FastGPT:  http://localhost:3000
⚫ fastgpt   ✔️ online     Reranker: http://localhost:18888
⚫ reranker  ✔️ online     Ollama:   http://localhost:11434
⚫ docker    ✔️ running
```

Open the live dashboard:
```powershell
start desktop-app/dashboard.html
```

## 📈 Use Cases

| Scenario | How This Helps |
|----------|---------------|
| Research Papers | Import PDFs, auto-extract metadata, search with reranker |
| Course Notes | Sync folders, chunk documents, query with RAG |
| GitHub Repos | Clone and index repo docs, search code with context |
| Team Wiki | Local knowledge base, no cloud dependency |
| Model Fine-Tuning | Collect conversation logs, train LoRA, deploy custom model |

## 🧩 Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| LLM | Qwen3-8B | Best open-source Chinese/English model, MIT license |
| Embedding | nomic-embed-text | Lightweight, local, no GPU needed |
| Reranker | BGE-Reranker-v2-M3 | +40% retrieval accuracy |
| RAG Platform | FastGPT v4.8.9 | Visual workflow, enterprise-grade |
| Vector DB | pgvector (PostgreSQL) | Rock-solid, HNSW indexing |
| Training | PEFT + TRL (HuggingFace) | 4-bit QLoRA, fits 8GB VRAM |
| AI Coding | OpenCode | Pre-configured local AI assistant |

## 📁 Project Structure

```
local-ai-stack/
├── config/  FastGPT & OpenCode configs
├── docker/  Docker Compose (with resource limits)
├── docs/  Documentation & GitHub Pages
├── knowledge-base/  Import tools + auto-sync pipeline
├── lora-finetune/  LoRA training (collect, train, export)
├── models/  Ollama Modelfiles
├── reranker/  BGE Reranker FastAPI service
├── scripts/  Setup, start, automation scripts
├── desktop-app/  Dashboard (HTML) + API server
├── tests/  E2E tests & model evaluation
```

---

## 🌟 Star the Project

If you find this useful, consider giving it a star on GitHub:

<p align="center">
<a href="https://github.com/caizefan34/local-ai-stack" class="star-btn" style="display:inline-block;padding:14px 40px;border-radius:12px;background:linear-gradient(135deg,#6366f1,#4f46e5);color:#fff;font-size:18px;font-weight:700;text-decoration:none;box-shadow:0 4px 20px rgba(99,102,241,.25)">⭐ Star on GitHub</a>
</p>

<p align="center">Questions? <a href="https://github.com/caizefan34/local-ai-stack/discussions">Join the discussion</a> . <a href="https://github.com/caizefan34/local-ai-stack/issues">Report an issue</a></p>

## License

MIT License © 2026 [caizefan34](https://github.com/caizefan34). Free to use, modify, and distribute.
