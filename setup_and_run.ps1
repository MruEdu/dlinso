# dlinso v2 — 새 PC 가상환경 생성 + 패키지 설치 + 앱 실행
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$pip = Join-Path $PSScriptRoot ".venv\Scripts\pip.exe"

if (-not (Test-Path $py)) {
    Write-Host "가상환경 생성 중..." -ForegroundColor Cyan
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Python이 필요합니다. https://www.python.org/downloads/ 에서 설치 후 다시 실행하세요." -ForegroundColor Red
        exit 1
    }
}

Write-Host "패키지 설치 중 (requirements.txt)..." -ForegroundColor Cyan
& $py -m pip install --upgrade pip
& $pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "패키지 설치 실패." -ForegroundColor Red
    exit 1
}

Write-Host "설치 완료. 앱을 시작합니다..." -ForegroundColor Green
& "$PSScriptRoot\run.ps1"
