#!/bin/bash
set -e

CODE_MODE=false
if [ "${1:-}" = "--code-mode" ]; then
    CODE_MODE=true
elif [ "$#" -gt 0 ]; then
    echo "Usage: bash scripts/setup.sh [--code-mode]"
    exit 1
fi

echo "=== Local AI Stack Setup ==="

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Check dependencies
command -v docker >/dev/null 2>&1 || { echo "Docker not found!"; exit 1; }
command -v ollama >/dev/null 2>&1 || { echo "Installing Ollama..."; curl -fsSL https://ollama.com/install.sh | sh; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 not found!"; exit 1; }

# Create local-only credentials on first setup.
if [ ! -f "$ROOT_DIR/.env" ]; then
    ADMIN_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(18))')"
    TOKEN_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
    {
        echo "ADMIN_PASSWORD=$ADMIN_PASSWORD"
        echo "TOKEN_KEY=$TOKEN_KEY"
        echo "BIND_ADDRESS=127.0.0.1"
    } > "$ROOT_DIR/.env"
    chmod 600 "$ROOT_DIR/.env"
    echo "Created .env with random local credentials."
fi

# Pull models
echo "Pulling models..."
ollama pull qwen3:8b
ollama pull nomic-embed-text:latest
if [ "$CODE_MODE" = true ]; then
    echo "Pulling code generation and completion models..."
    ollama pull qwen2.5-coder:7b
    ollama pull qwen2.5-coder:1.5b
fi

# Start docker stack
echo "Starting FastGPT..."
docker compose --env-file "$ROOT_DIR/.env" -f "$ROOT_DIR/docker/docker-compose.yml" up -d

# Install Python deps
echo "Installing Python packages..."
python3 -m pip install -r "$ROOT_DIR/reranker/requirements.txt" -q
python3 -m pip install -r "$ROOT_DIR/mcp_server/requirements.txt" -q
python3 -m pip install -r "$ROOT_DIR/control_plane/requirements.txt" -q

# Start reranker
echo "Starting reranker..."
python3 "$ROOT_DIR/reranker/server.py" &
RERANKER_PID=$!
echo $RERANKER_PID > /tmp/reranker.pid

echo
echo "=== Setup complete! ==="
echo "FastGPT:   http://localhost:3000"
echo "Ollama:    http://localhost:11434"
echo "Reranker:  http://localhost:18888"
