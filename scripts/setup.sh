#!/bin/bash
set -e

echo "=== Local AI Stack Setup ==="

# Check dependencies
command -v docker >/dev/null 2>&1 || { echo "Docker not found!"; exit 1; }
command -v ollama >/dev/null 2>&1 || { echo "Installing Ollama..."; curl -fsSL https://ollama.com/install.sh | sh; }

# Pull models
echo "Pulling models..."
ollama pull qwen3:8b
ollama pull nomic-embed-text:latest

# Start docker stack
echo "Starting FastGPT..."
cd "$(dirname "$0")/../docker"
docker compose up -d

# Install Python deps
echo "Installing Python packages..."
pip install -r "$(dirname "$0")/../reranker/requirements.txt" -q

# Start reranker
echo "Starting reranker..."
python "$(dirname "$0")/../reranker/server.py" &
RERANKER_PID=$!
echo $RERANKER_PID > /tmp/reranker.pid

echo
echo "=== Setup complete! ==="
echo "FastGPT:   http://localhost:3000"
echo "Ollama:    http://localhost:11434"
echo "Reranker:  http://localhost:18888"
