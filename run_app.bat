@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo.
echo ========================================
echo  dlinso v2 - 서사 동행자 (Narrative Companion)
echo  프로젝트: %~dp0
echo ========================================
echo  http://localhost:8501
echo  preview: http://localhost:8501/?preview=1
echo  salon:   http://localhost:8501/?revealed=1
echo ========================================
echo.
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m streamlit run app.py
) else (
  echo 가상환경이 없습니다. setup_and_run.ps1 을 먼저 실행하세요.
  pause
  exit /b 1
)
pause
