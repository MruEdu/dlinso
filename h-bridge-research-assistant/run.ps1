# h-bridge 서브모듈 — 부모 dlinso_v2(E:\dlinso_v2) 기준
Set-Location $PSScriptRoot
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "가상환경이 없습니다. setup_and_run.ps1 을 먼저 실행하세요." -ForegroundColor Red
    exit 1
}
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
Start-Process "http://localhost:8501"
.\.venv\Scripts\python.exe -m streamlit run app.py
