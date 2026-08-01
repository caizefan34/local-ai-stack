<#
Install/update desktop shortcuts so both "Local AI Stack" and "AI Desktop"
open the native Electron desktop app instead of a browser tab.
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
    @{ Name = "Local AI Stack"; Description = "Local AI Stack 桌面版（Electron 原生应用）" },
    @{ Name = "AI Desktop";     Description = "AI Desktop - Local AI Stack 原生桌面应用" }
)

foreach ($s in $shortcuts) {
    $shortcutPath = Join-Path $desktopDir "$($s.Name).lnk"
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $launcher
    $shortcut.WorkingDirectory = $electronDir
    $shortcut.IconLocation = "$icon,0"
    $shortcut.Description = $s.Description
    $shortcut.Save()
    Write-Host "Updated: $shortcutPath" -ForegroundColor Green
}
