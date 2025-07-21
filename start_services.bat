@echo off
echo ================================================
echo   FinanceFlow - Starting Services
echo   Built by Nabhi
echo ================================================
echo.

echo Starting FastAPI server...
start "FinanceFlow API" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak >nul

echo Starting Streamlit dashboard...
start "FinanceFlow Dashboard" cmd /k "streamlit run dashboard.py --server.port 8501"

echo.
echo ================================================
echo   Services Starting...
echo   API: http://localhost:8000
echo   Dashboard: http://localhost:8501
echo   API Docs: http://localhost:8000/docs
echo ================================================
echo.
echo Press any key to open dashboard in browser...
pause >nul
start http://localhost:8501
