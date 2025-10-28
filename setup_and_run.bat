@echo off
REM Employee Offboarding Tool - Automated Setup and Run Script for Windows
REM This script handles everything from setup to execution

setlocal enabledelayedexpansion

echo ===============================================================================
echo   Employee Offboarding Tool - Automated Setup ^& Run
echo ===============================================================================
echo.

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo [INFO] Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Found Python %PYTHON_VERSION%

REM Check if pip is installed
echo [INFO] Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed!
    echo [INFO] Installing pip...
    python -m ensurepip --default-pip
)
echo [SUCCESS] Found pip

REM Check for existing virtual environment
if exist "venv\" (
    echo [WARNING] Virtual environment already exists
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo [INFO] Removing existing virtual environment...
        rmdir /s /q venv
    ) else (
        echo [INFO] Using existing virtual environment
        goto :activate_venv
    )
)

REM Create virtual environment
echo [INFO] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created

:activate_venv
REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated

REM Install dependencies
echo [INFO] Installing dependencies...
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

echo [INFO] Installing Python packages (this may take a minute)...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo [INFO] Try running: pip install -r requirements.txt
    pause
    exit /b 1
)
echo [SUCCESS] All dependencies installed successfully

REM Check for credentials
echo [INFO] Checking for Google API credentials...
if exist "credentials.json" (
    echo [SUCCESS] Found credentials.json
) else (
    echo [WARNING] credentials.json not found
    echo.
    echo You need OAuth2 credentials from Google Cloud Console.
    echo.
    echo Quick setup:
    echo 1. Visit: https://console.cloud.google.com/apis/credentials
    echo 2. Create OAuth client ID (Desktop app^)
    echo 3. Download the JSON file
    echo 4. Save it as 'credentials.json' in this directory
    echo.
    pause

    if exist "credentials.json" (
        echo [SUCCESS] Found credentials.json
    ) else (
        echo [ERROR] credentials.json still not found!
        echo [INFO] The application will prompt you to provide credentials interactively
        echo.
        set /p CONTINUE="Continue anyway? (y/N): "
        if /i not "!CONTINUE!"=="y" (
            exit /b 1
        )
    )
)

echo.
echo [SUCCESS] Setup complete! Starting application...
echo.
timeout /t 2 /nobreak >nul

REM Run the application
echo [INFO] Starting Employee Offboarding Tool...
echo.

python main.py

set EXIT_CODE=%errorlevel%

echo.
if %EXIT_CODE% equ 0 (
    echo [SUCCESS] Application completed successfully
) else (
    echo [WARNING] Application exited with code %EXIT_CODE%
)

REM Deactivate virtual environment
call deactivate 2>nul

echo.
pause
exit /b %EXIT_CODE%
