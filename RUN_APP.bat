@echo off
echo ========================================
echo    CITY VOICE - Starting Application
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

REM Navigate to script directory
cd /d "%~dp0"

echo Checking dependencies...
python -m pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies (first time setup)...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting City Voice application...
echo.
echo The app will open in your browser automatically.
echo To stop the app, close this window or press CTRL+C
echo.
echo ========================================
echo.

REM Run Streamlit
streamlit run core/unified_app.py

pause

