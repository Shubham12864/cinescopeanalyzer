@echo off
title CineScope Analyzer - Starting...
color 0A

echo ================================
echo   CineScope Analyzer Startup
echo ================================
echo.

:: Set the project root directory
set PROJECT_ROOT=C:\Users\Acer\Downloads\CineScopeAnalyzer
set BACKEND_DIR=%PROJECT_ROOT%\backend
set FRONTEND_DIR=%PROJECT_ROOT%\frontend

:: Check if project directory exists
if not exist "%PROJECT_ROOT%" (
    echo ERROR: Project directory not found at %PROJECT_ROOT%
    echo Please check the path and try again.
    pause
    exit /b 1
)

echo Project Root: %PROJECT_ROOT%
echo Backend Dir:  %BACKEND_DIR%
echo Frontend Dir: %FRONTEND_DIR%
echo.

:: Change to project root
cd /d "%PROJECT_ROOT%"

echo ================================
echo   Checking Dependencies...
echo ================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
) else (
    echo ✓ Python is installed
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
) else (
    echo ✓ Node.js is installed
)

:: Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed or not in PATH
    pause
    exit /b 1
) else (
    echo ✓ npm is installed
)

echo.
echo ================================
echo   Installing Dependencies...
echo ================================

:: Install backend dependencies
echo Installing Python dependencies...
cd /d "%BACKEND_DIR%"
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install Python dependencies
        pause
        exit /b 1
    )
    echo ✓ Python dependencies installed
) else (
    echo WARNING: requirements.txt not found, installing basic dependencies...
    pip install fastapi uvicorn pydantic python-dotenv httpx aiofiles python-multipart jinja2
)

:: Install frontend dependencies
echo Installing Node.js dependencies...
cd /d "%FRONTEND_DIR%"
if exist package.json (
    if not exist node_modules (
        echo Running npm install...
        npm install
        if errorlevel 1 (
            echo ERROR: Failed to install Node.js dependencies
            pause
            exit /b 1
        )
    )
    echo ✓ Node.js dependencies ready
) else (
    echo ERROR: package.json not found in frontend directory
    pause
    exit /b 1
)

echo.
echo ================================
echo   Starting Servers...
echo ================================

:: Kill any existing processes on ports 3000 and 8000
echo Checking for existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a on port 8000...
    taskkill /f /pid %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    echo Killing process %%a on port 3000...
    taskkill /f /pid %%a >nul 2>&1
)

:: Start Backend Server
echo Starting Backend Server (Port 8000)...
cd /d "%BACKEND_DIR%"
start "CineScope Backend" cmd /k "title CineScope Backend - Port 8000 & echo Backend Server Starting... & python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Wait a moment for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

:: Start Frontend Server
echo Starting Frontend Server (Port 3000)...
cd /d "%FRONTEND_DIR%"
start "CineScope Frontend" cmd /k "title CineScope Frontend - Port 3000 & echo Frontend Server Starting... & npm run dev"

:: Wait for frontend to start
echo Waiting for frontend to initialize...
timeout /t 8 /nobreak >nul

echo.
echo ================================
echo   Application Started!
echo ================================
echo.
echo ✓ Backend Server:  http://localhost:8000
echo ✓ Frontend App:    http://localhost:3000
echo ✓ API Docs:        http://localhost:8000/docs
echo ✓ API Redoc:       http://localhost:8000/redoc
echo.
echo Opening application in browser...

:: Open the application in default browser
timeout /t 3 /nobreak >nul
start "" "http://localhost:3000"

echo.
echo ================================
echo   Server Management
echo ================================
echo.
echo The servers are now running in separate windows.
echo To stop the servers, close their respective command windows.
echo.
echo Press any key to view server status or Ctrl+C to exit...
pause >nul

:status_loop
cls
echo ================================
echo   CineScope Analyzer Status
echo ================================
echo.

:: Check if backend is running
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend:  Offline (Port 8000)
) else (
    echo ✅ Backend:  Running (Port 8000)
)

:: Check if frontend is running
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend: Offline (Port 3000)
) else (
    echo ✅ Frontend: Running (Port 3000)
)

echo.
echo Commands:
echo [1] Open Frontend (http://localhost:3000)
echo [2] Open Backend API Docs (http://localhost:8000/docs)
echo [3] Refresh Status
echo [4] Stop All Servers
echo [5] Exit Monitor
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" start "" "http://localhost:3000"
if "%choice%"=="2" start "" "http://localhost:8000/docs"
if "%choice%"=="3" goto status_loop
if "%choice%"=="4" goto stop_servers
if "%choice%"=="5" goto end

goto status_loop

:stop_servers
echo.
echo Stopping all servers...

:: Kill processes on ports 3000 and 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping backend server (PID: %%a)...
    taskkill /f /pid %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    echo Stopping frontend server (PID: %%a)...
    taskkill /f /pid %%a >nul 2>&1
)

echo ✓ All servers stopped.
timeout /t 2 /nobreak >nul

:end
echo.
echo Thank you for using CineScope Analyzer!
echo.
pause