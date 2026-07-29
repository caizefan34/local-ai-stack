#!/bin/bash
# ============================================================
# pull-models.sh — Interactive Ollama Model Downloader
# ============================================================
# Usage:  bash scripts/pull-models.sh
#         bash scripts/pull-models.sh --all    (download all)
#         bash scripts/pull-models.sh qwen3:8b (download specific)
#         bash scripts/pull-models.sh --code-mode (code generation + completion)
# ============================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   Local AI Stack — Model Puller${NC}"
echo -e "${BLUE}============================================${NC}"

# Check Ollama
if ! command -v ollama &>/dev/null; then
    echo -e "${RED}[ERROR] Ollama is not installed.${NC}"
    echo "  Install: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Or:      winget install Ollama.Ollama (Windows)"
    exit 1
fi

if ! ollama list &>/dev/null 2>&1; then
    echo -e "${YELLOW}[...] Ollama server not running. Starting...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open -a Ollama
    else
        ollama serve &
    fi
    sleep 3
fi

echo -e "${GREEN}[OK] Ollama is running${NC}"
echo ""

# Recommended models with descriptions
declare -A MODELS
MODELS["qwen3:8b"]="Qwen3 8B — Main LLM for RAG (default, ~4.7 GB)"
MODELS["qwen3:0.6b"]="Qwen3 0.6B — Fast lightweight (~600 MB)"
MODELS["qwen3:1.7b"]="Qwen3 1.7B — Lightweight (~1 GB)"
MODELS["qwen2.5:14b"]="Qwen2.5 14B — Fallback, higher accuracy (~8 GB)"
MODELS["qwen2.5-coder:7b"]="Qwen2.5-Coder 7B — Code generation and bug fixing (~4.7 GB)"
MODELS["qwen2.5-coder:1.5b"]="Qwen2.5-Coder 1.5B — Low-latency code completion (~1 GB)"
MODELS["deepseek-r1:7b"]="DeepSeek R1 7B — Reasoning model (~4.5 GB)"
MODELS["nomic-embed-text:latest"]="Nomic Embed Text — Embeddings for RAG (~274 MB)"
MODELS["llama3.2:3b"]="LLaMA 3.2 3B — Lightweight (~2 GB)"
MODELS["mistral:7b"]="Mistral 7B — Alternative main model (~4.1 GB)"

RECOMMENDED=("qwen3:8b" "nomic-embed-text:latest" "qwen3:0.6b" "deepseek-r1:7b" "qwen2.5:14b")
CODE_MODELS=("qwen2.5-coder:7b" "qwen2.5-coder:1.5b")

# If --all flag, download all
if [[ "$1" == "--all" ]]; then
    echo -e "${YELLOW}Downloading ALL recommended models...${NC}"
    for model in "${RECOMMENDED[@]}"; do
        echo ""
        echo -e "${BLUE}>>> Pulling: $model${NC}"
        echo -e "${BLUE}    ${MODELS[$model]}${NC}"
        ollama pull "$model"
        echo -e "${GREEN}[DONE] $model${NC}"
    done
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}   All models downloaded!${NC}"
    echo -e "${GREEN}============================================${NC}"
    ollama list
    exit 0
fi

if [[ "$1" == "--code-mode" ]]; then
    echo -e "${YELLOW}Downloading code generation and completion models...${NC}"
    for model in "${CODE_MODELS[@]}"; do
        ollama pull "$model"
    done
    exit 0
fi

# If a specific model name is passed, download that one
if [[ -n "$1" ]]; then
    echo -e "${YELLOW}Downloading: $1${NC}"
    ollama pull "$1"
    echo -e "${GREEN}[DONE] $1${NC}"
    exit 0
fi

# Interactive menu
echo -e "${YELLOW}Recommended models:${NC}"
echo ""

PS3="Select model to download (or 0 to quit): "
options=()
for m in "${RECOMMENDED[@]}"; do
    options+=("$m — ${MODELS[$m]}")
done
options+=("Download ALL recommended models")

select opt in "${options[@]}"; do
    if [[ -z "$opt" ]]; then
        echo -e "${RED}Invalid option. Try again.${NC}"
        continue
    fi
    if [[ "$opt" == "Download ALL recommended models" ]]; then
        for model in "${RECOMMENDED[@]}"; do
            echo ""
            echo -e "${BLUE}>>> Pulling: $model${NC}"
            ollama pull "$model"
            echo -e "${GREEN}[DONE] $model${NC}"
        done
        echo ""
        echo -e "${GREEN}All models downloaded!${NC}"
        ollama list
        break
    fi
    # Extract model name (before the em dash)
    model_name="${opt%% —*}"
    echo -e "${BLUE}>>> Pulling: $model_name${NC}"
    ollama pull "$model_name"
    echo -e "${GREEN}[DONE] $model_name${NC}"
    echo ""
    echo -e "${YELLOW}Current models:${NC}"
    ollama list
    echo ""
    echo -e "${YELLOW}Select another model (0 to quit):${NC}"
done

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   Done! Run 'ollama list' to see all models${NC}"
echo -e "${GREEN}============================================${NC}"
