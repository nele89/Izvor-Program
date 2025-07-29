# check_vs_code_git_integration.ps1
# Proverava Git ↔ VS Code integraciju za auto‐commit/push on save

function OK($msg)    { Write-Host "[OK]  $msg" -ForegroundColor Green }
function ERR($msg)   { Write-Host "[ERR] $msg" -ForegroundColor Red; $script:errors++ }

$errors = 0

# 1) .git direktorijum
if (Test-Path ".git") { OK ".git direktorijum pronadjen" }
else                 { ERR ".git direktorijum nije pronadjen" }

# 2) remote 'origin'
try {
    $r = git remote
    if ($r -contains "origin") { OK "Remote 'origin' postavljen" }
    else                       { ERR "Remote 'origin' nije postavljen" }
} catch {
    ERR "Git nije dostupan ili remote komanda nije uspela"
}

# 3) aktivna grana je main
try {
    $b = git rev-parse --abbrev-ref HEAD
    if ($b -eq "main") { OK "Aktivna grana je 'main'" }
    else               { ERR "Aktivna grana je '$b'; ocekivana je 'main'" }
} catch {
    ERR "Ne mogu da proverim aktivnu granu"
}

# 4) grana main prati origin
try {
    $t = git config branch.main.remote
    if ($t -eq "origin") { OK "Grana 'main' prati 'origin'" }
    else                 { ERR "Grana 'main' ne prati 'origin' (trenutno prati '$t')" }
} catch {
    ERR "Ne mogu da proverim tracking grane"
}

# 5) VS Code settings.json
$settings = ".vscode\settings.json"
if (Test-Path $settings) {
    OK "$settings pronadjen"
    $cfg = Get-Content $settings -Raw
    if ($cfg -match '"autogitcommit\.enable"\s*:\s*true' -and $cfg -match '"autogitcommit\.push"\s*:\s*true') {
        OK "autogitcommit.enable i autogitcommit.push su ispravno podeseni"
    } else {
        ERR "autogitcommit.enable/push nisu ispravno podeseni"
    }
    if ($cfg -match '"emeraldwalk\.runonsave"') {
        OK "runonsave konfiguracija pronadjena"
    } else {
        OK "runonsave konfiguracija nije obavezna"
    }
} else {
    ERR "$settings nije pronadjen"
}

# 6) skripta auto_git_push.ps1
if (Test-Path "auto_git_push.ps1") { OK "Skript auto_git_push.ps1 pronadjen" }
else                              { ERR "Skript auto_git_push.ps1 nije pronadjen" }

# 7) VS Code CLI i ekstenzije
try {
    & code --version > $null
    OK "VS Code CLI dostupan"
    $exts = code --list-extensions
    if ($exts -contains "YogeshValiya.autogitcommit") { OK "Ekstenzija Auto Git Commit and Push instalirana" }
    else                                              { ERR "Ekstenzija Auto Git Commit and Push nije instalirana" }
    if ($exts -contains "emeraldwalk.runonsave") { OK "Ekstenzija Run on Save instalirana" }
    else                                         { OK "Run on Save ekstenzija nije obavezna" }
} catch {
    ERR "VS Code CLI 'code' nije dostupan"
}

# Zakljucak
Write-Host "-----------------------------------"
if ($errors -eq 0) {
    Write-Host "SVE PROVERE USPESNE – mozete testirati Ctrl+S!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "PRONADJENO PROBLEMA: $errors – ispravite ih pa ponovite." -ForegroundColor Red
    exit 1
}
