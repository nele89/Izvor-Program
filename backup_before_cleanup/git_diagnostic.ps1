<#
.SYNOPSIS
Detaljna diagnostika Git repozitorijuma za otkrivanje zašto se fajlovi ne push-uju na GitHub

.AUTHOR
AI Assistant
#>

# 1. Proveri osnovne Git informacije
Write-Host "`n=== OSVETLJAVANJE GIT PROBLEMA ===`n" -ForegroundColor Cyan
Write-Host "[1/5] Provera Git konfiguracije..." -ForegroundColor Yellow
git --version
git config --list | Select-String "user.name|user.email|remote.origin.url"

# 2. Proveri status repozitorijuma
Write-Host "`n[2/5] Provera Git statusa..." -ForegroundColor Yellow
git status
git rev-parse --abbrev-ref HEAD

# 3. Detaljna provera fajlova
Write-Host "`n[3/5] Analiza fajlova..." -ForegroundColor Yellow
$tracked = git ls-files | Measure-Object | Select-Object -ExpandProperty Count
$untracked = git ls-files --others --exclude-standard | Measure-Object | Select-Object -ExpandProperty Count

Write-Host "Praceni fajlovi: $tracked" -ForegroundColor Green
Write-Host "Nepraceni fajlovi: $untracked" -ForegroundColor $(if ($untracked -gt 0) { "Red" } else { "Green" })

if ($untracked -gt 0) {
    Write-Host "`nNepraceni fajlovi:" -ForegroundColor Red
    git ls-files --others --exclude-standard | ForEach-Object { " - $_" }
}

# 4. Provera velicina fajlova
Write-Host "`n[4/5] Provera velicina fajlova..." -ForegroundColor Yellow
Get-ChildItem -Recurse -File | 
    Where-Object { $_.FullName -notmatch '\.git' } | 
    Sort-Object Length -Descending | 
    Select-Object -First 10 Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}} | 
    Format-Table -AutoSize

# 5. Simulacija push-a sa debugom
Write-Host "`n[5/5] Testiranje push-a..." -ForegroundColor Yellow
$GIT_TRACE = 1
$GIT_CURL_VERBOSE = 1
git push origin main --dry-run 2>&1 | Out-Host

# Zakljucak
Write-Host "`n=== PREPORUKE ===" -ForegroundColor Cyan
if ($untracked -gt 0) {
    Write-Host "1. Dodaj nepratene fajlove sa: git add ." -ForegroundColor Yellow
}
Write-Host "2. Proveri da li remote postoji: git remote -v" -ForegroundColor Yellow
Write-Host "3. Ako problemi traju, pokušaj sa: git push -u origin main --force" -ForegroundColor Yellow
Write-Host "4. Za detaljnije logove pokreni: GIT_TRACE=1 GIT_CURL_VERBOSE=1 git push origin main" -ForegroundColor Yellow

Write-Host "`nSkripta zavrsena. Proverite izlaz za probleme." -ForegroundColor Green