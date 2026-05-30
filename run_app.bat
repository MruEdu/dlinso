@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo.
echo ========================================
echo  dlinso v2 - 서사 동행자 (Narrative Companion)
echo  프로젝트: %~dp0  (E:\dlinso_v2 만 사용)
echo ========================================
echo  http://localhost:8501
echo  preview: http://localhost:8501/?preview=1
echo  salon:   http://localhost:8501/?revealed=1
echo ========================================
echo.
python -m streamlit run app.py
pause
