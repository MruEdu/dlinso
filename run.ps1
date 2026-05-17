# dlinso — Streamlit 실행 (D:\dlinso)
Set-Location "D:\dlinso\h-bridge-research-assistant"
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "가상환경이 없습니다. setup_and_run.ps1 을 먼저 실행하세요." -ForegroundColor Red
    exit 1
}
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
Start-Process "http://localhost:8501"
.\.venv\Scripts\python.exe -m streamlit run app.py
