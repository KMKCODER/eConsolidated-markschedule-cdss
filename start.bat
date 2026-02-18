@echo off
echo Starting eConsolidated Mark Schedule System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing/updating dependencies...
pip install -r requirements.txt

REM Run the application
echo.
echo ===============================================
echo   eConsolidated Mark Schedule System
echo   Starting server at http://127.0.0.1:5000
echo   Default login: admin / admin123
echo ===============================================
echo.
python app.py

pause