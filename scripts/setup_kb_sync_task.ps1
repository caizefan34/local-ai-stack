# FastGPT Knowledge Base Auto-Sync - Windows Task Scheduler Setup
# Run as Administrator to install the scheduled task

$KB_HOME = $env:KB_HOME
if (-not $KB_HOME) {
    $KB_HOME = "~/knowledge-base"
}

$actionScript = "bash $KB_HOME/sync/fastgpt-weekly-sync.sh"
$action = New-ScheduledTaskAction -Execute "wsl.exe" -Argument $actionScript

# Weekly trigger: every Sunday at 03:00
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 03:00 -WeeksInterval 1

# Run as current user with highest privileges
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -RunLevel Highest

# Task settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Register the task
Register-ScheduledTask -TaskName "FastGPT KB Auto-Sync" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Settings $settings `
  -Description "Weekly auto-sync of knowledge base files to FastGPT"

Write-Host "Scheduled task 'FastGPT KB Auto-Sync' created!" -ForegroundColor Green
Write-Host "Trigger: Every Sunday at 03:00" -ForegroundColor Yellow
Write-Host "To run immediately: Start-ScheduledTask -TaskName 'FastGPT KB Auto-Sync'" -ForegroundColor Cyan
