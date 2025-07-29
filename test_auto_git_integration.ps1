# test_auto_git_integration.ps1
# Automatski test Git↔VS Code auto‐commit/push workflow

$ErrorActionPreference = 'Stop'
$errors = 0

function LogOK($msg)  { Write-Host "[OK]   $msg" -ForegroundColor Green }
function LogERR($msg) { Write-Host "[ERR]  $msg" -ForegroundColor Red; $script:errors++ }

try {
    # 1) .git direktorijum
    if (Test-Path ".git") { LogOK ".git direktorijum pronađen" }
    else               { LogERR ".git direktorijum NIJE pronađen" }

    # 2) remote origin
    $remotes = git remote
    if ($remotes -contains "origin") { LogOK "Remote 'origin' konfigurisan" }
    else                              { LogERR "Remote 'origin' NIJE konfigurisan" }

    # 3) trenutno na main
    $cur = git rev-parse --abbrev-ref HEAD
    if ($cur -eq "main") { LogOK "Nalaziš se na grani 'main'" }
    else                 { LogERR "Na grani si '$cur'; očekivana 'main'" }

    # 4) Kreiraj i pređi na test‐granu
    $ts = Get-Date -Format "yyyyMMddHHmmss"
    $testBranch = "test-auto-$ts"
    git checkout -b $testBranch
    LogOK "Kreirana i aktivirana test‐grana '$testBranch'"

    # 5) Podsetnik na orig HEAD
    $origHEAD = git rev-parse HEAD
    LogOK "Početni commit: $origHEAD"

    # 6) Izmeni README.md
    Add-Content -Path "README.md" -Value ("`n**AUTO_TEST $ts**")
    LogOK "Dodata test linija u README.md"

    # 7) Postavi upstream da auto_git_push uspe (samo za test granu)
    git push --set-upstream origin $testBranch
    LogOK "Test‐grana '$testBranch' postavljena na remote"

    # 8) Pokreni auto‐commit skriptu
    Write-Host "`n… Pokrećem auto_git_push.ps1 …" -ForegroundColor Cyan
    .\auto_git_push.ps1
    LogOK "auto_git_push.ps1 izvršen"

    Start-Sleep -Seconds 2

    # 9) Provera novog commita
    $newHEAD = git rev-parse HEAD
    if ($newHEAD -ne $origHEAD) { LogOK "Novi commit detektovan: $newHEAD" }
    else                         { LogERR "Nije kreiran novi commit" }

    # 10) Provera poruke commita
    $msg = git log -1 --pretty=format:"%s"
    if ($msg -match "^Auto-save") {
        LogOK "Commit poruka važeća: '$msg'"
    } else {
        LogERR "Commit poruka neočekivana: '$msg'"
    }
}
finally {
    Write-Host "`n=== ČIŠĆENJE ===" -ForegroundColor Cyan

    # vrati izmene
    git reset --hard HEAD~1 2>$null
    LogOK "Lokalan HEAD vraćen na $origHEAD"

    # vratimo se na main
    git checkout main 2>$null
    LogOK "Prelazak na main"

    # obriši lokalnu test‐granu
    git branch -D $testBranch 2>$null
    LogOK "Lokalna test‐grana obrisana"

    # obriši remote test‐granu
    git push origin --delete $testBranch 2>$null
    LogOK "Remote test‐grana izbrisana"
}

Write-Host "`n=== REZULTAT ===" -ForegroundColor Cyan
if ($errors -eq 0) {
    Write-Host "🎉 TEST PASSED: auto‐commit/push workflow radi besprekorno!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❗ TEST FAILED: pronađeno problema: $errors" -ForegroundColor Red
    exit 1
}
