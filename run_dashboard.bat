@echo off
title FinanceFlow Startup
echo ================================================
echo   FinanceFlow - Starting Services
echo   Built by Nabhi
echo ================================================

echo.
echo Starting FastAPI server on port 8000...
start "FinanceFlow API" /min cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo Waiting for API to start...
timeout /t 8 /nobreak >nul

echo.
echo Starting Streamlit dashboard on port 8501...
streamlit run dashboard.py --server.port 8501

pause
