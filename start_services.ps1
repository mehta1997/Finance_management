Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   FinanceFlow - Starting Services" -ForegroundColor Green
Write-Host "   Built by Nabhi" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🚀 Starting FastAPI server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; Read-Host 'Press Enter to close'"

Start-Sleep -Seconds 5

Write-Host "📊 Starting Streamlit dashboard..." -ForegroundColor Green  
Start-Process powershell -ArgumentList "-Command", "streamlit run dashboard.py --server.port 8501"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Services Starting..." -ForegroundColor Yellow
Write-Host "   API: http://localhost:8000" -ForegroundColor White
Write-Host "   Dashboard: http://localhost:8501" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

Write-Host "🌐 Opening dashboard in browser..." -ForegroundColor Green
Start-Process "http://localhost:8501"

Write-Host ""
Write-Host "✅ Services started successfully!" -ForegroundColor Green
Write-Host 'If the dashboard does not open automatically, go to: http://localhost:8501' -ForegroundColor Yellow
