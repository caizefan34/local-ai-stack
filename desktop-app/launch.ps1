<#
Launch Local AI Stack as a desktop-style window.
The control plane stays local and authenticated; Edge/Chrome app mode provides
an independent window without adding an Electron runtime to the project.
#>
[CmdletBinding()]
param(
    [int]$Port = 18080,
    [switch]$BrowserOnly
)

$ErrorActionPreference = "Stop"
$rootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $rootDir ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) { $python = "python" }
$url = "http://127.0.0.1:$Port"

function Test-ControlPlane {
    try {
        $response = Invoke-WebRequest -Uri "$url/api/setup/status" -TimeoutSec 2 -UseBasicParsing
        return $response.StatusCode -lt 500
    } catch { return $false }
}

if (-not $BrowserOnly -and -not (Test-ControlPlane)) {
    Write-Host "Starting Local AI Stack control plane..." -ForegroundColor Cyan
    Start-Process -FilePath $python -ArgumentList @("-m", "control_plane", "serve", "--host", "127.0.0.1", "--port", "$Port") -WorkingDirectory $rootDir -WindowStyle Hidden
    $ready = $false
    1..30 | ForEach-Object {
        Start-Sleep -Milliseconds 500
        if (Test-ControlPlane) { $ready = $true; return }
    }
    if (-not $ready) { throw "Control plane did not become ready at $url" }
}

$edge = Get-Command msedge.exe -ErrorAction SilentlyContinue
$chrome = Get-Command chrome.exe -ErrorAction SilentlyContinue
if ($edge) {
    Start-Process -FilePath $edge.Source -ArgumentList @("--app=$url")
} elseif ($chrome) {
    Start-Process -FilePath $chrome.Source -ArgumentList @("--app=$url")
} else {
    Start-Process $url
}

Write-Host "Local AI Stack desktop window opened at $url" -ForegroundColor Green
