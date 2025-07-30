# auto_git_push.ps1
# Automatski git add, commit i push sa timestampom

# Idi u root folder repozitorijuma
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Proveri status
git status

# Dodaj sve izmene
git add .

# Kreiraj poruku sa vremenom
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMessage = "Auto-commit from VSCode at $time"

# Komituj
git commit -m "$commitMessage"

# Push na main branch
git push origin main

# Potvrda
Write-Host "`n✅ Izmene su uspešno push-ovane na GitHub!" -ForegroundColor Green
