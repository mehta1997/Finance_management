Write-Host "Starting FinanceFlow Services..." -ForegroundColor Green

Write-Host "Starting API server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 5

Write-Host "Starting dashboard..." -ForegroundColor Yellow  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run dashboard.py --server.port 8501"

Start-Sleep -Seconds 8

Write-Host "Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:8501"

Write-Host "Services started! Dashboard URL: http://localhost:8501" -ForegroundColor Green
