# auto_git_push.ps1
Set-Location $PSScriptRoot
git add -A
if (-not (git diff-index --quiet HEAD --)) {
  $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  git commit -m "Auto-save at $ts"
  git push
}
