@echo off
TITLE TRAFFIC TREND — Road Accident Intelligence Platform
echo ========================================================
echo  TRAFFIC TREND — Road Safety Intelligence Platform
echo ========================================================
echo.

IF NOT EXIST ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not detected!
    echo Please run: python -m venv .venv
    echo And install requirements: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Activating Python virtual environment...
call .venv\Scripts\activate.bat

echo Launching Streamlit application...
streamlit run app.py

pause

