@echo off
title FinanceFlow Dashboard
echo ================================================
echo   FinanceFlow Dashboard Starting...
echo   Built by Abhishek
echo ================================================
echo.
echo Dashboard will open at: http://localhost:8501
echo.
echo Starting dashboard...
streamlit run simple_dashboard.py --server.port 8501
pause
