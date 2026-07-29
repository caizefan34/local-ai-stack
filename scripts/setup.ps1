@"
================================================
   Local AI Stack - Windows Setup
  =================================================
"@
Write-Host ""

# Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[x] Docker Desktop not found!" -ForegroundColor Red
    Write-Host "    Download from: https://www.docker.com/products/docker-desktop/"
    exit 1
}

# Check / Install Ollama
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "[...] Installing Ollama..." -ForegroundColor Yellow
    winget install Ollama.Ollama
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[x] Ollama install failed. Download manually: https://ollama.com/download" -ForegroundColor Red
        exit 1
    }
}

# Pull models
Write-Host "[1/4] Pulling models..." -ForegroundColor Yellow
ollama pull qwen3:8b
ollama pull nomic-embed-text:latest
Write-Host "  [v] Models ready" -ForegroundColor Green

# Start Docker stack
Write-Host "[2/4] Starting FastGPT stack..." -ForegroundColor Yellow
$composeDir = Join-Path $PSScriptRoot "..\docker"
Set-Location $composeDir
docker compose up -d
Write-Host "  [v] FastGPT stack started" -ForegroundColor Green

# Install Python deps
Write-Host "[3/4] Installing Python packages..." -ForegroundColor Yellow
$reqFile = Join-Path $PSScriptRoot "..\reranker\requirements.txt"
pip install -r $reqFile -q
Write-Host "  [v] Python deps installed" -ForegroundColor Green

# Start reranker
Write-Host "[4/4] Starting BGE Reranker service..." -ForegroundColor Yellow
$rerankerDir = Join-Path $PSScriptRoot "..\reranker"
$logFile = Join-Path $rerankerDir "service.log"
Start-Process python -ArgumentList "$rerankerDir\server.py" -WindowStyle Hidden -RedirectStandardOutput $logFile
Write-Host "  [v] Reranker started" -ForegroundColor Green

Write-Host ""
Write-Host ("=" * 50)
Write-Host "  Setup complete!" -ForegroundColor Green
Write-Host "  FastGPT:   http://localhost:3000"
Write-Host "  Ollama:    http://localhost:11434"
Write-Host "  Reranker:  http://localhost:18888"
Write-Host "  Default password: 1234"
Write-Host ("=" * 50)
