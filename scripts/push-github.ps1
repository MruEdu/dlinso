# Cursor 터미널(PowerShell)에서 GitHub로 푸시
# 사용법: .\scripts\push-github.ps1 "커밋 메시지"
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Message
)
$ErrorActionPreference = "Stop"
$root = git rev-parse --show-toplevel 2>$null
if (-not $root) { throw "Git 저장소가 아닙니다. 저장소 루트에서 실행하세요." }
Set-Location $root

git add -A
git status
git commit -m $Message
$branch = git branch --show-current
git push -u origin $branch
Write-Host "완료: origin/$branch 에 푸시했습니다." -ForegroundColor Green
