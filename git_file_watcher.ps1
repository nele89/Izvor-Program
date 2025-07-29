# git_file_watcher.ps1
#  Watcher koji automatski git add/commit/push na svaku izmenu fajla

$folder = (Get-Location).Path
Write-Host "Watching for file changes in $folder ..." -ForegroundColor Cyan

$watcher = New-Object System.IO.FileSystemWatcher $folder -Property @{
    IncludeSubdirectories = $true
    Filter = "*.*"
    NotifyFilter = [System.IO.NotifyFilters]'FileName, LastWrite'
}

# Funkcija za akciju na izmenu
$action = {
    $path = $Event.SourceEventArgs.FullPath
    # preskoci .git folder, log fajlove i samu watcher skriptu
    if ($path -match '\\\.git\\' -or
        $path -match '\\logs\\' -or
        $path -match '\\git_file_watcher\.ps1$') {
        return
    }
    # kratka pauza da se fajl zatvori
    Start-Sleep -Milliseconds 200

    Set-Location $folder
    git add -A

    if (-not (git diff-index --quiet HEAD --)) {
        $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        $msg = "Auto-save: $([IO.Path]::GetFileName($path)) at $ts"
        git commit -m $msg
        git push
        Write-Host "Committed and pushed: $msg" -ForegroundColor Green
    }
}

# Registruj događaj
Register-ObjectEvent $watcher Changed -SourceIdentifier FileChanged -Action $action

# Uključi watcher
$watcher.EnableRaisingEvents = $true

# Ostani u sesiji dok korisnik ne pritisne Enter
Write-Host "Press Enter to stop watcher..." -ForegroundColor Yellow
[void][System.Console]::ReadLine()

# Čišćenje
Unregister-Event FileChanged
$watcher.Dispose()
Write-Host "Watcher stopped." -ForegroundColor Gray
