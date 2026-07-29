# Local AI Stack - Dashboard API Server
# Start with: powershell -File desktop-app/dashboard-server.ps1
# Dashboard at: http://localhost:18080/desktop-app/dashboard.html

$port = 18080
$baseDir = Split-Path -Parent $PSScriptRoot

# Simple HTTP listener
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()
Write-Host "Dashboard API running on http://localhost:$port" -ForegroundColor Green
Write-Host "Open dashboard.html in browser or use: start $baseDir/desktop-app/dashboard.html" -ForegroundColor Yellow

function Send-Response($ctx, $body, $status=200) {
    $buffer = [Text.Encoding]::UTF8.GetBytes($body)
    $ctx.Response.StatusCode = $status
    $ctx.Response.ContentType = "text/plain; charset=utf-8"
    $ctx.Response.ContentLength64 = $buffer.Length
    $ctx.Response.OutputStream.Write($buffer, 0, $buffer.Length)
    $ctx.Response.Close()
}

function Send-File($ctx, $filePath) {
    if (Test-Path $filePath) {
        $ext = [IO.Path]::GetExtension($filePath)
        $mime = @{
            ".html" = "text/html; charset=utf-8"
            ".css" = "text/css"
            ".js" = "application/javascript"
            ".json" = "application/json"
            ".png" = "image/png"
            ".jpg" = "image/jpeg"
        }
        $contentType = if ($mime.ContainsKey($ext)) { $mime[$ext] } else { "application/octet-stream" }
        $bytes = [IO.File]::ReadAllBytes($filePath)
        $ctx.Response.StatusCode = 200
        $ctx.Response.ContentType = $contentType
        $ctx.Response.ContentLength64 = $bytes.Length
        $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
        Send-Response $ctx "404 Not Found" 404
    }
    $ctx.Response.Close()
}

while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $url = $ctx.Request.Url.LocalPath.Trim("/")
    $method = $ctx.Request.HttpMethod

    # File server for static files
    if ($method -eq "GET" -and $url -eq "desktop-app/dashboard.html") {
        Send-File $ctx (Join-Path $baseDir "desktop-app/dashboard.html")
        continue
    }

    # API endpoints
    switch ($url) {
        "api/start-all" {
            Write-Host "[API] Starting all services..."
            $result = & (Join-Path $baseDir "scripts/start-all.ps1") 2>&1
            Send-Response $ctx "Services started`n$result"
        }
        "api/stop-all" {
            Write-Host "[API] Stopping services..."
            docker compose -f (Join-Path $baseDir "docker/docker-compose.yml") down 2>&1 | Out-Null
            Get-Process -Name python* -ErrorAction SilentlyContinue | Where-Object {
                (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -match "reranker"
            } | Stop-Process -Force -ErrorAction SilentlyContinue
            Send-Response $ctx "Services stopped"
        }
        "api/sync-kb" {
            Write-Host "[API] Syncing knowledge base..."
            $syncScript = Join-Path $baseDir "knowledge-base/sync/run-kb-sync.sh"
            if (Test-Path $syncScript) {
                $result = wsl bash $syncScript 2>&1
                Send-Response $ctx "Sync completed`n$result"
            } else {
                Send-Response $ctx "WSL sync script not found. Run setup_kb_sync_task.ps1 first." 400
            }
        }
        default {
            # Try static file
            $filePath = Join-Path $baseDir $url
            if (Test-Path $filePath -PathType Leaf) {
                Send-File $ctx $filePath
            } else {
                Send-Response $ctx "Unknown endpoint: $url" 404
            }
        }
    }
}
