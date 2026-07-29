param(
    [string]$RunnerDir = 'C:\local-ai-stack-runner'
)

$ErrorActionPreference = 'Stop'
$runCommand = Join-Path $RunnerDir 'run.cmd'
if (-not (Test-Path -LiteralPath $runCommand)) { throw "Runner command not found: $runCommand" }

$startupDir = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupDir 'Local AI Stack Runner.lnk'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "$env:SystemRoot\System32\cmd.exe"
$shortcut.Arguments = "/c `"$runCommand`""
$shortcut.WorkingDirectory = $RunnerDir
$shortcut.WindowStyle = 7
$shortcut.Save()

Write-Host "Created startup shortcut: $shortcutPath"
