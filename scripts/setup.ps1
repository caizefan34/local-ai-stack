@"
================================================
   Local AI Stack - Windows Setup
  =================================================
"@
Write-Host ""

$rootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$envFile = Join-Path $rootDir ".env"

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

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[x] Python 3 not found!" -ForegroundColor Red
    exit 1
}

# Create local-only credentials on first setup.
if (-not (Test-Path $envFile)) {
    $adminPassword = (([guid]::NewGuid().ToString("N")) + ([guid]::NewGuid().ToString("N"))).Substring(0, 32)
    $tokenKey = ([guid]::NewGuid().ToString("N")) + ([guid]::NewGuid().ToString("N"))
    @(
        "ADMIN_PASSWORD=$adminPassword"
        "TOKEN_KEY=$tokenKey"
        "BIND_ADDRESS=127.0.0.1"
    ) | Set-Content -Path $envFile -Encoding ascii
    Write-Host "  [v] Created .env with random local credentials" -ForegroundColor Green
}

# Pull models
Write-Host "[1/4] Pulling models..." -ForegroundColor Yellow
ollama pull qwen3:8b
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
ollama pull nomic-embed-text:latest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "  [v] Models ready" -ForegroundColor Green

# Start Docker stack
Write-Host "[2/4] Starting FastGPT stack..." -ForegroundColor Yellow
$composeFile = Join-Path $rootDir "docker\docker-compose.yml"
docker compose --env-file $envFile -f $composeFile up -d
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "  [v] FastGPT stack started" -ForegroundColor Green

# Install Python deps
Write-Host "[3/4] Installing Python packages..." -ForegroundColor Yellow
$reqFile = Join-Path $rootDir "reranker\requirements.txt"
python -m pip install -r $reqFile -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "  [v] Python deps installed" -ForegroundColor Green

# Start reranker
Write-Host "[4/4] Starting BGE Reranker service..." -ForegroundColor Yellow
$rerankerDir = Join-Path $rootDir "reranker"
$logFile = Join-Path $rerankerDir "service.log"
Start-Process python -ArgumentList "$rerankerDir\server.py" -WindowStyle Hidden -RedirectStandardOutput $logFile
Write-Host "  [v] Reranker started" -ForegroundColor Green

Write-Host ""
Write-Host ("=" * 50)
Write-Host "  Setup complete!" -ForegroundColor Green
Write-Host "  FastGPT:   http://localhost:3000"
Write-Host "  Ollama:    http://localhost:11434"
Write-Host "  Reranker:  http://localhost:18888"
Write-Host "  Admin password: stored in .env"
Write-Host ("=" * 50)
