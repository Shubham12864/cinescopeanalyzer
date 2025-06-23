@echo off
echo Starting CineScope Analyzer...
echo.

echo Starting Backend Server...
start "Backend" cmd /c "cd /d backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for backend to start...
timeout /t 3 /nobreak

echo Starting Frontend Server...
start "Frontend" cmd /c "cd /d frontend && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000 (or 3001 if 3000 is busy)
echo.
echo Press any key to exit...
pause
