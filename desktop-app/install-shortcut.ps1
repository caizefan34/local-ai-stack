<# Install a desktop shortcut with the Local AI Stack mascot icon. #>
[CmdletBinding()]
param(
    [string]$ShortcutName = "Local AI Stack"
)

$ErrorActionPreference = "Stop"
$rootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$desktopDir = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopDir "$ShortcutName.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $rootDir "Start Local AI Stack.cmd"
$shortcut.WorkingDirectory = $rootDir
$shortcut.IconLocation = "$(Join-Path $rootDir 'desktop-app\assets\nailong-mascot.ico'),0"
$shortcut.Description = "Open the Local AI Stack desktop control plane"
$shortcut.Save()
Write-Host "Desktop shortcut created: $shortcutPath" -ForegroundColor Green
