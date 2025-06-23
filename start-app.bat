@echo off
echo Starting CineScope Analyzer...
cd backend
start cmd /k "python -m uvicorn app.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
cd ../frontend
start cmd /k "npm run dev"
echo App is starting...
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
pause