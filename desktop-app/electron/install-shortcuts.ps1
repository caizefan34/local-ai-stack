<#
Install/update desktop shortcuts so both "Local AI Stack" and "AI Desktop"
open the native Electron desktop app instead of a browser tab.
  - Local AI Stack: opens the control-plane dashboard (http://127.0.0.1:18080)
  - AI Desktop:     opens FastGPT directly (http://127.0.0.1:3000)
Run:  powershell -ExecutionPolicy Bypass -File .\install-shortcuts.ps1
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$electronDir = $PSScriptRoot
$launcher = Join-Path $electronDir "start-local-ai-stack.cmd"
$repoRoot = (Resolve-Path (Join-Path $electronDir "..\..")).Path
$icon = Join-Path $repoRoot "desktop-app\assets\nailong-mascot.ico"
$desktopDir = [Environment]::GetFolderPath("Desktop")
$shell = New-Object -ComObject WScript.Shell

$shortcuts = @(
    @{ Name = "Local AI Stack"; Description = "Local AI Stack 桌面版（控制台）"; Arguments = "" },
    @{ Name = "AI Desktop";     Description = "AI Desktop - FastGPT 原生桌面入口"; Arguments = "--fastgpt" }
)

foreach ($s in $shortcuts) {
    $shortcutPath = Join-Path $desktopDir "$($s.Name).lnk"
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $launcher
    $shortcut.Arguments = $s.Arguments
    $shortcut.WorkingDirectory = $electronDir
    $shortcut.IconLocation = "$icon,0"
    $shortcut.Description = $s.Description
    $shortcut.Save()
    Write-Host "Updated: $shortcutPath" -ForegroundColor Green
}