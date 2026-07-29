# Setup Guide

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| RAM | 8 GB | 16 GB+ |
| Disk | 20 GB | 50 GB+ |
| GPU (optional) | — | RTX 3060+ (8 GB VRAM) |
| Docker | v24+ | v27+ |
| Python | 3.10+ | 3.11+ |

## Windows Setup

### 1. Install Dependencies

```powershell
# Install Docker Desktop
# https://www.docker.com/products/docker-desktop/

# Install Ollama
winget install Ollama.Ollama

# Install Python 3.11+
# https://www.python.org/downloads/
`

### 2. Clone and Pull Models

```powershell
git clone https://github.com/caizefan34/local-ai-stack.git
cd local-ai-stack

ollama pull qwen3:8b
ollama pull nomic-embed-text:latest
`

### 3. Configure Environment

Copy .env.example to .env and adjust settings:

```powershell
cp .env.example .env
# Replace ADMIN_PASSWORD and TOKEN_KEY before starting manually
`

### 4. Start FastGPT

```powershell
docker compose --env-file .env -f docker/docker-compose.yml up -d
`

Visit **http://localhost:3000** and use the `ADMIN_PASSWORD` stored in `.env`.

### 5. Start the Reranker Service

```powershell
.\scripts\start-all.ps1
`

This starts:
- **BGE Reranker** on port 18888
- Configures FastGPT with optimized settings

### 6. Create a Knowledge Base

1. Log in to FastGPT at http://localhost:3000
2. Create a new knowledge base → select vector model 
omic-embed-text
3. Upload documents or use the import scripts in knowledge-base/

## Linux Setup

`ash
# Install Docker & Ollama
curl -fsSL https://ollama.com/install.sh | sh
sudo apt install docker-compose

# Clone and run setup
git clone https://github.com/caizefan34/local-ai-stack.git
cd local-ai-stack
bash scripts/setup.sh
`

## Setting Up OpenCode (IDE Integration)

OpenCode uses the provided config file at config/opencode-config.json:

1. In OpenCode, select Ollama as your provider
2. Choose the qwen3-8b-stable model
3. The config file contains all necessary API endpoints and model limits

## Importing Knowledge Base Data

### From GitHub Starred Repos

`ash
python knowledge-base/sync_github_to_fastgpt.py
`
Requires the gh CLI to be authenticated. Syncs your starred repos and your own repos into FastGPT.

### From CC Switch Conversations

`ash
python knowledge-base/ccswitch_extract.py
`
Extracts conversation records from CC Switch's local LevelDB storage.

## Training a Fine-tuned Model

`ash
# Collect training data from your Codex sessions
python scripts/automation/prepare_lora_data.py --source codex --max 300

# Train with QLoRA (needs ~7 GB VRAM)
cd lora-finetune
python scripts/train.py --modelscope --quant 4bit --epochs 3

# Export to Ollama
python scripts/merge_and_export.py
ollama create my-finetuned-model -f Modelfile
`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| FastGPT won't start | Check Docker is running and ports 3000/5432/6379/27017 are free |
| Reranker fails to load model | Ensure you have at least 8 GB free RAM for the BGE model |
| Ollama out of memory | Use smaller models (qwen3:0.6b) or close other applications |
| MongoDB replica set error | Run docker compose down -v && docker compose up -d to reset data |


## Knowledge Base Auto-Sync

Set up automated syncing of your local files into FastGPT:

```bash
# Sync Windows folders to WSL knowledge base
cd knowledge-base/sync
export KB_WINDOWS_SOURCE=/mnt/d/your-knowledge-folder
python3 sync-from-windows.py
```

### Windows Scheduled Task (Admin):

```powershell
.\scripts\setup_kb_sync_task.ps1
```

## Desktop Dashboard

Monitor and control your stack via the desktop dashboard:

```powershell
# Start the API server
powershell -File desktop-app/dashboard-server.ps1

# Open the dashboard
start desktop-app/dashboard.html
```
