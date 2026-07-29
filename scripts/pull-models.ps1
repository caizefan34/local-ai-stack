# ============================================================
# pull-models.ps1 — Interactive Ollama Model Downloader
# ============================================================
# Usage:  .\scripts\pull-models.ps1
#         .\scripts\pull-models.ps1 -All
#         .\scripts\pull-models.ps1 -Model qwen3:8b
#         .\scripts\pull-models.ps1 -CodeMode
# ============================================================

param(
    [switch]$All,
    [switch]$CodeMode,
    [string]$Model = ""
)

function Write-Color($Text, $Color = "White") {
    Write-Host $Text -ForegroundColor $Color
}

Write-Color "============================================" "Blue"
Write-Color "   Local AI Stack - Model Puller" "Blue"
Write-Color "============================================" "Blue"

# Check Ollama
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Color "[ERROR] Ollama is not installed." "Red"
    Write-Color "  Install: winget install Ollama.Ollama"
    Write-Color "  Or:      https://ollama.com/download"
    exit 1
}

try {
    $null = ollama list 2>&1
    Write-Color "[OK] Ollama is running" "Green"
} catch {
    Write-Color "[...] Ollama server not running. Start Ollama Desktop first." "Yellow"
    Write-Color "  Then re-run this script."
    exit 1
}

# Model definitions
$models = @(
    @{Name = "qwen3:8b"; Desc = "Qwen3 8B - Main LLM for RAG (default, ~4.7 GB)"}
    @{Name = "qwen3:0.6b"; Desc = "Qwen3 0.6B - Fast lightweight (~600 MB)"}
    @{Name = "qwen3:1.7b"; Desc = "Qwen3 1.7B - Lightweight (~1 GB)"}
    @{Name = "qwen2.5:14b"; Desc = "Qwen2.5 14B - Fallback, higher accuracy (~8 GB)"}
    @{Name = "qwen2.5-coder:7b"; Desc = "Qwen2.5-Coder 7B - Code generation and bug fixing (~4.7 GB)"}
    @{Name = "qwen2.5-coder:1.5b"; Desc = "Qwen2.5-Coder 1.5B - Low-latency code completion (~1 GB)"}
    @{Name = "deepseek-r1:7b"; Desc = "DeepSeek R1 7B - Reasoning model (~4.5 GB)"}
    @{Name = "nomic-embed-text:latest"; Desc = "Nomic Embed Text - Embeddings for RAG (~274 MB)"}
    @{Name = "llama3.2:3b"; Desc = "LLaMA 3.2 3B - Lightweight (~2 GB)"}
    @{Name = "mistral:7b"; Desc = "Mistral 7B - Alternative main model (~4.1 GB)"}
)

$recommended = @("qwen3:8b", "nomic-embed-text:latest", "qwen3:0.6b", "deepseek-r1:7b", "qwen2.5:14b")
$codeModels = @("qwen2.5-coder:7b", "qwen2.5-coder:1.5b")

function Pull-Model($modelName) {
    $desc = ($models | Where-Object { $_.Name -eq $modelName }).Desc
    if (-not $desc) { $desc = $modelName }
    Write-Color ">>> Pulling: $modelName" "Blue"
    Write-Color "    $desc" "Blue"
    ollama pull $modelName
    if ($LASTEXITCODE -eq 0) {
        Write-Color "[DONE] $modelName" "Green"
        return $true
    } else {
        Write-Color "[FAILED] $modelName" "Red"
        return $false
    }
}

# Download ALL
if ($All) {
    Write-Color "Downloading ALL recommended models..." "Yellow"
    foreach ($m in $recommended) {
        Write-Host ""
        Pull-Model $m
    }
    Write-Host ""
    Write-Color "============================================" "Green"
    Write-Color "   All models downloaded!" "Green"
    Write-Color "============================================" "Green"
    ollama list
    exit 0
}

if ($CodeMode) {
    Write-Color "Downloading code generation and completion models..." "Yellow"
    foreach ($m in $codeModels) { Pull-Model $m }
    exit 0
}

# Download specific model
if ($Model -ne "") {
    Pull-Model $Model
    exit 0
}

# Interactive menu
Write-Color "" "White"
Write-Color "Recommended models:" "Yellow"
Write-Host ""

$menuItems = @()
foreach ($m in $recommended) {
    $desc = ($models | Where-Object { $_.Name -eq $m }).Desc
    $menuItems += [PSCustomObject]@{ Name = $m; Desc = $desc }
}
$menuItems += [PSCustomObject]@{ Name = "__ALL__"; Desc = "Download ALL recommended models" }

$selected = $false
while (-not $selected) {
    for ($i = 0; $i -lt $menuItems.Count; $i++) {
        Write-Host "  $($i + 1). $($menuItems[$i].Name) — $($menuItems[$i].Desc)"
    }
    Write-Host "  0. Quit"
    Write-Host ""
    $choice = Read-Host "Select model to download (0 to quit)"

    if ($choice -eq "0") { exit 0 }

    $index = [int]$choice - 1
    if ($index -ge 0 -and $index -lt $menuItems.Count) {
        if ($menuItems[$index].Name -eq "__ALL__") {
            Write-Color "" "White"
            foreach ($m in $recommended) {
                Write-Host ""
                Pull-Model $m
            }
            Write-Host ""
            Write-Color "All models downloaded!" "Green"
            ollama list
        } else {
            Write-Host ""
            Pull-Model $menuItems[$index].Name
            Write-Host ""
            Write-Color "Current models:" "Yellow"
            ollama list
            Write-Host ""
            Write-Color "Select another model (0 to quit):" "Yellow"
            continue
        }
        $selected = $true
    } else {
        Write-Color "Invalid option. Try again." "Red"
    }
}

Write-Host ""
Write-Color "============================================" "Green"
Write-Color "   Done! Run 'ollama list' to see all models" "Green"
Write-Color "============================================" "Green"
