@"
==================================================
   Local AI Stack - Service Launcher
  ==================================================
"@
Write-Host ""

# Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[x] Docker not found! Install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# 1. Start FastGPT stack
Write-Host "[1/3] Starting FastGPT + Databases..." -ForegroundColor Yellow
$composeDir = Join-Path $PSScriptRoot "..\docker"
Set-Location $composeDir
docker compose up -d 2>&1 | Out-Null
Write-Host "  [v] FastGPT running on http://localhost:3000" -ForegroundColor Green

# 2. Start reranker service
Write-Host "[2/3] Starting BGE Reranker Service..." -ForegroundColor Yellow
$rerankerDir = Join-Path $PSScriptRoot "..\reranker"
Get-Process -Name python* -ErrorAction SilentlyContinue | Where-Object {
    (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -match "reranker"
} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Process python -ArgumentList "$rerankerDir\server.py" -WindowStyle Hidden
Write-Host "  [v] Reranker running on http://localhost:18888" -ForegroundColor Green

# 3. Verify
Write-Host "[3/3] Verifying services..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
$ok = $true
try {
    $r = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    if ($r.StatusCode -eq 200) { Write-Host "  [v] FastGPT OK" -ForegroundColor Green }
} catch { Write-Host "  [x] FastGPT not responding" -ForegroundColor Red; $ok = $false }

if ($ok) {
    Write-Host ""
    Write-Host "All services running!" -ForegroundColor Green
    Write-Host "  FastGPT:    http://localhost:3000"
    Write-Host "  Reranker:   http://localhost:18888"
    Write-Host "  Ollama API: http://localhost:11434"
}
