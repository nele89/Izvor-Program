Set-Location -Path (Split-Path -Parent $PSScriptRoot)

git add .
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMessage = "Auto-commit from File Watcher at $time"

git commit -m "$commitMessage"
git push origin main

Write-Host "`n✅ Git push izvršen automatski!" -ForegroundColor Green
