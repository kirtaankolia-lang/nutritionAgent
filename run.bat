@echo off
:: ═══════════════════════════════════════════════════════════════
:: NutriGuide AI — IBM Granite Nutrition Planner
:: Setup & Launch Script for Windows
:: ═══════════════════════════════════════════════════════════════

title NutriGuide AI Launcher
color 1F

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║         NutriGuide — IBM Granite AI Nutrition Planner    ║
echo  ║         Agentic AI Application  ^|  HAM ^| AI Ethics       ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: ── Step 1: Check Python ─────────────────────────────────────
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Please install Python 3.10+ from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
python --version
echo  Python found.
echo.

:: ── Step 2: Navigate to script directory ─────────────────────
cd /d "%~dp0"
echo [2/5] Working directory: %CD%
echo.

:: ── Step 3: Create virtual environment if needed ─────────────
echo [3/5] Setting up virtual environment...
if not exist "venv\" (
    echo  Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  Virtual environment created.
) else (
    echo  Virtual environment already exists.
)
echo.

:: ── Step 4: Activate venv and install dependencies ───────────
echo [4/5] Installing dependencies...
call venv\Scripts\activate.bat

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Failed to install dependencies.
    echo  Check requirements.txt and your internet connection.
    pause
    exit /b 1
)
echo  All dependencies installed successfully.
echo.

:: ── Step 5: Check .env file ───────────────────────────────────
echo [5/5] Checking configuration...
if not exist ".env" (
    echo.
    echo  [NOTICE] No .env file found.
    echo  Copying .env.example to .env ...
    copy .env.example .env >nul
    echo.
    echo  ┌──────────────────────────────────────────────────────┐
    echo  │  ACTION REQUIRED: Open .env and set your credentials │
    echo  │                                                      │
    echo  │  WATSONX_API_KEY=your_api_key_here                   │
    echo  │  WATSONX_PROJECT_ID=your_project_id_here             │
    echo  │                                                      │
    echo  │  Get credentials at:                                 │
    echo  │  https://cloud.ibm.com/iam/apikeys                   │
    echo  └──────────────────────────────────────────────────────┘
    echo.
    echo  Press any key after updating .env to continue...
    pause >nul
) else (
    echo  .env file found.
)
echo.

:: ── Launch the Flask application ─────────────────────────────
echo  ════════════════════════════════════════════════════════
echo  Starting NutriGuide AI server...
echo  Open your browser and go to:  http://localhost:5000
echo  Press Ctrl+C to stop the server.
echo  ════════════════════════════════════════════════════════
echo.

:: Open browser after a short delay (in background)
start "" /min cmd /c "timeout /t 2 >nul && start http://localhost:5000"

:: Start Flask
python app.py

echo.
echo  Server stopped.
pause
