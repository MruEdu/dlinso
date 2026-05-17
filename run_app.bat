@echo off
cd /d "%~dp0"
echo.
echo ========================================
echo  dlinso - 나의 지난 이야기 동반자
echo ========================================
echo  [터미널]  앱 실행 명령만 입력 (여기서 채팅 X)
echo  [브라우저] 대화/닉네임은 아래 주소 화면에서 입력
echo.
echo  http://localhost:8501
echo  미리보기: http://localhost:8501/?preview=1
echo ========================================
echo.
".venv\Scripts\python.exe" -m streamlit run app.py
pause
