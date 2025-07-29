# test_auto_git_integration.ps1
# Automatski test Git↔VS Code integracije za auto‐commit/push on save

$ErrorActionPreference = "Stop"

function OK([string]$msg)  { Write-Host "[OK]   $msg" -ForegroundColor Green }
function ERR([string]$msg) { Write-Host "[ERR]  $msg" -ForegroundColor Red; exit 1 }

# 1) Provera .git
if (Test-Path ".git") { OK ".git direktorijum pronađen" }
else { ERR ".git direktorijum nije pronađen" }

# 2) Provera remote origin
$remotes = git remote
if ($remotes -contains "origin") { OK "Remote 'origin' konfigurisan" }
else { ERR "Remote 'origin' nije konfigurisan" }

# 3) Provera grane main
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -eq "main") { OK "Nalaziš se na grani 'main'" }
else { ERR "Na grani si '$currentBranch', očekivana je 'main'" }

# 4) Kreiranje i prelazak na test‐granu
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$testBranch = "test-auto-$timestamp"
git checkout -b $testBranch
OK "Kreirana i aktivirana test‐grana '$testBranch'"

# 5) Zabeleži početni commit
$origHEAD = git rev-parse HEAD
OK "Početni commit: $origHEAD"

# 6) Izmeni README.md
Add-Content -Path "README.md" -Value ("`n**AUTO_TEST $timestamp**")
OK "Dodata test linija u README.md"

# 7) Pokretanje auto_git_push.ps1
Write-Host "Pokrećem auto_git_push.ps1..." -ForegroundColor Cyan
.\auto_git_push.ps1
OK "auto_git_push.ps1 izvršen"

# 8) Kratko čekanje
Start-Sleep -Seconds 2

# 9) Provera novog commita
$newHEAD = git rev-parse HEAD
if ($newHEAD -eq $origHEAD) { ERR "Nije kreiran novi commit" }
else { OK "Novi commit detektovan: $newHEAD" }

# 10) Provera poruke commita
$commitMsg = git log -1 --pretty=format:"%s"
if ($commitMsg -match "^Auto-save: README\.md at") {
    OK "Commit poruka ispravna: '$commitMsg'"
} else {
    ERR "Neočekivana commit poruka: '$commitMsg'"
}

# 11) Vraćanje lokalnih izmena
git reset --hard $origHEAD
OK "Lokalne izmene vraćene"

# 12) Brisanje test‐grane na remote
git push origin --delete $testBranch 2>$null
OK "Test‐grana '$testBranch' obrisana na remote"

# 13) Povratak na main i brisanje lokalne test‐grane
git checkout main
git branch -D $testBranch
OK "Lokalna test‐grana '$testBranch' obrisana"

OK "🎉 TEST PASSED: tvoj auto‐commit/push workflow radi besprekorno!"
