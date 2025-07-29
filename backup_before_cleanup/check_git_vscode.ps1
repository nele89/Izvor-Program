<#
.SYNOPSIS
  Proverava da li je Git i VS Code Auto-Git ekstenzija ispravno podešena.
#>

# 1) Proveri da li postoji .git folder
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: .git folder nije pronadjen" -Foreground Red
    exit 1
}

# 2) Proveri remote origin
if (-not (git remote | Select-String '^origin' -Quiet)) {
    Write-Host "ERROR: Remote 'origin' nije postavljen" -Foreground Red
    exit 2
}

# 3) Proveri da li si na grani main
$current = (git rev-parse --abbrev-ref HEAD).Trim()
if ($current -ne 'main') {
    Write-Host "ERROR: Trenutna grana je '$current', ocekivana je 'main'" -Foreground Red
    exit 3
}

# 4) Proveri da grana main prati origin
$tracking = git config branch.main.remote
if ($tracking -ne 'origin') {
    Write-Host "ERROR: Grana 'main' ne prati 'origin' (sada prati '$tracking')" -Foreground Red
    exit 4
}

# 5) Proveri VS Code settings za Auto Git Commit and Push
$settingsPath = ".vscode\settings.json"
if (-not (Test-Path $settingsPath)) {
    Write-Host "ERROR: Ne postoji $settingsPath" -Foreground Red
    exit 5
}
$cfg = Get-Content $settingsPath -Raw
if ($cfg -notmatch '"autogitcommit\.enable"\s*:\s*true') {
    Write-Host "ERROR: 'autogitcommit.enable' nije postavljeno na true" -Foreground Red
    exit 6
}
if ($cfg -notmatch '"autogitcommit\.push"\s*:\s*true') {
    Write-Host "ERROR: 'autogitcommit.push' nije postavljeno na true" -Foreground Red
    exit 7
}

# 6) Proveri da je ekstenzija instalirana
if (-not (& code --list-extensions | Select-String 'YogeshValiya.autogitcommit' -Quiet)) {
    Write-Host "ERROR: Ekstenzija 'YogeshValiya.autogitcommit' nije instalirana" -Foreground Red
    exit 8
}

Write-Host "OK: Sve provere prosle. Git i VS Code Auto-Git su ispravno podeseni." -Foreground Green
exit 0
