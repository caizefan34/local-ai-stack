# Starts the authenticated Python control plane in place of the legacy unauthenticated dashboard server.
param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 18080
)

$rootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $rootDir
try {
    Write-Host "Starting authenticated Local AI Stack control plane on http://${Host}:$Port" -ForegroundColor Green
    Write-Host "Create the first admin first: python -m control_plane bootstrap-admin" -ForegroundColor Yellow
    python -m control_plane serve --host $Host --port $Port
} finally {
    Pop-Location
}
