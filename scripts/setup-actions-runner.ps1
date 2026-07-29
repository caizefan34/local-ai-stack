param(
    [string]$Repository = 'caizefan34/local-ai-stack',
    [string]$RunnerName = 'local-ai-gpu',
    [string]$RunnerDir = 'C:\local-ai-stack-runner'
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI (gh) is required.' }
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { throw 'Ollama is required before registering an ollama runner.' }
if (Test-Path -LiteralPath $RunnerDir) { throw "Runner directory already exists: $RunnerDir" }

$release = gh api repos/actions/runner/releases/latest | ConvertFrom-Json
$asset = $release.assets | Where-Object { $_.name -like 'actions-runner-win-x64-*.zip' } | Select-Object -First 1
if (-not $asset) { throw 'No Windows x64 GitHub Actions runner release was found.' }

New-Item -ItemType Directory -Path $RunnerDir | Out-Null
$archive = Join-Path $RunnerDir $asset.name
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $archive
Expand-Archive -LiteralPath $archive -DestinationPath $RunnerDir

# The registration token is short-lived and is never printed or written to disk.
$registrationToken = gh api "repos/$Repository/actions/runners/registration-token" --method POST --jq '.token'
& (Join-Path $RunnerDir 'config.cmd') --unattended --url "https://github.com/$Repository" --token $registrationToken --name $RunnerName --labels 'ollama,gpu' --work '_work'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Registered $RunnerName for $Repository."
Write-Host "Start it in a dedicated terminal: & '$RunnerDir\run.cmd'"
Write-Host "For automatic start after sign-in, run .\scripts\install-runner-startup.ps1."
